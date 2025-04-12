import json
import os
from datetime import datetime

CONFIG_FILE = "config.json"
STRATEGY_LOG = "logs/strategy_updates.json"

def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

def update_strategy(new_settings):
    config = load_config()
    config["strategy"].update(new_settings)

    # Save updated strategy to config file
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

    # Log strategy update with timestamp
    log = []
    if os.path.exists(STRATEGY_LOG):
        with open(STRATEGY_LOG, "r") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []

    log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_strategy": new_settings
    })

    os.makedirs("logs", exist_ok=True)
    with open(STRATEGY_LOG, "w") as f:
        json.dump(log, f, indent=4)
