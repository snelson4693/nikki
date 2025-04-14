import json
import os
from datetime import datetime
from trade_engine import evaluate_trade
from sentiment import summarize_sentiments
from utils.helpers import log_error
from config_loader import load_config
from utils.helpers import log_message
import random


PATTERN_FILE = "logs/pattern_learning.json"
SIMULATION_LOG = "logs/clone_decision_log.json"
SIM_RESULT_FILE = "logs/simulation_results.json"

def simulate_future_performance():
    config = load_config()
    base_buy = config.get("buy_rsi_threshold", 30)
    base_sell = config.get("sell_rsi_threshold", 70)

    clones = []

    for i in range(5):
        buy_threshold = base_buy + random.uniform(-2, 2)
        sell_threshold = base_sell + random.uniform(-2, 2)

        simulated_profit = simulate_trades(buy_threshold, sell_threshold)

        clone = {
            "buy_rsi_threshold": round(buy_threshold, 2),
            "sell_rsi_threshold": round(sell_threshold, 2),
            "simulated_profit": round(simulated_profit, 4),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        clones.append(clone)

    os.makedirs("logs", exist_ok=True)
    with open(SIM_RESULT_FILE, "w") as f:
        json.dump(clones, f, indent=2)

    log_message(f"📊 Simulated strategy clones saved to {SIM_RESULT_FILE}")

def simulate_trades(buy_rsi, sell_rsi):
    # Simulate pseudo trade logic (replace this with more advanced logic later)
    profit = 0
    for _ in range(20):  # simulate 20 trades
        rsi = random.uniform(10, 90)
        if rsi < buy_rsi:
            profit += random.uniform(-2, 4)
        elif rsi > sell_rsi:
            profit += random.uniform(-1, 5)
        else:
            profit += random.uniform(-1, 1)
    return profit

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
