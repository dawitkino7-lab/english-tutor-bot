import os
import sys
import time
import json
import requests
import threading
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
        " urs ": " yours ",
    }
    
    for wrong, right in fixes.items():
        corrected = corrected.replace(wrong, right)
    
    return corrected

def get_response(user_message, user_name):
    """Generate response based on message"""
    msg_lower = user_message.lower()
    
    if any(word in msg_lower for word in ['hi', 'hello', 'hey']):
        return f"Hey {user_name}! How are you?"
    elif 'how are you' in msg_lower:
        return "I'm doing great! Thanks for asking! How about you?"
    elif 'thank' in msg_lower:
        return "You're welcome! 😊"
    elif 'bye' in msg_lower:
        return "Goodbye! Talk to you soon! 👋"
    elif 'weather' in msg_lower:
        return "I hope the weather is nice where you are! ☀️"
    elif 'name' in msg_lower:
        return f"My name is John, and I'm your English tutor! What's your name?"
    else:
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
        requests.post(url, json=data)
    except Exception as e:
        print(f"Error sending message: {e}")

def process_updates():
    """Main bot loop"""
    last_update_id = 0
    
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
            
            if data["ok"] and data["result"]:
                for update in data["result"]:
                    last_update_id = update["update_id"]
                    
                    # Check if it's a message
                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        user_name = message["from"].get("first_name", "Friend")
                        
                        print(f"📨 Message from {user_name}: {text}")
                        
                        # Handle commands
                        if text == "/start":
                            welcome = f"👋 Hi {user_name}! I'm your English tutor bot!\n\nSend me any message and I'll help with your English."
                            send_message(chat_id, welcome)
                        
                        elif text == "/help":
                            help_text = "Just send me messages! I'll correct your English."
                            send_message(chat_id, help_text)
                        
                        elif text:
                            # Regular message - correct and respond
                            corrected = correct_english(text)
                            
                            if corrected != text:
                                send_message(chat_id, f"✅ {corrected}")
                                time.sleep(0.5)
                            
                            response = get_response(text, user_name)
                            send_message(chat_id, response)
        
        except requests.exceptions.ReadTimeout:
            # This is normal - just continue
            pass
        
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
    
    # Run bot in main thread
    process_updates()
