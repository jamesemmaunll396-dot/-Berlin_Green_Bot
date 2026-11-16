import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging (for troubleshooting on Render)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get Token (set BOT_TOKEN in Render's environment variables)
TOKEN = os.environ.get("BOT_TOKEN")

# Store user chat_id (simplified version uses memory; production environment should use a database)
# Note: On Render's free tier, service restarts will lose this data. For production, use Supabase or Redis.
user_chat_ids = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command, send welcome message and buttons"""
    chat_id = update.effective_chat.id
    user_chat_ids.add(chat_id)  # Record user so reminders can be sent later
    
    # This is the welcome message you requested
    welcome_text = (
        "Welcome to this bot!\n\n"
        "Click here to shop now."
    )
    
    # Create button (URL must be replaced with your actual compliant link)
    keyboard = [
        [InlineKeyboardButton("Shop Now 🛒", url="https://your-actual-store-link.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup
    )

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Reminder function: executed every 3 hours"""
    # This is the content sent every 3 hours
    reminder_text = (
        "⏰ Reminder from us!\n\n"
        "Don't forget to check out our latest offers.\n"
        "Click /start to see the shop button again."
    )
    
    # Iterate over all users who have started the bot
    for chat_id in list(user_chat_ids):
        try:
            await context.bot.send_message(chat_id=chat_id, text=reminder_text)
        except Exception as e:
            logging.error(f"Failed to send to {chat_id}: {e}")
            # If user blocks the bot, remove from list
            user_chat_ids.discard(chat_id)

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")

    # Build Application
    application = Application.builder().token(TOKEN).build()

    # Add /start handler
    application.add_handler(CommandHandler("start", start))

    # Set scheduled task: execute every 3 hours (3 * 60 * 60 = 10800 seconds)
    job_queue = application.job_queue
    job_queue.run_repeating(send_reminder, interval=10800, first=10) 
    # first=10 means first reminder 10 seconds after startup (for testing), change to 10800 for production

    # Start the bot (polling mode is suitable for Background Worker)
    logging.info("Bot started...")
    application.run_polling()

if __name__ == "__main__":
    main()
