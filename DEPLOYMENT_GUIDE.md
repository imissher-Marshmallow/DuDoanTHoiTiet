# 🚀 FloodSense Deployment Guide

## Overview
This guide covers deploying the FloodSense system in a production environment with proper configuration, logging, and monitoring.

---

## 📋 Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Create `.env` file with secure credentials
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=0`
- [ ] Configure valid `OPENAI_API_KEY`
- [ ] Verify Firebase URLs are accessible
- [ ] Update `LAT` and `LON` for weather data

### 2. Security Review
- [ ] Remove all hardcoded credentials from code
- [ ] Never commit `.env` file to repository
- [ ] Use environment variables for all secrets
- [ ] Enable CORS only for trusted domains
- [ ] Configure rate limiting for APIs
- [ ] Enable HTTPS in production

### 3. Logging Setup
- [ ] Verify `./logs` directory is writable
- [ ] Configure log rotation (default: 5MB per file)
- [ ] Monitor disk space for log files
- [ ] Set up log aggregation (optional)

---

## 🔧 Configuration (.env File)

```bash
# OpenAI - CRITICAL: Replace with your actual key
OPENAI_API_KEY=sk-proj-your-real-key-here

# Firebase - Already configured for your project
FB_SENSOR=https://edfwef-default-rtdb.firebaseio.com/water_level/sensor1.json
FB_FORECAST=https://edfwef-default-rtdb.firebaseio.com/forecast/sensor1.json
FB_CONFIG=https://edfwef-default-rtdb.firebaseio.com/config/sensor1.json
FB_COMMANDS=https://edfwef-default-rtdb.firebaseio.com/commands/sensor1.json

# Weather Location
LAT=10.7769
LON=106.7009

# Sensor Configuration
SENSOR_HEIGHT_CM=50
UPDATE_INTERVAL_SEC=5
ALERT_THRESHOLD_CM=30

# Flask Configuration - PRODUCTION SETTINGS
FLASK_ENV=production
FLASK_DEBUG=0
LOG_LEVEL=INFO

# AI Configuration
AI_MODEL=gpt-4o-mini
AI_MAX_TOKENS=300
AI_TEMPERATURE=0.7
CONVERSATION_HISTORY_LIMIT=10

# Security & Logging
SESSION_TIMEOUT=3600
ENABLE_LOGGING=1
LOG_DIR=./logs
```

---

## 🐳 Deployment Options

### Option 1: Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

EXPOSE 5000

CMD ["python", "backend/app.py"]
```

Build and run:
```bash
docker build -t floodsense .
docker run -p 5000:5000 \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd)/logs:/app/logs \
  floodsense
```

### Option 2: Heroku

1. **Install Heroku CLI**
   ```bash
   npm install -g heroku
   heroku login
   ```

2. **Create Procfile**
   ```
   web: cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   ```

3. **Create runtime.txt**
   ```
   python-3.9.16
   ```

4. **Deploy**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your_key
   git push heroku main
   ```

### Option 3: Railway

1. **Create railway.json**
   ```json
   {
     "build": {
       "builder": "nixpacks"
     },
     "deploy": {
       "startCommand": "cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app"
     }
   }
   ```

2. **Deploy via Railway CLI**
   ```bash
   railway link
   railway up
   railway variables add OPENAI_API_KEY=your_key
   ```

### Option 4: PythonAnywhere

1. **Upload files via web interface**
2. **Create virtual environment**
3. **Install requirements**
   ```bash
   pip install -r backend/requirements.txt
   ```
4. **Configure WSGI file** to point to `backend/app.py`
5. **Set environment variables** in PythonAnywhere settings

---

## 📊 Monitoring & Logs

### Log Files Location
- **Application Logs**: `./logs/app.log`
- **Rotation**: Automatically rotates at 5MB with 5 backup files

### Viewing Logs

```bash
# Last 50 lines
tail -50 ./logs/app.log

# Real-time monitoring
tail -f ./logs/app.log

# Search for errors
grep -i error ./logs/app.log

# View specific action type
grep "CHAT_MESSAGE" ./logs/app.log
```

### Log Format
```
2024-11-19 15:30:45,123 - FloodSense - INFO - [water_status:45] - ✓ Sensor data retrieved: waterLevel=125mm
```

### Monitoring via API

Get last 100 log lines:
```bash
curl http://localhost:5000/api/logs
```

Response:
```json
{
  "logs": ["2024-11-19 15:30:45,123 - FloodSense - INFO - ...", ...],
  "total_lines": 1250,
  "status": "success"
}
```

---

## 🔍 Health Checks

### Backend Health
```bash
# Check water status endpoint
curl http://localhost:5000/api/water-status

