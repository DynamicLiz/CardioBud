from telegram.ext import Updater, CommandHandler
import os

BOT_TOKEN = os.getenv("8376707878:AAFNAVK1GTL9BWLLG6YKOQME8DIGNW2AZZE")

def start(update, context):
    update.message.reply_text("✅ Bot is connected!")

updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))

updater.start_polling()
updater.idle()
