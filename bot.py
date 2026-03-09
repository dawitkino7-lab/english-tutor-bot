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
    text_lower = text.lower().strip()
    
    # Question words
    question_words = ['what', 'who', 'where', 'when', 'why', 'how', 'which', 'whom', 'whose']
    
    # Check if starts with question word
    words = text_lower.split()
    if words and words[0] in question_words:
        return True
    
    # Check for question patterns
    question_patterns = [
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
        r'^whats',
        r'^whos',
        r'^wheres',
        r'^whens',
        r'^whys',
        r'^hows',
    ]
    
    for pattern in question_patterns:
        if re.match(pattern, text_lower):
            return True
    
    # Check for question structure (verb before subject)
    structures = [
        r'^can .+ \?*$',
        r'^could .+ \?*$',
        r'^would .+ \?*$',
        r'^will .+ \?*$',
        r'^do .+ \?*$',
        r'^does .+ \?*$',
        r'^did .+ \?*$',
        r'^are .+ \?*$',
        r'^is .+ \?*$',
        r'^have .+ \?*$',
        r'^has .+ \?*$',
    ]
    
    for pattern in structures:
        if re.match(pattern, text_lower):
            return True
    
    return '?' in text

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
    
    # Check if it's a question
    question_detected = is_question(text)
    
    # Fix punctuation: Add appropriate ending punctuation
    if text and text[-1] not in ['.', '!', '?']:
        if question_detected:
            text += '?'
        else:
            text += '.'
    elif text and text[-1] == '.' and question_detected:
        # Replace period with question mark if it's a question
        text = text[:-1] + '?'
    
    # Fix multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Fix space before punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    # Fix space after punctuation
    text = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', text)
    
    return text

def correct_grammar_and_spelling(text):
    """Fix common grammar and spelling mistakes"""
    
    # Dictionary of fixes (case insensitive)
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
        r'\bmustnt\b': "mustn't",
        r'\bneednt\b': "needn't",
        
        # Informal to formal
        r'\bwanna\b': "want to",
        r'\bgonna\b': "going to",
        r'\bgotta\b': "got to",
        r'\bkinda\b': "kind of",
        r'\bsorta\b': "sort of",
        r'\boutta\b': "out of",
        r'\bcuz\b': "because",
        r'\bcoz\b': "because",
        r'\bcoz\b': "because",
        
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
        r'\btommorow\b': "tomorrow",
        r'\btoday\b': "today",
        r'\btomorow\b': "tomorrow",
        r'\btomoro\b': "tomorrow",
        r'\bbeutiful\b': "beautiful",
        r'\bbeautyful\b': "beautiful",
        r'\bbecouse\b': "because",
        r'\bbecuz\b': "because",
        r'\bbecuse\b': "because",
        r'\bbegining\b': "beginning",
        r'\bbuisness\b': "business",
        r'\bcalender\b': "calendar",
        r'\bcarryng\b': "carrying",
        r'\bcenters\b': "centres",
        r'\bcheif\b': "chief",
        r'\bcollegue\b': "colleague",
        r'\bcomit\b': "commit",
        r'\bcomited\b': "committed",
        r'\bcomittee\b': "committee",
        r'\bcompletly\b': "completely",
        r'\bconcensus\b': "consensus",
        r'\bconcious\b': "conscious",
        r'\bconsistant\b': "consistent",
        r'\bcontridiction\b': "contradiction",
        r'\bcopywrite\b': "copyright",
        r'\bdeffinitely\b': "definitely",
        r'\bdependancy\b': "dependence",
        r'\bdesparate\b': "desperate",
        r'\bdevelopement\b': "development",
        r'\bdifferant\b': "different",
        r'\bdilema\b': "dilemma",
        r'\bdisapear\b': "disappear",
        r'\bdisapoint\b': "disappoint",
        r'\becstacy\b': "ecstasy",
        r'\beffective\b': "effective",
        r'\bembarass\b': "embarrass",
        r'\benviroment\b': "environment",
        r'\bexagerate\b': "exaggerate",
        r'\bexcell\b': "excel",
        r'\bexcellant\b': "excellent",
        r'\bexistance\b': "existence",
        r'\bexperiance\b': "experience",
        r'\bfebuary\b': "February",
        r'\bFebuary\b': "February",
        r'\bFeb\b': "February",
        r'\bforiegn\b': "foreign",
        r'\bforth\b': "fourth",
        r'\bfoward\b': "forward",
        r'\bfreqent\b': "frequent",
        r'\bgarantee\b': "guarantee",
        r'\bgrammer\b': "grammar",
        r'\bgratful\b': "grateful",
        r'\bguidence\b': "guidance",
        r'\bhapened\b': "happened",
        r'\bhapening\b': "happening",
        r'\bheared\b': "heard",
        r'\bhelpless\b': "helpless",
        r'\bherat\b': "heart",
        r'\bheres\b': "here's",
        r'\bhere's\b': "here is",
        r'\bhowever\b': "however",
        r'\bhumour\b': "humor",
        r'\bideah\b': "idea",
        r'\bidear\b': "idea",
        r'\bidae\b': "idea",
        r'\bimediately\b': "immediately",
        r'\bindependant\b': "independent",
        r'\binterum\b': "interim",
        r'\bintresting\b': "interesting",
        r'\binvite\b': "invitation",
        r'\bij\b': "I",
        r'\bim\b': "I'm",
        r'\bive\b': "I've",
        r'\bid\b': "I'd",
        r'\bill\b': "I'll",
        r'\bjan\b': "January",
        r'\bjanuary\b': "January",
        r'\bjuly\b': "July",
        r'\bjune\b': "June",
        r'\bknowlege\b': "knowledge",
        r'\blabratory\b': "laboratory",
        r'\blayed\b': "laid",
        r'\bloose\b': "lose",
        r'\bloosing\b': "losing",
        r'\bloss\b': "loss",
        r'\bmaintance\b': "maintenance",
        r'\bmarch\b': "March",
        r'\bmay\b': "May",
        r'\bnov\b': "November",
        r'\boct\b': "October",
        r'\bsept\b': "September",
        r'\baug\b': "August",
        r'\bdec\b': "December",
    }
    
    # Apply fixes
    for pattern, replacement in fixes.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def correct_english(text):
    """Full correction pipeline"""
    if not text:
        return text
    
    original = text
    
    # Step 1: Fix punctuation and capitalization
    text = correct_punctuation_and_capitalization(text)
    
    # Step 2: Fix grammar and spelling
    text = correct_grammar_and_spelling(text)
    
    return text

