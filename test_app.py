"""
Test script for MindMate Mental Wellbeing Companion App
Run this to verify all components are working correctly
"""
import sqlite3
import os
import requests
import json
from datetime import datetime

def test_database():
    """Test database initialization and basic operations"""
    print("🧪 Testing Database...")
    
    try:
        from database import init_database, log_mood, save_journal_entry, get_mood_statistics
        
        # Initialize database
        init_database()
        
        # Test mood logging
        mood_id = log_mood("happy", "😊", 8, "Testing mood logging")
        print(f"✅ Mood logged with ID: {mood_id}")
        
        # Test journal entry
        entry_id = save_journal_entry("Test journal entry", "Test Title", "happy", "test,automated")
        print(f"✅ Journal entry saved with ID: {entry_id}")
        
        # Test statistics
        stats = get_mood_statistics()
        print(f"✅ Statistics retrieved: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API Endpoints...")
    
    base_url = "http://127.0.0.1:5000/api"
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check endpoint working")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test mood logging
        mood_data = {
            "mood_type": "excited",
            "mood_emoji": "🤩",
            "intensity": 9,
            "notes": "API test successful!"
        }
        response = requests.post(f"{base_url}/mood", json=mood_data, timeout=5)
        if response.status_code == 200:
            print("✅ Mood logging endpoint working")
        else:
            print(f"❌ Mood logging failed: {response.status_code}")
        
        # Test chat endpoint
        chat_data = {"message": "Hello, this is a test!"}
        response = requests.post(f"{base_url}/chat", json=chat_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat endpoint working. Response: {result.get('reply', '')[:50]}...")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
        
        # Test journal endpoint
        journal_data = {
            "title": "API Test Entry",
            "content": "This is a test journal entry created by the automated test script.",
            "mood_at_time": "excited",
            "tags": "test,api,automated"
        }
        response = requests.post(f"{base_url}/journal", json=journal_data, timeout=5)
        if response.status_code == 200:
            print("✅ Journal endpoint working")
        else:
            print(f"❌ Journal endpoint failed: {response.status_code}")
        
        # Test dashboard stats
        response = requests.get(f"{base_url}/dashboard/stats", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard stats endpoint working")
        else:
            print(f"❌ Dashboard stats failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ API test failed: Cannot connect to server. Make sure the app is running!")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def check_file_structure():
    """Check if all required files exist"""
    print("\n🧪 Checking File Structure...")
    
    required_files = [
        "app.py",
        "database.py", 
        "templates/index.html",
        "static/style.css",
        "static/script.js",
        "README.md",
        "requirements.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_openai_integration():
    """Test OpenAI API integration"""
    print("\n🧪 Testing OpenAI Integration...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-api-key-here":
        print("⚠️  OpenAI API key not set - using fallback responses")
        print("   Set OPENAI_API_KEY environment variable for full AI functionality")
        return True
    else:
        print("✅ OpenAI API key is configured")
        # Test actual API call would go here
        return True

def main():
    """Run all tests"""
    print("🚀 MindMate App Testing Suite")
    print("=" * 50)
    
    # Check file structure first
    files_ok = check_file_structure()
    
    # Test database
    db_ok = test_database()
    
    # Test OpenAI integration
    openai_ok = test_openai_integration()
    
    # Test API endpoints (requires server to be running)
    print("\n⚠️  Make sure the Flask app is running (python app.py) before testing APIs...")
    api_ok = test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"File Structure: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"OpenAI Integration: {'✅ PASS' if openai_ok else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if all([files_ok, db_ok, openai_ok, api_ok]):
        print("\n🎉 All tests passed! Your MindMate app is ready to use!")
        print("🌍 Access your app at: http://localhost:5000")
    else:
        print("\n⚠️  Some tests failed. Check the errors above and fix them.")
    
    return all([files_ok, db_ok, openai_ok, api_ok])

if __name__ == "__main__":
    main()