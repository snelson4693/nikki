import threading
import time
import re
from datetime import datetime
import os

LOG_PATH = "logs/nikki.log"
ERROR_LOG_PATH = "logs/error_patterns.json"
BUG_REPORT_PATH = "logs/bug_reports.txt"

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
            r"sklearn\.utils\.validation\.py:.*UserWarning.*",
        ]

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

    def save_bug(self, error_line, matched_pattern):
        with open(BUG_REPORT_PATH, 'a') as report:
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            report.write(f"[{timestamp}] Pattern: {matched_pattern} | Error: {error_line}\n")

    def stop(self):
        self.running = False


# Launch in background
if __name__ == "__main__":
    debugger = SelfDebugger()
    debugger.daemon = True
    debugger.start()
