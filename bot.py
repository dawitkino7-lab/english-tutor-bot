import os
import sys
import time
import json
import requests
import threading
import random
import re
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

def correct_punctuation_and_capitalization(text):
    """SPECIFICALLY fix punctuation and capitalization"""
    if not text:
        return text
    
    # Trim whitespace
    text = text.strip()
    
    # Fix CAPITALIZATION: First letter of sentence
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    
    # Fix I pronoun (standalone)
    text = re.sub(r'\bi\b', 'I', text)
    
    # Fix punctuation: Add period if missing at the end
    if text and text[-1] not in ['.', '!', '?']:
        text += '.'
    
    # Fix multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Fix space before punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    # Fix space after punctuation
    text = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', text)
    
    return text

def correct_grammar_and_spelling(text):
    """Fix common grammar and spelling mistakes"""
    
    # Dictionary of fixes
    fixes = {
        # Contractions
        r'\bdont\b': "don't",
        r'\bdoesnt\b': "doesn't",
        r'\bdidnt\b': "didn't",
        r'\bcant\b': "can't",
        r'\bcannot\b': "can't",
        r'\bwont\b': "won't",
        r'\bwouldnt\b': "wouldn't",
        r'\bcouldnt\b': "couldn't",
        r'\bshouldnt\b': "shouldn't",
        r'\bisnt\b': "isn't",
        r'\barent\b': "aren't",
        r'\bwasnt\b': "wasn't",
        r'\bwerent\b': "weren't",
        r'\bhasnt\b': "hasn't",
        r'\bhavent\b': "haven't",
        r'\bhadnt\b': "hadn't",
        
        # Informal to formal
        r'\bwanna\b': "want to",
        r'\bgonna\b': "going to",
        r'\bgotta\b': "got to",
        r'\bkinda\b': "kind of",
        r'\bsorta\b': "sort of",
        
        # Common misspellings
        r'\brecieve\b': "receive",
        r'\bacheive\b': "achieve",
        r'\bbeleive\b': "believe",
        r'\bseperate\b': "separate",
        r'\bdefinately\b': "definitely",
        r'\baccomodate\b': "accommodate",
        r'\boccurred\b': "occurred",
        r'\boccured\b': "occurred",
        r'\bthier\b': "their",
        r'\btheres\b': "there's",
        r'\byour\b welcome\b': "you're welcome",
    }
    
    for pattern, replacement in fixes.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def correct_english(text):
    """Full correction pipeline"""
    if not text:
        return text
    
    # Step 1: Fix punctuation and capitalization
    text = correct_punctuation_and_capitalization(text)
    
    # Step 2: Fix grammar and spelling
    text = correct_grammar_and_spelling(text)
    
    return text

