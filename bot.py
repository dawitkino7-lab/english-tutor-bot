import os
import sys
import time
import json
import requests
import threading
import random
from flask import Flask
from datetime import datetime

# Get token from environment variable
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    print("❌ ERROR: No BOT_TOKEN found!")
    sys.exit(1)

print(f"✅ Token found: {TOKEN[:10]}...")

# Flask app for web server
app = Flask(__name__)

@app.route('/')
def home():
    return "English Tutor Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_web_server():
    """Run Flask web server"""
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Web server starting on port {port}")
    app.run(host='0.0.0.0', port=port)

def correct_english(text):
    """Advanced correction with more rules"""
    if not text:
        return text
    
    original = text
    
    # Capitalize first letter
    corrected = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    # Add period if missing and not a question/exclamation
    if corrected and corrected[-1] not in ['.', '!', '?']:
        corrected += '.'
    
    # Common fixes dictionary
    fixes = {
        # Pronouns
        " i ": " I ",
        " i'm ": " I'm ",
        " im ": " I'm ",
        "Im ": "I'm ",
        " im ": " I'm ",
        " ive ": " I've ",
        " id ": " I'd ",
        " ill ": " I'll ",
        
        # Contractions
        " dont ": " don't ",
        " dont't ": " don't ",
        " doesnt ": " doesn't ",
        " didnt ": " didn't ",
        " cant ": " can't ",
        " cant't ": " can't ",
        " cannot ": " can't ",
        " wont ": " won't ",
        " wont't ": " won't ",
        " wouldnt ": " wouldn't ",
        " couldnt ": " couldn't ",
        " shouldnt ": " shouldn't ",
        " isnt ": " isn't ",
        " arent ": " aren't ",
        " wasnt ": " wasn't ",
        " werent ": " weren't ",
        " hasnt ": " hasn't ",
        " havnt ": " haven't ",
        " hadnt ": " hadn't ",
        
        # Informal
        " u ": " you ",
        " ur ": " your ",
        " urs ": " yours ",
        " ya ": " you ",
        " wanna ": " want to ",
        " gonna ": " going to ",
        " gotta ": " got to ",
        " kinda ": " kind of ",
        " sorta ": " sort of ",
        " outta ": " out of ",
        
        # Common misspellings
        " recieve ": " receive ",
        " acheive ": " achieve ",
        " beleive ": " believe ",
        " seperate ": " separate ",
        " definately ": " definitely ",
        " accomodate ": " accommodate ",
        " ocurred ": " occurred ",
        " occured ": " occurred ",
        " thier ": " their ",
        " there's ": " theirs ",
    }
    
    for wrong, right in fixes.items():
        corrected = corrected.replace(wrong, right)
    
    return corrected

def get_smart_response(user_message, user_name, conversation_history):
    """Generate intelligent responses based on context"""
    
    msg_lower = user_message.lower()
    
    # Greetings with variety
    greetings = ['hi', 'hello', 'hey', 'greetings', 'whats up', 'sup', 'howdy']
    if any(word in msg_lower for word in greetings):
        responses = [
            f"Hey {user_name}! Great to see you! How's your day going?",
            f"Hello {user_name}! Ready to practice some English?",
            f"Hi there {user_name}! What would you like to talk about today?",
            f"Hey {user_name}! I'm here to help you with English. What's new?"
        ]
        return random.choice(responses)
    
    # How are you responses
    if 'how are you' in msg_lower:
        responses = [
            "I'm doing really well, thanks for asking! I'm here and ready to help you with English. How about you?",
            "I'm great! Just waiting for our next English conversation. How are you today?",
            "I'm fantastic! Thanks for checking in. Tell me about your day!",
            "I'm wonderful! Always happy to chat with you. How are things on your end?"
        ]
        return random.choice(responses)
    
    # Thanks responses
    if any(word in msg_lower for word in ['thank', 'thanks', 'thx']):
        responses = [
            "You're very welcome! 😊",
            "My pleasure! That's what I'm here for.",
            "Happy to help! Keep practicing!",
            "Anytime! Let's keep learning together."
        ]
        return random.choice(responses)
    
    # Farewells
    if any(word in msg_lower for word in ['bye', 'goodbye', 'see you', 'cya']):
        responses = [
            f"Goodbye {user_name}! Come back soon to practice more English! 👋",
            f"See you later! Keep practicing your English!",
            f"Bye! It was great chatting with you. Talk to you soon!",
            f"Take care, {user_name}! I'll be here when you need me."
        ]
        return random.choice(responses)
    
    # Questions about the bot
    if any(word in msg_lower for word in ['your name', 'who are you']):
        responses = [
            "I'm John, your personal English tutor bot! I'm here to help you improve your English skills.",
            "My name is John! Think of me as your friendly English practice partner.",
            "I'm John, your AI English tutor! I can help you with grammar, spelling, and conversation."
        ]
        return random.choice(responses)
    
    # Questions about what the bot does
    if any(word in msg_lower for word in ['what can you do', 'help me', 'what do you do']):
        responses = [
            "I can help you with English! I'll correct your spelling, grammar, and punctuation. We can chat about anything to help you practice!",
            "I'm your English tutor! Send me messages and I'll correct them. We can talk about any topic you like!",
            "I help you improve your English! Just chat with me naturally, and I'll fix your mistakes and keep the conversation going."
        ]
        return random.choice(responses)
    
    # Weather talk
    if 'weather' in msg_lower:
        responses = [
            "Weather is always a great topic! What's it like where you are today?",
            "I hope the weather is nice for you! Do you prefer sunny days or rainy days?",
            "Tell me about the weather! I love hearing about different places."
        ]
        return random.choice(responses)
    
    # Food talk
    if any(word in msg_lower for word in ['food', 'eat', 'restaurant', 'cook', 'meal']):
        responses = [
            "Food is wonderful! What's your favorite dish?",
            "I love talking about food! Do you enjoy cooking or eating out more?",
            "That sounds delicious! Tell me more about what you like to eat."
        ]
        return random.choice(responses)
    
    # Learning English
    if any(word in msg_lower for word in ['learn english', 'improve english', 'practice english']):
        responses = [
            "That's great that you're learning English! You're doing really well. What part of English do you find most challenging?",
            "I'm here to help you improve! Your English is getting better with every message. What would you like to focus on?",
            "Practice makes perfect! You're doing a great job. Is there anything specific you want to work on?"
        ]
        return random.choice(responses)
    
    # Compliments
    if any(word in msg_lower for word in ['good bot', 'great bot', 'nice bot', 'you rock']):
        responses = [
            "Aww, thank you! 😊 You're doing great with your English too!",
            "Thanks! But YOU'RE the one doing all the hard work learning English!",
            "I appreciate that! But the real star is you for practicing so diligently!"
        ]
        return random.choice(responses)
    
    # Check if it's a question
    if '?' in user_message:
        responses = [
            f"That's an interesting question! What do you think about it, {user_name}?",
            "Good question! I'm curious to hear your thoughts first.",
            "Hmm, let me think about that. What's your opinion?",
            "That's a thoughtful question. Tell me what you think!"
        ]
        return random.choice(responses)
    
    # Short messages (1-3 words)
    if len(user_message.split()) <= 3:
        responses = [
            f"Tell me more about that, {user_name}!",
            "I'd love to hear more details!",
            "That's interesting! Can you elaborate?",
            "Go on, I'm listening!",
            f"What else comes to mind, {user_name}?"
        ]
        return random.choice(responses)
    
    # Default responses for everything else
    default_responses = [
        f"That's really interesting, {user_name}! Tell me more.",
        "I see! What else would you like to share?",
        "Thanks for sharing that with me! How does that make you feel?",
        "I'm following along! Please continue.",
        f"Great! Keep going, {user_name}. I'm learning about you.",
        "That's cool! Is there anything specific you want to practice?",
        "I'm here to help with your English. What would you like to discuss next?"
    ]
    
    return random.choice(default_responses)

