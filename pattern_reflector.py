import json
import os
from datetime import datetime
from config_loader import update_strategy

TRADE_LOG = "logs/trade_history.json"
REFLECTION_LOG = "logs/pattern_reflections.json"

def reflect_on_trades():
    if not os.path.exists(TRADE_LOG):
        print("📭 No trade history found.")
        return

    with open(TRADE_LOG, "r") as file:
        wallet_data = json.load(file)

    history = wallet_data.get("trade_history", [])
    if not history:
        print("📭 No trade history entries to reflect on.")
        return

    reflections = []
    profitable_sells = []
    failed_sells = []

    for trade in history[-100:]:  # Reflect only on last 100 trades
        if trade["action"] == "sell":
            profit = trade.get("usd_gained", 0) - trade.get("usd_spent", 0)
            rsi = trade.get("rsi", None)
            if profit > 0:
                profitable_sells.append(rsi)
                reflections.append({
                    "timestamp": trade["timestamp"],
                    "coin": trade["coin"],
                    "profit": round(profit, 2),
                    "rsi": rsi,
                    "verdict": "✅ Good Sale"
                })
            else:
                failed_sells.append(rsi)
                reflections.append({
                    "timestamp": trade["timestamp"],
                    "coin": trade["coin"],
                    "profit": round(profit, 2),
                    "rsi": rsi,
                    "verdict": "❌ Bad Sale"
                })

    avg_good = sum([r for r in profitable_sells if r]) / len(profitable_sells) if profitable_sells else None
    avg_bad = sum([r for r in failed_sells if r]) / len(failed_sells) if failed_sells else None

    print("🪞 Nikki's Self-Reflection Summary:")
    print(f"✅ Avg RSI for profitable sells: {avg_good}")
    print(f"❌ Avg RSI for failed sells: {avg_bad}")

    # Update strategy with this refined logic
    if avg_good:
        update_strategy({
            "sell_rsi_threshold": round(avg_good, 2)
        })

    os.makedirs("logs", exist_ok=True)
    with open(REFLECTION_LOG, "w") as f:
        json.dump(reflections, f, indent=2)

    print(f"🧠 {len(reflections)} trade reflections saved to {REFLECTION_LOG}.")

if __name__ == "__main__":
    reflect_on_trades()
