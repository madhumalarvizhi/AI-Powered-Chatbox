from flask import Flask, render_template, request, jsonify
import sqlite3
import nltk
from nltk.stem import WordNetLemmatizer
import random

# Download required NLTK data automatically
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet', quiet=True)

app = Flask(__name__)
lemmatizer = WordNetLemmatizer()

# 1. Setup SQLite Database for User Interaction Logs
def init_db():
    conn = sqlite3.connect('chatbot_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_message TEXT, 
                  bot_response TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 2. NLP Knowledge Base (Intents)
intents = {
    "greeting": {
        "patterns": ["hi", "hello", "hey", "good morning", "good evening", "vanakkam"],
        "responses": ["Hello! How can I help you today?", "Hi there! What can I do for you?"]
    },
    "hours": {
        "patterns": ["hours", "open", "time", "timing", "when are you open"],
        "responses": ["Our support team is available Monday to Friday, 9 AM to 6 PM."]
    },
    "services": {
        "patterns": ["services", "offer", "help", "support", "what do you do"],
        "responses": ["We provide AI solutions, web development, and 24/7 customer FAQ support."]
    },
    "contact": {
        "patterns": ["contact", "email", "phone", "call", "reach"],
        "responses": ["You can reach us at support@example.com or call +91-9876543210."]
    },
    "goodbye": {
        "patterns": ["bye", "goodbye", "see you", "thanks", "thank you"],
        "responses": ["Goodbye! Have a great day!", "You're welcome! Feel free to ask anytime."]
    }
}

# 3. NLP Processing Function
def get_bot_response(user_input):
    tokens = nltk.word_tokenize(user_input.lower())
    lemmatized_words = [lemmatizer.lemmatize(word) for word in tokens]
    
    for intent, data in intents.items():
        for pattern in data["patterns"]:
            if pattern in user_input.lower() or any(word in lemmatized_words for word in pattern.split()):
                return random.choice(data["responses"])
                
    return "I'm sorry, I didn't understand that. Could you please rephrase your question?"

# 4. Web Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    bot_reply = get_bot_response(user_msg)
    
    # Log interaction into SQLite database
    conn = sqlite3.connect('chatbot_logs.db')
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_message, bot_response) VALUES (?, ?)", (user_msg, bot_reply))
    conn.commit()
    conn.close()
    
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)