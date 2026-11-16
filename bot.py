import os
import logging
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get Tokens & URLs from Render Environment Variables
TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
PORT = int(os.environ.get("PORT", "8443"))

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
            logger.error(f"Failed to send to {chat_id}: {e}")
            user_chat_ids.discard(chat_id)

async def webhook_handler(request):
    """Handle incoming Telegram updates via Webhook"""
    application = request.app['application']
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
    return web.Response(text="OK")

async def health_check(request):
    """Endpoint for Cron Job to ping and keep the bot awake"""
    return web.Response(text="Bot is alive!")

async def main():
    if not TOKEN or not RENDER_EXTERNAL_URL:
        raise ValueError("BOT_TOKEN or RENDER_EXTERNAL_URL environment variable not set!")

    # Build Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))

    # Set scheduled task: every 3 hours (3 * 60 * 60 = 10800 seconds)
    job_queue = application.job_queue
    job_queue.run_repeating(send_reminder, interval=10800, first=10) # first=10 for testing

    # Initialize webhook
    await application.initialize()
    await application.bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{TOKEN}")
    await application.start()

    # Create aiohttp web server
    app = web.Application()
    app['application'] = application
    app.router.add_post(f"/{TOKEN}", webhook_handler)
    app.router.add_get("/", health_check)  # <--- Crucial for Cron Job

    # Start web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    
    logger.info("Bot started in Webhook mode...")
    
    # Keep the server running
    import asyncio
    await asyncio.Event().wait()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