def answer_question(user_message, user_name):
    """Actually answer questions instead of deflecting"""
    
    msg_lower = user_message.lower()
    
    # Question about bot's name
    if any(word in msg_lower for word in ['your name', 'who are you', 'what are you']):
        return f"My name is John! I'm your personal English tutor bot. I'm here to help you practice and improve your English skills. What's your name?"
    
    # Question about user's name
    if 'my name' in msg_lower and '?' in msg_lower or msg_lower.startswith('my name is'):
        return f"Nice to meet you! I'll call you {user_name}. How can I help you with your English today?"
    
    # Question about what bot can do
    if any(word in msg_lower for word in ['what can you do', 'what do you do', 'your purpose', 'what are you for']):
        return "I can help you improve your English! I'll correct your spelling, grammar, punctuation, and capitalization. We can chat about anything - your day, hobbies, interests, or specific topics you want to practice. Just talk to me naturally!"
    
    # Question about age
    if ('how old' in msg_lower and ('you' in msg_lower or 'bot' in msg_lower)) or ('your age' in msg_lower):
        return "I'm a bot, so I don't have an age! But I was created recently to help people like you learn English. 😊 How old are you? (if you don't mind sharing)"
    
    # Question about location
    if any(word in msg_lower for word in ['where are you from', 'where do you live', 'your location', 'where are you located']):
        return "I live in the cloud! ☁️ I'm an AI bot, so I don't have a physical location. But I'm always here whenever you need me! Where are you from?"
    
    # Question about time
    if any(word in msg_lower for word in ['what time', 'time now', 'current time', 'tell me the time']):
        current_time = datetime.now().strftime("%I:%M %p")
        return f"I don't have a watch, but I know it's {current_time} where my server is! What time is it where you are?"
    
    # Question about date
    if any(word in msg_lower for word in ['what date', "today's date", 'date today', 'what day']):
        current_date = datetime.now().strftime("%B %d, %Y")
        return f"Today is {current_date}. Is there something special happening today?"
    
    # Question about weather
    if 'weather' in msg_lower and ('?' in user_message or is_question(user_message)):
        return "I wish I could check the weather for you, but I don't have internet access for that. Tell me about the weather where you are! Is it sunny, rainy, or something else?"
    
    # Question about helping with English
    if any(word in msg_lower for word in ['help me', 'can you help']):
        return "Of course! I'd love to help you with English. The best way to practice is just to chat with me naturally. I'll correct your mistakes as we talk. What would you like to discuss today?"
    
    # Question about favorites
    if 'favorite' in msg_lower and ('?' in user_message or is_question(user_message)):
        if 'color' in msg_lower:
            return "My favorite color is blue! 💙 It's calm and peaceful. What's your favorite color?"
        elif 'food' in msg_lower:
            return "I don't eat food, but I hear pizza and chocolate are pretty popular! What's your favorite food?"
        elif 'movie' in msg_lower:
            return "I don't watch movies, but I'd love to hear about your favorite movie! What do you like about it?"
        elif 'music' in msg_lower:
            return "I don't listen to music, but I know it's wonderful! What kind of music do you enjoy?"
        elif 'book' in msg_lower:
            return "Books are great! I don't read, but I'd love to know what book you like. What's it about?"
        elif 'sport' in msg_lower:
            return "Sports are exciting! What's your favorite sport to watch or play?"
        else:
            return f"That's a great question! I don't have favorites since I'm a bot, but I'd love to hear what your favorite is!"
    
    # Question about feelings
    if any(word in msg_lower for word in ['how do you feel', 'are you happy', 'are you sad', 'do you have feelings']):
        return "I don't have feelings like humans do, but I'm programmed to be friendly and helpful! Talking with you makes my code happy. 😊 How are you feeling today?"
    
    # Question about capabilities
    if 'can you' in msg_lower and ('?' in user_message or is_question(user_message)):
        if 'correct' in msg_lower:
            return "Yes, I can definitely correct your English! That's my main job. Just keep chatting and I'll fix any mistakes I see."
        elif 'understand' in msg_lower:
            return "Yes, I understand English pretty well! I might miss some things occasionally, but I'll do my best to understand you."
        elif 'speak' in msg_lower:
            return "I can only communicate through text for now, but I'm pretty good at it! 😊"
        else:
            return "I can help you practice English, correct your mistakes, and chat with you about various topics. What specifically would you like me to do?"
    
    # Question about today's topic
    if 'today\'s topic' in msg_lower or 'topic today' in msg_lower:
        topics = ["conversation practice", "daily life", "hobbies", "travel", "food", "movies", "music", "work", "school", "weather"]
        topic = random.choice(topics)
        return f"How about we talk about {topic}? What do you think? Or is there something specific you'd like to discuss?"
    
    # Question about learning
    if any(word in msg_lower for word in ['how to learn', 'best way to learn', 'improve my english']):
        return "The best way to improve your English is to practice regularly! Chat with me often, try to express your thoughts in English, and pay attention to the corrections I make. Also, watching English movies, reading books, and listening to English music can help a lot! What do you enjoy doing in your free time?"
    
    # Question about bot's intelligence
    if any(word in msg_lower for word in ['are you ai', 'are you smart', 'are you intelligent']):
        return "I'm an AI bot, but I'm not as smart as humans! I follow rules and patterns to help you practice English. But I'm getting better with every conversation! 😊"
    
    return None  # Not a question we have an answer for