def answer_question(user_message, user_name):
    """Actually answer questions instead of deflecting"""
    
    msg_lower = user_message.lower()
    
    # Question about bot's name
    if 'your name' in msg_lower or 'who are you' in msg_lower:
        return f"My name is John! I'm your personal English tutor bot. I'm here to help you practice and improve your English skills. What's your name?"
    
    # Question about what bot can do
    if 'what can you do' in msg_lower or 'your purpose' in msg_lower:
        return "I can help you improve your English! I'll correct your spelling, grammar, and punctuation. We can chat about anything - your day, hobbies, interests, or specific topics you want to practice. Just talk to me naturally!"
    
    # Question about age
    if 'how old' in msg_lower and ('you' in msg_lower or 'bot' in msg_lower):
        return "I'm a bot, so I don't have an age! But I was created recently to help people like you learn English. 😊"
    
    # Question about location
    if 'where are you from' in msg_lower or 'where do you live' in msg_lower:
        return "I live in the cloud! ☁️ I'm an AI bot, so I don't have a physical location. But I'm always here whenever you need me!"
    
    # Question about time
    if 'what time' in msg_lower or 'what is the time' in msg_lower:
        current_time = datetime.now().strftime("%I:%M %p")
        return f"I don't have a watch, but I know it's {current_time} where my server is! What time is it where you are?"
    
    # Question about weather
    if 'weather' in msg_lower and '?' in user_message:
        return "I wish I could check the weather for you, but I don't have internet access for that. Tell me about the weather where you are! Is it sunny, rainy, or something else?"
    
    # Question about helping with English
    if 'help me' in msg_lower and ('english' in msg_lower or 'learn' in msg_lower):
        return "Of course! I'd love to help you with English. The best way to practice is just to chat with me naturally. I'll correct your mistakes as we talk. What would you like to discuss today?"
    
    # Question about favorites
    if 'favorite' in msg_lower and '?' in user_message:
        if 'color' in msg_lower:
            return "My favorite color is blue! 💙 It's calm and peaceful. What's your favorite color?"
        elif 'food' in msg_lower:
            return "I don't eat food, but I hear pizza and chocolate are pretty popular! What's your favorite food?"
        elif 'movie' in msg_lower:
            return "I don't watch movies, but I'd love to hear about your favorite movie! What do you like about it?"
        elif 'music' in msg_lower:
            return "I don't listen to music, but I know it's wonderful! What kind of music do you enjoy?"
        else:
            return f"That's a great question! I don't have favorites since I'm a bot, but I'd love to hear what your favorite is!"
    
    # Question about feelings
    if 'how do you feel' in msg_lower or 'are you happy' in msg_lower:
        return "I don't have feelings like humans do, but I'm programmed to be friendly and helpful! Talking with you makes my code happy. 😊 How are you feeling today?"
    
    # Question about capabilities
    if 'can you' in msg_lower and '?' in user_message:
        if 'correct' in msg_lower:
            return "Yes, I can definitely correct your English! That's my main job. Just keep chatting and I'll fix any mistakes I see."
        elif 'understand' in msg_lower:
            return "Yes, I understand English pretty well! I might miss some things occasionally, but I'll do my best to understand you."
        else:
            return "I can help you practice English, correct your mistakes, and chat with you about various topics. What specifically would you like me to do?"
    
    return None  # Not a question we have an answer for

def get_smart_response(user_message, user_name, conversation_history):
    """Generate intelligent responses based on context"""
    
    msg_lower = user_message.lower()
    
    # FIRST: Check if it's a question we can answer directly
    question_answer = answer_question(user_message, user_name)
    if question_answer:
        return question_answer
    
    # Greetings with variety
    greetings = ['hi', 'hello', 'hey', 'greetings', 'whats up', 'sup', 'howdy']
    if any(word in msg_lower for word in greetings) and len(user_message.split()) <= 2:
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
    
    # Weather talk (not a question)
    if 'weather' in msg_lower and '?' not in user_message:
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
        "Thanks for sharing that with me!",
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
                        user_id = str(chat_id)
                        
                        print(f"💬 Message from {user_name}: {text}")
                        
                        # Initialize conversation history for new users
                        if user_id not in user_conversations:
                            user_conversations[user_id] = []
                        
                        # Send typing indicator
                        send_typing_action(chat_id)
                        time.sleep(1)
                        
                        # Handle commands
                        if text == "/start":
                            welcome = f"👋 Hi {user_name}! I'm your English tutor bot!\n\nI can help you with:\n✅ Spelling\n✅ Grammar\n✅ Punctuation\n✅ Capitalization\n✅ Conversation practice\n\nJust chat with me like a friend and I'll help you improve your English! What would you like to talk about today?"
                            send_message(chat_id, welcome)
                            print("✅ Sent welcome message")
                        
                        elif text == "/help":
                            help_text = "📚 <b>How to use me:</b>\n\n• Just chat with me normally\n• I'll correct your punctuation and capitalization\n• I'll fix spelling and grammar mistakes\n• I'll answer your questions directly\n• We can talk about ANY topic\n\nThe more you chat, the more you learn!"
                            send_message(chat_id, help_text)
                            print("✅ Sent help message")
                        
                        elif text:
                            # Add to conversation history
                            user_conversations[user_id].append({"role": "user", "text": text})
                            
                            # Keep history manageable
                            if len(user_conversations[user_id]) > 5:
                                user_conversations[user_id] = user_conversations[user_id][-5:]
                            
                            # CORRECT the message (punctuation, capitalization, grammar)
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
            
            time.sleep(1)
            
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
