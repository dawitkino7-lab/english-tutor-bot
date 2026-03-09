import os
import sys
import logging
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging - FIXED the typo!
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    print("❌ ERROR: No BOT_TOKEN found!")
    sys.exit(1)

print(f"✅ Token found: {TOKEN[:10]}...")

# Create Flask app for web server
app = Flask(__name__)

@app.route('/')
def home():
    return "English Tutor Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_web_server():
    """Run Flask web server"""
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Web server starting on port {port}")
    app.run(host='0.0.0.0', port=port)

def correct_english(text):
    """Simple rule-based correction"""
    if not text:
        return text
    
    # Capitalize first letter
    corrected = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    # Add period if missing
    if corrected and corrected[-1] not in ['.', '!', '?']:
        corrected += '.'
    
    # Common fixes
    fixes = {
        " i ": " I ",
        " im ": " I'm ",
        "Im ": "I'm ",
        " dont ": " don't ",
        " didnt ": " didn't ",
        " cant ": " can't ",
        " isnt ": " isn't ",
        " wasnt ": " wasn't ",
        " u ": " you ",
        " ur ": " your ",
    }
    
    for wrong, right in fixes.items():
        corrected = corrected.replace(wrong, right)
    
    return corrected

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Hi {user.first_name}! I'm your English tutor bot!\n\n"
        "Send me any message and I'll help with your English."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages"""
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    logger.info(f"Message from {user_name}: {user_message}")
    
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        await asyncio.sleep(0.5)
        
        # Correct the message
        corrected = correct_english(user_message)
        
        # Send correction if needed
        if corrected != user_message:
            await update.message.reply_text(f"✅ {corrected}")
            await asyncio.sleep(0.5)
        
        # Generate response
        msg_lower = user_message.lower()
        
        if any(word in msg_lower for word in ['hi', 'hello', 'hey']):
            response = f"Hey {user_name}! How are you?"
        elif 'how are you' in msg_lower:
            response = "I'm doing great! Thanks for asking! How about you?"
        elif 'thank' in msg_lower:
            response = "You're welcome! 😊"
        elif 'bye' in msg_lower:
            response = "Goodbye! Talk to you soon! 👋"
        else:
            response = f"Interesting! Tell me more, {user_name}."
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("I'm here! Tell me more.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "Just send me messages! I'll correct your English."
    )

def run_bot():
    """Run the Telegram bot"""
    print("🚀 Starting Telegram bot...")
    
    # Create application - this is the CORRECT way for v20+
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    print("✅ Bot is polling for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    print("🎯 Starting English Tutor Bot...")
    print("=" * 40)
    
    # Start web server in a separate thread
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    print("✅ Web server thread started")
    
    # Run bot in main thread
    try:
        run_bot()
    except Exception as e:
        print(f"❌ Bot error: {e}")
        # Keep trying to restart
        while True:
            print("🔄 Restarting bot in 5 seconds...")
            import time
            time.sleep(5)
            run_bot()