def get_topic_response(topic, user_name):
    """Generate response based on detected topic"""
    
    topic_responses = {
        'greeting': [
            f"Hey {user_name}! Great to see you! How's your day going?",
            f"Hello {user_name}! Ready to practice some English?",
            f"Hi there {user_name}! What would you like to talk about today?",
        ],
        'how_are_you': [
            "I'm doing really well, thanks for asking! I'm here and ready to help you with English. How about you?",
            "I'm great! Just waiting for our next English conversation. How are you today?",
            "I'm fantastic! Thanks for checking in. Tell me about your day!",
        ],
        'thanks': [
            "You're very welcome! 😊",
            "My pleasure! That's what I'm here for.",
            "Happy to help! Keep practicing!",
            "Anytime! Let's keep learning together.",
        ],
        'bye': [
            f"Goodbye {user_name}! Come back soon to practice more English! 👋",
            f"See you later! Keep practicing your English!",
            f"Bye! It was great chatting with you. Talk to you soon!",
        ],
        'weather': [
            "Weather is always a great topic! What's it like where you are today?",
            "I hope the weather is nice for you! Do you prefer sunny days or rainy days?",
            "Tell me about the weather! I love hearing about different places.",
        ],
        'food': [
            "Food is wonderful! What's your favorite dish?",
            "I love talking about food! Do you enjoy cooking or eating out more?",
            "That sounds delicious! Tell me more about what you like to eat.",
        ],
        'learning': [
            "That's great that you're learning English! You're doing really well. What part of English do you find most challenging?",
            "I'm here to help you improve! Your English is getting better with every message. What would you like to focus on?",
            "Practice makes perfect! You're doing a great job. Is there anything specific you want to work on?",
        ],
        'compliment': [
            "Aww, thank you! 😊 You're doing great with your English too!",
            "Thanks! But YOU'RE the one doing all the hard work learning English!",
            "I appreciate that! But the real star is you for practicing so diligently!",
        ],
        'question': [
            f"That's a good question! Let me think...",
            f"Interesting question! I'd say...",
            f"Great question! Here's what I think:",
        ],
        'short': [
            f"Tell me more about that, {user_name}!",
            "I'd love to hear more details!",
            "That's interesting! Can you elaborate?",
            f"What else comes to mind, {user_name}?",
        ],
        'default': [
            f"That's really interesting, {user_name}! Tell me more.",
            "I see! What else would you like to share?",
            "Thanks for sharing that with me!",
            "I'm following along! Please continue.",
            f"Great! Keep going, {user_name}. I'm learning about you.",
        ]
    }
    
    return random.choice(topic_responses.get(topic, topic_responses['default']))

