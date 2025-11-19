# Water Level Monitoring & AI Assistant Integration Guide

## System Overview

Your system now fully integrates IoT sensor data with Machine Learning predictions and AI-powered responses. Here's the complete data flow:

```
Arduino (HC-SR04 Sensor)
    ↓
Firebase Realtime Database
    ↓
main.py (Fetch & Store)
    ↓
history.csv (Local History)
    ↓
ml_forecast_weather.py (ML Training)
    ↓
Firebase (Predictions)
    ↓
Flask Backend (app.py)
    ↓
OpenAI + Context
    ↓
AI Assistant Frontend (ai-assistant.html)
```

---

## Component Details

### 1. Arduino (arduino.cpp)
**Role:** Measure water level and send to Firebase

- Uses **HC-SR04 ultrasonic sensor** to measure distance
- Calculates water level: `waterLevel = sensorHeight - distance`
- Sends every 5 seconds (configurable) to Firebase:
  ```json
  {
    "distance": 15.23,
    "waterLevel": 34.77,
    "timestamp": 1700400000000
  }
  ```
- Fetches config from Firebase for remote updates

### 2. main.py
**Role:** Fetch latest sensor data and build history

- Polls Firebase every 5 seconds
- Validates timestamps and removes duplicates
- Stores data in `history.csv`:
  ```csv
  distance,waterLevel,timestamp
  15.23,34.77,1700400000000
  15.45,34.55,1700400005000
  ```
- Maintains a clean local database for ML training

### 3. ml_forecast_weather.py
**Role:** Train ML models and predict future water levels

**Key Features:**
- **Fetches sensor data** from Firebase
- **Incorporates weather** via Open-Meteo API (rainfall)
- **Trains LinearRegression model** using:
  - Time elapsed (relative seconds)
  - Recent precipitation (optional feature)
- **Predicts** water level for +10min and +30min
- **Pushes predictions** back to Firebase:
  ```json
  {
    "pred_10min": 35.42,
    "pred_30min": 36.15,
    "timestamp": 1700400010000,
    "model": "LinearRegression",
    "features": "time_series+weather"
  }
  ```

**ML Logic:**
```python
X = [time_elapsed, rainfall]  # Features
y = water_level               # Target
model = LinearRegression().fit(X, y)
prediction = model.predict([future_time, future_rainfall])
```

### 4. Flask Backend (backend/app.py)
**Role:** Serve water data and AI responses with context

**New Endpoints:**

#### GET `/api/water-status`
Returns current water level, forecast, and statistics:
```json
{
  "sensor": {
    "waterLevel": 34.77,
    "distance": 15.23,
    "timestamp": 1700400000000
  },
  "forecast": {
    "pred_10min": 35.42,
    "pred_30min": 36.15,
    "timestamp": 1700400010000
  },
  "history": {
    "current": 34.77,
    "min": 20.15,
    "max": 45.30,
    "avg": 32.45,
    "records": 120
  }
}
```

#### POST `/chat`
Chat with AI using water level context:

**Request:**
```json
{"message": "What is the current water level?"}
```

**System Prompt Now Includes:**
- Current water level from sensor
- ML prediction for +10min
- Min/max/avg from history
- Instructions to use this data

**Response Example:**
```json
{
  "reply": "Mực nước hiện tại là 34.77 mm. Dự báo trong 10 phút tới là 35.42 mm (tăng nhẹ). Mực nước trung bình là 32.45 mm."
}
```

### 5. AI Assistant Frontend (frontend/ai-assistant.html)
**New Features:**

#### Live Water Status Panel
- Displays current water level with color coding:
  - 🟢 **Normal** (< 150 mm)
  - 🟡 **Warning** (150-200 mm)
  - 🔴 **Danger** (> 200 mm)
- Shows ML forecast (+10 min)
- Displays min/max/avg statistics
- Auto-updates every 5 seconds
- Manual refresh button

#### Enhanced Chat
- Chat interface fetches AI responses with water context
- User can ask about current/future water levels
- AI responds based on real sensor data

---

## How to Run

### Prerequisites
```bash
pip install -r backend/requirements.txt
```

### Step 1: Start Arduino
- Upload `arduino.cpp` to ESP32
- Ensure WiFi credentials are correct
- Sensor begins transmitting to Firebase

### Step 2: Run Data Collection (main.py)
```bash
python main.py
```
- Runs once to fetch latest data and append to history
- Can be scheduled as a cron job or run continuously

### Step 3: Start ML Pipeline
```bash
python ml_forecast_weather.py
```
- Trains model every 5 seconds
- Updates Firebase with predictions
- Monitor output:
  ```
  [SUMMARY]
    Current water level: 34.77 mm
    10-min forecast: 35.42 mm
    30-min forecast: 36.15 mm
    Recent rainfall: 2.5 mm
    Data points in history: 120
  ```

### Step 4: Run Flask Backend
```bash
cd backend
python app.py
```
- Starts on `http://localhost:5000`
- Serves frontend + AI endpoints

