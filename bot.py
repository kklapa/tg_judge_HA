import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL = "mistral-medium"

chat_logs = {}

async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    if chat_id not in chat_logs:
        chat_logs[chat_id] = []
    chat_logs[chat_id].append(text)
    chat_logs[chat_id] = chat_logs[chat_id][-200:]

async def judge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in chat_logs or len(chat_logs[chat_id]) < 10:
        await update.message.reply_text("Замало повідомлень для аналізу (мінімум 10).")
        return

    history = "\n".join(chat_logs[chat_id])

    system_prompt = (
        "Ти — нейтральний суддя у груповому чаті. "
        "Формат відповіді:\n"
        "1️⃣ Аргументи кожної сторони\n"
        "2️⃣ Аналіз\n"
        "3️⃣ Висновок"
    )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": history}
        ],
        "max_tokens": 500,
        "temperature": 0.5
    }

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(MISTRAL_URL, headers=headers, json=payload)
    data = response.json()

    try:
        reply_text = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        reply_text = f"Помилка від API: {e}\n{data}"

    await update.message.reply_text(reply_text)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("judge", judge))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_message))
    print("🤖 Бот запущений!")
    app.run_polling()

if __name__ == "__main__":
    main()