def detect_topic(user_message, user_name, is_question_flag):
    """Detect the topic of the message"""
    
    msg_lower = user_message.lower()
    
    # Check if it's a question first (for proper handling)
    if is_question_flag:
        return 'question'
    
    # Greetings
    greetings = ['hi', 'hello', 'hey', 'greetings', 'whats up', 'sup', 'howdy']
    if any(word in msg_lower for word in greetings) and len(user_message.split()) <= 3:
        return 'greeting'
    
    # How are you
    if 'how are you' in msg_lower:
        return 'how_are_you'
    
    # Thanks
    if any(word in msg_lower for word in ['thank', 'thanks', 'thx']):
        return 'thanks'
    
    # Farewells
    if any(word in msg_lower for word in ['bye', 'goodbye', 'see you', 'cya']):
        return 'bye'
    
    # Weather
    if 'weather' in msg_lower:
        return 'weather'
    
    # Food
    if any(word in msg_lower for word in ['food', 'eat', 'restaurant', 'cook', 'meal', 'pizza', 'pasta', 'rice']):
        return 'food'
    
    # Learning English
    if any(word in msg_lower for word in ['learn english', 'improve english', 'practice english', 'study english']):
        return 'learning'
    
    # Compliments
    if any(word in msg_lower for word in ['good bot', 'great bot', 'nice bot', 'you rock', 'awesome bot']):
        return 'compliment'
    
    # Short messages
    if len(user_message.split()) <= 3:
        return 'short'
    
    return 'default'

def get_smart_response(user_message, user_name, conversation_history):
    """Generate intelligent responses based on context"""
    
    # FIRST: Check if it's a question we can answer directly
    question_answer = answer_question(user_message, user_name)
    if question_answer:
        return question_answer
    
    # Check if it's a question (for proper punctuation)
    question_detected = is_question(user_message)
    
    # Detect topic
    topic = detect_topic(user_message, user_name, question_detected)
    
    # Get topic-based response
    response = get_topic_response(topic, user_name)
    
    return response

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
                            help_text = "📚 <b>How to use me:</b>\n\n• Just chat with me normally\n• I'll correct your punctuation and capitalization\n• I'll add question marks when you ask questions\n• I'll fix spelling and grammar mistakes\n• I'll answer your questions directly\n• We can talk about ANY topic\n\nThe more you chat, the more you learn!"
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
