import json
import os
from config_loader import update_strategy
from datetime import datetime

INFLUENCE_PATTERN_FILE = "logs/influence_patterns.json"
INFLUENCE_REINFORCE_LOG = "logs/influence_adjustments.json"

def adjust_strategy_based_on_influence():
    if not os.path.exists(INFLUENCE_PATTERN_FILE):
        print("📭 No influence pattern data found.")
        return

    try:
        with open(INFLUENCE_PATTERN_FILE, "r") as f:
            summary = json.load(f)

        influence_score = summary["positive_influences"] - summary["negative_influences"]
        total = summary["total_trades_analyzed"]

        if total == 0:
            print("📭 No trades analyzed for influence.")
            return

        ratio = influence_score / total

        # Define strategy reinforcement logic
        if ratio > 0.4:
            adjustment = -2
            tone = "assertive"
        elif ratio < -0.3:
            adjustment = 2
            tone = "cautious"
        else:
            adjustment = 0
            tone = "neutral"

        # Update strategy thresholds if necessary
        if adjustment != 0:
            print(f"🔁 Adjusting strategy from influence ratio: {round(ratio, 2)}")
            update_strategy({
                "sell_rsi_threshold": summary["sell_summary"]["avg"] + adjustment,
                "buy_rsi_threshold": summary["buy_summary"]["avg"] + adjustment
            })

        # Optionally evolve personality
        os.makedirs("logs", exist_ok=True)
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "influence_ratio": round(ratio, 3),
            "new_response_style": tone
        }

        if os.path.exists(INFLUENCE_REINFORCE_LOG):
            with open(INFLUENCE_REINFORCE_LOG, "r") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        logs.append(log_entry)
        with open(INFLUENCE_REINFORCE_LOG, "w") as f:
            json.dump(logs[-100:], f, indent=2)

        print(f"✅ Influence-based adjustment complete — New style: {tone}")

    except Exception as e:
        print(f"❌ Influence strategy adjustment error: {e}")

if __name__ == "__main__":
    adjust_strategy_based_on_influence()
