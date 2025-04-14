import os
import json
from datetime import datetime

INFLUENCE_LOG_FILE = "logs/influence_log.json"
INFLUENCE_PATTERN_FILE = "logs/influence_patterns.json"

def detect_influence_patterns():
    if not os.path.exists(INFLUENCE_LOG_FILE):
        print("📭 No influence log found.")
        return

    with open(INFLUENCE_LOG_FILE, "r") as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            print("❌ Error reading influence log.")
            return

    patterns = {
        "buy_impact": [],
        "sell_impact": [],
        "positive_influences": 0,
        "negative_influences": 0
    }

    for entry in logs:
        action = entry["action"]
        percent_change = entry["percent_change"]

        if action == "buy":
            patterns["buy_impact"].append(percent_change)
        elif action == "sell":
            patterns["sell_impact"].append(percent_change)

        if percent_change > 0:
            patterns["positive_influences"] += 1
        elif percent_change < 0:
            patterns["negative_influences"] += 1

    def summarize(changes):
        if not changes:
            return {"avg": 0, "max": 0, "min": 0}
        return {
            "avg": round(sum(changes) / len(changes), 4),
            "max": round(max(changes), 4),
            "min": round(min(changes), 4)
        }

    summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "buy_summary": summarize(patterns["buy_impact"]),
        "sell_summary": summarize(patterns["sell_impact"]),
        "positive_influences": patterns["positive_influences"],
        "negative_influences": patterns["negative_influences"],
        "total_trades_analyzed": len(logs)
    }

    os.makedirs("logs", exist_ok=True)
    with open(INFLUENCE_PATTERN_FILE, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"📊 Influence pattern summary saved → {INFLUENCE_PATTERN_FILE}")

if __name__ == "__main__":
    detect_influence_patterns()
