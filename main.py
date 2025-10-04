import os
import json
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions

BOT_TOKEN = os.environ["BOT_TOKEN"]
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]

app = Client("rose_like_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Storage files
RULES_FILE = "rules.json"
WELCOME_FILE = "welcome.json"
WARNS_FILE = "warns.json"
FILTERS_FILE = "filters.json"

# Load or init storage
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

group_rules = load_json(RULES_FILE)
welcome_msgs = load_json(WELCOME_FILE)
warns = load_json(WARNS_FILE)
filters_dict = load_json(FILTERS_FILE)

# -------- RULES --------
@app.on_message(filters.command("setrules") & filters.group)
async def setrules(_, m):
    if len(m.command) < 2:
        return await m.reply("Usage: /setrules <rules>")
    text = m.text.split(None, 1)[1]
    group_rules[str(m.chat.id)] = text
    save_json(RULES_FILE, group_rules)
    await m.reply("✅ Rules updated!")

@app.on_message(filters.command("rules") & filters.group)
async def rules(_, m):
    text = group_rules.get(str(m.chat.id), "No rules set.")
    await m.reply(f"📜 Rules:\n{text}")

# -------- WELCOME --------
@app.on_message(filters.command("welcome") & filters.group)
async def welcome_set(_, m):
    if len(m.command) < 2:
        return await m.reply("Usage: /welcome <text>")
    text = m.text.split(None, 1)[1]
    welcome_msgs[str(m.chat.id)] = text
    save_json(WELCOME_FILE, welcome_msgs)
    await m.reply("✅ Welcome message set!")

@app.on_message(filters.command("disablewelcome") & filters.group)
async def welcome_disable(_, m):
    welcome_msgs.pop(str(m.chat.id), None)
    save_json(WELCOME_FILE, welcome_msgs)
    await m.reply("🚫 Welcome disabled.")

@app.on_message(filters.new_chat_members)
async def greet(_, m):
    text = welcome_msgs.get(str(m.chat.id))
    if text:
        for u in m.new_chat_members:
            await m.reply(text.replace("{first_name}", u.first_name))

# -------- MODERATION --------
@app.on_message(filters.command("ban") & filters.group)
async def ban(_, m):
    if not m.reply_to_message:
        return await m.reply("Reply to ban.")
    user = m.reply_to_message.from_user
    await _.ban_chat_member(m.chat.id, user.id)
    await m.reply(f"🚫 {user.mention} banned!")

@app.on_message(filters.command("unban") & filters.group)
async def unban(_, m):
    if len(m.command) < 2:
        return await m.reply("Usage: /unban <user_id>")
    uid = int(m.command[1])
    await _.unban_chat_member(m.chat.id, uid)
    await m.reply(f"✅ User {uid} unbanned!")

@app.on_message(filters.command("kick") & filters.group)
async def kick(_, m):
    if not m.reply_to_message:
        return await m.reply("Reply to kick.")
    user = m.reply_to_message.from_user
    await _.ban_chat_member(m.chat.id, user.id)
    await _.unban_chat_member(m.chat.id, user.id)
    await m.reply(f"👢 {user.mention} kicked!")

@app.on_message(filters.command("mute") & filters.group)
async def mute(_, m):
    if not m.reply_to_message:
        return await m.reply("Reply to mute.")
    user = m.reply_to_message.from_user
    await _.restrict_chat_member(m.chat.id, user.id, ChatPermissions(can_send_messages=False))
    await m.reply(f"🔇 {user.mention} muted!")

@app.on_message(filters.command("unmute") & filters.group)
async def unmute(_, m):
    if not m.reply_to_message:
        return await m.reply("Reply to unmute.")
    user = m.reply_to_message.from_user
    await _.restrict_chat_member(m.chat.id, user.id, ChatPermissions(can_send_messages=True))
    await m.reply(f"🔊 {user.mention} unmuted!")

# -------- WARNINGS --------
@app.on_message(filters.command("warn") & filters.group)
async def warn(_, m):
    if not m.reply_to_message:
        return await m.reply("Reply to warn.")
    user = m.reply_to_message.from_user
    chat_id = str(m.chat.id)
    warns.setdefault(chat_id, {})
    warns[chat_id].setdefault(str(user.id), 0)
    warns[chat_id][str(user.id)] += 1
    save_json(WARNS_FILE, warns)
    count = warns[chat_id][str(user.id)]
    if count >= 3:
        await _.ban_chat_member(m.chat.id, user.id)
        await m.reply(f"🚨 {user.mention} warned 3 times → banned!")
    else:
        await m.reply(f"⚠️ {user.mention} warned ({count}/3)")

@app.on_message(filters.command("warns") & filters.group)
async def warns_list(_, m):
    if not m.reply_to_message:
        return await m.reply("Reply to see warns.")
    user = m.reply_to_message.from_user
    count = warns.get(str(m.chat.id), {}).get(str(user.id), 0)
    await m.reply(f"⚠️ {user.mention} has {count} warns.")

@app.on_message(filters.command("resetwarns") & filters.group)
async def resetwarns(_, m):
    if not m.reply_to_message:
        return await m.reply("Reply to reset warns.")
    user = m.reply_to_message.from_user
    warns.get(str(m.chat.id), {}).pop(str(user.id), None)
    save_json(WARNS_FILE, warns)
    await m.reply(f"✅ Warns reset for {user.mention}")

# -------- FILTERS --------
@app.on_message(filters.command("filter") & filters.group)
async def add_filter(_, m):
    if len(m.command) < 3:
        return await m.reply("Usage: /filter <word> <reply>")
    _, word, reply = m.text.split(None, 2)
    filters_dict.setdefault(str(m.chat.id), {})
    filters_dict[str(m.chat.id)][word.lower()] = reply
    save_json(FILTERS_FILE, filters_dict)
    await m.reply(f"✅ Filter set for '{word}'")

@app.on_message(filters.command("stopfilter") & filters.group)
async def remove_filter(_, m):
    if len(m.command) < 2:
        return await m.reply("Usage: /stopfilter <word>")
    word = m.command[1].lower()
    filters_dict.get(str(m.chat.id), {}).pop(word, None)
    save_json(FILTERS_FILE, filters_dict)
    await m.reply(f"🗑 Filter '{word}' removed.")

@app.on_message(filters.command("filters") & filters.group)
async def list_filters(_, m):
    fl = filters_dict.get(str(m.chat.id), {})
    if not fl:
        return await m.reply("No filters set.")
    text = "\n".join([f"- {k}: {v}" for k,v in fl.items()])
    await m.reply(f"📌 Filters:\n{text}")

@app.on_message(filters.text & filters.group)
async def auto_reply(_, m):
    fl = filters_dict.get(str(m.chat.id), {})
    for word, reply in fl.items():
        if word in m.text.lower():
            return await m.reply(reply)

# -------- EXTRA --------
@app.on_message(filters.command("stats") & filters.group)
async def stats(_, m):
    members = await _.get_chat_members_count(m.chat.id)
    admins = await _.get_chat_members(m.chat.id, filter="administrators")
    admins_list = ", ".join([a.user.first_name for a in admins])
    await m.reply(f"👥 Members: {members}\n🛡 Admins: {admins_list}")

@app.on_message(filters.command("info") & filters.group)
async def info(_, m):
    if m.reply_to_message:
        u = m.reply_to_message.from_user
    else:
        u = m.from_user
    await m.reply(f"ℹ️ User Info:\nID: {u.id}\nName: {u.first_name}\nUsername: @{u.username if u.username else 'N/A'}")

@app.on_message(filters.command("tagall") & filters.group)
async def tagall(_, m):
    mentions = []
    async for member in _.get_chat_members(m.chat.id):
        if not member.user.is_bot:
            mentions.append(member.user.mention)
    if mentions:
        await m.reply(" ".join(mentions))

@app.on_message(filters.command("pin") & filters.group)
async def pin(_, m):
    if not m.reply_to_message:
        return await m.reply("Reply to a message to pin.")
    await _.pin_chat_message(m.chat.id, m.reply_to_message.id)
    await m.reply("📌 Pinned!")

@app.on_message(filters.command("unpin") & filters.group)
async def unpin(_, m):
    await _.unpin_chat_message(m.chat.id)
    await m.reply("📍 Unpinned.")

@app.on_message(filters.command("purge") & filters.group)
async def purge(_, m):
    if not m.reply_to_message:
        return await m.reply("Reply to a message to start purge.")
    start_id = m.reply_to_message.id
    end_id = m.id
    for msg_id in range(start_id, end_id):
        try:
            await _.delete_messages(m.chat.id, msg_id)
        except:
            pass
    await m.reply("🧹 Purge complete.")

app.run()
