from telegram.ext import Updater, MessageHandler, Filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

def reply_message(text):
    text = text.lower()

    if "hello" in text or "hi" in text:
        return "Hello! How can I help you today?"

    if "help" in text:
        return "Sure! Tell me what you need help with."

    if "your name" in text:
        return "I'm your friendly Telegram bot!"

    return "I didn't fully understand that, but I'm here to help!"

def handle_message(update, context):
    user_text = update.message.text
    response = reply_message(user_text)
    update.message.reply_text(response)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
