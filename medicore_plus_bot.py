
import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import logging

TOKEN = "8464909663:AAG8FwClHrnDdwz-bXsaN8A4M-pQGzu_H7U"

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load MCQs
with open("mcqs.json", "r") as f:
    mcqs = json.load(f)

# Load tips
with open("tips.json", "r") as f:
    tips = json.load(f)

# Load mnemonics
with open("mnemonics.json", "r") as f:
    mnemonics = json.load(f)

# Load Anki flashcards
with open("anki_cards.json", "r") as f:
    anki_cards = json.load(f)

# Load PDF links
with open("pdfs.json", "r") as f:
    pdfs = json.load(f)

# Load user scores
try:
    with open("scores.json", "r") as f:
        scores = json.load(f)
except:
    scores = {}

# Save scores
def save_scores():
    with open("scores.json", "w") as f:
        json.dump(scores, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍⚕️ Welcome to MediCore+ Bot!

Commands:
/mcq – Advanced MCQ
/case – Clinical scenario
/mnemonic – Memory aid
/tip – Study tip
/anki – Flashcard
/pdf – Get PDF
/score – Your score"
    )

async def mcq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(mcqs)
    question = q["question"]
    options = q["options"]
    answer = q["answer"]
    explanation = q["explanation"]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"{opt}|{answer}|{explanation}")]
        for opt in options
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"📘 *MCQ:*

{question}", parse_mode='Markdown', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = str(query.from_user.id)
    selected, correct, explanation = query.data.split("|")
    if user not in scores:
        scores[user] = 0
    if selected == correct:
        scores[user] += 1
        reply = f"✅ Correct!\n
Explanation: {explanation}"
    else:
        reply = f"❌ Wrong. Correct answer: {correct}\n
Explanation: {explanation}"
    save_scores()
    await query.edit_message_text(text=reply)

async def tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 " + random.choice(tips))

async def mnemonic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 " + random.choice(mnemonics))

async def anki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    card = random.choice(anki_cards)
    await update.message.reply_text(f"🗂️ *Q:* {card['front']}

*A:* {card['back']}", parse_mode='Markdown')

async def pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = random.choice(pdfs)
    await update.message.reply_text(f"📄 *{file['title']}*:
{file['url']}", parse_mode='Markdown')

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = str(update.message.from_user.id)
    sc = scores.get(user, 0)
    await update.message.reply_text(f"📊 Your current score: {sc}")

def scheduled_post(app):
    async def job():
        bot = await app.bot.get_me()
        await app.bot.send_message(chat_id=bot.id, text="🕘 Time for your daily MCQ!")
    return job

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mcq", mcq))
app.add_handler(CommandHandler("tip", tip))
app.add_handler(CommandHandler("mnemonic", mnemonic))
app.add_handler(CommandHandler("anki", anki))
app.add_handler(CommandHandler("pdf", pdf))
app.add_handler(CommandHandler("score", score))
app.add_handler(CallbackQueryHandler(button))

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_post(app), "cron", hour=3, minute=30)  # 9:00 AM IST
scheduler.start()

app.run_polling()