def send_message(chat_id, text):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            print(f"Error sending message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def send_typing_action(chat_id):
    """Send typing indicator"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendChatAction"
    data = {
        "chat_id": chat_id,
        "action": "typing"
    }
    try:
        requests.post(url, json=data)
    except:
        pass

def process_updates():
    """Main bot loop"""
    last_update_id = 0
    # Store conversation history for each user
    user_conversations = {}
    
    print("🚀 Bot started! Waiting for messages...")
    
    while True:
        try:
            # Get updates from Telegram
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {
                "offset": last_update_id + 1,
                "timeout": 30
            }
            
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            
            if data.get("ok") and data.get("result"):
                for update in data["result"]:
                    last_update_id = update["update_id"]
                    
                    # Check if it's a message
                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        user_name = message["from"].get("first_name", "Friend")
                        user_id = str(chat_id)  # Use chat_id as user identifier
                        
                        print(f"💬 Message from {user_name}: {text}")
                        
                        # Initialize conversation history for new users
                        if user_id not in user_conversations:
                            user_conversations[user_id] = []
                        
                        # Send typing indicator (makes it feel more human)
                        send_typing_action(chat_id)
                        time.sleep(1)
                        
                        # Handle commands
                        if text == "/start":
                            welcome = f"👋 Hi {user_name}! I'm your English tutor bot!\n\nI can help you with:\n✅ Spelling\n✅ Grammar\n✅ Punctuation\n✅ Conversation practice\n\nJust chat with me like a friend and I'll help you improve your English! What would you like to talk about today?"
                            send_message(chat_id, welcome)
                            print("✅ Sent welcome message")
                        
                        elif text == "/help":
                            help_text = "📚 <b>How to use me:</b>\n\n• Just chat with me normally\n• I'll correct your mistakes\n• We can talk about ANY topic\n• The more you chat, the more you learn!\n\nTry telling me about your day, your hobbies, or ask me questions!"
                            send_message(chat_id, help_text)
                            print("✅ Sent help message")
                        
                        elif text:
                            # Add to conversation history
                            user_conversations[user_id].append({"role": "user", "text": text})
                            
                            # Keep history manageable (last 5 messages)
                            if len(user_conversations[user_id]) > 5:
                                user_conversations[user_id] = user_conversations[user_id][-5:]
                            
                            # Correct the message
                            corrected = correct_english(text)
                            
                            # Send correction if needed
                            if corrected != text:
                                send_message(chat_id, f"✅ {corrected}")
                                print(f"✅ Sent correction")
                                time.sleep(0.5)
                                send_typing_action(chat_id)
                                time.sleep(0.5)
                            
                            # Get smart response
                            response = get_smart_response(text, user_name, user_conversations[user_id])
                            send_message(chat_id, response)
                            print(f"✅ Sent response: {response}")
                            
                            # Add bot response to history
                            user_conversations[user_id].append({"role": "bot", "text": response})
            
            time.sleep(1)  # Small delay between checks
            
        except requests.exceptions.ReadTimeout:
            continue
        
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("🎯 Starting English Tutor Bot...")
    print("=" * 40)
    
    # Start web server in thread
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    print("✅ Web server started")
    time.sleep(2)
    
    # Run bot in main thread
    process_updates()
