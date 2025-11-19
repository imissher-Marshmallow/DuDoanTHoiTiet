import requests
import pandas as pd
import os
from datetime import datetime
import time

FIREBASE_URL = "https://edfwef-default-rtdb.firebaseio.com/water_level/sensor1.json"
LOCAL_HISTORY = "history.csv"
LOG_FILE = "fetch_log.txt"

def log(msg):
    ts = datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)

def fetch_latest():
    try:
        r = requests.get(FIREBASE_URL, timeout=5)
        if r.status_code != 200:
            log(f"Fetch error: HTTP {r.status_code}")
            return None
        data = r.json()
        log(f"Fetched from Firebase: {data}")
        return data
    except Exception as e:
        log(f"Fetch exception: {e}")
        return None

def append_history(record):
    if record is None:
        log("No record to append")
        return None

    df_new = pd.DataFrame([record])
    df_new["timestamp"] = pd.to_numeric(df_new.get("timestamp", 0), errors="coerce")
    now_ms = int(datetime.now().timestamp() * 1000)
    df_new = df_new[(df_new["timestamp"] > 0) & (df_new["timestamp"] < now_ms + 3600_000)]

    if os.path.exists(LOCAL_HISTORY):
        try:
            df_old = pd.read_csv(LOCAL_HISTORY)
            df = pd.concat([df_old, df_new], ignore_index=True)
        except Exception as e:
            log(f"Read/concat error: {e}")
            df = df_new
    else:
        df = df_new

    df.dropna(subset=["timestamp"], inplace=True)
    df.sort_values("timestamp", inplace=True)
    df.to_csv(LOCAL_HISTORY, index=False)
    log(f"Appended to {LOCAL_HISTORY}: {record}")
    return df

if __name__ == "__main__":
    while True:
        time.sleep(5)
        latest = fetch_latest()
        df = append_history(latest)
        if df is not None:
            log(f"History now has {len(df)} records")
        else:
            log("No history updated")
