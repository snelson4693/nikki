import os
import json
import pandas as pd
import subprocess
from datetime import datetime
from prediction_engine import train_and_save_model

MEMORY_FILE = "logs/pattern_learning.json"
BRAIN_FOLDER = "brain_repo"

def load_recent_memory(limit=300):
    if not os.path.exists(MEMORY_FILE):
        print("📭 No pattern memory found.")
        return []

    with open(MEMORY_FILE, "r") as f:
        records = json.load(f)

    recent = records[-limit:] if len(records) > limit else records
    return recent

def prepare_training_data(memory):
    data = []
    labels = []

    for entry in memory:
        try:
            rsi = float(entry["rsi"])
            volume = float(entry["volume"])
            change = float(entry["change_24h"])
            sentiment = float(entry["sentiment_score"])
            price = float(entry["price"])
            action = entry["trade_action"]

            label = 1 if action == "buy" else -1 if action == "sell" else 0
            features = [rsi, volume, change, sentiment, price]
            data.append(features)
            labels.append(label)
        except:
            continue

    return pd.DataFrame(data, columns=["rsi", "volume", "change_24h", "sentiment", "price"]), pd.Series(labels)

def push_to_brain_repo():
    try:
        subprocess.run(["git", "-C", BRAIN_FOLDER, "pull"], check=True)
        subprocess.run(["cp", "model/model.pkl", f"{BRAIN_FOLDER}/model.pkl"])
        subprocess.run(["cp", "model/scaler.pkl", f"{BRAIN_FOLDER}/scaler.pkl"])
        subprocess.run(["git", "-C", BRAIN_FOLDER, "add", "."], check=True)
        subprocess.run([
            "git", "-C", BRAIN_FOLDER, "commit",
            "-m", f"🧠 Auto-sync retrained brain: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ], check=True)
        subprocess.run(["git", "-C", BRAIN_FOLDER, "push"], check=True)
        print("✅ Brain pushed to GitHub successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error syncing brain to GitHub: {e}")

def train_brain():
    memory = load_recent_memory()
    if not memory:
        print("⚠️ No memory to train from.")
        return

    X, y = prepare_training_data(memory)
    train_and_save_model(X, y)
    print("✅ Nikki's brain has been retrained and saved.")

    push_to_brain_repo()

if __name__ == "__main__":
    train_brain()
