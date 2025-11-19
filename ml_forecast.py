import requests
import pandas as pd
import os
import time
from sklearn.linear_model import LinearRegression
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

FIREBASE_SENSOR = os.getenv(
    "FB_SENSOR",
    "https://edfwef-default-rtdb.firebaseio.com/water_level/sensor1.json")
FIREBASE_FORECAST = os.getenv(
    "FB_FORECAST",
    "https://edfwef-default-rtdb.firebaseio.com/forecast/sensor1.json")

LOCAL_HISTORY = "history.csv"


def fetch_latest():
    try:
        r = requests.get(FIREBASE_SENSOR, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


def append_history(record):
    df_new = pd.DataFrame([record])
    df_new["timestamp"] = pd.to_numeric(df_new["timestamp"], errors="coerce")

    if os.path.exists(LOCAL_HISTORY):
        df_old = pd.read_csv(LOCAL_HISTORY)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    now_ms = int(datetime.now().timestamp() * 1000)
    df = df[(df["timestamp"] > 0) & (df["timestamp"] < now_ms + 3600_000)]
    df.dropna(subset=["timestamp"], inplace=True)
    df.sort_values("timestamp", inplace=True)
    df.to_csv(LOCAL_HISTORY, index=False)
    return df


def prepare_ts(df):
    if len(df) < 2:
        return None
    df["dt"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
    df.dropna(subset=["dt"], inplace=True)
    t0 = df["timestamp"].iloc[0]
    df["t_rel"] = (df["timestamp"] - t0) / 1000.0
    return df


def train_model(df):
    X = df[["t_rel"]].values
    y = df["waterLevel"].values
    model = LinearRegression().fit(X, y)
    return model


def forecast(model, df, minutes=10):
    last_t = df["t_rel"].iloc[-1]
    future_t = last_t + minutes * 60
    pred = float(model.predict([[future_t]])[0])
    return pred


def push_forecast(pred):
    payload = {
        "pred_10min": round(pred, 2),
        "timestamp": int(datetime.now().timestamp() * 1000)
    }
    try:
        requests.put(FIREBASE_FORECAST, json=payload, timeout=5)
        print(f"[ML] Forecast pushed: {payload}")
    except Exception as e:
        print(f"[ML] Push error: {e}")


def pipeline():
    latest = fetch_latest()
    if not latest:
        print("[ML] No data fetched")
        return

    df = append_history(latest)
    df_ts = prepare_ts(df)
    if df_ts is None:
        print("[ML] Not enough data yet")
        return

    model = train_model(df_ts)
    pred10 = forecast(model, df_ts, minutes=10)
    push_forecast(pred10)
    print(
        f"[ML] Latest: {latest['waterLevel']}, Pred+10min: {round(pred10,2)}")


if __name__ == "__main__":
    while True:
        pipeline()
        time.sleep(5)
