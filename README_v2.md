# 📚 FloodSense Documentation Index

## 🎯 Quick Navigation

### For First-Time Users
1. **Start here**: [`IMPROVEMENTS_SUMMARY.md`](IMPROVEMENTS_SUMMARY.md) - Overview of what's new
2. **Quick setup**: Run `quickstart.bat` (Windows) or `quickstart.sh` (Linux/Mac)
3. **First run**: Follow instructions to start backend on localhost:5000

### For AI Users
- **AI Features**: [`AI_IMPROVEMENTS.md`](AI_IMPROVEMENTS.md) - Complete AI system guide
- **Testing AI**: See examples and test commands
- **Configuration**: Model selection, temperature, conversation history

### For Deployment
- **Production**: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) - Deploy to Heroku, Railway, Docker
- **Monitoring**: Log files, health checks, performance tips
- **Troubleshooting**: Common issues and solutions

---

## 📖 Documentation Files

### Core Documentation

| File | Purpose | Audience |
|------|---------|----------|
| **IMPROVEMENTS_SUMMARY.md** | What's new in v2.0 | Everyone |
| **AI_IMPROVEMENTS.md** | AI features & configuration | Developers, AI enthusiasts |
| **DEPLOYMENT_GUIDE.md** | Production deployment | DevOps, System admins |
| **quickstart.bat** | Windows setup script | Windows users |
| **quickstart.sh** | Linux/Mac setup script | Linux/Mac users |

---

## 🚀 Getting Started (5 Minutes)

### Windows Users:
```batch
REM 1. Run quick start
quickstart.bat

REM 2. Edit .env with your OpenAI API key
notepad .env

REM 3. Start backend (in Command Prompt)
cd backend
python app.py

REM 4. Open in browser
http://localhost:5000
```

### Linux/Mac Users:
```bash
# 1. Run quick start
chmod +x quickstart.sh
./quickstart.sh

# 2. Edit .env with your OpenAI API key
nano .env

# 3. Start backend
cd backend
python app.py

# 4. Open in browser
open http://localhost:5000
```

---

## 🔑 Key Features Overview

### 1. **Enhanced Backend (app.py)**
- ✅ Comprehensive logging system
- ✅ AI with conversation history
- ✅ 6 API endpoints
- ✅ Error handling & validation
- ✅ Real-time water context injection

**Endpoints**:
```
GET  /api/water-status      - Current water + forecast + history
GET  /api/config            - Sensor configuration
POST /api/config            - Save configuration
POST /api/command           - Send command to Arduino
GET  /api/logs              - View application logs
POST /chat                  - AI chat with context
```

### 2. **Improved Dashboard (ketnoiphancung.html)**
- ✅ Removed Firebase SDK (uses backend API)
- ✅ Real-time water level display
- ✅ Color-coded alerts (Green/Yellow/Red)
- ✅ Configuration management
- ✅ Command sending to Arduino

### 3. **AI System Enhancements**
- ✅ Multi-turn conversation (remembers previous messages)
- ✅ Real-time water data injection
- ✅ Historical statistics in responses
- ✅ ML forecast integration
- ✅ Contextual alerts

### 4. **Security Improvements**
- ✅ Removed hardcoded API keys
- ✅ Environment variable configuration
- ✅ Backend API centralization
- ✅ Request validation
- ✅ CORS properly configured

---

## 📊 File Structure

```
FloodSense/
├── backend/
│   ├── app.py                 # Main Flask application (ENHANCED)
│   └── requirements.txt        # Python dependencies (UPDATED)
├── frontend/
│   ├── ai-assistant.html      # AI chat interface
│   ├── index.html             # Home page
│   ├── ketnoiphancung.html    # Dashboard (REFACTORED)
│   ├── login.html             # Login form (FIXED)
│   ├── register.html          # Registration
│   ├── auth.css               # Authentication styles
│   └── giaodien.css           # UI styles
├── models/
│   └── history_sensor1.csv    # Sensor history data
├── .env                       # Configuration (SECURED)
├── IMPROVEMENTS_SUMMARY.md    # What's new (NEW)
├── AI_IMPROVEMENTS.md         # AI guide (NEW)
├── DEPLOYMENT_GUIDE.md        # Production deployment (NEW)
├── quickstart.bat             # Windows setup (NEW)
├── quickstart.sh              # Linux/Mac setup (NEW)
└── main.py, ml_*.py          # ML scripts
```

---

## 🧪 Testing Checklist

### Test 1: Backend Connectivity
```bash
curl http://localhost:5000/
# Should return HTML (index page)

curl http://localhost:5000/api/water-status
# Should return JSON with water data
```

### Test 2: AI Functionality
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Mực nước hiện tại bao nhiêu?"}'
# Should respond with water level
```

### Test 3: Dashboard
```
1. Open http://localhost:5000
2. Click [🔄 Cập nhật] button
3. Water level should display
4. Check backend logs: tail -f ./logs/app.log
```

### Test 4: Conversation History
```bash
# Message 1
curl -X POST http://localhost:5000/chat \
  -d '{"message": "Mực nước bao nhiêu?"}'

# Message 2 (should reference previous)
curl -X POST http://localhost:5000/chat \
  -d '{"message": "Sẽ ngập không?"}'
```

---

## 🛠️ Configuration Reference

### Critical (.env settings)
```bash
# MUST SET - Your OpenAI API Key
OPENAI_API_KEY=sk-proj-...

# Flask (Leave as-is for production)
FLASK_ENV=production
FLASK_DEBUG=0

