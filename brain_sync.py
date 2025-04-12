import os
import subprocess
from datetime import datetime

MODEL_DIR = "model"

def sync_brain_repo():
    print("🔁 Syncing Nikki's brain repo...")

    try:
        # Pull latest brain files
        subprocess.run(["git", "-C", MODEL_DIR, "pull"], check=True)

        # Add new/changed brain files
        subprocess.run(["git", "-C", MODEL_DIR, "add", "."], check=True)

        # Commit with timestamp
        commit_message = f"🧠 Auto-sync Nikki brain: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "-C", MODEL_DIR, "commit", "-m", commit_message], check=True)

        # Push to GitHub
        subprocess.run(["git", "-C", MODEL_DIR, "push"], check=True)

        print("✅ Brain repo synced successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Brain sync error: {e}")

if __name__ == "__main__":
    sync_brain_repo()
