# MindMate - AI-Powered Mental Wellbeing Companion

## 🌟 Complete Installation & Setup Guide

### 📁 Project Structure
```
New App/
├── app.py                 # Main Flask application
├── database.py           # Database setup and utilities
├── templates/
│   └── index.html        # Main HTML interface
├── static/
│   ├── style.css         # Styling and design
│   └── script.js         # Interactive JavaScript
├── mindmate.db          # SQLite database (auto-created)
└── requirements.txt      # Python dependencies
```

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.8+** installed on your system
- **Internet connection** for OpenAI API (optional, works with fallback responses)

### 2. Install Dependencies
```bash
pip install flask flask-cors openai
```

### 3. Set Up OpenAI API (Optional but Recommended)
For full AI chat functionality, set your OpenAI API key:

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-actual-openai-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your-actual-openai-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your-actual-openai-api-key-here"
```

> 💡 **Note:** The app works without an API key using intelligent fallback responses, but OpenAI integration provides better conversational AI.

### 4. Initialize Database
```bash
python database.py
```
You should see: ✅ Database initialized successfully!

### 5. Run the Application
```bash
python app.py
```

### 6. Access Your App
Open your browser and navigate to: **http://localhost:5000**

## 🎯 Features Overview

### 💬 AI Chat Companion
- **Empathetic AI responses** powered by OpenAI GPT-3.5/4
- **Crisis detection** with emergency resource suggestions
- **Fallback responses** when API is unavailable
- **Conversation logging** for continuity

### 😊 Mood Tracking
- **Visual mood selection** with emoji interface
- **Intensity scaling** (1-10) for detailed tracking
- **Note taking** for mood context
- **Historical mood charts** using Chart.js
- **7-day and 30-day trend analysis**

### 📝 Journaling
- **Rich text journaling** with title and tagging
- **Mood association** with journal entries
- **Auto-draft saving** (localStorage)
- **Entry history** with search and filtering
- **Export capabilities** (future enhancement)

### 🫁 Breathing Exercises
- **4-7-8 breathing technique** with visual guidance
- **Animated breathing circle** with color transitions
- **Session tracking** (cycles completed, duration)
- **Pause/resume functionality**
- **Progress statistics**

### 📊 Dashboard Analytics
- **Mood distribution charts** (doughnut chart)
- **Weekly statistics** (average mood, activity counts)
- **Quick action buttons** for immediate access
- **Visual progress indicators**

### 🆘 Emergency Resources
- **Crisis hotlines** with direct contact information
- **Online support resources** with active links
- **Mental health apps** recommendations
- **Emergency services** information

## 🔧 API Endpoints Reference

### Core Endpoints
- `GET /` - Main application interface
- `GET /api/health` - Health check
- `GET /api/emergency-resources` - Crisis resources

### Chat System
- `POST /api/chat` - Send message to AI companion
  ```json
  {
    "message": "I'm feeling stressed",
    "conversation_id": "optional-id"
  }
  ```

### Mood Tracking
- `POST /api/mood` - Log mood entry
  ```json
  {
    "mood_type": "happy",
    "mood_emoji": "😊",
    "intensity": 7,
    "notes": "Great day at work!"
  }
  ```
- `GET /api/mood/history?days=30` - Get mood history

### Journaling
- `POST /api/journal` - Save journal entry
  ```json
  {
    "title": "My Day",
    "content": "Today was amazing...",
    "mood_at_time": "happy",
    "tags": "work, success, gratitude"
  }
  ```
- `GET /api/journal/entries?limit=20` - Get journal entries

### Breathing Exercises
- `POST /api/breathing` - Log breathing session
  ```json
  {
    "duration": 300,
    "cycles_completed": 5,
    "session_type": "4-7-8"
  }
  ```

### Analytics
- `GET /api/dashboard/stats` - Dashboard statistics

### Settings
- `GET/POST /api/settings` - User preferences

## 🎨 Customization Guide

### Color Scheme
The app uses CSS custom properties for easy theming:
```css
:root {
  --primary-color: #667eea;
  --secondary-color: #f093fb;
  --accent-color: #4ecdc4;
  /* Modify these in static/style.css */
}
```

### Adding New Moods
In `static/script.js`, update the mood options:
```javascript
// Add new mood button in HTML
<button class="mood-btn" data-mood="grateful" data-emoji="🙏">
    <span class="mood-emoji">🙏</span>
    <span class="mood-label">Grateful</span>
</button>
```

### Custom AI Responses
Modify the `MINDMATE_SYSTEM_PROMPT` in `app.py`:
```python
MINDMATE_SYSTEM_PROMPT = """
Your custom AI personality and instructions here...
"""
```

## 🛠️ Development & Deployment

### Development Mode
- Debug mode is enabled by default
- Hot reload for code changes
- Console logging for troubleshooting

### Production Deployment
1. **Disable debug mode** in `app.py`:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

2. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set environment variables**:
   ```bash
   export FLASK_ENV=production
   export OPENAI_API_KEY=your-key-here
   ```

### Database Backups
```bash
# Backup database
cp mindmate.db mindmate_backup_$(date +%Y%m%d).db

