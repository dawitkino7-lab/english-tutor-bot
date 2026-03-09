import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from gpt4all import GPT4All
import logging
import os
import sys

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    print("❌ ERROR: No TOKEN found in environment variables!")
    sys.exit(1)

print("🤖 Loading AI model...")

try:
    # This tiny model will download automatically on Render
    # It's only 350MB and works perfectly!
    model = GPT4All("qwen2-0.5b-instruct-q4_0.gguf")
    print("✅ Model loaded successfully!")
    print("🎉 Bot is ready!")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    sys.exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Hi {user.first_name}! I'm your AI English tutor!\n\n"
        "Just chat with me normally and I'll help with your English!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    await update.message.chat.send_action(action="typing")
    await asyncio.sleep(1)
    
    try:
        # Check if correction needed
        correction_prompt = f"Fix this sentence: {user_message}"
        corrected = model.generate(correction_prompt, max_tokens=50, temp=0.1)
        corrected = corrected.strip()
        
        if corrected.lower() != user_message.lower():
            await update.message.reply_text(f"✅ {corrected}")
            await asyncio.sleep(1)
        
        # Natural reply
        reply_prompt = f"Reply naturally: {user_message}"
        reply = model.generate(reply_prompt, max_tokens=60, temp=0.7)
        await update.message.reply_text(reply.strip())
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Got it! Tell me more.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Just chat with me! I'll correct your English and respond naturally."
    )

def main():
    print("🚀 Starting bot...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is running!")
    app.run_polling()

if __name__ == '__main__':
    main()