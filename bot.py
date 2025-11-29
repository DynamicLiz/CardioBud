import logging
from telegram.ext import Updater, MessageHandler, Filters
import requests
import os

logging.basicConfig(level=logging.INFO)

# Load keys from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_reply(user_message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    body = {
        "contents": [
            {"parts": [{"text": user_message}]}
        ]
    }

    try:
        response = requests.post(url, json=body)
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Error:", e)
        return "Sorry, I couldn't process that."

def handle_message(update, context):
    user_text = update.message.text
    reply = generate_reply(user_text)

    update.message.reply_text(reply)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
