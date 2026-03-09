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

def is_question(text):
    """Detect if text is a question even without question mark"""
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    # Question words at start
    question_words = ['what', 'who', 'where', 'when', 'why', 'how', 'which', 'whom', 'whose']
    words = text_lower.split()
    if words and words[0] in question_words:
        return True
    
    # Question patterns
    patterns = [
        r'^can you',
        r'^could you',
        r'^would you',
        r'^will you',
        r'^do you',
        r'^does you',
        r'^did you',
        r'^are you',
        r'^is you',
        r'^have you',
        r'^has you',
        r'^should you',
        r'^may i',
        r'^can i',
        r'^could i',
        r'^shall i',
        r'^what\'s',
        r'^who\'s',
        r'^where\'s',
        r'^when\'s',
        r'^why\'s',
        r'^how\'s',
    ]
    
    for pattern in patterns:
        if re.match(pattern, text_lower):
            return True
    
    return '?' in text

def correct_punctuation_and_capitalization(text):
    """Fix punctuation and capitalization"""
    if not text:
        return text
    
    # Trim whitespace
    text = text.strip()
    
    # Fix capitalization of first letter
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    
    # Fix "i" to "I"
    text = re.sub(r'\bi\b', 'I', text)
    
    # Check if it's a question
    question_detected = is_question(text)
    
    # Add appropriate ending punctuation
    if text and text[-1] not in ['.', '!', '?']:
        if question_detected:
            text += '?'
        else:
            text += '.'
    elif text and text[-1] == '.' and question_detected:
        text = text[:-1] + '?'
    
    # Fix spaces
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', text)
    
    return text

def correct_grammar_and_spelling(text):
    """Fix common grammar and spelling mistakes"""
    
    fixes = {
        r'\bdont\b': "don't",
        r'\bdoesnt\b': "doesn't",
        r'\bdidnt\b': "didn't",
        r'\bcant\b': "can't",
        r'\bwont\b': "won't",
        r'\bwouldnt\b': "wouldn't",
        r'\bcouldnt\b': "couldn't",
        r'\bshouldnt\b': "shouldn't",
        r'\bisnt\b': "isn't",
        r'\barent\b': "aren't",
        r'\bwasnt\b': "wasn't",
        r'\bwerent\b': "weren't",
        r'\bhavent\b': "haven't",
        r'\bwanna\b': "want to",
        r'\bgonna\b': "going to",
        r'\bgotta\b': "got to",
        r'\bkinda\b': "kind of",
        r'\bcuz\b': "because",
        r'\bcoz\b': "because",
        r'\brecieve\b': "receive",
        r'\bacheive\b': "achieve",
        r'\bbeleive\b': "believe",
        r'\bseperate\b': "separate",
        r'\bdefinately\b': "definitely",
        r'\bthier\b': "their",
        r'\byour\b welcome\b': "you're welcome",
        r'\btommorow\b': "tomorrow",
        r'\btoday\b': "today",
        r'\bbeutiful\b': "beautiful",
    }
    
    for pattern, replacement in fixes.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def correct_english(text):
    """Full correction pipeline"""
    if not text:
        return text
    
    text = correct_punctuation_and_capitalization(text)
    text = correct_grammar_and_spelling(text)
    
    return text

def get_response(user_message, user_name):
    """Generate response based on message"""
    
    msg_lower = user_message.lower()
    
    # Name response
    if user_message.strip().lower() == user_name.lower() or len(user_message.strip().split()) == 1 and user_message.strip().lower() not in ['hi', 'hello', 'hey']:
        return f"Hi {user_name}! Nice to meet you. How can I help you with your English today?"
    
    # Question about today's topic
    if 'today\'s topic' in msg_lower or 'topic today' in msg_lower:
        topics = ["daily life", "hobbies", "travel", "food", "movies", "music", "work", "school", "weather"]
        topic = random.choice(topics)
        return f"How about we talk about {topic}? What do you think? Or is there something specific you'd like to discuss?"
    
    # Question about bot's name
    if 'your name' in msg_lower or 'who are you' in msg_lower:
        return f"My name is John! I'm your personal English tutor bot. What's your name?"
    
    # Question about what bot can do
    if 'what can you do' in msg_lower or 'help me' in msg_lower:
        return "I can help you improve your English! I'll correct your spelling, grammar, punctuation, and capitalization. Just chat with me naturally!"
    
    # Greetings
    if any(word in msg_lower for word in ['hi', 'hello', 'hey']):
        return f"Hey {user_name}! How are you today?"
    
    # How are you
    if 'how are you' in msg_lower:
        return "I'm doing great, thanks for asking! How about you?"
    
    # Thanks
    if 'thank' in msg_lower:
        return "You're welcome! 😊"
    
    # Bye
    if any(word in msg_lower for word in ['bye', 'goodbye']):
        return f"Goodbye {user_name}! Come back soon to practice more English! 👋"
    
    # Default response
    return f"Interesting! Tell me more, {user_name}."

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
    
    print("🚀 Bot started! Waiting for messages...")
    
    while True:
        try:
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
                    
                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        user_name = message["from"].get("first_name", "Friend")
                        
                        print(f"💬 Message from {user_name}: {text}")
                        
                        send_typing_action(chat_id)
                        time.sleep(1)
                        
                        if text == "/start":
                            welcome = f"👋 Hi {user_name}! I'm your English tutor bot!\n\nI'll help you with:\n✅ Spelling\n✅ Grammar\n✅ Punctuation\n✅ Capitalization\n\nJust chat with me!"
                            send_message(chat_id, welcome)
                        
                        elif text == "/help":
                            help_text = "Just chat with me normally. I'll correct your English!"
                            send_message(chat_id, help_text)
                        
                        elif text:
                            corrected = correct_english(text)
                            
                            if corrected != text:
                                send_message(chat_id, f"✅ {corrected}")
                                time.sleep(0.5)
                                send_typing_action(chat_id)
                                time.sleep(0.5)
                            
                            response = get_response(text, user_name)
                            send_message(chat_id, response)
            
            time.sleep(1)
            
        except requests.exceptions.ReadTimeout:
            continue
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("🎯 Starting English Tutor Bot...")
    print("=" * 40)
    
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    print("✅ Web server started")
    time.sleep(2)
    
    process_updates()
