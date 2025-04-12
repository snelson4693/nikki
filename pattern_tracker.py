import os
import json
from datetime import datetime

# Updated pattern_tracker.py with extended pattern logging

PATTERN_LOG_JSON = "logs/pattern_learning.json"
PATTERN_LOG_CSV = "logs/pattern_memory.csv"

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
        "trade_amount": trade_signal["amount"] if trade_signal else 0
    }

    # Save to JSON (for backup/history)
    if os.path.exists(PATTERN_LOG_JSON):
        with open(PATTERN_LOG_JSON, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(record)
    with open(PATTERN_LOG_JSON, "w") as f:
        json.dump(logs[-500:], f, indent=2)  # Retain only the last 500 entries

    # Save to CSV (for strategy_optimizer)
    import csv
    write_header = not os.path.exists(PATTERN_LOG_CSV)
    with open(PATTERN_LOG_CSV, "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=record.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(record)