# Check config endpoint
curl http://localhost:5000/api/config

# Check AI service
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "mực nước hiện tại bao nhiêu?"}'
```

### Expected Responses

**Water Status (200 OK)**
```json
{
  "sensor": {"distance": 45.2, "waterLevel": 125.0, "timestamp": 1700400645000},
  "forecast": {"pred_10min": 130.0, "pred_30min": 135.0},
  "history": {"current": 125.0, "min": 50.0, "max": 200.0, "avg": 120.0, "records": 1250},
  "timestamp": "2024-11-19T15:30:45.123456",
  "status": "success"
}
```

**Chat Response (200 OK)**
```json
{
  "reply": "Mực nước hiện tại là 125mm, trong ngưỡng bình thường. Dự báo 10 phút tới sẽ là 130mm.",
  "status": "success",
  "timestamp": "2024-11-19T15:30:45.123456"
}
```

---

## 🚨 Troubleshooting

### Issue: "OPENAI_API_KEY not configured"
**Solution**: 
1. Check `.env` file exists
2. Verify key is set: `echo $OPENAI_API_KEY`
3. Restart Flask: `python backend/app.py`

### Issue: "Timeout fetching sensor data"
**Solution**:
1. Check Firebase URLs in `.env`
2. Verify internet connectivity
3. Check Firebase service status
4. Increase timeout in `requests.get(..., timeout=10)`

### Issue: "Cannot connect to Backend"
**Solution** (for frontend):
1. Verify Flask is running: `ps aux | grep python`
2. Check Flask is listening: `netstat -an | grep 5000`
3. Verify `API_BASE` in HTML points to correct URL
4. Check CORS settings in Flask

### Issue: "No data in logs"
**Solution**:
1. Verify `./logs` directory exists: `mkdir -p ./logs`
2. Check directory permissions: `chmod 755 ./logs`
3. Check `LOG_LEVEL` in `.env`
4. Verify `ENABLE_LOGGING=1`

### Issue: "High memory usage"
**Solution**:
1. Reduce `CONVERSATION_HISTORY_LIMIT` in `.env`
2. Archive old log files
3. Use `gunicorn` with `--max-requests` option
4. Monitor with: `top -p $(pidof python)`

---

## 📈 Performance Tips

1. **Use Gunicorn in production** (not Flask dev server)
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
   ```

2. **Enable caching headers**
   - Already configured in Flask static routes
   - Frontend assets cached with `Cache-Control: no-cache`

3. **Monitor API response times**
   - Watch logs for slow queries
   - Set timeouts appropriately
   - Consider caching forecast data

4. **Database/Firebase optimization**
   - Limit history.csv to last 1000 records
   - Archive old data separately
   - Use indexed queries in Firebase

---

## 🔐 Security Best Practices

1. **Never commit .env file**
   ```bash
   echo ".env" >> .gitignore
   echo "logs/" >> .gitignore
   ```

2. **Use environment variables**
   - Don't hardcode secrets in code
   - Rotate keys regularly

3. **Enable HTTPS**
   - Use Let's Encrypt (free SSL)
   - Configure reverse proxy (nginx, Apache)
   - Enforce HTTPS redirect

4. **Rate limiting** (optional)
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app)
   
   @limiter.limit("100 per hour")
   @app.route('/chat', methods=['POST'])
   ```

5. **Input validation**
   - Already implemented with `validate_json` decorator
   - Sanitize user messages before passing to AI

---

## 📞 Support

For issues or questions:
1. Check logs: `tail -f ./logs/app.log`
2. Verify configuration in `.env`
3. Test endpoints manually with curl
4. Check Firebase console for data issues
5. Review OpenAI API status

---

## 📝 Deployment Checklist

- [ ] `.env` file created with correct keys
- [ ] `FLASK_ENV=production` and `FLASK_DEBUG=0`
- [ ] `./logs` directory exists and is writable
- [ ] All Python dependencies installed
- [ ] Firebase endpoints verified
- [ ] OpenAI API key tested
- [ ] CORS configured correctly
- [ ] Database backup strategy in place
- [ ] Monitoring/alerting set up
- [ ] DNS/domain configured (if applicable)
- [ ] SSL certificate installed (if applicable)
- [ ] Logs rotated automatically
- [ ] Rate limiting configured
- [ ] Backup/recovery plan documented
- [ ] Performance baseline established

---

**Last Updated**: November 19, 2024
**Version**: 2.0 - Enhanced with Logging & Monitoring
