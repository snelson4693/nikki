import json
import os
from collections import defaultdict
from datetime import datetime

PATTERN_FILE = "logs/pattern_learning.json"
META_MEMORY_FILE = "logs/meta_memory.json"

def update_meta_memory():
    if not os.path.exists(PATTERN_FILE):
        print("📭 No pattern logs found.")
        return

    with open(PATTERN_FILE, "r") as f:
        pattern_logs = json.load(f)

    meta = defaultdict(lambda: {"count": 0, "profit_triggers": 0, "loss_triggers": 0})

    for entry in pattern_logs[-300:]:  # Look at last 300 trades
        coin = entry.get("coin")
        action = entry.get("trade_action")
        rsi = entry.get("rsi")
        confidence = entry.get("confidence", 0)
        sentiment_score = entry.get("sentiment_score", 0)

        key = f"{coin}_rsi{int(rsi)}_conf{round(confidence, 1)}_sent{round(sentiment_score, 1)}"

        meta[key]["count"] += 1
        if action == "sell" and sentiment_score > 0:
            meta[key]["profit_triggers"] += 1
        elif action == "sell" and sentiment_score < 0:
            meta[key]["loss_triggers"] += 1

    summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "meta_patterns": meta
    }

    with open(META_MEMORY_FILE, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"🧬 Meta-memory updated → {len(meta)} patterns stored.")

if __name__ == "__main__":
    update_meta_memory()
