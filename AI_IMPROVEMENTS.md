# 🤖 AI System Improvements & Configuration Guide

## Overview

The FloodSense AI system has been significantly enhanced with:
- **Conversation History**: Multi-turn dialogue with context awareness
- **Comprehensive Logging**: Track all AI interactions with timestamps
- **Real-time Water Context**: Latest sensor/forecast/history data automatically injected
- **Session Management**: Per-user conversation tracking
- **Enhanced Error Handling**: Detailed error messages and recovery

---

## 🎯 New AI Features

### 1. Conversation History
The AI now remembers previous messages in a conversation, allowing for:
- Follow-up questions without repeating context
- Better understanding of user intent
- Consistent conversation flow

**How it works**:
```python
# Last 10 messages (default) stored per session
conversation_history[session_id] = [
    {'role': 'user', 'content': 'Mực nước hiện tại bao nhiêu?'},
    {'role': 'assistant', 'content': 'Mực nước hiện tại là 125mm...'},
    {'role': 'user', 'content': 'Sẽ ngập không?'},
    {'role': 'assistant', 'content': 'Dựa trên dự báo ML...'}
]
```

**Configuration**:
```bash
# In .env file
CONVERSATION_HISTORY_LIMIT=10  # Number of message pairs to keep
```

### 2. Real-time Water Context

Every AI response includes fresh water data:

**📊 Current Sensor Data**
- Real-time water level from Arduino
- Distance measurement from ultrasonic sensor
- Last update timestamp

**🔮 ML Forecasts**
- 10-minute ahead prediction
- 30-minute ahead prediction
- Training sample count (confidence indicator)

**📈 Historical Statistics**
- Min/max/average water levels
- Trend direction (increasing/decreasing)
- Total number of historical records

**⚙️ Sensor Configuration**
- Alert threshold setting
- Update interval configuration

### 3. Enhanced System Prompt

The AI now uses a sophisticated system prompt that:

```
Bạn là trợ lý AI chuyên CẢNH BÁO LŨ LỤT Việt Nam - FloodSense System.

**Hướng dẫn Hành Động:**
- Trả lời ngắn gọn, hữu ích bằng tiếng Việt (tối đa 3 câu)
- Dựa trên dữ liệu mới nhất từ cảm biến IoT và mô hình ML
- Sử dụng dữ liệu thực tế dưới đây
- Cảnh báo theo cấp độ: <150mm (✓), 150-200mm (⚠️), >200mm (🚨)
- Không bịa đặt dữ liệu - nếu không có, nói rõ "Dữ liệu chưa có"
```

### 4. Logging All Interactions

Every AI interaction is logged with:
- **Timestamp**: Exact time of interaction
- **User ID**: Session/IP address
- **Message**: User's input message
- **Response**: AI's reply
- **Metadata**: Model used, tokens consumed

**Log Example**:
```
2024-11-19 15:45:23,456 - FloodSense - INFO - [chat:245] - [CHAT_MESSAGE] Session:192.168.1.100 | User: mực nước hiện tại bao nhiêu?
2024-11-19 15:45:25,789 - FloodSense - INFO - [chat:290] - [CHAT_RESPONSE] Session:192.168.1.100 | AI: Mực nước hiện tại là 125mm, trong ngưỡng bình thường...
```

---

## 🔧 Configuration Options

### OpenAI Settings

```bash
# Model selection
AI_MODEL=gpt-4o-mini  # Options: gpt-4o, gpt-4o-mini, gpt-3.5-turbo

# Response quality
AI_MAX_TOKENS=300     # Max tokens per response (increase for longer answers)
AI_TEMPERATURE=0.7    # Creativity: 0.0 (deterministic) to 1.0 (creative)
```

**Temperature Guidance**:
- `0.0-0.3`: Strict, factual responses (best for water level data)
- `0.4-0.7`: Balanced, natural responses (current setting)
- `0.8-1.0`: Creative, varied responses (not recommended for alerts)

### Conversation Settings

```bash
# Session management
CONVERSATION_HISTORY_LIMIT=10  # Messages to keep per user
SESSION_TIMEOUT=3600            # Session expiration (seconds)

# Logging
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
LOG_DIR=./logs                  # Where to store log files
ENABLE_LOGGING=1                # 1 to enable, 0 to disable
```

### Model Comparison

| Model | Speed | Cost | Quality | Recommendation |
|-------|-------|------|---------|-----------------|
| gpt-3.5-turbo | ⚡⚡⚡ | $ | Good | Quick responses |
| gpt-4o-mini | ⚡⚡ | $$ | Excellent | **Current** (best value) |
| gpt-4o | ⚡ | $$$ | Excellent | Premium/enterprise |
| gpt-4 | ⚡ | $$$$ | Best | Maximum accuracy |

---

## 🧪 Testing the AI System

### Test 1: Basic Water Query
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Mực nước hiện tại bao nhiêu?"}'
```

**Expected Response**:
```json
{
  "reply": "Mực nước hiện tại là 125mm, trong ngưỡng bình thường (< 150mm). Dự báo 10 phút tới sẽ là ~130mm.",
  "status": "success",
  "timestamp": "2024-11-19T15:45:23.456789"
}
```

### Test 2: Follow-up Question (Tests History)
```bash
# First message
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Mực nước hiện tại bao nhiêu?"}'

# Follow-up (should reference previous answer)
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Sẽ ngập không?"}'
```

**Expected**: Second response should reference the water level mentioned in first response, showing history is working.

### Test 3: Danger Scenario
```bash
# Simulate by manually setting high water level in Firebase
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Mực nước hiện tại là bao nhiêu? Nguy hiểm không?"}'
```

**Expected Response** (if water > 200mm):
```
🚨 NGUY HIỂM! Mực nước đã vượt ngưỡng cảnh báo (>200mm). Cảnh báo! Di tản ngay!
```

### Test 4: No Data Scenario
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Dự báo tiếp theo sẽ bao nhiêu?"}'
```

