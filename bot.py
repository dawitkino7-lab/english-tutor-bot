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

# Get token from environment variable
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    print("❌ ERROR: No BOT_TOKEN found in environment variables!")
    sys.exit(1)

print(f"✅ Token found: {TOKEN[:10]}...")

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
        " idk ": " I don't know ",
        " lol ": " haha ",
        " omg ": " oh my god ",
        " wanna ": " want to ",
        " gonna ": " going to ",
        " gotta ": " got to ",
    }
    
    for wrong, right in corrections.items():
        corrected = corrected.replace(wrong, right)
    
    return corrected

def get_context_response(user_id, user_message, user_name):
    """Generate a response based on conversation context"""
    
    # Get conversation history
    history = conversations.get(user_id, [])
    
    # Get last topic if exists
    last_topic = user_context[user_id].get('last_topic', '')
    topic_count = user_context[user_id].get('topic_count', 0)
    
    # Update topic if new message
    words = user_message.lower().split()
    topics = ['weather', 'school', 'work', 'food', 'movie', 'music', 'sports', 
              'family', 'friend', 'travel', 'book', 'game', 'pet', 'hobby']
    
    current_topic = ''
    for topic in topics:
        if topic in user_message.lower():
            current_topic = topic
            break
    
    if current_topic:
        user_context[user_id]['last_topic'] = current_topic
        user_context[user_id]['topic_count'] = topic_count + 1
    else:
        current_topic = last_topic
    
    # Add to history
    conversations[user_id].append({
        'message': user_message,
        'time': datetime.now(),
        'topic': current_topic or 'general'
    })
    
    # Keep only last 10 messages
    if len(conversations[user_id]) > 10:
        conversations[user_id] = conversations[user_id][-10:]
    
    # Generate appropriate response based on context
    message_lower = user_message.lower()
    
    # Greeting detection
    greetings = ['hello', 'hi', 'hey', 'hola', 'greetings', 'whats up', 'sup']
    if any(greet in message_lower for greet in greetings):
        return random.choice([
            f"Hey {user_name}! How are you today?",
            f"Hi {user_name}! What's new?",
            f"Hello {user_name}! Great to see you!",
            f"Hey there {user_name}! How's it going?"
        ])
    
    # Question about bot
    if 'how are you' in message_lower:
        return random.choice([
            "I'm doing great, thanks for asking! How about you?",
            "I'm wonderful! Thanks for checking in. How are you?",
            "Doing well! Just enjoying our conversation. How are you?"
        ])
    
    # Topic-based responses
    if 'weather' in message_lower:
        return random.choice([
            "I love talking about weather! Is it sunny where you are?",
            "Weather is always a good topic! What's it like outside?",
            "Tell me more about the weather! Do you prefer hot or cold days?"
        ])
    
    elif 'school' in message_lower or 'study' in message_lower:
        return random.choice([
            "School is important! What subjects do you enjoy most?",
            "Learning is great! What are you studying these days?",
            "Tell me about your school! Do you have favorite classes?"
        ])
    
    elif 'work' in message_lower or 'job' in message_lower:
        return random.choice([
            "Work keeps us busy! What do you do?",
            "Tell me about your job! Do you enjoy it?",
            "Work-life balance is important! How's work treating you?"
        ])
    
    elif 'food' in message_lower or 'eat' in message_lower:
        return random.choice([
            "Food is awesome! What's your favorite cuisine?",
            "I love talking about food! What did you eat today?",
            "Tell me about your favorite foods! Are you a good cook?"
        ])
    
    elif 'movie' in message_lower or 'film' in message_lower or 'watch' in message_lower:
        return random.choice([
            "Movies are great entertainment! Seen anything good lately?",
            "I love movies! What genre do you prefer?",
            "Tell me about the last movie you watched! Was it good?"
        ])
    
    elif 'music' in message_lower or 'song' in message_lower:
        return random.choice([
            "Music makes life better! What do you like to listen to?",
            "Great topic! What's your favorite artist or band?",
            "Tell me about your music taste! Any recommendations?"
        ])
    
    elif 'game' in message_lower or 'play' in message_lower:
        return random.choice([
            "Games are fun! What games do you play?",
            "Tell me about your favorite games!",
            "Do you prefer video games or board games?"
        ])
    
    elif 'travel' in message_lower or 'trip' in message_lower or 'vacation' in message_lower:
        return random.choice([
            "Travel is amazing! Where's the best place you've visited?",
            "I love hearing about travels! Any trips planned?",
            "Tell me about your dream vacation destination!"
        ])
    
    elif 'family' in message_lower:
        return random.choice([
            "Family is special! Tell me about yours!",
            "Family time is precious! Do you have siblings?",
            "That's nice! What do you enjoy doing with your family?"
        ])
    
    elif 'friend' in message_lower:
        return random.choice([
            "Friends make life better! Tell me about your friends!",
            "Good friends are hard to find! Have you known them long?",
            "That's wonderful! What do you like to do with friends?"
        ])
    
    # Short responses
    if len(user_message.split()) < 4:
        if '?' in user_message:
            return "That's an interesting question! Tell me more."
        else:
            return random.choice([
                f"Tell me more about that, {user_name}!",
                "I'd love to hear more!",
                "Go on, I'm listening!",
                "That's interesting! What else?"
            ])
    
    # Check for questions
    if '?' in user_message:
        return random.choice([
            "That's a good question! What do you think?",
            "Interesting question! Tell me your thoughts first.",
            "I'm curious about that too! What's your opinion?"
        ])
    
    # Based on conversation length
    if len(history) > 3:
        return random.choice([
            f"I really enjoy our conversations, {user_name}! What else is new?",
            "This is great! Tell me more about your day.",
            "I love hearing from you! What else would you like to share?",
            "You're doing great with your English! Keep talking!"
        ])
    
    # Default responses
    return random.choice([
        f"That's interesting, {user_name}! Tell me more.",
        "I see! What else is on your mind?",
        "Thanks for sharing! What else?",
        "Got it! Anything else you want to talk about?",
        "That's cool! Tell me more about that."
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    user_id = user.id
    
    # Clear old conversation
    conversations[user_id] = []
    user_context[user_id] = {}
    
    welcome = f"""👋 Welcome {user.first_name}! I'm your English tutor bot!

**I can help you with:**
✅ Capitalization & punctuation
✅ Common spelling mistakes
✅ Natural conversation

**Tips:**
• Just chat with me normally
• I'll correct your mistakes
• I remember our conversation
• Ask me about: weather, school, work, food, movies, music, travel, and more!

Let's start! How are you today?"""
    
    await update.message.reply_text(welcome)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages"""
    user_message = update.message.text
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    
    logger.info(f"Message from {user_name}: {user_message}")
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    await asyncio.sleep(0.5)
    
    # Step 1: Correct the message
    corrected = correct_english(user_message)
    
    # Step 2: Send correction if needed
    if corrected != user_message:
        await update.message.reply_text(f"✅ {corrected}")
        
        # Give specific feedback
        if corrected[0].isupper() and user_message[0].islower():
            await update.message.reply_text("📝 Remember to capitalize the first letter of sentences!")
        elif corrected.endswith('.') and not user_message.endswith('.'):
            await update.message.reply_text("📝 Don't forget to end sentences with a period!")
        
        await asyncio.sleep(0.5)
        
        # Use corrected version for response
        response_message = corrected
    else:
        response_message = user_message
    
    # Step 3: Generate contextual response
    response = get_context_response(user_id, response_message, user_name)
    
    # Send response
    await update.message.reply_text(response)
    
    # Step 4: Occasionally ask a follow-up question
    if random.random() < 0.2:  # 20% chance
        await asyncio.sleep(1)
        follow_ups = [
            "What do you think about that?",
            "Tell me more!",
            "How does that make you feel?",
            "What else is new?",
            "Any plans for the weekend?",
            "What's your favorite thing about that?"
        ]
        await update.message.reply_text(random.choice(follow_ups))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """📚 **English Tutor Bot Help**

**Just chat naturally!** I'll help with:
• Capitalization
• Punctuation
• Common mistakes

**Topics we can discuss:**
☀️ Weather
📚 School/Study
💼 Work
🍔 Food
🎬 Movies
🎵 Music
🎮 Games
✈️ Travel
👨‍👩‍👧 Family
👥 Friends

**Commands:**
/start - Start fresh conversation
/help - Show this message
/new - Clear conversation history"""

    await update.message.reply_text(help_text, parse_mode='Markdown')

async def new_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear conversation history"""
    user_id = update.effective_user.id
    conversations[user_id] = []
    user_context[user_id] = {}
    await update.message.reply_text("🔄 Starting fresh! What would you like to talk about?")

# Flask web server to keep Render happy
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
    bot_app.add_handler(CommandHandler("new", new_conversation))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    print("✅ Bot is polling for messages...")
    bot_app.run_polling()

def main():
    """Main function - starts both Flask and Telegram bot"""
    print("🎯 Starting English Tutor Bot with Memory...")
    
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
