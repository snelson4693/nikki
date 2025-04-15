import json
import os
from datetime import datetime
from device_identity import get_instance_id  # New import

CONFIG_FILE = "config.json"
STRATEGY_LOG = "logs/strategy_updates.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("⚠️ config.json not found — loading default config.")
        return {"strategy": {}, "instance_id": get_instance_id()}

    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)

    # Inject or update instance_id
    config["instance_id"] = get_instance_id()

    return config

def update_strategy(new_settings):
    config = load_config()
    config.setdefault("strategy", {}).update(new_settings)
    config["instance_id"] = get_instance_id()  # Ensure instance_id stays current

    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

    log = []
    if os.path.exists(STRATEGY_LOG):
        with open(STRATEGY_LOG, "r") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []

    log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_strategy": new_settings,
        "instance_id": get_instance_id()
    })

    os.makedirs("logs", exist_ok=True)
    with open(STRATEGY_LOG, "w") as f:
        json.dump(log, f, indent=4)

def get_personality_profile():
    config = load_config()
    return config.get("personality", {
        "confidence_tone": "neutral",
        "risk_profile": "balanced",
        "response_style": "professional"
    })
