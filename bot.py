import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Telegram bot token (set BOT_TOKEN as an environment variable)
TOKEN = os.environ.get("BOT_TOKEN")

# Store user chat IDs in memory (cleared when the bot restarts)
user_chat_ids = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the welcome message and save the user's chat ID."""
    chat_id = update.effective_chat.id
    user_chat_ids.add(chat_id)

    welcome_text = (
        "Welcome to this bot!\n\n"
        "❄️🌿💊\n"
        "🍀💊🚕\n\n"
        "❄️🍁 jon 💊🍀\n\n"
        "💎❄️ Anni 🍁🌿\n\n"
        "❄️☃️  🌿🌳  🐴🚛  🍄🌈\n\n"
        "Click here to shop now."
    )

    keyboard = [
        [InlineKeyboardButton("Shop Now 🛒", url="https://your-actual-store-link.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup,
    )


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send a shopping reminder every 3 hours."""
    reminder_text = "🎉🎉🎉🎉✌✌❤❤\n\nDon't forget to shop with us today!"

    for chat_id in list(user_chat_ids):
        try:
            await context.bot.send_message(chat_id=chat_id, text=reminder_text)
        except Exception as exc:
            logging.error("Failed to send to %s: %s", chat_id, exc)
            user_chat_ids.discard(chat_id)


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # First reminder 10 seconds after startup, then every 3 hours.
    application.job_queue.run_repeating(
        send_reminder,
        interval=3 * 60 * 60,
        first=10,
    )

    logging.info("Bot started in polling mode...")
    application.run_polling()


if __name__ == "__main__":
    main()
