import os
import json
from datetime import datetime

REFLECTION_LOG = "logs/self_reflection.json"

def reflect_on_decision(context, observation, suggestion=None):
    os.makedirs("logs", exist_ok=True)

    reflection = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "context": context,
        "observation": observation,
        "suggestion": suggestion or "none"
    }

    # Load existing log or initialize
    if os.path.exists(REFLECTION_LOG):
        try:
            with open(REFLECTION_LOG, "r") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    else:
        logs = []

    logs.append(reflection)

    with open(REFLECTION_LOG, "w") as f:
        json.dump(logs[-100:], f, indent=2)

    print(f"🧠 Nikki reflected on: {context} → {observation}")
def log_reflection(reflection_text, category="general"):
    """
    Logs Nikki's reflection about her behavior, decisions, or performance.
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "reflection": reflection_text
    }

    log_file = "reflections.json"

    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(log_entry)

    with open(log_file, "w") as f:
        json.dump(data, f, indent=4)

    print(f"🧠 Reflection logged: {reflection_text}")