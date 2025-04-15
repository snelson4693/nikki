import socket
import os
import json

CONFIG_PATH = "config.json"


def get_instance_id():
    """Return a unique identifier for the machine."""
    return socket.gethostname()


def update_instance_id():
    instance_id = get_instance_id()

    if not os.path.exists(CONFIG_PATH):
        config = {}
    else:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)

    config['instance_id'] = instance_id

    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

    print(f"🧠 Nikki is running as instance: {instance_id}")


if __name__ == "__main__":
    update_instance_id()
