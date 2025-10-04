import os
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions

BOT_TOKEN = os.environ["8438358592:AAG1HhPeJVM7FXkUJTTspcKVQRZnPazURX4"]
API_ID = int(os.environ["29091290"])
API_HASH = os.environ["5e17bf0a5ed30289842f686647b48da5"]

app = Client("management_bot", api_id=29091290, api_hash=5e17bf0a5ed30289842f686647b48da5, bot_token=8438358592:AAG1HhPeJVM7FXkUJTTspcKVQRZnPazURX4)

@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    for new_member in message.new_chat_members:
        await message.reply_text(f"👋 Welcome, {new_member.first_name}!\nPlease read the rules with /rules.")

@app.on_message(filters.command("rules") & filters.group)
async def show_rules(client, message):
    rules = "1. Be respectful.\n2. No spam.\n3. Follow admin instructions."
    await message.reply_text(f"📜 Group Rules:\n{rules}")

@app.on_message(filters.command("ban") & filters.group)
async def ban(client, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to ban them.")
        return
    user = message.reply_to_message.from_user
    await client.kick_chat_member(message.chat.id, user.id)
    await message.reply_text(f"🚫 {user.first_name} has been banned!")

@app.on_message(filters.command("unban") & filters.group)
async def unban(client, message):
    if len(message.command) < 2:
        await message.reply_text("Send: /unban <user_id>")
        return
    try:
        user_id = int(message.command[1])
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"✅ User {user_id} has been unbanned!")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@app.on_message(filters.command("mute") & filters.group)
async def mute(client, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to mute them.")
        return
    user = message.reply_to_message.from_user
    await client.restrict_chat_member(
        message.chat.id,
        user.id,
        permissions=ChatPermissions(can_send_messages=False)
    )
    await message.reply_text(f"🔇 {user.first_name} has been muted!")

@app.on_message(filters.command("unmute") & filters.group)
async def unmute(client, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to unmute them.")
        return
    user = message.reply_to_message.from_user
    await client.restrict_chat_member(
        message.chat.id,
        user.id,
        permissions=ChatPermissions(can_send_messages=True)
    )
    await message.reply_text(f"🔊 {user.first_name} has been unmuted!")

@app.on_message(filters.command("tagall") & filters.group)
async def tagall(client, message):
    mentions = []
    async for member in client.get_chat_members(message.chat.id):
        if not member.user.is_bot:
            mentions.append(f"@{member.user.username}" if member.user.username else member.user.first_name)
    if mentions:
        await message.reply_text(" ".join(mentions))
    else:
        await message.reply_text("No members to tag.")

@app.on_message(filters.command("stats") & filters.group)
async def stats(client, message):
    members = await client.get_chat_members_count(message.chat.id)
    admins = await client.get_chat_members(message.chat.id, filter="administrators")
    admin_names = ", ".join([admin.user.first_name for admin in admins])
    await message.reply_text(f"👥 Members: {members}\n🛡 Admins: {admin_names}")

app.run()
