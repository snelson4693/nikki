import os
import csv
import json
from datetime import datetime

from trade_engine import evaluate_trade
from sentiment import summarize_sentiments
from config_loader import load_config, update_strategy

PATTERN_FILE = "logs/pattern_memory.csv"
REPLAY_LOG_FILE = "logs/replay_results.json"
REPLAY_ACCURACY_HISTORY = "logs/replay_accuracy_log.json"
DEBUG_EDGE_CASES_FILE = "logs/debug_edge_cases.json"

def replay_pattern_decisions():
    try:
        with open(PATTERN_FILE, "r") as file:
            reader = csv.DictReader(file)
            logs = list(reader)

        if not logs:
            print("📭 No past pattern data to test.")
            return

        matches = 0
        total = 0
        mismatches = []
        edge_cases = []

        for row in logs:
            try:
                data = {
                    "rsi": float(row["rsi"]),
                    "price": float(row["price"]),
                    "volume": float(row["volume"]),
                }

                sentiment_summary = {
                    "positive": int(row["sentiment_positive"]),
                    "negative": int(row["sentiment_negative"]),
                    "neutral": int(row["sentiment_neutral"]),
                }

                expected_action = row["trade_action"]
                signal = evaluate_trade(data, sentiment_summary)
                predicted_action = signal["action"] if signal else "none"

                print(f"🧠 RSI={data['rsi']} → Nikki said: {predicted_action} (Expected: {expected_action})")

                if predicted_action == expected_action:
                    matches += 1
                else:
                    mismatches.append({
                        "timestamp": row["timestamp"],
                        "coin": row.get("coin", "unknown"),
                        "rsi": data["rsi"],
                        "volume": data["volume"],
                        "expected": expected_action,
                        "predicted": predicted_action
                    })

                total += 1

            except Exception as e:
                edge_cases.append({
                    "timestamp": row.get("timestamp"),
                    "coin": row.get("coin", "unknown"),
                    "error": str(e),
                    "raw_row": row
                })
                continue

        accuracy = (matches / total) * 100 if total > 0 else 0
        print(f"\n🧪 Replay Test Complete → Accuracy: {accuracy:.2f}% ({matches}/{total} matched)")

        os.makedirs("logs", exist_ok=True)
        replay_log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "accuracy": accuracy,
            "matches": matches,
            "total": total,
            "mismatches": mismatches[:10]
        }
        with open(REPLAY_LOG_FILE, "w") as f:
            json.dump(replay_log, f, indent=2)

        # ⏺️ Save edge cases separately
        if edge_cases:
            with open(DEBUG_EDGE_CASES_FILE, "w") as f:
                json.dump(edge_cases[-50:], f, indent=2)
            print(f"⚠️ {len(edge_cases)} edge cases logged to debug_edge_cases.json")

        # Strategy tuning if needed
        history_entry = {
            "timestamp": replay_log["timestamp"],
            "accuracy": accuracy,
            "adjustments": None
        }
        try:
            with open(REPLAY_ACCURACY_HISTORY, "r") as f:
                history = json.load(f)
        except:
            history = []

        adjustments = {}
        if accuracy < 80:
            print("⚠️ Low accuracy detected — tuning strategy...")
            strategy = load_config().get("strategy", {})
            new_buy = max(10, strategy.get("buy_rsi_threshold", 40) - 1)
            new_sell = min(90, strategy.get("sell_rsi_threshold", 60) + 1)
            update_strategy({
                "buy_rsi_threshold": new_buy,
                "sell_rsi_threshold": new_sell
            })
            adjustments = {
                "buy_rsi_threshold": new_buy,
                "sell_rsi_threshold": new_sell
            }
            print(f"🔧 Strategy auto-adjusted → Buy < {new_buy}, Sell > {new_sell}")
        else:
            print("✅ Accuracy is healthy. No adjustment made.")

        history_entry["adjustments"] = adjustments if adjustments else "none"
        history.append(history_entry)
        with open(REPLAY_ACCURACY_HISTORY, "w") as f:
            json.dump(history[-100:], f, indent=2)

    except Exception as e:
        print(f"❌ Replay test error: {e}")

if __name__ == "__main__":
    replay_pattern_decisions()
