import os
import json
import threading
import time
import requests
import difflib
import traceback
from datetime import datetime
from utils.sandbox import run_code_sandbox
from utils.file_utils import read_file_lines, write_file_lines
from config_loader import load_config

BUG_REPORT_FILE = "logs/bug_reports.txt"
ERROR_POOL_FILE = "logs/error_pool.json"
PATCH_HISTORY_FILE = "logs/patch_history.json"
SOURCES_FILE = "patch_sources.json"
CHECK_INTERVAL = 180  # seconds

# Load instance ID
instance_id = load_config().get("instance_id", "unknown")

# Default patch sources
default_sources = [
    "https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={query}&site=stackoverflow",
    "https://www.reddit.com/search.json?q={query}&sort=relevance",
    "https://huggingface.co/search/full-text?q={query}",
    "https://github.com/search?q={query}&type=code"
]

# Ensure patch_sources.json exists
if not os.path.exists(SOURCES_FILE):
    with open(SOURCES_FILE, "w") as f:
        json.dump(default_sources, f)

def load_sources():
    with open(SOURCES_FILE, "r") as f:
        return json.load(f)

def save_patch_history(entry):
    if not os.path.exists(PATCH_HISTORY_FILE):
        with open(PATCH_HISTORY_FILE, "w") as f:
            json.dump([], f)
    with open(PATCH_HISTORY_FILE, "r") as f:
        history = json.load(f)
    history.append(entry)
    with open(PATCH_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def update_error_pool():
    if not os.path.exists(BUG_REPORT_FILE):
        return

    with open(BUG_REPORT_FILE, "r") as f:
        bugs = [line.strip() for line in f.readlines() if line.strip()]
    if not bugs:
        return

    # Ensure brain_repo/logs directory exists
    os.makedirs(os.path.dirname(ERROR_POOL_FILE), exist_ok=True)

    try:
        if os.path.exists(ERROR_POOL_FILE):
            with open(ERROR_POOL_FILE, "r") as f:
                error_pool = json.load(f)
        else:
            error_pool = []

        for bug in bugs:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "instance": instance_id,
                "error": bug
            }
            if entry not in error_pool:
                error_pool.append(entry)

        with open(ERROR_POOL_FILE, "w") as f:
            json.dump(error_pool, f, indent=4)
        open(BUG_REPORT_FILE, "w").close()  # Clear local bug log after sync
    except Exception as e:
        print(f"❌ Failed to update error pool: {e}")

def search_for_patch_explanation(query):
    sources = load_sources()
    explanations = []
    for url_template in sources:
        try:
            url = url_template.replace("{query}", requests.utils.quote(query))
            headers = {"User-Agent": "NikkiBot/1.0"}
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                explanations.append((url, res.text[:2000]))
        except:
            continue
    return explanations

def attempt_patch(file_path, buggy_line, new_line, explanation_url):
    lines = read_file_lines(file_path)
    backup = lines[:]
    patched = False

    for i, line in enumerate(lines):
        if buggy_line.strip() in line.strip():
            lines[i] = new_line + "\n"
            patched = True
            break

    if not patched:
        return False

    write_file_lines(file_path, lines)
    success = run_code_sandbox(file_path)

    save_patch_history({
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "buggy_line": buggy_line,
        "new_line": new_line,
        "success": success,
        "source": explanation_url,
        "sandbox_verified": success,
        "instance": instance_id
    })

    if not success:
        write_file_lines(file_path, backup)
    return success

def extract_buggy_line(error_msg):
    if "NameError" in error_msg:
        return error_msg.split("'")[1]
    return "unknown"

def extract_patch_line(explanation_text):
    lines = explanation_text.split("\n")
    for line in lines:
        if "def" in line or "=" in line:
            return line.strip()
    return None

def self_patch_loop():
    while True:
        update_error_pool()  # Push local bugs to shared pool

        try:
            with open(ERROR_POOL_FILE, "r") as f:
                errors = json.load(f)
        except:
            errors = []

        for err in errors:
            query = err["error"]
            source_instance = err["instance"]
            print(f"🧠 Attempting global patch for: {query} from {source_instance}")

            try:
                responses = search_for_patch_explanation(query)
                for url, explanation in responses:
                    buggy_line = extract_buggy_line(query)
                    suggested_line = extract_patch_line(explanation)
                    if suggested_line and buggy_line:
                        for attempt in range(3):
                            print(f"🔧 Attempt {attempt+1}/3 → patching...")
                            success = attempt_patch("main.py", buggy_line, suggested_line, url)
                            if success:
                                print("✅ Patch succeeded!")
                                break
                            else:
                                print("🔁 Patch failed. Trying again...")
            except Exception as e:
                print("⚠️ Patch attempt failed:", e)
                traceback.print_exc()

        time.sleep(CHECK_INTERVAL)

def start_patch_engine():
    thread = threading.Thread(target=self_patch_loop, daemon=True)
    thread.start()
    print("🧠 Global self-patching engine running in background.")
