import os
import json
import time
from datetime import datetime
from prediction_engine import load_model
from config_loader import load_config

MODEL_DIR = "model"
HISTORY_FILE = "logs/model_history.json"
MAX_MODEL_AGE = 60 * 60 * 6  # 6 hours

def get_model_metadata():
    model_path = os.path.join(MODEL_DIR, "model.pkl")
    if not os.path.exists(model_path):
        return None

    return {
        "last_updated": os.path.getmtime(model_path),
        "timestamp": datetime.fromtimestamp(os.path.getmtime(model_path)).strftime("%Y-%m-%d %H:%M:%S"),
    }

def should_retrain_model():
    metadata = get_model_metadata()
    if not metadata:
        print("🧠 No model found. Training from scratch.")
        return True

    model_age = time.time() - metadata["last_updated"]
    if model_age > MAX_MODEL_AGE:
        print(f"🧠 Model is older than {MAX_MODEL_AGE/3600:.1f}h. Triggering retrain.")
        return True

    return False

def update_model_history(accuracy=None):
    os.makedirs("logs", exist_ok=True)

    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "accuracy": round(accuracy, 2) if accuracy else None
    }

    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-100:], f, indent=2)  # keep last 100 entries
