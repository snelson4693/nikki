import os
import csv
import json
from datetime import datetime

from trade_engine import evaluate_trade
from sentiment import summarize_sentiments
from config_loader import load_config, update_strategy

PATTERN_FILE = "logs/pattern_memory.csv"
REPLAY_LOG_FILE = "logs/replay_accuracy_log.json"

def run_pattern_replay():
    try:
        if not os.path.exists(PATTERN_FILE):
            print("📭 No pattern data available.")
            return

        with open(PATTERN_FILE, "r") as file:
            reader = csv.DictReader(file)
            logs = list(reader)

        matches = 0
        total = 0
        mismatches = []

        for row in logs:
            data = {
                "rsi": float(row["rsi"]),
                "price": float(row["price"]),
                "volume": float(row["volume"])
            }

            sentiment = {
                "positive": int(row.get("sentiment_positive", 0)),
                "negative": int(row.get("sentiment_negative", 0)),
                "neutral": int(row.get("sentiment_neutral", 0))
            }

            expected = row["trade_action"]
            predicted_signal = evaluate_trade(data, sentiment)
            predicted = predicted_signal["action"] if predicted_signal else "none"

            if predicted == expected:
                matches += 1
            else:
                mismatches.append({
                    "timestamp": row.get("timestamp"),
                    "coin": row.get("coin"),
                    "rsi": data["rsi"],
                    "expected": expected,
                    "predicted": predicted
                })

            total += 1

        accuracy = (matches / total) * 100 if total > 0 else 0
        print(f"\n🧠 Pattern Replay Accuracy: {accuracy:.2f}% | {matches}/{total} matched")

        os.makedirs("logs", exist_ok=True)
        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "accuracy": accuracy,
            "matched": matches,
            "total": total,
            "mismatches": mismatches[:10]  # Show a few mismatches only
        }

        with open(REPLAY_LOG_FILE, "w") as f:
            json.dump(result, f, indent=2)

        # 🧠 Optional tuning if accuracy drops
        if accuracy < 75:
            strategy = load_config().get("strategy", {})
            update_strategy({
                "buy_rsi_threshold": max(10, strategy.get("buy_rsi_threshold", 40) - 1),
                "sell_rsi_threshold": min(90, strategy.get("sell_rsi_threshold", 60) + 1)
            })
            print("🔧 Strategy thresholds updated based on pattern replay accuracy.")

    except Exception as e:
        print(f"❌ Pattern replay error: {e}")

if __name__ == "__main__":
    run_pattern_replay()
