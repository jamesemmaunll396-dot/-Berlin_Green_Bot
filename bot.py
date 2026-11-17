
import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID")

# Default bot mode
GLOBAL_BOT_MODE = "REDIRECT"

# Replace these with your actual store links
REDIRECT_URL = "https://your-redirect-link.com"
SHOPPING_URL = "https://your-shopping-link.com"

user_chat_ids = set()


def is_admin(update: Update):
    if not ADMIN_USER_ID:
        return False

    return str(update.effective_user.id) == ADMIN_USER_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_ids.add(update.effective_chat.id)

    if GLOBAL_BOT_MODE == "REDIRECT":
        welcome_text = (
            "Welcome to this bot!\n\n"
            "❄️🌿💊\n"
            "🍀💊🚕\n\n"
            "❄️🍁 jon 💊🍀\n\n"
            "💎❄️ Anni 🍁🌿\n\n"
            "❄️☃️  🌿🌳  🐴🚛  🍄🌈\n\n"
            "Click here to shop now."
        )

        button_url = REDIRECT_URL

    else:
        welcome_text = (
            "Welcome to this bot!\n\n"
            "❄️🌿💊\n"
            "🍀💊🚕\n\n"
            "❄️🍁 jon 💊🍀\n\n"
            "💎❄️ Anni 🍁🌿\n\n"
            "❄️☃️  🌿🌳  🐴🚛  🍄🌈\n\n"
            "Click here to shop now."
        )

        button_url = SHOPPING_URL

    keyboard = [
        [
            InlineKeyboardButton(
                "Shop Now 🛒",
                url=button_url
            )
        ]
    ]

    await update.message.reply_text(
        text=welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_admin_commands(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    global GLOBAL_BOT_MODE

    message = (update.message.text or "").strip().upper()

    if message not in ("REDIRECT", "REVERSE"):
        return

    if not is_admin(update):
        logging.warning(
            "Unauthorized mode change attempt from user %s",
            update.effective_user.id
        )
        return

    if message == "REDIRECT":
        GLOBAL_BOT_MODE = "REDIRECT"

        await update.message.reply_text(
            "✅ REDIRECT mode activated!\n\n"
            "The bot is now using the redirect welcome message."
        )

    elif message == "REVERSE":
        GLOBAL_BOT_MODE = "REVERSE"

        await update.message.reply_text(
            "✅ REVERSE mode activated!\n\n"
            "The bot has returned to shopping mode."
        )

    logging.info("Bot mode changed to %s", GLOBAL_BOT_MODE)


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    reminder_text = (
        "🎉🎉🎉🎉✌✌❤❤\n\n"
        "Don't forget to shop with us today!"
    )

    for chat_id in list(user_chat_ids):
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=reminder_text
            )
        except Exception as exc:
            logging.error("Failed to send to %s: %s", chat_id, exc)
            user_chat_ids.discard(chat_id)


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")

    if not ADMIN_USER_ID:
        logging.warning(
            "ADMIN_USER_ID is missing. Mode switching is disabled."
        )

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_admin_commands
        )
    )

    application.job_queue.run_repeating(
        send_reminder,
        interval=3 * 60 * 60,
        first=10
    )

    logging.info("Telegram bot started in %s mode", GLOBAL_BOT_MODE)

    application.run_polling()


if __name__ == "__main__":
    main()
