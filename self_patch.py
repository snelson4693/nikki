import os
import json
import threading
import time
import requests
import difflib
import traceback
from datetime import datetime
from utils.sandbox import test_code_in_sandbox
from utils.file_utils import read_file_lines, write_file_lines

BUG_REPORT_FILE = "bug_reports.txt"
PATCH_HISTORY_FILE = "patch_history.json"
SOURCES_FILE = "patch_sources.json"
CHECK_INTERVAL = 180  # seconds

# Initialize known sources
default_sources = [
    "https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={query}&site=stackoverflow",
    "https://www.reddit.com/search.json?q={query}&sort=relevance",
    "https://huggingface.co/search/full-text?q={query}",
    "https://github.com/search?q={query}&type=repositories"
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
    success = test_code_in_sandbox(file_path)

    save_patch_history({
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "buggy_line": buggy_line,
        "new_line": new_line,
        "success": success,
        "source": explanation_url,
        "sandbox_verified": success
    })

    if not success:
        write_file_lines(file_path, backup)
    return success

def self_patch_loop():
    while True:
        if os.path.exists(BUG_REPORT_FILE):
            with open(BUG_REPORT_FILE, "r") as f:
                bugs = f.readlines()

            for bug in bugs:
                try:
                    query = bug.strip()
                    print(f"\U0001f9e0 Searching for patch: {query}")
                    responses = search_for_patch_explanation(query)

                    for url, explanation in responses:
                        suggested_line = extract_patch_line(explanation)
                        buggy_line = extract_buggy_line(query)

                        if suggested_line and buggy_line:
                            for attempt in range(3):
                                print(f"\U0001f527 Attempt {attempt+1}/3 → Patching...")
                                success = attempt_patch("main.py", buggy_line, suggested_line, url)
                                if success:
                                    print("✅ Patch applied successfully.")
                                    break
                                else:
                                    print("❌ Patch failed. Retrying...")
                except Exception as e:
                    print("⚠️ Error during patching:", e)
                    traceback.print_exc()

            open(BUG_REPORT_FILE, "w").close()

        time.sleep(CHECK_INTERVAL)

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

def start_patch_engine():
    thread = threading.Thread(target=self_patch_loop, daemon=True)
    thread.start()
    print("\U0001f9e0 Self-patching engine activated in background.")
