import os
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

# Environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# -------------------
# Memory / Data Stores
# -------------------
user_data = {}  # Stores medication logs, symptoms, quiz scores

# -------------------
# Helper Functions
# -------------------
def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"meds": [], "symptoms": [], "quiz_score": 0}
    return user_data[user_id]

# -------------------
# Command Handlers
# -------------------
def start(update: Update, context: CallbackContext):
    keyboard = [[
        InlineKeyboardButton("Education", callback_data='education'),
        InlineKeyboardButton("Medication Log", callback_data='medlog')
    ],[
        InlineKeyboardButton("Symptom Checker", callback_data='symptoms'),
        InlineKeyboardButton("Quiz", callback_data='quiz')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome to the Heart Health Bot! Choose an option:', reply_markup=reply_markup)

# -------------------
# Callback Query (Buttons)
# -------------------
quiz_questions = [
    {"q": "Which activity is best for heart health?", "options": ["Running", "Sleeping", "Watching TV"], "answer": "Running"},
    {"q": "Which food is best for reducing cholesterol?", "options": ["Fried chicken", "Oats", "Candy"], "answer": "Oats"}
]

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = get_user(query.from_user.id)
    query.answer()

    if query.data == 'education':
        query.edit_message_text("Heart disease is the leading cause of death globally. Tips:\n- Exercise 30 mins/day\n- Eat fruits & vegetables\n- Limit salt & sugar")

    elif query.data == 'medlog':
        query.edit_message_text("Use /log_med <med_name> to add a medication, /view_meds to see your list.")

    elif query.data == 'symptoms':
        query.edit_message_text("Use /symptom <symptom> to log a symptom. Example: /symptom chest pain")

    elif query.data == 'quiz':
        user['current_q'] = 0
        send_quiz_question(query, user)

def send_quiz_question(query, user):
    q_index = user.get('current_q', 0)
    if q_index >= len(quiz_questions):
        query.edit_message_text(f"Quiz finished! Your score: {user['quiz_score']}/{len(quiz_questions)}")
        user['quiz_score'] = 0
        return

    q = quiz_questions[q_index]
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"answer_{opt}")] for opt in q['options']]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(q['q'], reply_markup=reply_markup)

# -------------------
# Answer handler
# -------------------
def handle_quiz_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    user = get_user(query.from_user.id)
    query.answer()

    q_index = user.get('current_q', 0)
    if q_index >= len(quiz_questions):
        return

    q = quiz_questions[q_index]
    selected = query.data.replace('answer_', '')
    if selected == q['answer']:
        user['quiz_score'] += 1
        result = "Correct!"
    else:
        result = f"Wrong! Correct answer: {q['answer']}"

    user['current_q'] += 1
    query.edit_message_text(result)

    # Send next question after 2s
    threading.Timer(2, lambda: send_next_question(query, user)).start()

def send_next_question(query, user):
    send_quiz_question(query, user)

# -------------------
# Medication commands
# -------------------
def log_med(update: Update, context: CallbackContext):
    user = get_user(update.message.from_user.id)
    med = ' '.join(context.args)
    if not med:
        update.message.reply_text("Please specify a medication. Example: /log_med Aspirin")
        return
    user['meds'].append(med)
    update.message.reply_text(f"Logged medication: {med}")

def view_meds(update: Update, context: CallbackContext):
    user = get_user(update.message.from_user.id)
    meds = user['meds']
    if meds:
        update.message.reply_text("Your medications:\n" + '\n'.join(meds))
    else:
        update.message.reply_text("You have no medications logged.")

# -------------------
# Symptom commands
# -------------------
def symptom(update: Update, context: CallbackContext):
    user = get_user(update.message.from_user.id)
    symp = ' '.join(context.args)
    if not symp:
        update.message.reply_text("Please specify a symptom. Example: /symptom chest pain")
        return
    user['symptoms'].append(symp)
    advice = "Monitor your symptoms. Seek medical attention if severe or persistent." 
    if "chest pain" in symp.lower() or "shortness of breath" in symp.lower():
        advice = "⚠️ Alert! Seek medical attention immediately."
    update.message.reply_text(f"Logged symptom: {symp}\nAdvice: {advice}")

# -------------------
# Message fallback
# -------------------
def handle_text(update: Update, context: CallbackContext):
    update.message.reply_text("Use /start to see the menu or type a command like /log_med, /view_meds, /symptom, /quiz")

# -------------------
# Main
# -------------------
updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher

# Commands
 dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("log_med", log_med))
dp.add_handler(CommandHandler("view_meds", view_meds))
dp.add_handler(CommandHandler("symptom", symptom))

# Button callbacks
 dp.add_handler(CallbackQueryHandler(handle_quiz_answer, pattern='^answer_'))
dp.add_handler(CallbackQueryHandler(button, pattern='^(education|medlog|symptoms|quiz)$'))

# Text fallback
 dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

updater.start_polling()
updater.idle()
