import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = "8661344486:AAFZ5-x5hxTz0I6eTJKVmKcmXEYmWedPw2Y"
FASTAPI_URL = "http://localhost:8000/run_blueprint"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Multi-Agent System Live!\nUsage: /trade EURUSD=X 15m Trend-Following Strategy"
    )


async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_text = (
        " ".join(context.args)
        if context.args
        else "EURUSD=X 15m scalp trading strategy"
    )

    status_msg = await update.message.reply_text(
        "⏳ Agent pipeline executing... (Fetching live market data & running Worker ➔ Reviewer loop)"
    )

    try:
        payload = {"task": task_text, "max_iterations": 2}
        response = requests.post(FASTAPI_URL, json=payload, timeout=180)

        if response.status_code == 200:
            data = response.json()
            output = data.get("worker_output", "No output generated.")
            status = data.get("review_status", "UNKNOWN")

            reply_text = f"✅ **Status:** {status}\n\n**Strategy Output:**\n{output}"
        else:
            reply_text = f"❌ Error from backend pipeline: HTTP {response.status_code}"

    except Exception as e:
        reply_text = f"❌ Pipeline Exception: {str(e)}"

    # Truncate if output exceeds Telegram message limits (4096 chars)
    if len(reply_text) > 4000:
        reply_text = reply_text[:4000] + "\n\n...[Truncated]"

    await status_msg.edit_text(reply_text, parse_mode="Markdown")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Exception while handling an update:", exc_info=context.error)


def main():
    request = HTTPXRequest(read_timeout=60.0, connect_timeout=30.0)
    app = ApplicationBuilder().token(TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trade", trade))
    app.add_error_handler(error_handler)

    print("🤖 Async Telegram Bot active and listening...")
    app.run_polling(poll_interval=1.0)


if __name__ == "__main__":
    main()
