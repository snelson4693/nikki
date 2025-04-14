# logs/trade_outcome_logger.py

import os
import json
from datetime import datetime

OUTCOME_FILE = "logs/trade_outcomes.json"

def log_trade_outcome(coin, action, amount, buy_price=None, sell_price=None):
    os.makedirs("logs", exist_ok=True)

    outcome = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "coin": coin,
        "action": action,
        "amount": amount,
        "buy_price": buy_price,
        "sell_price": sell_price
    }

    if action == "sell" and buy_price is not None and sell_price is not None:
        diff = sell_price - buy_price
        outcome["outcome"] = "profit" if diff > 0 else "loss" if diff < 0 else "neutral"
        outcome["gain"] = round(diff * amount, 4)
    else:
        outcome["outcome"] = "n/a"
        outcome["gain"] = 0.0

    try:
        if os.path.exists(OUTCOME_FILE):
            with open(OUTCOME_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append(outcome)
        with open(OUTCOME_FILE, "w") as f:
            json.dump(data[-1000:], f, indent=2)  # Keep last 1000 records
    except Exception as e:
        print(f"❌ Trade outcome logging error: {e}")
