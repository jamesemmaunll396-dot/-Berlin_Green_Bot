import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get Token
TOKEN = os.environ.get("BOT_TOKEN")

# Store user chat_ids in memory
user_chat_ids = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message and save user"""
    chat_id = update.effective_chat.id
    user_chat_ids.add(chat_id)
    
    welcome_text = (
        "Welcome to this bot!\n\n"
        "Click here to shop now."
    )
    
    keyboard = [
        [InlineKeyboardButton("Shop Now 🛒", url="https://your-actual-store-link.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup
    )

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Reminder function: executed every 3 hours with simple emojis"""
    reminder_text = (
        "🎉🎉🎉🎉✌✌❤❤\n\n"
        "Don't forget to shop with us today!"
    )
    
    for chat_id in list(user_chat_ids):
        try:
            await context.bot.send_message(chat_id=chat_id, text=reminder_text)
        except Exception as e:
            logging.error(f"Failed to send to {chat_id}: {e}")
            user_chat_ids.discard(chat_id)

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")

    # Build Application
    application = Application.builder().token(TOKEN).build()

    # Add /start handler
    application.add_handler(CommandHandler("start", start))

    # Set scheduled task: every 3 hours (3 * 60 * 60 = 10800 seconds)
    job_queue = application.job_queue
    job_queue.run_repeating(send_reminder, interval=10800, first=10) 
    # first=10 means it sends the first reminder 10 seconds after startup (change to 10800 for production)

    # Start the bot (Polling)
    logging.info("Bot started in Polling mode...")
    application.run_polling()

if __name__ == "__main__":
    main()
