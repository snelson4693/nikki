import csv
import json
import os
from datetime import datetime
from collections import Counter
from config_loader import update_strategy
from utils.helpers import log_error
from trade_simulator import simulate_future_performance

PATTERN_FILE = "logs/pattern_memory.csv"
TRADE_OUTCOMES_FILE = "logs/trade_outcomes.json"
FEEDBACK_LOG = "logs/prediction_feedback.json"
FREQUENCY_FILE = "logs/pattern_frequency.json"
SIM_RESULT_FILE = "logs/simulation_results.json"

def analyze_patterns():
    try:
        with open(PATTERN_FILE, "r") as file:
            reader = csv.DictReader(file)
            patterns = list(reader)

        if not patterns:
            print("📭 No pattern data to analyze.")
            return None

        successful = []
        failed = []
        profitable_rsi = []
        unprofitable_rsi = []
        all_rsi_values = []

        for row in patterns:
            try:
                rsi = float(row["rsi"])
                sentiment = int(row["sentiment_positive"]) - int(row["sentiment_negative"])
                profit = float(row.get("profit", 0))
                action = row["trade_action"]
                all_rsi_values.append(round(rsi))

                if action == "sell":
                    if profit > 0:
                        profitable_rsi.append(rsi)
                    else:
                        unprofitable_rsi.append(rsi)

                    if sentiment > 0:
                        successful.append(rsi)
                    else:
                        failed.append(rsi)
            except Exception as e:
                log_error("strategy_optimizer.py", f"Error parsing row → {row}", e)

        rsi_counter = Counter(all_rsi_values)
        top_rsi_ranges = rsi_counter.most_common(10)
        rsi_clusters = [{"rsi": r, "count": c} for r, c in top_rsi_ranges]

        avg_success_rsi = sum(successful) / len(successful) if successful else None
        avg_fail_rsi = sum(failed) / len(failed) if failed else None
        avg_profitable_rsi = sum(profitable_rsi) / len(profitable_rsi) if profitable_rsi else None
        avg_unprofitable_rsi = sum(unprofitable_rsi) / len(unprofitable_rsi) if unprofitable_rsi else None

        print("📊 RSI Pattern Clusters →", rsi_clusters)
        print("📈 Self-Optimization Summary:")
        print(f"✅ Avg RSI on successful trades: {avg_success_rsi}")
        print(f"❌ Avg RSI on failed/neutral trades: {avg_fail_rsi}")
        print(f"💰 Avg RSI on profitable trades: {avg_profitable_rsi}")
        print(f"📉 Avg RSI on unprofitable trades: {avg_unprofitable_rsi}")

        os.makedirs("logs", exist_ok=True)
        with open(FREQUENCY_FILE, "w") as f:
            json.dump({
                "timestamp": patterns[-1]["timestamp"],
                "rsi_clusters": rsi_clusters
            }, f, indent=2)

        confidence_adjustment = adjust_from_prediction_feedback()
        outcome_rsi_min, outcome_rsi_max = learn_from_trade_outcomes()
        new_threshold = avg_success_rsi or avg_profitable_rsi or outcome_rsi_max or 70
        sentiment_bias = 1 if avg_success_rsi and avg_fail_rsi and avg_success_rsi < avg_fail_rsi else 0

        update_strategy({
            "sell_rsi_threshold": round(new_threshold + confidence_adjustment, 2),
            "sentiment_bias": sentiment_bias,
            "profit_rsi_range": {
                "min": round(min(profitable_rsi), 2) if profitable_rsi else outcome_rsi_min,
                "max": round(max(profitable_rsi), 2) if profitable_rsi else outcome_rsi_max
            }
        })

        # ✅ NEW: Run simulation and analyze best strategy clone
        simulate_future_performance()
        apply_best_clone_if_available()

        return {
            "recommended_sell_rsi": avg_success_rsi,
            "avoid_rsi": avg_fail_rsi,
            "profit_rsi_range": {
                "min": round(min(profitable_rsi), 2) if profitable_rsi else outcome_rsi_min,
                "max": round(max(profitable_rsi), 2) if profitable_rsi else outcome_rsi_max
            },
            "rsi_clusters": rsi_clusters
        }

    except Exception as e:
        log_error("strategy_optimizer.py", "Fatal error in analyze_patterns()", e)
        return None

def learn_from_trade_outcomes():
    try:
        if not os.path.exists(TRADE_OUTCOMES_FILE):
            return None, None

        with open(TRADE_OUTCOMES_FILE, "r") as f:
            trades = json.load(f)

        outcome_rsi = [t["rsi"] for t in trades if t["action"] == "sell" and "rsi" in t]
        if not outcome_rsi:
            return None, None

        return round(min(outcome_rsi), 2), round(max(outcome_rsi), 2)

    except Exception as e:
        log_error("strategy_optimizer.py", "Error reading trade outcomes", e)
        return None, None

def adjust_from_prediction_feedback():
    try:
        if not os.path.exists(FEEDBACK_LOG):
            return 0

        with open(FEEDBACK_LOG, "r") as f:
            logs = json.load(f)

        recent_logs = logs[-100:]
        if not recent_logs:
            return 0

        correct = [1 for log in recent_logs if log["was_correct"]]
        accuracy = len(correct) / len(recent_logs)

        if accuracy < 0.6:
            print("⚠️ Model confidence low — decreasing RSI threshold slightly.")
            return -1
        elif accuracy > 0.8:
            print("🚀 Model confidence high — increasing RSI threshold slightly.")
            return 1

        return 0
    except Exception as e:
        log_error("strategy_optimizer.py", "Error reading prediction feedback", e)
        return 0

def apply_best_clone_if_available():
    try:
        if not os.path.exists(SIM_RESULT_FILE):
            print("📭 No clone simulation data found.")
            return

        with open(SIM_RESULT_FILE, "r") as f:
            clones = json.load(f)

        if not clones:
            return

        # Choose clone with highest profit
        best = max(clones, key=lambda x: x.get("simulated_profit", -999))
        print(f"🧬 Best performing clone → Profit: ${best['simulated_profit']:.2f}")

        update_strategy({
            "buy_rsi_threshold": best["buy_rsi_threshold"],
            "sell_rsi_threshold": best["sell_rsi_threshold"]
        })

        print("🎯 Strategy auto-updated from simulated clone.")
    except Exception as e:
        log_error("strategy_optimizer.py", "Error applying best clone strategy", e)

if __name__ == "__main__":
    analyze_patterns()
