import threading
import time
import re
from datetime import datetime
import os
import json
from config_loader import load_config

LOG_PATH = "logs/nikki.log"
ERROR_LOG_PATH = "logs/error_patterns.json"
BUG_REPORT_PATH = "logs/bug_reports.txt"
ERROR_POOL_PATH = "brain_repo/logs/error_pool.json"

class SelfDebugger(threading.Thread):
    def __init__(self, log_path=LOG_PATH):
        super().__init__()
        self.log_path = log_path
        self.running = True
        self.last_read_position = 0
        self.error_patterns = [
            r"KeyError:.*",
            r"ValueError:.*",
            r"TypeError:.*",
            r"IndexError:.*",
            r"FileNotFoundError:.*",
            r"ModuleNotFoundError:.*",
            r"sklearn\\.utils\\.validation\\.py:.*UserWarning.*",
        ]

        # Get instance ID
        config = load_config()
        self.instance_id = config.get("instance_id", "unknown")

    def run(self):
        while self.running:
            self.scan_log()
            time.sleep(5)

    def scan_log(self):
        if not os.path.exists(self.log_path):
            return

        with open(self.log_path, 'r') as file:
            file.seek(self.last_read_position)
            new_lines = file.readlines()
            self.last_read_position = file.tell()

        for line in new_lines:
            for pattern in self.error_patterns:
                if re.search(pattern, line):
                    self.save_bug(line.strip(), pattern)
                    self.append_to_error_pool(line.strip(), pattern)

    def save_bug(self, error_line, matched_pattern):
        with open(BUG_REPORT_PATH, 'a') as report:
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            report.write(f"[{timestamp}] Pattern: {matched_pattern} | Error: {error_line}\n")

    def append_to_error_pool(self, error_line, matched_pattern):
        error_entry = {
            "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            "instance_id": self.instance_id,
            "pattern": matched_pattern,
            "error": error_line
        }

        try:
            if os.path.exists(ERROR_POOL_PATH):
                with open(ERROR_POOL_PATH, 'r') as f:
                    errors = json.load(f)
            else:
                errors = []
        except json.JSONDecodeError:
            errors = []

        errors.append(error_entry)
        os.makedirs(os.path.dirname(ERROR_POOL_PATH), exist_ok=True)
        with open(ERROR_POOL_PATH, 'w') as f:
            json.dump(errors, f, indent=4)

    def stop(self):
        self.running = False

# Launch in background
if __name__ == "__main__":
    debugger = SelfDebugger()
    debugger.daemon = True
    debugger.start()