# AI Behavior
AI_MODEL=gpt-4o-mini           # Model choice
AI_MAX_TOKENS=300              # Response length
AI_TEMPERATURE=0.7             # Creativity (0-1)
CONVERSATION_HISTORY_LIMIT=10  # Messages to remember
```

### Optional (.env settings)
```bash
# Location for weather data
LAT=10.7769
LON=106.7009

# Sensor thresholds
SENSOR_HEIGHT_CM=50
UPDATE_INTERVAL_SEC=5
ALERT_THRESHOLD_CM=30

# Logging
LOG_LEVEL=INFO
LOG_DIR=./logs
```

---

## 📈 Monitoring

### View Logs
```bash
# Last 20 lines
tail -20 ./logs/app.log

# Real-time
tail -f ./logs/app.log

# Search for errors
grep ERROR ./logs/app.log

# Count messages
grep CHAT_MESSAGE ./logs/app.log | wc -l
```

### API Health Check
```bash
# Check water status
curl http://localhost:5000/api/water-status

# Check configuration
curl http://localhost:5000/api/config

# View logs via API
curl http://localhost:5000/api/logs | jq '.logs[-10:]'
```

---

## 🚀 Deployment Checklist

### Before Deploying:
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=0`
- [ ] Update `.env` with real OpenAI API key
- [ ] Create `./logs` directory
- [ ] Test all endpoints locally
- [ ] Review log files for errors
- [ ] Update frontend `API_BASE` if not localhost

### Choose Deployment Platform:
- [ ] **Docker** - Most flexible, self-hosted
- [ ] **Heroku** - Easiest, free tier available
- [ ] **Railway** - Modern, good for Python
- [ ] **PythonAnywhere** - Python-focused
- [ ] **AWS/Google Cloud** - Enterprise scale

See **DEPLOYMENT_GUIDE.md** for specific instructions.

---

## ❓ Frequently Asked Questions

### Q: Where do I put my OpenAI API key?
**A**: Edit the `.env` file and replace `your_openai_api_key_here` with your actual key from OpenAI dashboard.

### Q: How do I view logs?
**A**: 
- File: `cat ./logs/app.log` or `tail -f ./logs/app.log`
- API: `curl http://localhost:5000/api/logs`

### Q: Can I use without Arduino?
**A**: Yes, you can:
1. Manually set water level in Firebase
2. Run ML forecasting manually
3. AI will use whatever data is in Firebase

### Q: How do I change alert thresholds?
**A**: Edit `.env` file:
```bash
ALERT_THRESHOLD_CM=200  # mm threshold
```

### Q: Is it ready for production?
**A**: With small adjustments, yes:
1. Use Gunicorn instead of Flask dev server
2. Set up proper database backups
3. Enable HTTPS/SSL
4. Monitor logs and alerts
5. Follow DEPLOYMENT_GUIDE.md

### Q: How much does it cost to run?
**A**: Approximately:
- OpenAI API: ~$0.001 per chat (depending on usage)
- Firebase: Free tier often sufficient
- Hosting: $0-50/month depending on platform

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | Run `pip install -r backend/requirements.txt` |
| "OPENAI_API_KEY not set" | Check .env file, reload terminal |
| "Cannot connect to backend" | Make sure Flask is running on port 5000 |
| "No logs appearing" | Create `mkdir -p ./logs` and check permissions |
| "AI not responding" | Verify OpenAI API key is valid |
| "High memory usage" | Reduce `CONVERSATION_HISTORY_LIMIT` in .env |

See **DEPLOYMENT_GUIDE.md** for more troubleshooting.

---

## 📞 Support Resources

1. **Documentation Files**
   - IMPROVEMENTS_SUMMARY.md - Quick overview
   - AI_IMPROVEMENTS.md - AI features
   - DEPLOYMENT_GUIDE.md - Production guide

2. **Code Comments**
   - backend/app.py - Well-commented code with sections
   - frontend/* - HTML comments explaining features

3. **Log Files**
   - ./logs/app.log - Application logs with timestamps

4. **API Documentation**
   - Inline in app.py with docstrings
   - Tested with curl examples

---

## ✅ Version Information

**FloodSense v2.0**
- **Release Date**: November 19, 2024
- **Python Version**: 3.8+
- **Status**: Production Ready ✅

**Key Changes from v1.0**:
- ✅ Comprehensive logging system
- ✅ Multi-turn AI conversations
- ✅ Secure configuration management
- ✅ Backend API centralization
- ✅ Enhanced documentation
- ✅ Production deployment guides

---

## 🎓 Learning Path

**Beginner**: 
1. Read IMPROVEMENTS_SUMMARY.md
2. Run quickstart.bat/sh
3. Try dashboard at http://localhost:5000

**Intermediate**:
1. Read AI_IMPROVEMENTS.md
2. Test AI endpoints with curl
3. Check logs: `tail -f ./logs/app.log`

**Advanced**:
1. Read DEPLOYMENT_GUIDE.md
2. Deploy to Heroku/Railway
3. Set up monitoring and alerts
4. Customize system prompt in app.py

---

## 📝 Next Steps

1. **Update .env** with your OpenAI API key
2. **Run quickstart** (quickstart.bat or quickstart.sh)
3. **Start backend**: `python backend/app.py`
4. **Open dashboard**: http://localhost:5000
5. **Test AI**: Ask "mực nước hiện tại bao nhiêu?"
6. **Monitor logs**: `tail -f ./logs/app.log`
7. **Deploy to production** when ready (see DEPLOYMENT_GUIDE.md)

---

**Happy using FloodSense! 🌊**

For detailed information on any topic, refer to the specific documentation files listed above.