### Step 5: Access Frontend
Open browser: `http://localhost:5000`
- View water status panel
- Ask AI questions about water level

---

## Example Questions for AI Assistant

### Current Status
- "Mực nước hiện tại là bao nhiêu mm?"
  - Response: Uses sensor data
- "Mực nước so với trung bình thế nào?"
  - Response: Compares with history

### Forecasts
- "Mực nước sẽ bao nhiêu trong 10 phút tới?"
  - Response: Uses ML prediction
- "Có nguy hiểm lũ lụt không?"
  - Response: Analyzes forecast vs thresholds

### Trends
- "Mực nước đang tăng hay giảm?"
  - Response: Compares current vs history min/max
- "Mực nước cao nhất là bao nhiêu?"
  - Response: Uses history max

---

## Configuration

### Firebase URLs (in .env file)
```
FB_SENSOR=https://your-project.firebaseio.com/water_level/sensor1.json
FB_FORECAST=https://your-project.firebaseio.com/forecast/sensor1.json
```

### Weather Location (ml_forecast_weather.py)
```python
LAT = "10.7769"   # Ho Chi Minh City
LON = "106.7009"
```
Modify for your location

### Water Level Thresholds (frontend/ai-assistant.html)
```javascript
if (waterLevel > 200) levelClass = "danger";    // Red
else if (waterLevel > 150) levelClass = "warning"; // Yellow
else levelClass = "normal";                     // Green
```

### Update Intervals
- Arduino: 5 seconds (configurable in Firebase `/config/sensor1.json`)
- main.py: Run manually or via cron
- ML pipeline: Every 5 seconds
- Frontend: Auto-refresh every 5 seconds

---

## File Structure
```
/
├── arduino.cpp                    # IoT sensor code
├── main.py                        # Data collection
├── ml_forecast_weather.py         # ML predictions
├── history.csv                    # Local data store
├── backend/
│   ├── app.py                     # Flask server (UPDATED)
│   └── requirements.txt
├── frontend/
│   ├── ai-assistant.html          # AI chat (UPDATED)
│   ├── index.html
│   ├── giaodien.css
│   └── ...
└── INTEGRATION_GUIDE.md           # This file
```

---

## Data Flow Example

**Time: 14:30:00**

1. **Arduino** → Firebase: `{waterLevel: 34.77, timestamp: 1700400000000}`
2. **main.py** → Reads Firebase, appends to CSV
3. **ML Pipeline** → Reads history, trains model, predicts
4. **Firebase** → Updated with forecast `{pred_10min: 35.42}`
5. **User** → Opens frontend, sees water panel with current level + forecast
6. **User** → Asks "Mực nước sẽ bao nhiêu?"
7. **Frontend** → Calls `/chat` endpoint
8. **Backend** → Fetches current + forecast data, builds context
9. **OpenAI** → Responds with contextualized answer
10. **User** → Sees AI response

---

## Troubleshooting

### No water data in frontend
- Check if Flask can access `history.csv` (path must be relative to Flask root)
- Verify main.py is running and populating CSV
- Check Firebase URL is correct

### ML predictions not updating
- Verify ml_forecast_weather.py is running
- Check Firebase has at least 2 data points
- Look at console output for errors

### AI responses not using water context
- Verify `/api/water-status` endpoint works: `curl http://localhost:5000/api/water-status`
- Check OpenAI API key in .env file
- System prompt should include water context (check app.py)

### Water panel shows "❌ Lỗi tải dữ liệu"
- Open browser DevTools (F12) → Console
- Check network requests to `/api/water-status`
- Verify CORS is enabled in Flask

---

## Advanced Customization

### Use Different ML Model
Replace LinearRegression in `ml_forecast_weather.py`:
```python
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor(n_estimators=10).fit(X, y)
```

### Add More Weather Features
```python
# Modify fetch_weather() to include temperature, humidity, etc.
X["temp"] = temperature
X["humidity"] = humidity
```

### Custom Thresholds
Modify system prompt in `backend/app.py`:
```python
if float(sensor.get('waterLevel', 0)) > 500:
    context += "\n⚠️ ALERT: Water level critically high!"
```

### Persistence & Logging
Add database instead of CSV for better scalability:
```python
# Use SQLAlchemy, MongoDB, or PostgreSQL instead of CSV
from sqlalchemy import create_engine
engine = create_engine('sqlite:///water_data.db')
df.to_sql('water_level', engine, index=False)
```

---

## Next Steps

1. **Deploy to cloud** (AWS Lambda, Heroku, etc.)
2. **Add multi-sensor support** (sensor1, sensor2, etc.)
3. **Implement user authentication** for login page
4. **Create mobile app** version
5. **Add notifications** (SMS, push when threshold exceeded)
6. **Advanced ML** (LSTM for longer-term forecasts)
7. **Dashboard** with charts and trends

---

## Support

For issues:
1. Check console output of each component
2. Verify all files have correct paths
3. Test Firebase connectivity
4. Check OpenAI API quota
5. Review .env file for correct credentials

---

**Last Updated:** November 19, 2025
**Version:** 1.0
