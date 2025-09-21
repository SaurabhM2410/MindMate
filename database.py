"""
Database setup and management for MindMate Mental Wellbeing Companion App
"""
import sqlite3
from datetime import datetime
import os

DATABASE_PATH = 'wellbeing.db'

def init_database():
    """Initialize the database with all required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create moods table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood_type TEXT NOT NULL,
            mood_emoji TEXT NOT NULL,
            intensity INTEGER DEFAULT 5,
            notes TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create journal entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT NOT NULL,
            mood_at_time TEXT,
            tags TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create chat conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            conversation_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create breathing sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS breathing_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_duration INTEGER NOT NULL,
            cycles_completed INTEGER NOT NULL,
            session_type TEXT DEFAULT '4-7-8',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def log_mood(mood_type, mood_emoji, intensity=5, notes=""):
    """Log a mood entry to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO moods (mood_type, mood_emoji, intensity, notes)
        VALUES (?, ?, ?, ?)
    ''', (mood_type, mood_emoji, intensity, notes))
    
    mood_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return mood_id

def save_journal_entry(content, title="", mood_at_time="", tags=""):
    """Save a journal entry to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO journal_entries (title, content, mood_at_time, tags)
        VALUES (?, ?, ?, ?)
    ''', (title, content, mood_at_time, tags))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return entry_id

def log_chat_conversation(user_message, ai_response, conversation_id=None):
    """Log a chat conversation to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    if not conversation_id:
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    cursor.execute('''
        INSERT INTO chat_conversations (user_message, ai_response, conversation_id)
        VALUES (?, ?, ?)
    ''', (user_message, ai_response, conversation_id))
    
    chat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return chat_id

def log_breathing_session(duration, cycles_completed, session_type="4-7-8"):
    """Log a breathing session to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO breathing_sessions (session_duration, cycles_completed, session_type)
        VALUES (?, ?, ?)
    ''', (duration, cycles_completed, session_type))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return session_id

def get_mood_history(days=30):
    """Get mood history for the last N days."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT mood_type, mood_emoji, intensity, notes, timestamp
        FROM moods 
        WHERE timestamp >= datetime('now', '-{} days')
        ORDER BY timestamp DESC
    '''.format(days))
    
    moods = cursor.fetchall()
    conn.close()
    
    return [{"type": mood[0], "emoji": mood[1], "intensity": mood[2], 
             "notes": mood[3], "timestamp": mood[4]} for mood in moods]

def get_journal_entries(limit=20):
    """Get recent journal entries."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, content, mood_at_time, tags, timestamp
        FROM journal_entries 
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    entries = cursor.fetchall()
    conn.close()
    
    return [{"id": entry[0], "title": entry[1], "content": entry[2], 
             "mood": entry[3], "tags": entry[4], "timestamp": entry[5]} for entry in entries]

def get_mood_statistics():
    """Get mood statistics for dashboard."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get mood counts by type for the last 30 days
    cursor.execute('''
        SELECT mood_type, COUNT(*) as count
        FROM moods 
        WHERE timestamp >= datetime('now', '-30 days')
        GROUP BY mood_type
        ORDER BY count DESC
    ''')
    
    mood_counts = cursor.fetchall()
    
    # Get average mood intensity for the last 7 days
    cursor.execute('''
        SELECT AVG(intensity) as avg_intensity
        FROM moods 
        WHERE timestamp >= datetime('now', '-7 days')
    ''')
    
    avg_intensity = cursor.fetchone()[0] or 5
    
    # Get total journal entries
    cursor.execute('SELECT COUNT(*) FROM journal_entries')
    total_entries = cursor.fetchone()[0]
    
    # Get total breathing sessions
    cursor.execute('SELECT COUNT(*) FROM breathing_sessions')
    total_sessions = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "mood_counts": [{"mood": mood[0], "count": mood[1]} for mood in mood_counts],
        "avg_intensity": round(avg_intensity, 1),
        "total_entries": total_entries,
        "total_breathing_sessions": total_sessions
    }

def update_user_setting(key, value):
    """Update or insert a user setting."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO user_settings (setting_key, setting_value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (key, value))
    
    conn.commit()
    conn.close()

def get_user_setting(key, default_value=""):
    """Get a user setting value."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT setting_value FROM user_settings WHERE setting_key = ?', (key,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else default_value

if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
    print("Database setup completed!")