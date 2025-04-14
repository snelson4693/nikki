import os
import json
import random
from datetime import datetime
from config_loader import load_config, update_strategy

ACCURACY_LOG = "logs/replay_accuracy_log.json"
MUTATION_LOG = "logs/mutation_log.json"

def mutate_strategy():
    try:
        if not os.path.exists(ACCURACY_LOG):
            print("📭 No accuracy data found for mutation.")
            return

        with open(ACCURACY_LOG, "r") as f:
            replay_data = json.load(f)

        current_accuracy = replay_data.get("accuracy", 100)
        print(f"🧪 Accuracy check: {current_accuracy:.2f}%")

        config = load_config()
        strategy = config.get("strategy", {})

        mutation_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prev_strategy": strategy.copy(),
            "accuracy": current_accuracy,
        }

        if current_accuracy >= 90:
            print("✅ Accuracy high — no mutation needed.")
            return

        # Mutate strategy parameters
        new_strategy = strategy.copy()
        new_strategy["buy_rsi_threshold"] = max(10, min(90, strategy["buy_rsi_threshold"] + random.randint(-2, 2)))
        new_strategy["sell_rsi_threshold"] = max(10, min(90, strategy["sell_rsi_threshold"] + random.randint(-2, 2)))
        new_strategy["sentiment_bias"] = random.choice([0, 1])

        update_strategy(new_strategy)
        mutation_record["new_strategy"] = new_strategy

        print("🧬 Strategy mutated:", new_strategy)

        # Log mutation
        os.makedirs("logs", exist_ok=True)
        if os.path.exists(MUTATION_LOG):
            with open(MUTATION_LOG, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append(mutation_record)

        with open(MUTATION_LOG, "w") as f:
            json.dump(history[-50:], f, indent=2)  # Keep latest 50 entries

    except Exception as e:
        print(f"❌ Mutation error: {e}")

if __name__ == "__main__":
    mutate_strategy()
