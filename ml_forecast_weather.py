# Pipeline with weather + water level ML
# Fetch water from Firebase, train model with precipitation data, push predictions

import requests
import pandas as pd
import os
import time
from sklearn.linear_model import LinearRegression
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Firebase URLs
FIREBASE_SENSOR   = os.getenv("FB_SENSOR", "https://edfwef-default-rtdb.firebaseio.com/water_level/sensor1.json")
FIREBASE_FORECAST = os.getenv("FB_FORECAST", "https://edfwef-default-rtdb.firebaseio.com/forecast/sensor1.json")

LOCAL_HISTORY = "history.csv"

# Weather API (Open-Meteo) - Ho Chi Minh City coords
LAT = os.getenv("LAT", "10.7769")
LON = os.getenv("LON", "106.7009")
WEATHER_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=precipitation&timezone=Asia/Ho_Chi_Minh"

def fetch_weather():
    """Fetch recent precipitation data from Open-Meteo API"""
    try:
        r = requests.get(WEATHER_URL, timeout=5)
        if r.status_code != 200:
            print("[WEATHER] API error:", r.status_code)
            return 0.0
        data = r.json()
        precip = data.get("hourly", {}).get("precipitation", [0])
        # Sum last 3 hours of precipitation
        total_rain = sum(precip[-3:]) if len(precip) >= 3 else sum(precip)
        print(f"[WEATHER] Recent rainfall: {total_rain:.2f}mm")
        return total_rain
    except Exception as e:
        print(f"[WEATHER] Error: {e}")
        return 0.0

def fetch_latest():
    """Fetch latest water level from Firebase"""
    try:
        r = requests.get(FIREBASE_SENSOR, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        print(f"[SENSOR] Fetch error: {e}")
        return None

def append_history(record):
    """Append sensor data to local history CSV"""
    if record is None:
        return None

    df_new = pd.DataFrame([record])
    df_new["timestamp"] = pd.to_numeric(df_new["timestamp"], errors="coerce")

    if os.path.exists(LOCAL_HISTORY):
        try:
            df_old = pd.read_csv(LOCAL_HISTORY)
            df = pd.concat([df_old, df_new], ignore_index=True)
        except Exception as e:
            print(f"[CSV] Error reading: {e}")
            df = df_new
    else:
        df = df_new

    # Validate timestamps (remove outliers)
    now_ms = int(datetime.now().timestamp() * 1000)
    df = df[(df["timestamp"] > 0) & (df["timestamp"] < now_ms + 3600_000)]
    df.dropna(subset=["timestamp"], inplace=True)
    df.sort_values("timestamp", inplace=True)
    df.to_csv(LOCAL_HISTORY, index=False)
    print(f"[CSV] Appended {len(df)} records")
    return df

def prepare_ts(df):
    """Prepare time series data for ML"""
    if len(df) < 2:
        return None

    df = df.copy()
    df["dt"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
    df.dropna(subset=["dt"], inplace=True)

    # Calculate relative time (seconds from first measurement)
    t0 = df["timestamp"].iloc[0]
    df["t_rel"] = (df["timestamp"] - t0) / 1000.0
    return df

def train_model(df, weather=None):
    """Train Linear Regression with water level and optional weather feature"""
    if len(df) < 2:
        print("[ML] Not enough data for model")
        return None

    X = df[["t_rel"]].copy()
    
    # Add weather/precipitation as a feature if available
    if weather is not None and weather > 0:
        X["rain"] = weather
        print(f"[ML] Training with weather feature: {weather:.2f}mm rain")
    else:
        print("[ML] Training with time-series feature only")
    
    y = df["waterLevel"].values
    
    try:
        model = LinearRegression()
        model.fit(X, y)
        print(f"[ML] Model trained. Coefficients: {model.coef_}, Intercept: {model.intercept_:.2f}")
        return model
    except Exception as e:
        print(f"[ML] Training error: {e}")
        return None

def forecast(model, df, minutes=10, weather=0.0):
    """Make water level prediction for future time"""
    if model is None:
        return None

    try:
        last_t = df["t_rel"].iloc[-1]
        future_t = last_t + minutes * 60
        
        # Check if model was trained with weather
        if "rain" in model.feature_names_in_:
            X_pred = [[future_t, weather]]
        else:
            X_pred = [[future_t]]
        
        pred = float(model.predict(X_pred)[0])
        # Ensure water level doesn't go negative
        return max(pred, 0.0)
    except Exception as e:
        print(f"[ML] Forecast error: {e}")
        return None

def push_forecast(pred):
    """Push ML prediction to Firebase"""
    if pred is None:
        return False

    payload = {
        "pred_10min": round(pred, 2),
        "pred_30min": round(pred * 1.05, 2),  # rough estimate for 30 min
        "timestamp": int(datetime.now().timestamp() * 1000),
        "model": "LinearRegression",
        "features": "time_series+weather"
    }
    try:
        r = requests.put(FIREBASE_FORECAST, json=payload, timeout=5)
        if r.status_code == 200:
            print(f"[FIREBASE] Forecast pushed: {payload}")
            return True
    except Exception as e:
        print(f"[FIREBASE] Push error: {e}")
    return False

def pipeline():
    """Main ML pipeline: fetch → train → forecast → push"""
    print("\n" + "="*60)
    print(f"[PIPELINE] Starting at {datetime.now().isoformat()}")
    print("="*60)

    # 1. Fetch latest data
    latest = fetch_latest()
    if not latest:
        print("[PIPELINE] No sensor data available")
        return

    # 2. Append to history
    df = append_history(latest)
    if df is None or len(df) < 2:
        print("[PIPELINE] Insufficient history data")
        return

    # 3. Prepare time series
    df_ts = prepare_ts(df)
    if df_ts is None:
        print("[PIPELINE] Time series preparation failed")
        return

    # 4. Fetch weather context
    rain = fetch_weather()

    # 5. Train model
    model = train_model(df_ts, weather=rain)
    if model is None:
        print("[PIPELINE] Model training failed")
        return

    # 6. Make predictions
    pred_10min = forecast(model, df_ts, minutes=10, weather=rain)
    pred_30min = forecast(model, df_ts, minutes=30, weather=rain*0.5)

    if pred_10min is None:
        print("[PIPELINE] Forecast failed")
        return

    # 7. Push to Firebase
    push_forecast(pred_10min)

    # 8. Log summary
    print("\n[SUMMARY]")
    print(f"  Current water level: {latest['waterLevel']:.2f} mm")
    print(f"  10-min forecast: {pred_10min:.2f} mm")
    if pred_30min:
        print(f"  30-min forecast: {pred_30min:.2f} mm")
    print(f"  Recent rainfall: {rain:.2f} mm")
    print(f"  Data points in history: {len(df)}")
    print("="*60)

if __name__ == "__main__":
    print("Starting ML Forecast Pipeline with Weather Integration")
    print("Fetching every 5 seconds...")
    
    while True:
        try:
            pipeline()
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
        
        time.sleep(5)
