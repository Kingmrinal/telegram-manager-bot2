from telegram import Update, ChatPermissions
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import config
import time

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I'm your Rose clone bot 🤖")

# Welcome new members
def welcome(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        update.message.reply_text(config.WELCOME_MESSAGE.format(first_name=member.first_name))

# Ban user
def ban(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        update.message.reply_text("Reply to a user's message to ban them.")
        return
    user = update.message.reply_to_message.from_user
    context.bot.kick_chat_member(update.message.chat_id, user.id)
    update.message.reply_text(f"Banned {user.first_name} ✅")

# Unban user
def unban(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /unban <user_id>")
        return
    user_id = int(context.args[0])
    context.bot.unban_chat_member(update.message.chat_id, user_id)
    update.message.reply_text(f"Unbanned user {user_id} ✅")

# Anti-spam filter
LAST_MESSAGES = {}
def anti_spam(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    now = time.time()

    if user_id in LAST_MESSAGES:
        if now - LAST_MESSAGES[user_id] < 2:  # Messages within 2 seconds
            update.message.delete()
            return
    LAST_MESSAGES[user_id] = now

    # Anti-bad word filter
    text = update.message.text.lower()
    for word in config.BAD_WORDS:
        if word in text:
            update.message.delete()
            update.message.reply_text(f"{update.message.from_user.first_name}, bad word detected 🚫")
            return

# Pin a message
def pin(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        update.message.reply_text("Reply to a message to pin it.")
        return
    context.bot.pin_chat_message(update.message.chat_id, update.message.reply_to_message.message_id)
    update.message.reply_text("Message pinned 📌")

def main():
    updater = Updater(config.TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ban", ban))
    dp.add_handler(CommandHandler("unban", unban))
    dp.add_handler(CommandHandler("pin", pin))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, anti_spam))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

