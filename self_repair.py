import os
import time
import threading
import difflib
import shutil
import json

from self_reflection import log_reflection
from datetime import datetime

BUG_LOG = "bug_reports.txt"
REPAIR_FOLDER = "repaired_versions"

# Ensure the repair folder exists
os.makedirs(REPAIR_FOLDER, exist_ok=True)

def load_bug_reports():
    if not os.path.exists(BUG_LOG):
        return []
    with open(BUG_LOG, "r") as file:
        return [line.strip() for line in file if line.strip()]

def patch_code(file_path, bug_hint):
    if not os.path.exists(file_path):
        return False, "File not found."

    with open(file_path, "r") as file:
        original_code = file.readlines()

    patched_code = []
    changed = False

    for line in original_code:
        if bug_hint in line:
            # Attempt to comment out and patch logic
            patched_code.append(f"# ⚠️ Auto-commented due to: {bug_hint}\n")
            patched_code.append(f"# {line.strip()}\n")
            patched_code.append(f"# Nikki's suggestion: Review this line manually.\n")
            changed = True
        else:
            patched_code.append(line)

    if changed:
        filename = os.path.basename(file_path)
        backup_path = os.path.join(REPAIR_FOLDER, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
        shutil.copyfile(file_path, backup_path)

        with open(file_path, "w") as file:
            file.writelines(patched_code)

        return True, backup_path

    return False, "No changes made."

def run_self_repair():
    bug_reports = load_bug_reports()
    results = []
    for bug in bug_reports:
        if "File" in bug and "line" in bug:
            try:
                parts = bug.split(" in ")
                file_path = parts[1].split(" at ")[0].strip()
                hint = parts[0].strip()
                success, detail = patch_code(file_path, hint)
                if success:
                    results.append(f"✅ Patched {file_path} → Backup: {detail}")
                else:
                    results.append(f"⚠️ Skipped {file_path} → {detail}")
            except Exception as e:
                results.append(f"❌ Error parsing: {bug} → {str(e)}")

    log_reflection("Self-repair completed", results)

def start_self_repair():
    thread = threading.Thread(target=run_self_repair, daemon=True)
    thread.start()
