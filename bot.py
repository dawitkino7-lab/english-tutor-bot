import os
import sys
import logging
import asyncio
import random
from datetime import datetime
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request
import threading

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# DEBUG: Print all environment variables
print("🔍 DEBUG: Checking environment variables...")
all_vars = list(os.environ.keys())
print(f"🔍 Available env vars: {all_vars}")

# Get token from environment variable
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in environment variables!")
    print("❌ Tried to get 'BOT_TOKEN' but got None")
    print("❌ Please add BOT_TOKEN to Render Environment Variables")
    sys.exit(1)

print(f"✅ SUCCESS: Found BOT_TOKEN!")
print(f"✅ Token starts with: {TOKEN[:10]}...")
print(f"✅ Token length: {len(TOKEN)} characters")

# Store conversation history for each user
conversations = defaultdict(list)
user_context = defaultdict(dict)

def correct_english(text):
    """Simple rule-based correction"""
    if not text:
        return text
    
    # Capitalize first letter
    corrected = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    # Add period if missing and not a question/exclamation
    if corrected and corrected[-1] not in ['.', '!', '?']:
        corrected += '.'
    
    # Common fixes
    corrections = {
        " i ": " I ",
        " im ": " I'm ",
        "Im ": "I'm ",
        " dont ": " don't ",
        " didnt ": " didn't ",
        " cant ": " can't ",
        " isnt ": " isn't ",
        " wasnt ": " wasn't ",
        " were'nt ": " weren't ",
        " u ": " you ",
        " ur ": " your ",
    }
    
    for wrong, right in corrections.items():
        corrected = corrected.replace(wrong, right)
    
    return corrected

def get_response(user_id, user_message, user_name):
    """Generate a response based on context"""
    
    message_lower = user_message.lower()
    
    # Greetings
    if any(word in message_lower for word in ['hi', 'hello', 'hey']):
        return f"Hey {user_name}! How are you today?"
    
    # How are you
    if 'how are you' in message_lower:
        return "I'm doing great! Thanks for asking. How about you?"
    
    # Weather
    if 'weather' in message_lower:
        return "Weather is always a good topic! What's it like where you are?"
    
    # School/Study
    if any(word in message_lower for word in ['school', 'study', 'learn']):
        return "That's great! What are you studying?"
    
    # Work/Job
    if any(word in message_lower for word in ['work', 'job']):
        return "Tell me about your work! Do you enjoy it?"
    
    # Food
    if any(word in message_lower for word in ['food', 'eat', 'pizza', 'cook']):
        return "Food is awesome! What's your favorite thing to eat?"
    
    # Default response
    return f"Interesting! Tell me more about that, {user_name}."

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
    user_id = update.effective_user.id
    
    logger.info(f"Message from {user_name}: {user_message}")
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    await asyncio.sleep(0.5)
    
    # Correct the message
    corrected = correct_english(user_message)
    
    # Send correction if needed
    if corrected != user_message:
        await update.message.reply_text(f"✅ {corrected}")
        await asyncio.sleep(0.5)
    
    # Get response
    response = get_response(user_id, corrected, user_name)
    await update.message.reply_text(response)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "Just send me messages! I'll correct your English."
    )

# Flask web server
app = Flask(__name__)

@app.route('/')
def home():
    return "English Tutor Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    """Run the Telegram bot"""
    print("🚀 Starting Telegram bot...")
    
    # Create application
    bot_app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    print("✅ Bot is polling for messages...")
    bot_app.run_polling()

def main():
    """Main function"""
    print("🎯 Starting English Tutor Bot...")
    
    # Start Telegram bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Get port from environment
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Web server starting on port {port}...")
    
    # Start Flask server
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
