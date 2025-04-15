import subprocess
from datetime import datetime
import socket

MODEL_DIR = "model"

def get_instance_id():
    return socket.gethostname()

def pull_latest_brain():
    print("🔄 Pulling latest brain from GitHub...")
    try:
        subprocess.run(["git", "-C", MODEL_DIR, "pull"], check=True)
        print("✅ Pulled latest brain.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Pull failed: {e}")

def push_brain_update():
    print("🔼 Pushing updated brain to GitHub...")
    try:
        subprocess.run(["git", "-C", MODEL_DIR, "add", "."], check=True)
        commit_message = f"🧠 Auto-sync from {get_instance_id()} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "-C", MODEL_DIR, "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "-C", MODEL_DIR, "push"], check=True)
        print("✅ Pushed updated brain.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Push failed: {e}")

if __name__ == "__main__":
    pull_latest_brain()
    push_brain_update()
