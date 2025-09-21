from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Database setup
def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect('mood_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def ai_chat(user_message):
    """Simple AI chat function - returns a basic response."""
    # This is a placeholder function since we don't have OpenAI integration here
    # You can integrate with OpenAI API or any other AI service
    responses = {
        "hello": "Hello! How are you feeling today?",
        "how are you": "I'm doing well! How can I help you track your mood?",
        "sad": "I'm sorry to hear you're feeling sad. Would you like to talk about it?",
        "happy": "That's wonderful to hear! What's making you happy today?",
        "angry": "I understand you're feeling angry. Take a deep breath. What's bothering you?",
        "default": "I'm here to listen and help you track your mood. How are you feeling?"
    }
    
    message_lower = user_message.lower()
    for key in responses:
        if key in message_lower:
            return responses[key]
    return responses["default"]

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not request.json or 'message' not in request.json:
            return jsonify({"error": "Missing 'message' in request"}), 400
        
        user_message = request.json['message']
        ai_response = ai_chat(user_message)
        
        # Log the conversation to database
        conn = sqlite3.connect('mood_tracker.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_logs (user_message, ai_response) VALUES (?, ?)",
            (user_message, ai_response)
        )
        conn.commit()
        conn.close()
        
        return jsonify({"reply": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/log_mood', methods=['POST'])
def log_mood():
    try:
        if not request.json or 'mood' not in request.json:
            return jsonify({"error": "Missing 'mood' in request"}), 400
        
        mood = request.json['mood']
        
        # Save to database
        conn = sqlite3.connect('mood_tracker.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO moods (mood) VALUES (?)",
            (mood,)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success", 
            "message": f"Mood '{mood}' logged successfully",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/moods', methods=['GET'])
def get_moods():
    """Get all logged moods."""
    try:
        conn = sqlite3.connect('mood_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT mood, timestamp FROM moods ORDER BY timestamp DESC")
        moods = cursor.fetchall()
        conn.close()
        
        return jsonify({"moods": [{"mood": mood, "timestamp": timestamp} for mood, timestamp in moods]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Mood tracker API is running"})

if __name__ == '__main__':
    # Initialize database before starting the app
    init_db()
    print("Database initialized successfully!")
    print("Starting Mood Tracker API...")
    print("Available endpoints:")
    print("  POST /chat - Chat with AI")
    print("  POST /log_mood - Log your mood")
    print("  GET /moods - Get all logged moods")
    print("  GET /health - Health check")
    app.run(debug=True)