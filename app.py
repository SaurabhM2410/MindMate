"""
MindMate - AI-Powered Mental Wellbeing Companion App
Flask Backend with OpenAI Integration
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import uuid
from openai import OpenAI
from database import (
    init_database, log_mood, save_journal_entry, log_chat_conversation,
    log_breathing_session, get_mood_history, get_journal_entries,
    get_mood_statistics, update_user_setting, get_user_setting
)

app = Flask(__name__)
CORS(app)

# Configure OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
)

# System prompt for MindMate AI
MINDMATE_SYSTEM_PROMPT = """You are MindMate, a compassionate mental wellbeing companion designed to support young adults. 

Core Principles:
- Respond with empathy, kindness, and genuine care
- Offer practical coping strategies and emotional support
- Never provide medical advice or diagnose conditions
- If someone mentions crisis, self-harm, or suicidal thoughts, immediately suggest emergency resources
- Keep responses warm, supportive, and age-appropriate for young adults
- Encourage healthy habits like journaling, breathing exercises, and self-care

Emergency Resources to Share When Needed:
- Crisis Text Line: Text HOME to 741741
- National Suicide Prevention Lifeline: 988
- International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/

Your responses should be:
- Supportive and validating
- 2-3 paragraphs maximum
- Include actionable suggestions when appropriate
- Encourage the user's strengths and resilience"""

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy", 
        "message": "MindMate API is running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """Chat with MindMate AI companion."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' in request"}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        conversation_id = data.get('conversation_id', str(uuid.uuid4()))
        
        # Check for crisis keywords
        crisis_keywords = ['suicide', 'kill myself', 'end it all', 'hurt myself', 'self-harm', 'crisis']
        is_crisis = any(keyword in user_message.lower() for keyword in crisis_keywords)
        
        if is_crisis:
            crisis_response = """I'm really concerned about you and want you to know that you're not alone. Please reach out for immediate help:

🆘 **Emergency Resources:**
- **Crisis Text Line**: Text HOME to 741741
- **National Suicide Prevention Lifeline**: Call or text 988
- **Emergency**: Call 911

You matter, and there are people who want to help you through this difficult time. Would you like to talk about what's making you feel this way?"""
            
            # Log the conversation
            log_chat_conversation(user_message, crisis_response, conversation_id)
            
            return jsonify({
                "reply": crisis_response,
                "conversation_id": conversation_id,
                "is_crisis": True
            })
        
        # Generate AI response using OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": MINDMATE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            if ai_response:
                ai_response = ai_response.strip()
            else:
                ai_response = "I'm here to listen. Please tell me more."
            
        except Exception as openai_error:
            # Fallback responses if OpenAI API fails
            fallback_responses = {
                "stressed": "I understand you're feeling stressed. Try taking three deep breaths with me: inhale for 4 counts, hold for 7, exhale for 8. Stress is temporary, and you have the strength to work through this. What's one small thing you could do right now to feel a bit better?",
                "anxious": "Anxiety can feel overwhelming, but you're not alone in this. Ground yourself by naming 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste. Would you like to try some breathing exercises or talk about what's making you anxious?",
                "sad": "I'm sorry you're feeling sad. It's okay to feel this way - your emotions are valid. Sometimes sadness helps us process important experiences. Would journaling help? Writing down your thoughts can sometimes bring clarity and relief.",
                "happy": "I'm so glad to hear you're feeling good! It's wonderful when we can appreciate positive moments. What's bringing you joy today? Celebrating these feelings can help us remember them during tougher times.",
                "tired": "Being tired can affect everything - your mood, thoughts, and energy. Are you getting enough sleep? Sometimes tiredness is our body's way of asking for rest or self-care. What would help you feel more energized?"
            }
            
            message_lower = user_message.lower()
            ai_response = None
            
            for emotion, response in fallback_responses.items():
                if emotion in message_lower:
                    ai_response = response
                    break
            
            if not ai_response:
                ai_response = "Thank you for sharing with me. I'm here to listen and support you. Sometimes it helps to talk through what we're experiencing. Would you like to tell me more about how you're feeling today?"
        
        # Log the conversation
        log_chat_conversation(user_message, ai_response, conversation_id)
        
        return jsonify({
            "reply": ai_response,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Chat error: {str(e)}"}), 500

@app.route('/api/mood', methods=['POST'])
def log_user_mood():
    """Log a user's mood."""
    try:
        data = request.get_json()
        if not data or 'mood_type' not in data or 'mood_emoji' not in data:
            return jsonify({"error": "Missing mood_type or mood_emoji"}), 400
        
        mood_type = data['mood_type']
        mood_emoji = data['mood_emoji']
        intensity = data.get('intensity', 5)
        notes = data.get('notes', '')
        
        mood_id = log_mood(mood_type, mood_emoji, intensity, notes)
        
        return jsonify({
            "status": "success",
            "message": f"Mood '{mood_type}' logged successfully",
            "mood_id": mood_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Mood logging error: {str(e)}"}), 500

@app.route('/api/mood/history')
def get_user_mood_history():
    """Get user's mood history."""
    try:
        days = request.args.get('days', 30, type=int)
        mood_history = get_mood_history(days)
        
        return jsonify({
            "moods": mood_history,
            "total_count": len(mood_history),
            "days_requested": days
        })
        
    except Exception as e:
        return jsonify({"error": f"Error fetching mood history: {str(e)}"}), 500

@app.route('/api/journal', methods=['POST'])
def save_user_journal():
    """Save a journal entry."""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Missing journal content"}), 400
        
        content = data['content'].strip()
        if not content:
            return jsonify({"error": "Journal content cannot be empty"}), 400
        
        title = data.get('title', '').strip()
        mood_at_time = data.get('mood_at_time', '')
        tags = data.get('tags', '')
        
        entry_id = save_journal_entry(content, title, mood_at_time, tags)
        
        return jsonify({
            "status": "success",
            "message": "Journal entry saved successfully",
            "entry_id": entry_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Journal save error: {str(e)}"}), 500

@app.route('/api/journal/entries')
def get_user_journal_entries():
    """Get user's journal entries."""
    try:
        limit = request.args.get('limit', 20, type=int)
        entries = get_journal_entries(limit)
        
        return jsonify({
            "entries": entries,
            "total_count": len(entries)
        })
        
    except Exception as e:
        return jsonify({"error": f"Error fetching journal entries: {str(e)}"}), 500

@app.route('/api/breathing', methods=['POST'])
def log_breathing_session():
    """Log a breathing exercise session."""
    try:
        data = request.get_json()
        if not data or 'duration' not in data or 'cycles_completed' not in data:
            return jsonify({"error": "Missing duration or cycles_completed"}), 400
        
        duration = data['duration']
        cycles_completed = data['cycles_completed']
        session_type = data.get('session_type', '4-7-8')
        
        session_id = log_breathing_session(duration, cycles_completed, session_type)
        
        return jsonify({
            "status": "success",
            "message": f"Breathing session logged: {cycles_completed} cycles in {duration} seconds",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Breathing session error: {str(e)}"}), 500

@app.route('/api/dashboard/stats')
def get_dashboard_statistics():
    """Get statistics for the dashboard."""
    try:
        stats = get_mood_statistics()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": f"Dashboard stats error: {str(e)}"}), 500

@app.route('/api/emergency-resources')
def get_emergency_resources():
    """Get emergency mental health resources."""
    resources = {
        "crisis_hotlines": [
            {
                "name": "Crisis Text Line",
                "contact": "Text HOME to 741741",
                "description": "24/7 crisis support via text message",
                "website": "https://www.crisistextline.org/"
            },
            {
                "name": "National Suicide Prevention Lifeline",
                "contact": "Call or text 988",
                "description": "24/7 free and confidential support",
                "website": "https://suicidepreventionlifeline.org/"
            },
            {
                "name": "SAMHSA National Helpline",
                "contact": "1-800-662-HELP (4357)",
                "description": "Treatment referral and information service",
                "website": "https://www.samhsa.gov/find-help/national-helpline"
            }
        ],
        "online_resources": [
            {
                "name": "7 Cups",
                "description": "Free online emotional support",
                "website": "https://www.7cups.com/"
            },
            {
                "name": "MindShift",
                "description": "Anxiety management app",
                "website": "https://www.anxietycanada.com/resources/mindshift-app/"
            },
            {
                "name": "Headspace",
                "description": "Meditation and mindfulness",
                "website": "https://www.headspace.com/"
            }
        ],
        "emergency": {
            "name": "Emergency Services",
            "contact": "911",
            "description": "For immediate life-threatening emergencies"
        }
    }
    
    return jsonify(resources)

@app.route('/api/settings', methods=['GET', 'POST'])
def user_settings():
    """Get or update user settings."""
    if request.method == 'GET':
        try:
            settings = {
                "notifications": get_user_setting("notifications", "true"),
                "theme": get_user_setting("theme", "light"),
                "reminder_frequency": get_user_setting("reminder_frequency", "daily"),
                "name": get_user_setting("name", "Friend")
            }
            return jsonify(settings)
        except Exception as e:
            return jsonify({"error": f"Settings fetch error: {str(e)}"}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No settings data provided"}), 400
            
            for key, value in data.items():
                update_user_setting(key, str(value))
            
            return jsonify({
                "status": "success",
                "message": "Settings updated successfully"
            })
        except Exception as e:
            return jsonify({"error": f"Settings update error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Initialize database
    print("🚀 Starting MindMate Mental Wellbeing Companion...")
    init_database()
    
    print("\n✨ MindMate Features Available:")
    print("   💬 AI Chat Companion (POST /api/chat)")
    print("   😊 Mood Tracking (POST /api/mood)")
    print("   📝 Journaling (POST /api/journal)")
    print("   🫁 Breathing Exercises (POST /api/breathing)")
    print("   📊 Dashboard Stats (GET /api/dashboard/stats)")
    print("   🆘 Emergency Resources (GET /api/emergency-resources)")
    print("   ⚙️  User Settings (GET/POST /api/settings)")
    
    print(f"\n🌍 Access your app at: http://localhost:5000")
    print("💡 Make sure to set your OPENAI_API_KEY environment variable!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)