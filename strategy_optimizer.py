import csv
from config_loader import update_strategy

PATTERN_FILE = "logs/pattern_memory.csv"

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

        for row in patterns:
            rsi = float(row["rsi"])
            action = row["trade_action"]
            sentiment = int(row["sentiment_positive"]) - int(row["sentiment_negative"])
            profit = float(row.get("profit", 0))

            if action == "sell":
                if profit > 0:
                    profitable_rsi.append(rsi)
                else:
                    unprofitable_rsi.append(rsi)

                if sentiment > 0:
                    successful.append(rsi)
                else:
                    failed.append(rsi)

        avg_success_rsi = sum(successful) / len(successful) if successful else None
        avg_fail_rsi = sum(failed) / len(failed) if failed else None
        avg_profitable_rsi = sum(profitable_rsi) / len(profitable_rsi) if profitable_rsi else None
        avg_unprofitable_rsi = sum(unprofitable_rsi) / len(unprofitable_rsi) if unprofitable_rsi else None

        print("📈 Self-Optimization Summary:")
        print(f"✅ Avg RSI on successful trades: {avg_success_rsi}")
        print(f"❌ Avg RSI on failed/neutral trades: {avg_fail_rsi}")
        print(f"💰 Avg RSI on profitable trades: {avg_profitable_rsi}")
        print(f"📉 Avg RSI on unprofitable trades: {avg_unprofitable_rsi}")

        if avg_success_rsi:
            update_strategy({
                "sell_rsi_threshold": round(avg_success_rsi or 70, 2),
                "sentiment_bias": 1 if avg_success_rsi < avg_fail_rsi else 0,
                "profit_rsi_range": {
                    "min": round(min(profitable_rsi), 2) if profitable_rsi else None,
                    "max": round(max(profitable_rsi), 2) if profitable_rsi else None
                }
            })

        return {
            "recommended_sell_rsi": avg_success_rsi,
            "avoid_rsi": avg_fail_rsi,
            "profit_rsi_range": {
                "min": round(min(profitable_rsi), 2) if profitable_rsi else None,
                "max": round(max(profitable_rsi), 2) if profitable_rsi else None
            }
        }

    except Exception as e:
        print(f"❌ Strategy optimization error: {e}")
        return None

if __name__ == "__main__":
    analyze_patterns()
