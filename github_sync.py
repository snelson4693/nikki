import os
import subprocess
from datetime import datetime

def sync_main_repo():
    print("🔁 Syncing Nikki's code repo...")

    try:
        # Pull latest changes
        subprocess.run(["git", "pull"], check=True)

        # Add changes
        subprocess.run(["git", "add", "."], check=True)

        # Commit with timestamp
        commit_message = f"🧠 Auto-sync Nikki code: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push to GitHub
        subprocess.run(["git", "push"], check=True)

        print("✅ Code repo synced successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Code sync error: {e}")

if __name__ == "__main__":
    sync_main_repo()
