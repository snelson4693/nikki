import threading
import subprocess
import time
import traceback

def run_main():
    while True:
        try:
            print("🧠 Starting Nikki Brain...")
            subprocess.run(["python", "main.py"], check=True)
        except subprocess.CalledProcessError as e:
            print("❌ Nikki Brain crashed.")
            traceback.print_exc()
            time.sleep(5)

def run_dashboard():
    while True:
        try:
            print("🖥️ Starting Nikki Dashboard...")
            subprocess.run(["python", "dashboard/app.py"], check=True)
        except subprocess.CalledProcessError as e:
            print("❌ Dashboard crashed.")
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    brain_thread = threading.Thread(target=run_main, daemon=True)
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)

    brain_thread.start()
    dashboard_thread.start()

    while True:
        time.sleep(1)
