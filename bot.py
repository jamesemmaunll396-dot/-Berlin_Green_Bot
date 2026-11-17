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

# Set the default mode
GLOBAL_BOT_MODE = "REDIRECT"

# Put your real Telegram destinations here
REDIRECT_URL = "https://your-redirect-link.com"
SHOPPING_URL = "https://your-shopping-link.com"

user_chat_ids = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_ids.add(update.effective_chat.id)

    welcome_text = (
        "Welcome to this bot!\n\n"
        "❄️🌿💊\n"
        "🍀💊🚕\n\n"
        "❄️🍁 jon 💊🍀\n\n"
        "💎❄️ Anni 🍁🌿\n\n"
        "❄️☃️  🌿🌳  🐴🚛  🍄🌈\n\n"
        "Click here to shop now."
    )

    if GLOBAL_BOT_MODE == "REDIRECT":
        button_url = REDIRECT_URL
    else:
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
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def change_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE

    command = update.message.text.strip().upper()

    if command == "REDIRECT":
        GLOBAL_BOT_MODE = "REDIRECT"

        await update.message.reply_text(
            "✅ REDIRECT MODE ACTIVATED!\n\n"
            "All users will now receive the redirect link when they press /start."
        )

    elif command == "REVERSE":
        GLOBAL_BOT_MODE = "REVERSE"

        await update.message.reply_text(
            "✅ REVERSE MODE ACTIVATED!\n\n"
            "All users will now receive the shopping link when they press /start."
        )


async def redirect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE

    GLOBAL_BOT_MODE = "REDIRECT"

    await update.message.reply_text(
        "✅ REDIRECT MODE ACTIVATED!"
    )


async def reverse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_BOT_MODE

    GLOBAL_BOT_MODE = "REVERSE"

    await update.message.reply_text(
        "✅ REVERSE MODE ACTIVATED!"
    )


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    reminder_text = (
        "🎉🎉🎉🎉✌️✌️❤️❤️\n\n"
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

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("redirect", redirect_command))
    application.add_handler(CommandHandler("reverse", reverse_command))

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            change_mode
        )
    )

    application.job_queue.run_repeating(
        send_reminder,
        interval=3 * 60 * 60,
        first=10
    )

    logging.info("Bot started in %s mode", GLOBAL_BOT_MODE)

    application.run_polling()


if _name_ == "_main_":
    main()
