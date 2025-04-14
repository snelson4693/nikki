import csv
import os
import json
from datetime import datetime
import time
import random
from config_loader import get_personality_profile

LOG_FILE = "logs/trade_log.csv"
ERROR_LOG_FILE = "logs/error_log.json"

def log_trade(data, signal, status="executed"):
    tone = get_personality_profile().get("response_style", "professional")
    confidence = round(data.get("confidence", 0), 2)
    coin = data.get("coin", "unknown")

    if tone == "playful":
        print(f"🎯 Whoa! Nikki traded {coin} with {confidence} confidence. Status: {status}")
    elif tone == "serious":
        print(f"[{coin.upper()}] Trade finalized. Confidence: {confidence} | Status: {status}")
    else:
        print(f"🧠 Trade logged for {coin} → Status: {status} | Confidence: {confidence}")

    os.makedirs("logs", exist_ok=True)
    log_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode="a", newline='') as file:
        writer = csv.writer(file)
        if not log_exists:
            writer.writerow(["timestamp", "coin", "price", "volume", "change_24h", "signal", "amount", "status"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data['coin'],
            data['price'],
            data['volume'],
            data['change_24h'],
            signal.get("action") if signal else "none",
            signal.get("amount") if signal else 0,
            status
        ])

def log_message(message):
    tone = get_personality_profile().get("response_style", "professional")
    timestamp = datetime.now().strftime('%H:%M:%S')

    if tone == "playful":
        print(f"🗯️ [{timestamp}] Nikki says: {message}")
    elif tone == "serious":
        print(f"⚙️ [{timestamp}] SYSTEM >> {message}")
    else:
        print(f"[{timestamp}] {message}")


def adaptive_sleep(coin_name):
    delay = round(random.uniform(2.5, 5.5), 1)
    print(f"⏳ Waiting {delay}s to avoid spamming {coin_name}...")
    time.sleep(delay)

def log_error(error_message, context=None):
    os.makedirs("logs", exist_ok=True)
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": str(error_message),
        "context": context or "general"
    }

    if os.path.exists(ERROR_LOG_FILE):
        with open(ERROR_LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []

    logs.append(log_entry)
    with open(ERROR_LOG_FILE, "w") as f:
        json.dump(logs[-500:], f, indent=2)
