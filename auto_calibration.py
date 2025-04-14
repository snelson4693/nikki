import json
import os
from datetime import datetime
from config_loader import load_config, update_strategy

SIMULATION_LOG = "logs/simulation_results.json"

def auto_calibrate_strategy():
    if not os.path.exists(SIMULATION_LOG):
        print("📭 No simulation results to calibrate from.")
        return

    with open(SIMULATION_LOG, "r") as f:
        data = json.load(f)

    avg_actual = data.get("average_actual_profit", 0)
    avg_simulated = data.get("average_simulated_profit", 0)

    if avg_simulated > avg_actual:
        print("🔧 Calibrating strategy — simulated trades outperformed real ones!")

        config = load_config().get("strategy", {})
        new_buy_rsi = max(10, config.get("buy_rsi_threshold", 40) - 2)
        new_sell_rsi = min(90, config.get("sell_rsi_threshold", 60) + 2)

        update_strategy({
            "buy_rsi_threshold": new_buy_rsi,
            "sell_rsi_threshold": new_sell_rsi,
            "sentiment_bias": 1
        })

        print(f"✅ Strategy auto-calibrated: Buy RSI → {new_buy_rsi}, Sell RSI → {new_sell_rsi}")
    else:
        print("🧠 Current strategy is still more profitable — no calibration needed.")

if __name__ == "__main__":
    auto_calibrate_strategy()
