import json
import os
from datetime import datetime
from trade_engine import evaluate_trade
from sentiment import summarize_sentiments
from utils.helpers import log_error

PATTERN_FILE = "logs/pattern_learning.json"
SIMULATION_LOG = "logs/clone_decision_log.json"

def run_simulation():
    if not os.path.exists(PATTERN_FILE):
        print("📭 No pattern memory to simulate.")
        return

    with open(PATTERN_FILE, "r") as f:
        try:
            memory = json.load(f)
        except json.JSONDecodeError as e:
            log_error("trade_simulator.py", "Failed to load pattern memory", e)
            return

    results = []
    for entry in memory:
        try:
            data = {
                "rsi": float(entry["rsi"]),
                "price": float(entry["price"]),
                "volume": float(entry["volume"]),
                "change_24h": float(entry.get("change_24h", 0)),
                "coin": entry["coin"]
            }

            sentiment = {
                "positive": entry.get("sentiment_positive", 0),
                "negative": entry.get("sentiment_negative", 0),
                "neutral": entry.get("sentiment_neutral", 0)
            }

            prediction = evaluate_trade(data, sentiment)
            simulated_action = prediction["action"] if prediction else "none"

            results.append({
                "timestamp": entry["timestamp"],
                "coin": entry["coin"],
                "original_action": entry["trade_action"],
                "simulated_action": simulated_action,
                "confidence": entry.get("confidence", 0),
                "price": entry["price"]
            })
        except Exception as e:
            log_error("trade_simulator.py", f"Error simulating entry: {entry}", e)

    with open(SIMULATION_LOG, "w") as f:
        json.dump(results[-1000:], f, indent=2)

    print(f"🧪 Clone simulation complete — {len(results)} patterns analyzed.")

if __name__ == "__main__":
    run_simulation()
