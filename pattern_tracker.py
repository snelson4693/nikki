import csv
import os
from datetime import datetime

MEMORY_FILE = "logs/pattern_memory.csv"

def save_market_snapshot(data, sentiment_summary, trade_signal):
    os.makedirs("logs", exist_ok=True)
    file_exists = os.path.isfile(MEMORY_FILE)

    with open(MEMORY_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "timestamp", "rsi", "price", "volume",
                "sentiment_positive", "sentiment_negative", "sentiment_neutral",
                "trade_action"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data["rsi"],
            data["price"],
            data["volume"],
            sentiment_summary.get("positive", 0),
            sentiment_summary.get("negative", 0),
            sentiment_summary.get("neutral", 0),
            trade_signal.get("action") if trade_signal else "none"
        ])