**Expected**: Should mention "Chưa có dữ liệu dự báo" if no forecast data available.

---

## 📊 Monitoring AI Performance

### View Recent AI Conversations

```bash
# Get last 100 log lines
curl http://localhost:5000/api/logs | jq '.logs[-20:]'

# Or directly from file
tail -50 ./logs/app.log | grep CHAT
```

### Key Metrics to Monitor

1. **Response Time**
   ```bash
   grep "CHAT_RESPONSE" ./logs/app.log | \
   awk -F'|' '{print $1}' | \
   head -20
   ```

2. **Error Rate**
   ```bash
   grep "CHAT_ERROR" ./logs/app.log | wc -l
   ```

3. **Active Sessions**
   ```bash
   grep "CHAT_MESSAGE" ./logs/app.log | \
   cut -d: -f7 | sort -u | wc -l
   ```

4. **Model Costs** (estimate)
   ```bash
   # gpt-4o-mini: ~$0.00015 per 1K input tokens, ~$0.0006 per 1K output tokens
   # Average: ~$0.001 per chat (300 tokens)
   ```

---

## 🎓 AI Response Examples

### Water Level Questions

**User**: "Mực nước hiện tại bao nhiêu?"

**AI Response**:
> Mực nước hiện tại là 125mm, trong ngưỡng bình thường (< 150mm). Dự báo 10 phút tới sẽ là ~130mm.

### Risk Assessment

**User**: "Sẽ xảy ra lũ lụt không?"

**AI Response**:
> Dựa trên dữ liệu hiện tại (125mm), bạn vẫn an toàn. Tuy nhiên, nếu mức nước tiếp tục tăng vượt quá 200mm, cần cảnh báo. Theo dõi liên tục!

### Historical Analysis

**User**: "Mực nước bình thường là bao nhiêu?"

**AI Response**:
> Dựa trên lịch sử: mực nước trung bình 95mm, thấp nhất 40mm, cao nhất 220mm. Mức 125mm hiện tại cao hơn trung bình nhưng vẫn an toàn.

### Trend Analysis

**User**: "Mực nước có tăng không?"

**AI Response**:
> Có, xu hướng hiện tại là tăng. Từ trung bình 95mm lên 125mm. Dự báo tiếp tục tăng ~5mm mỗi 10 phút.

---

## 🛠️ Advanced Customization

### Custom System Prompt

To modify AI behavior, edit the `build_water_context()` function in `backend/app.py`:

```python
system_prompt = f'''Bạn là trợ lý AI chuyên CẢNH BÁO LŨ LỤT Việt Nam.

**Tùy chỉnh hướng dẫn:**
- Thêm quy tắc riêng ở đây
- Thay đổi tone/style nếu cần
- Điều chỉnh alert thresholds

{water_context}
'''
```

### Custom Alert Thresholds

In `ketnoiphancung.html`:

```javascript
const ALERT_THRESHOLD = 200; // mm - thay đổi giá trị này

if (sensor.waterLevel >= threshold) {
    showAlert('🚨 NGUY HIỂM! ...', 0, 'danger');
} else if (sensor.waterLevel >= threshold * 0.75) {
    showAlert('⚠️ CHÚ Ý: Mực nước cao...', 5000, 'warning');
}
```

### Rate Limiting (Production)

Add to `backend/app.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    # ... existing code ...
```

---

## 🐛 Debugging AI Issues

### Issue: "AI service not configured"
**Solution**: Verify `OPENAI_API_KEY` in `.env`:
```bash
echo $OPENAI_API_KEY
# Should output: sk-proj-...
```

### Issue: "Slow AI responses"
**Solution**:
1. Reduce `AI_MAX_TOKENS` (currently 300)
2. Use cheaper model: `AI_MODEL=gpt-3.5-turbo`
3. Monitor API status: https://status.openai.com

### Issue: "AI gives generic responses"
**Solution**:
1. Increase `AI_TEMPERATURE` to 0.9 for more variety
2. Add more specific examples to system prompt
3. Check if water_context is empty

### Issue: "Memory usage increasing"
**Solution**:
1. Reduce `CONVERSATION_HISTORY_LIMIT` (currently 10)
2. Monitor sessions: `grep "CHAT_MESSAGE" ./logs/app.log | wc -l`
3. Clear old logs: `rm ./logs/app.log.* `

---

## 📈 Cost Estimation

Using gpt-4o-mini (current):

| Metric | Rate | Monthly (100 users, 10 chats/day) |
|--------|------|----------------------------------|
| Input tokens | $0.00015/1K | ~$0.50 |
| Output tokens | $0.0006/1K | ~$0.80 |
| **Total** | - | **~$1.30** |

Switching to gpt-3.5-turbo (cheaper):
- Input: $0.0005/1K
- Output: $0.0015/1K
- **Monthly: ~$0.80** (38% savings)

---

## ✅ Quality Checklist

- [ ] AI responses are in Vietnamese
- [ ] Water data is real-time (not cached)
- [ ] Alert thresholds are appropriate
- [ ] Conversation history works (follow-up questions understood)
- [ ] No sensitive data in logs
- [ ] Error messages are user-friendly
- [ ] Response time < 2 seconds
- [ ] API key never exposed in logs
- [ ] Log rotation working (files capped at 5MB)

---

**Last Updated**: November 19, 2024
**Version**: 2.0 - Full AI Enhancement with Conversation History & Logging
