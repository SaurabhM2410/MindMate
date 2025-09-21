@echo off
echo Starting MindMate Mental Wellbeing Companion...
echo.
echo Prerequisites Check:
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python detected - OK
echo.
echo Installing dependencies...
pip install flask==3.1.1 flask-cors==6.0.1 openai==1.97.1 requests>=2.31.0

echo.
echo Initializing database...
python database.py

echo.
echo Starting MindMate application...
echo Your app will be available at: http://localhost:5000
echo Set OPENAI_API_KEY environment variable for full AI functionality
echo.
python app.py
pause