import os
import json
import csv
from datetime import datetime, timedelta

# Enhanced pattern tracker that fully replaces memory_engine functionality
PATTERN_LOG_JSON = "logs/pattern_learning.json"
PATTERN_LOG_CSV = "logs/pattern_memory.csv"
TRADE_LOG = "logs/trade_log.csv"
RECENT_WINDOW_MINUTES = 15

def save_market_snapshot(data, sentiment_summary, trade_signal):
    os.makedirs("logs", exist_ok=True)

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "coin": data["coin"],
        "price": data["price"],
        "rsi": data.get("rsi"),
        "volume": data["volume"],
        "change_24h": data["change_24h"],
        "confidence": data.get("confidence"),
        "sentiment_score": sentiment_summary.get("score", 0),
        "sentiment_positive": sentiment_summary.get("positive", 0),
        "sentiment_negative": sentiment_summary.get("negative", 0),
        "sentiment_neutral": sentiment_summary.get("neutral", 0),
        "trade_action": trade_signal["action"] if trade_signal else "none",
        "trade_amount": trade_signal["amount"] if trade_signal else 0,
        "outcome": "pending"
    }

    # Save to JSON
    if os.path.exists(PATTERN_LOG_JSON):
        with open(PATTERN_LOG_JSON, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(record)
    with open(PATTERN_LOG_JSON, "w") as f:
        json.dump(logs[-500:], f, indent=2)

    # Save to CSV
    write_header = not os.path.exists(PATTERN_LOG_CSV)
    with open(PATTERN_LOG_CSV, "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=record.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(record)

    return record
def was_recent_trade(symbol):
    if not os.path.exists(TRADE_LOG):
        return False
    try:
        with open(TRADE_LOG, "r") as f:
            lines = f.readlines()[::-1]  # read in reverse (most recent first)
            for line in lines:
                parts = line.strip().split(",")
                if len(parts) < 2:
                    continue
                timestamp, coin = parts[0], parts[1]
                if coin.lower() == symbol.lower():
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    if datetime.utcnow() - dt < timedelta(minutes=RECENT_WINDOW_MINUTES):
                        return True
                    break
    except Exception as e:
        print(f"❌ Error checking recent trades: {e}")
    return False