import subprocess
import threading
import os
import time
from datetime import datetime

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_process(name, command, log_file):
    while True:
        try:
            log(f"🚀 Starting {name}...")
            with open(os.path.join(LOGS_DIR, log_file), "a") as f:
                f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {name} started.\n")
                process = subprocess.Popen(command, stdout=f, stderr=f)
                process.wait()
                f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {name} crashed. Restarting in 5 seconds...\n")
        except Exception as e:
            log(f"❌ Error running {name}: {e}")
        time.sleep(5)

def run_main():
    run_process("Nikki Brain (main.py)", ["python", "main.py"], "main.log")

def run_dashboard():
    run_process("Nikki Dashboard (app.py)", ["python", os.path.join("dashboard", "app.py")], "dashboard.log")

if __name__ == "__main__":
    threading.Thread(target=run_main, daemon=True).start()
    threading.Thread(target=run_dashboard, daemon=True).start()

    # Keep main thread alive
    while True:
        time.sleep(60)
