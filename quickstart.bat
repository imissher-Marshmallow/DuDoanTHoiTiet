@echo off
REM FloodSense Quick Start for Windows

echo.
echo 🌊 FloodSense Quick Start (Windows)
echo ===================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo ✓ Python found

REM Check pip
echo Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip not found
    pause
    exit /b 1
)
echo ✓ pip found

REM Install dependencies
echo.
echo 📦 Installing dependencies...
cd backend
pip install -r requirements.txt
cd ..

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Check .env file
echo.
echo 🔐 Checking .env configuration...
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    (
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo FB_SENSOR=https://edfwef-default-rtdb.firebaseio.com/water_level/sensor1.json
        echo FB_FORECAST=https://edfwef-default-rtdb.firebaseio.com/forecast/sensor1.json
        echo FB_CONFIG=https://edfwef-default-rtdb.firebaseio.com/config/sensor1.json
        echo FB_COMMANDS=https://edfwef-default-rtdb.firebaseio.com/commands/sensor1.json
        echo LAT=10.7769
        echo LON=106.7009
        echo SENSOR_HEIGHT_CM=50
        echo UPDATE_INTERVAL_SEC=5
        echo ALERT_THRESHOLD_CM=30
        echo FLASK_ENV=production
        echo FLASK_DEBUG=0
        echo LOG_LEVEL=INFO
        echo AI_MODEL=gpt-4o-mini
        echo AI_MAX_TOKENS=300
        echo AI_TEMPERATURE=0.7
        echo CONVERSATION_HISTORY_LIMIT=10
        echo SESSION_TIMEOUT=3600
        echo ENABLE_LOGGING=1
        echo LOG_DIR=./logs
    ) > .env
    echo ✓ .env created with template values
) else (
    echo ✓ .env file exists
    findstr "your_openai_api_key_here" .env >nul
    if not errorlevel 1 (
        echo ⚠️  WARNING: .env still has placeholder API key!
        echo    Please edit .env and replace with your actual OpenAI key
    )
)

REM Create logs directory
echo.
echo 📁 Creating logs directory...
if not exist logs mkdir logs
echo ✓ Logs directory ready

REM Summary
echo.
echo ===================================
echo ✅ Setup Complete!
echo ===================================
echo.
echo Next steps:
echo.
echo 1. Edit .env and add your OpenAI API key:
echo    OPENAI_API_KEY=sk-proj-your-real-key-here
echo.
echo 2. Start the backend (in Command Prompt):
echo    python backend/app.py
echo.
echo 3. Open in browser:
echo    http://localhost:5000
echo.
echo 4. View logs (in another Command Prompt):
echo    type logs/app.log
echo.
echo Documentation:
echo   - IMPROVEMENTS_SUMMARY.md (overview)
echo   - AI_IMPROVEMENTS.md (AI features)
echo   - DEPLOYMENT_GUIDE.md (production)
echo.
pause
