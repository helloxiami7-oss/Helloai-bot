
import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters
)
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

histories = {}

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    chat_id = message.chat_id
    histories.setdefault(chat_id, [])

    histories[chat_id].append({
        "role": "user",
        "content": message.text
    })

    try:
        response = await asyncio.to_thread(
            client.responses.create,
            model="gpt-5.5",
            instructions=(
                "Sen samimiy, aqlli va odobli shaxsiy AI yordamchisan. "
                "O'zbek tilida tabiiy, qisqa va tushunarli gapir. "
                "Suhbatdosh bilan hurmat bilan muomala qil."
            ),
            input=histories[chat_id][-20:]
        )

        answer = response.output_text
        histories[chat_id].append({
            "role": "assistant",
            "content": answer
        })

        await message.reply_text(answer)

    except Exception:
        await message.reply_text(
            "Kechirasiz, hozir javob bera olmadim. Qayta urinib ko'ring."
        )

def main():
    app = ApplicationBuilder().token(
        os.environ["TELEGRAM_BOT_TOKEN"]
    ).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, reply)
    )

    app.run_polling()

if __name__ == "__main__":
    main()