# Restore from backup
cp mindmate_backup_20241221.db mindmate.db
```

## 🧪 Testing the Application

### Manual Testing Checklist
- [ ] **Navigation**: All tabs switch correctly
- [ ] **Chat**: Send messages and receive responses
- [ ] **Mood Logging**: Select mood, adjust intensity, add notes
- [ ] **Journal**: Write and save entries
- [ ] **Breathing**: Start/pause/stop exercise
- [ ] **Dashboard**: View statistics and charts
- [ ] **Resources**: Access emergency information
- [ ] **Mobile**: Test responsive design

### API Testing
Use PowerShell/curl to test endpoints:
```powershell
# Test health check
Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET

# Test mood logging
Invoke-RestMethod -Uri "http://localhost:5000/api/mood" -Method POST -Body '{"mood_type": "happy", "mood_emoji": "😊", "intensity": 8}' -ContentType "application/json"

# Test chat
Invoke-RestMethod -Uri "http://localhost:5000/api/chat" -Method POST -Body '{"message": "Hello!"}' -ContentType "application/json"
```

## 🔍 Troubleshooting

### Common Issues

**1. Database Not Found**
```bash
# Solution: Initialize database
python database.py
```

**2. OpenAI API Errors**
- Check API key is set correctly
- Verify account has credits
- App works with fallback responses if API fails

**3. Static Files Not Loading**
- Ensure `static/` and `templates/` directories exist
- Check file permissions
- Verify Flask app can access files

**4. Port Already in Use**
```bash
# Find process using port 5000
netstat -ano | findstr :5000
# Kill process or change port in app.py
```

**5. JavaScript Errors**
- Open browser developer tools (F12)
- Check console for errors
- Verify all script files are loading

### Performance Optimization
- **Database indexing** for large datasets
- **Caching** for repeated API calls
- **Compression** for static assets
- **CDN** for external libraries

## 📱 Mobile Responsiveness

The app is fully responsive and works on:
- **Desktop** (Chrome, Firefox, Safari, Edge)
- **Tablets** (iPad, Android tablets)
- **Mobile phones** (iOS Safari, Android Chrome)

### Mobile-Specific Features
- Touch-friendly interface
- Swipe gestures (future enhancement)
- Progressive Web App capabilities (future enhancement)

## 🔐 Security Considerations

### Data Protection
- **Local SQLite database** - data stays on your device
- **No external data transmission** except OpenAI API calls
- **Environment variables** for sensitive keys
- **Input validation** on all forms

### Privacy Features
- **No user registration** required
- **Anonymous usage** by default
- **Local data storage** only
- **Optional cloud sync** (future enhancement)

## 🎯 Future Enhancements

### Planned Features
- [ ] **Data export/import** (JSON, CSV)
- [ ] **Advanced analytics** (mood patterns, correlations)
- [ ] **Meditation timer** with guided sessions
- [ ] **Goal setting** and progress tracking
- [ ] **Social features** (anonymous community support)
- [ ] **Therapist integration** (secure communication)
- [ ] **Mobile app** (React Native/Flutter)
- [ ] **Voice interaction** (speech-to-text)
- [ ] **Wearable integration** (Apple Watch, Fitbit)

### Technical Improvements
- [ ] **Progressive Web App** (PWA) capabilities
- [ ] **Offline functionality** with service workers
- [ ] **Real-time sync** across devices
- [ ] **Advanced security** (encryption, authentication)
- [ ] **Performance optimization** (lazy loading, caching)

## 📞 Support & Contributing

### Getting Help
- **GitHub Issues**: Report bugs or request features
- **Documentation**: Check this README for guidance
- **Community**: Join discussions and share feedback

### Contributing Guidelines
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License & Acknowledgments

### License
This project is open source and available under the MIT License.

### Acknowledgments
- **OpenAI** for GPT API integration
- **Chart.js** for beautiful data visualization
- **Font Awesome** for icons
- **Inter Font** by Google Fonts

### Third-Party Libraries
- Flask (web framework)
- SQLite (database)
- Chart.js (charts)
- Font Awesome (icons)

---

## 🎉 Congratulations!

You now have a fully functional AI-Powered Mental Wellbeing Companion App! This comprehensive platform supports young adults in their mental health journey with empathetic AI chat, mood tracking, journaling, breathing exercises, and emergency resources.

**Start your wellness journey today:** http://localhost:5000

Remember: This app complements but doesn't replace professional mental health care. Always seek professional help for serious mental health concerns.

---

*Built with ❤️ for mental wellness and wellbeing*
