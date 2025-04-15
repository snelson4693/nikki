import os
import subprocess
from datetime import datetime

def is_git_repo():
    result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
    return result.returncode == 0 and result.stdout.strip() == "true"

def create_auto_sync_branch():
    subprocess.run(["git", "checkout", "-B", "auto-sync"], check=True)

def create_pull_request():
    try:
        # Check for differences
        diff_check = subprocess.run(["git", "diff", "--quiet", "main", "auto-sync"])
        if diff_check.returncode == 0:
            print("⚠️ No changes between 'main' and 'auto-sync'. No PR needed.")
            return

        # Create pull request via GitHub CLI
        pr_message = "🚀 Nikki's auto-generated pull request for code improvements"
        subprocess.run([
            "gh", "pr", "create",
            "--title", "Auto-sync and improvements",
            "--body", pr_message,
            "--base", "main",
            "--head", "auto-sync"
        ], check=True)
        print("✅ Pull request created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating pull request: {e}")

def sync_main_repo():
    print("🔁 Syncing Nikki's code repo...")

    if not is_git_repo():
        print("❌ Not a Git repository. Make sure you run this inside Nikki’s project folder.")
        return

    try:
        subprocess.run(["git", "checkout", "main"], check=True)
        subprocess.run(["git", "pull", "origin", "main"], check=True)

        create_auto_sync_branch()

        subprocess.run(["git", "add", "."], check=True)

        commit_message = f"🧠 Auto-sync Nikki code: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        subprocess.run(["git", "push", "-u", "origin", "auto-sync"], check=True)

        create_pull_request()

        print("✅ Code repo synced and pull request created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Code sync error: {e}")

if __name__ == "__main__":
    sync_main_repo()
