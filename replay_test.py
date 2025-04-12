import csv
from trade_engine import evaluate_trade
from sentiment import summarize_sentiments
from config_loader import load_config

PATTERN_FILE = "logs/pattern_memory.csv"

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

        for row in logs:
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

            print(f"🧠 Past: RSI={data['rsi']}, Sentiment={sentiment_summary} → Nikki said: {predicted_action} (Expected: {expected_action})")

            if predicted_action == expected_action:
                matches += 1
            total += 1

        accuracy = (matches / total) * 100 if total > 0 else 0
        print(f"\n🧪 Replay Test Complete → Accuracy: {accuracy:.2f}% ({matches}/{total} matched)")

    except Exception as e:
        print(f"❌ Replay test error: {e}")

if __name__ == "__main__":
    replay_pattern_decisions()
