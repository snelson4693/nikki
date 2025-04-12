import json

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

def update_strategy(new_settings):
    config = load_config()
    config["strategy"].update(new_settings)

    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)
