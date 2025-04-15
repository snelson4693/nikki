import os
import subprocess
from datetime import datetime
from log_merge_wiring import run_full_log_merge  # ✅ Import the log merging system

MODEL_DIR = "model"

def sync_brain_repo():
    print("🔁 Syncing Nikki's brain repo...")

    try:
        # ✅ Step 1: Merge logs before syncing to prevent overwrite conflicts
        run_full_log_merge()

        # ✅ Step 2: Pull latest from GitHub to avoid sync errors
        subprocess.run(["git", "-C", MODEL_DIR, "pull"], check=True)

        # ✅ Step 3: Add any new or changed brain files
        subprocess.run(["git", "-C", MODEL_DIR, "add", "."], check=True)

        # ✅ Step 4: Commit with a clear timestamp
        commit_message = f"🧠 Auto-sync Nikki brain: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "-C", MODEL_DIR, "commit", "-m", commit_message], check=True)

        # ✅ Step 5: Push to remote brain repo
        subprocess.run(["git", "-C", MODEL_DIR, "push"], check=True)

        print("✅ Brain repo synced successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Brain sync error: {e}")

if __name__ == "__main__":
    sync_brain_repo()
