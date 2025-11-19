#!/bin/bash
# Quick start script for Water Level AI Assistant

echo "🌊 Water Level Monitoring + AI Assistant Setup"
echo "=============================================="
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Install Python 3.8+"
    exit 1
fi

echo "✓ Python found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r backend/requirements.txt

echo ""
echo "✓ Dependencies installed"

echo ""
echo "=============================================="
echo "🚀 To start the system, run these in separate terminals:"
echo ""
echo "Terminal 1 - Data Collection:"
echo "  python main.py"
echo ""
echo "Terminal 2 - ML Forecasting:"
echo "  python ml_forecast_weather.py"
echo ""
echo "Terminal 3 - Backend Server:"
echo "  cd backend && python app.py"
echo ""
echo "Then open: http://localhost:5000"
echo ""
echo "=============================================="
echo ""
echo "📝 Requirements:"
echo "  - Arduino with HC-SR04 sensor running (arduino.cpp)"
echo "  - Firebase Realtime Database configured"
echo "  - OpenAI API key in .env file"
echo ""
echo "🔑 Environment variables (.env):"
echo "  OPENAI_API_KEY=your_key_here"
echo "  FB_SENSOR=your_firebase_url"
echo "  FB_FORECAST=your_forecast_url"
echo "  LAT=10.7769  (your location latitude)"
echo "  LON=106.7009 (your location longitude)"
