from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os
from dotenv import load_dotenv
from flask_cors import CORS
import requests
import pandas as pd
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import json
from functools import wraps
from collections import defaultdict

# ========================================
# Configuration & Logging Setup
# ========================================
load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Create logs directory
os.makedirs('./logs', exist_ok=True)

# Configure logging with rotating file handler
log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
file_handler = RotatingFileHandler('./logs/app.log', maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(logging.Formatter(log_format))

logger = logging.getLogger('FloodSense')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(console_handler)

logger.info("="*60)
logger.info("FloodSense Backend Started")
logger.info("="*60)

# ========================================
# OpenAI Client
# ========================================
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY or API_KEY == 'your_openai_api_key_here':
    logger.warning("  OPENAI_API_KEY not configured! AI features will fail.")
    API_KEY = None
else:
    logger.info("✓ OpenAI API Key loaded")

if API_KEY:
    client = OpenAI(api_key=API_KEY)

# ========================================
# Firebase Configuration
# ========================================
FIREBASE_SENSOR = os.getenv(
    "FB_SENSOR",
    "https://edfwef-default-rtdb.firebaseio.com/water_level/sensor1.json")
FIREBASE_FORECAST = os.getenv(
    "FB_FORECAST",
    "https://edfwef-default-rtdb.firebaseio.com/forecast/sensor1.json")
FIREBASE_CONFIG = os.getenv(
    "FB_CONFIG",
    "https://edfwef-default-rtdb.firebaseio.com/config/sensor1.json")
FIREBASE_COMMANDS = os.getenv(
    "FB_COMMANDS",
    "https://edfwef-default-rtdb.firebaseio.com/commands/sensor1.json")

LOCAL_HISTORY = "../history.csv"

logger.info(f"Firebase Sensor URL: {FIREBASE_SENSOR}")
logger.info(f"Firebase Forecast URL: {FIREBASE_FORECAST}")

# ========================================
# Conversation History (In-Memory, per session)
# ========================================
conversation_history = defaultdict(list)
MAX_HISTORY = int(os.getenv('CONVERSATION_HISTORY_LIMIT', 10))

def get_session_id():
    """Extract or generate session ID from request"""
    return request.remote_addr

# ========================================
# Utility Functions
# ========================================
def log_action(action_type, details):
    """Log user actions with details"""
    session_id = request.remote_addr
    logger.info(f"[{action_type}] Session:{session_id} | {details}")

def get_latest_sensor_data():
    """Fetch latest sensor reading from Firebase"""
    try:
        logger.debug(f"Fetching sensor data from {FIREBASE_SENSOR}")
        r = requests.get(FIREBASE_SENSOR, timeout=5)
        if r.status_code == 200:
            data = r.json()
            logger.info(f"✓ Sensor data retrieved: waterLevel={data.get('waterLevel')}mm")
            return data
        else:
            logger.warning(f"Firebase sensor returned status {r.status_code}")
    except requests.Timeout:
        logger.error("Timeout fetching sensor data from Firebase")
    except Exception as e:
        logger.error(f"Error fetching sensor data: {str(e)}")
    return None

def get_forecast_data():
    """Fetch ML forecast from Firebase"""
    try:
        logger.debug(f"Fetching forecast from {FIREBASE_FORECAST}")
        r = requests.get(FIREBASE_FORECAST, timeout=5)
        if r.status_code == 200:
            data = r.json()
            logger.info(f"✓ Forecast retrieved: pred_10min={data.get('pred_10min')}mm")
            return data
        else:
            logger.warning(f"Firebase forecast returned status {r.status_code}")
    except requests.Timeout:
        logger.error("Timeout fetching forecast from Firebase")
    except Exception as e:
        logger.error(f"Error fetching forecast: {str(e)}")
    return None

def get_history_stats():
    """Get statistics from historical data"""
    try:
        if os.path.exists(LOCAL_HISTORY):
            df = pd.read_csv(LOCAL_HISTORY)
            if len(df) > 0 and 'waterLevel' in df.columns:
                stats = {
                    'current': float(df['waterLevel'].iloc[-1]),
                    'min': float(df['waterLevel'].min()),
                    'max': float(df['waterLevel'].max()),
                    'avg': float(df['waterLevel'].mean()),
                    'records': len(df),
                    'trend': 'increasing' if len(df) > 1 and df['waterLevel'].iloc[-1] > df['waterLevel'].iloc[-2] else 'decreasing'
                }
                logger.debug(f"History stats: {stats}")
                return stats
    except Exception as e:
        logger.error(f"Error reading history stats: {str(e)}")
    return None

def get_config_data():
    """Fetch current sensor configuration from Firebase"""
    try:
        logger.debug(f"Fetching config from {FIREBASE_CONFIG}")
        r = requests.get(FIREBASE_CONFIG, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        logger.error(f"Error fetching config: {str(e)}")
    return None

def build_water_context():
    """Build comprehensive context string with water level data for OpenAI"""
    sensor = get_latest_sensor_data()
    forecast = get_forecast_data()
    history = get_history_stats()
    config = get_config_data()
    
    context = "\n**📊 Dữ Liệu Cảm Biến Nước Thực Tế:**\n"
    
    if sensor:
        context += f"- Mực nước hiện tại: {sensor.get('waterLevel', 'N/A')} mm\n"
        context += f"- Khoảng cách: {sensor.get('distance', 'N/A')} cm\n"
        context += f"- Cập nhật lúc: {datetime.fromtimestamp(sensor.get('timestamp', 0)/1000).strftime('%H:%M:%S') if sensor.get('timestamp') else 'N/A'}\n"
    else:
        context += "- ⚠️ Không có dữ liệu từ cảm biến (Kiểm tra kết nối Arduino)\n"
    
    if forecast:
        pred_10 = forecast.get('pred_10min', 'N/A')
        pred_30 = forecast.get('pred_30min', 'N/A')
        context += f"\n**🔮 Dự Báo ML:**\n"
        context += f"- Dự báo 10 phút tới: {pred_10} mm\n"
        context += f"- Dự báo 30 phút tới: {pred_30} mm\n"
        context += f"- Độ tin cậy: Dựa trên {forecast.get('training_samples', '?')} mẫu lịch sử\n"
    else:
        context += f"\n**🔮 Dự Báo ML:**\n- Chưa có dữ liệu (Chạy ml_forecast_weather.py lần đầu)\n"
    
    if history:
        context += f"\n**📈 Thống Kê Lịch Sử:**\n"
        context += f"- Mực nước min: {history['min']:.1f} mm\n"
        context += f"- Mực nước max: {history['max']:.1f} mm\n"
        context += f"- Mực nước trung bình: {history['avg']:.1f} mm\n"
        context += f"- Xu hướng: {history['trend']}\n"
        context += f"- Số lần đo: {history['records']}\n"
    
    if config:
        threshold = config.get('alertThreshold', 'N/A')
        context += f"\n**⚙️ Cấu Hình Cảm Biến:**\n"
        context += f"- Ngưỡng cảnh báo: {threshold} mm\n"
        context += f"- Chu kỳ cập nhật: {config.get('updateInterval', 'N/A')} giây\n"
    
    return context

# ========================================
# Request Validation Decorator
# ========================================
def validate_json(*expected_fields):
    """Decorator to validate JSON request contains expected fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                logger.warning(f"Non-JSON request to {request.endpoint}")
                return jsonify({'error': 'Request must be JSON'}), 400
            
            data = request.get_json()
            missing = [field for field in expected_fields if field not in data]
            
            if missing:
                logger.warning(f"Missing fields in {request.endpoint}: {missing}")
                return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ========================================
# API Routes (MUST be before catch-all route)
# ========================================

@app.route('/api/water-status', methods=['GET'])
def water_status():
    """Get current water level, predictions, and history"""
    try:
        log_action("WATER_STATUS_REQUEST", "Fetching water data")
        
        sensor = get_latest_sensor_data()
        forecast = get_forecast_data()
        history = get_history_stats()
        
        return jsonify({
            'sensor': sensor,
            'forecast': forecast,
            'history': history,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error in /api/water-status: {str(e)}")
        return jsonify({
            'error': f'Internal error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current sensor configuration"""
    try:
        log_action("CONFIG_GET", "Fetching configuration")
        config = get_config_data()
        return jsonify({'config': config, 'status': 'success'})
    except Exception as e:
        logger.error(f"Error in /api/config: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/config', methods=['POST'])
def save_config():
    """Save sensor configuration to Firebase"""
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("Empty config update attempt")
            return jsonify({'error': 'Empty config'}), 400
        
        logger.info(f"Updating config: {data}")
        log_action("CONFIG_UPDATE", f"New config: {json.dumps(data)}")
        
        # Push to Firebase config
        config_response = requests.put(FIREBASE_CONFIG, json=data, timeout=5)
        
        # Also push to Arduino commands so it picks up the new config
        cmd_data = {
            'action': 'update_config',
            'config': data,
            'timestamp': datetime.now().isoformat(),
            'source': 'web-ui'
        }
        requests.post(FIREBASE_COMMANDS.replace('.json', '.json'), json=cmd_data, timeout=5)
        
        if config_response.status_code in [200, 201]:
            logger.info("✓ Config saved to Firebase and sent to Arduino")
            return jsonify({'status': 'success', 'message': 'Config saved and sent to Arduino'})
        else:
            logger.error(f"Firebase returned {config_response.status_code}")
            return jsonify({'error': 'Failed to save config'}), 500
            
    except requests.Timeout:
        logger.error("Timeout saving config to Firebase")
        return jsonify({'error': 'Firebase timeout'}), 504
    except Exception as e:
        logger.error(f"Error in /api/config POST: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/command', methods=['POST'])
def send_command():
    """Send command to Arduino via Firebase"""
    try:
        data = request.get_json()
        command = data.get('command')
        
        if not command:
            return jsonify({'error': 'Missing command'}), 400
        
        logger.info(f"Sending command: {command}")
        log_action("COMMAND_SEND", f"Command: {command}")
        
        # Push to Firebase
        cmd_data = {
            'action': command,
            'timestamp': datetime.now().isoformat(),
            'source': 'web-ui'
        }
        
        response = requests.post(FIREBASE_COMMANDS.replace('.json', '.json'), json=cmd_data, timeout=5)
        
        if response.status_code in [200, 201]:
            logger.info(f"✓ Command '{command}' sent successfully")
            return jsonify({'status': 'success', 'message': f'Command "{command}" sent'})
        else:
            logger.error(f"Firebase returned {response.status_code}")
            return jsonify({'error': 'Command failed'}), 500
            
    except Exception as e:
        logger.error(f"Error in /api/command: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent application logs (last 100 lines)"""
    try:
        if not os.path.exists('./logs/app.log'):
            return jsonify({'logs': [], 'status': 'no_logs'})
        
        with open('./logs/app.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        recent_logs = lines[-100:]  # Last 100 lines
        return jsonify({
            'logs': recent_logs,
            'total_lines': len(lines),
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error reading logs: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """AI chat endpoint with context-aware responses and conversation history"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            logger.warning("Empty message received")
            return jsonify({'error': 'Empty message'}), 400
        
        if not API_KEY:
            logger.error("OpenAI API key not configured")
            return jsonify({'error': 'AI service not configured'}), 503
        
        session_id = get_session_id()
        log_action("CHAT_MESSAGE", f"User: {message[:50]}...")
        
        # Get water context
        water_context = build_water_context()
        
        # Get conversation history for this session
        history = conversation_history[session_id]
        
        # Build enhanced system prompt
        system_prompt = f'''Bạn là trợ lý AI chuyên CẢNH BÁO LŨ LỤT Việt Nam - FloodSense System.

**Hướng dẫn Hành Động:**
- Trả lời **ngắn gọn, hữu ích** bằng tiếng Việt (tối đa 3 câu).
- Dựa trên dữ liệu **mới nhất** từ cảm biến IoT và mô hình Machine Learning.
- Khi người dùng hỏi về mực nước: **sử dụng dữ liệu thực tế** dưới đây.
- **Cảnh báo Cấp Độ:**
  - < 150mm: Bình thường ✓
  - 150-200mm: Chú ý ⚠️
  - > 200mm: Nguy hiểm 🚨 "Cảnh báo! Mực nước vượt ngưỡng! Di tản ngay!"
- Gợi ý: Theo dõi vndms.dmc.gov.vn hoặc app chính thức.
- **Không bịa đặt dữ liệu** - nếu không có, nói rõ "Dữ liệu chưa có".

{water_context}

**Ví dụ Phản Hồi:**
- "Mực nước hiện tại bao nhiêu?" → Nêu giá trị từ cảm biến + tình trạng
- "Sẽ ngập không?" → Dùng dự báo ML + lịch sử
- "Bây giờ đang nguy hiểm?" → So sánh với ngưỡng cảnh báo'''
        
        # Prepare messages with history
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add conversation history (last N messages)
        for hist_msg in history[-MAX_HISTORY:]:
            messages.append(hist_msg)
        
        # Add current user message
        messages.append({'role': 'user', 'content': message})
        
        logger.info(f"Calling OpenAI with {len(messages)} messages (including system)")
        
        # Call OpenAI
        completion = client.chat.completions.create(
            model=os.getenv('AI_MODEL', 'gpt-4o-mini'),
            messages=messages,
            max_tokens=int(os.getenv('AI_MAX_TOKENS', 300)),
            temperature=float(os.getenv('AI_TEMPERATURE', 0.7))
        )
        
        reply = completion.choices[0].message.content
        
        # Store in conversation history
        history.append({'role': 'user', 'content': message})
        history.append({'role': 'assistant', 'content': reply})
        conversation_history[session_id] = history[-MAX_HISTORY*2:]  # Keep last N pairs
        
        logger.info(f"✓ AI replied: {reply[:50]}...")
        log_action("CHAT_RESPONSE", f"AI: {reply[:50]}...")
        
        return jsonify({
            'reply': reply,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in /chat: {str(e)}")
        log_action("CHAT_ERROR", str(e))
        return jsonify({
            'error': f'Lỗi AI: {str(e)}',
            'status': 'error'
        }), 500

# ========================================
# Static Files & Catch-all Routes (MUST be after API routes)
# ========================================
@app.route('/')
def index():
    logger.info(f"Serving index.html to {request.remote_addr}")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # IMPORTANT: Don't match API routes - let them be handled by error handler
    if path.startswith('api/'):
        logger.warning(f"API route {path} not found - returning 404")
        return jsonify({'error': 'Not found', 'path': f'/{path}'}), 404
    
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        logger.debug(f"Serving static file: {path}")
        response = send_from_directory(app.static_folder, path)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    logger.debug(f"File not found, serving index: {path}")
    return send_from_directory(app.static_folder, 'index.html')

# ========================================
# Error Handlers
# ========================================
@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 error: {request.path}")
    return jsonify({'error': 'Not found', 'path': request.path}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500 error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# ========================================
# Application Entry Point
# ========================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask server on 0.0.0.0:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
