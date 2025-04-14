import os
import json
import pandas as pd
from datetime import datetime
from prediction_engine import load_model, predict_price_movement
from config_loader import load_config
from trade_engine import evaluate_trade
from sentiment import summarize_sentiments

MEMORY_FILE = "logs/pattern_learning.json"
CLONE_RESULTS_FILE = "logs/clone_simulation_results.json"

def load_memory(limit=500):
    if not os.path.exists(MEMORY_FILE):
        print("📭 No memory available for clone simulation.")
        return []

    with open(MEMORY_FILE, "r") as f:
        records = json.load(f)

    return records[-limit:] if len(records) > limit else records

def run_simulated_clone():
    memory = load_memory()
    if not memory:
        return

    print(f"🤖 Running clone simulation on {len(memory)} memory records...")
    model_data = load_model()
    if not model_data:
        print("⚠️ No model available — aborting clone sim.")
        return

    model, scaler = model_data
    config = load_config()
    results = []
    correct = 0

    for entry in memory:
        try:
            rsi = float(entry["rsi"])
            volume = float(entry["volume"])
            change = float(entry["change_24h"])
            price = float(entry["price"])
            sentiment_score = float(entry["sentiment_score"])
            actual_action = entry["trade_action"]

            data = {
                "rsi": rsi,
                "volume": volume,
                "change_24h": change,
                "price": price,
                "coin": entry.get("coin", "unknown"),
                "confidence": entry.get("confidence", 0)
            }

            sentiment_summary = {
                "positive": entry.get("sentiment_positive", 0),
                "negative": entry.get("sentiment_negative", 0),
                "neutral": entry.get("sentiment_neutral", 0),
                "score": sentiment_score
            }

            simulated_signal = evaluate_trade(data, sentiment_summary)
            predicted_action = simulated_signal["action"] if simulated_signal else "none"

            is_correct = predicted_action == actual_action
            if is_correct:
                correct += 1

            results.append({
                "timestamp": entry["timestamp"],
                "coin": data["coin"],
                "actual": actual_action,
                "predicted": predicted_action,
                "rsi": rsi,
                "volume": volume,
                "confidence": data.get("confidence", 0),
                "was_correct": is_correct
            })
        except Exception as e:
            print(f"❌ Clone sim error: {e}")

    accuracy = round((correct / len(results)) * 100, 2) if results else 0
    print(f"🧠 Clone Accuracy: {accuracy:.2f}% ({correct}/{len(results)})")

    os.makedirs("logs", exist_ok=True)
    with open(CLONE_RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "accuracy": accuracy,
            "results": results[-100:]  # keep last 100
        }, f, indent=2)

if __name__ == "__main__":
    run_simulated_clone()
