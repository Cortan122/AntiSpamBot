import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging to see errors in the console
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define the /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I am your new Telegram bot. How can I help you today?")

# Define the echo handler (repeats what the user says)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"You said: {user_text}")

def main():
    # Fetch the token from environment variables (secure practice)
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not TOKEN:
        print("Error: No TELEGRAM_TOKEN found in environment variables.")
        return

    # Build the application
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the bot using Polling (great for development and small bots)
    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()