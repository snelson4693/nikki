import csv
import os
from datetime import datetime
import time
import random

LOG_FILE = "logs/trade_log.csv"

def log_trade(data, signal, status="executed"):
    """Log a trade decision to a CSV file."""
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
    """Prints and time-stamps a general log message."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
def adaptive_sleep(coin_name):
    # Random delay between 2-5s to avoid rate limiting (adjust if needed)
    delay = round(random.uniform(2.5, 5.5), 1)
    print(f"⏳ Waiting {delay}s to avoid spamming {coin_name}...")
    time.sleep(delay)