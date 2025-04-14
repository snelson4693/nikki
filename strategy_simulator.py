import json
import os
from datetime import datetime
from statistics import mean

PATTERN_FILE = "logs/pattern_learning.json"
SIMULATION_LOG = "logs/simulation_results.json"

def simulate_strategies():
    if not os.path.exists(PATTERN_FILE):
        print("📭 No pattern data found.")
        return

    with open(PATTERN_FILE, "r") as f:
        trades = json.load(f)

    simulations = []
    profits_actual = []
    profits_simulated = []

    for trade in trades:
        price = float(trade["price"])
        rsi = float(trade["rsi"])
        conf = float(trade.get("confidence", 0))
        sentiment = float(trade.get("sentiment_score", 0))
        action = trade["trade_action"]

        # Simulate a rule: Only sell if RSI > 60 and sentiment is positive
        simulated_action = "none"
        if rsi > 60 and sentiment > 0:
            simulated_action = "sell"

        # Only simulate trades that actually happened
        if action == "sell":
            usd_actual = float(trade.get("usd_gained", trade.get("usd_spent", 0)))
            profits_actual.append(usd_actual)

            if simulated_action == "sell":
                usd_simulated = usd_actual * (1 + conf * 0.01)
                profits_simulated.append(usd_simulated)

                simulations.append({
                    "timestamp": trade["timestamp"],
                    "coin": trade["coin"],
                    "original_action": action,
                    "simulated_action": simulated_action,
                    "original_profit": round(usd_actual, 4),
                    "simulated_profit": round(usd_simulated, 4)
                })

    accuracy = (len(profits_simulated) / len(profits_actual)) * 100 if profits_actual else 0
    avg_actual = mean(profits_actual) if profits_actual else 0
    avg_simulated = mean(profits_simulated) if profits_simulated else 0

    print(f"\n🧪 Strategy Simulation Complete:")
    print(f"📊 Simulated Strategy Accuracy: {accuracy:.2f}%")
    print(f"💰 Avg Actual Profit: ${avg_actual:.4f}")
    print(f"💡 Avg Simulated Profit: ${avg_simulated:.4f}")

    os.makedirs("logs", exist_ok=True)
    with open(SIMULATION_LOG, "w") as f:
        json.dump({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "accuracy": accuracy,
            "average_actual_profit": avg_actual,
            "average_simulated_profit": avg_simulated,
            "simulations": simulations[:15]  # Save first 15 entries only
        }, f, indent=2)

if __name__ == "__main__":
    simulate_strategies()
