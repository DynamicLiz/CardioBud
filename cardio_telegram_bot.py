from telegram.ext import Updater, CommandHandler

BOT_TOKEN = 8220693959:AAHLSHfJBt7LJmet0-CquZWU4SE0uJuOl1o

def start(update, context):
    update.message.reply_text("✅ Bot is connected!")

updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))

updater.start_polling()
updater.idle()
