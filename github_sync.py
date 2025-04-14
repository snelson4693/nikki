import os
import subprocess
from datetime import datetime

def create_pull_request():
    try:
        # Define the commit message
        commit_message = f"🧠 Auto-sync Nikki code and brain update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Add changes and commit
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push to GitHub
        subprocess.run(["git", "push"], check=True)
        
        # Create a pull request via GitHub CLI (assuming gh CLI is set up)
        pr_message = "🚀 Nikki's auto-generated pull request for code improvements"
        subprocess.run(["gh", "pr", "create", "--title", "Auto-sync and improvements", "--body", pr_message, "--base", "main", "--head", "auto-sync"], check=True)
        print("✅ Pull request created successfully.")
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating pull request: {e}")

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

        # Create pull request after syncing
        create_pull_request()

        print("✅ Code repo synced and pull request created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Code sync error: {e}")

if __name__ == "__main__":
    sync_main_repo()
