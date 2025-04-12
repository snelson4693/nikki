import os

def pull_brain():
    if not os.path.exists("model"):
        os.makedirs("model")
    print("🧠 Pulling latest brain from GitHub...")

    # Clone only if not already cloned
    if not os.path.exists("brain_repo"):
        os.system("git clone https://github.com/snelson4693/nikki-brain.git brain_repo")
    else:
        os.chdir("brain_repo")
        os.system("git pull")
        os.chdir("..")

    # Copy model to active folder
    os.system("copy brain_repo\\model.pkl model\\model.pkl")
    os.system("copy brain_repo\\scaler.pkl model\\scaler.pkl")
    print("✅ Brain synced.")

if __name__ == "__main__":
    pull_brain()
