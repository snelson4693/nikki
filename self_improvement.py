import csv
import os
import json
from datetime import datetime
from collections import defaultdict
from utils.helpers import log_message

LOG_FILE = "logs/trade_log.csv"
SELF_IMPROVEMENT_LOG = "logs/self_improvement_log.json"

def analyze_trade_log():
    if not os.path.exists(LOG_FILE):
        print("📭 Trade log not found.")
        return

    with open(LOG_FILE, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows or len(rows) < 2:
        print("📭 Not enough trade data to analyze.")
        return

    # Handle missing header
    if "status" not in rows[0]:
        header = ["timestamp", "coin", "price", "volume", "change_24h", "signal", "amount", "status"]
        trades = [dict(zip(header, row)) for row in rows]
    else:
        trades = [dict(row) for row in csv.DictReader(rows)]

    executed_trades = [t for t in trades if t["status"] == "executed" and t["signal"] != "none"]
    if len(executed_trades) < 10:
        print("📊 Not enough executed trades to analyze patterns.")
        return

    signal_performance = defaultdict(lambda: {"total": 0, "profitable": 0})

    for trade in executed_trades:
        try:
            coin = trade["coin"]
            action = trade["signal"]
            price = float(trade["price"])
            change = float(trade["change_24h"])
            key = f"{coin}_{action}"

            signal_performance[key]["total"] += 1
            if (action == "buy" and change > 0) or (action == "sell" and change < 0):
                signal_performance[key]["profitable"] += 1
        except Exception as e:
            print(f"⚠️ Error analyzing trade: {e}")

    insights = {}
    for signal, stats in signal_performance.items():
        accuracy = stats["profitable"] / stats["total"]
        insights[signal] = {
            "total_trades": stats["total"],
            "profitable_trades": stats["profitable"],
            "accuracy": round(accuracy, 2)
        }

    print("🧠 Self-Improvement Report:")
    for signal, data in insights.items():
        print(f"📈 {signal}: Accuracy → {data['accuracy'] * 100:.1f}% ({data['profitable_trades']}/{data['total_trades']})")

    os.makedirs("logs", exist_ok=True)
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "insights": insights
    }

    if os.path.exists(SELF_IMPROVEMENT_LOG):
        with open(SELF_IMPROVEMENT_LOG, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []

    logs.append(log_entry)
    with open(SELF_IMPROVEMENT_LOG, "w") as f:
        json.dump(logs[-100:], f, indent=2)

    log_message("🧬 Self-Improvement log updated.")

if __name__ == "__main__":
    analyze_trade_log()
