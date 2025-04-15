import json
import os
from datetime import datetime

def merge_logs(file_path, key="timestamp"):
    """
    Merge log entries from the local and remote version of a log file,
    keeping all unique entries and sorting by timestamp.
    """
    merged = []
    seen = set()
    
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []

    for entry in data:
        id_val = entry.get(key)
        if id_val and id_val not in seen:
            seen.add(id_val)
            merged.append(entry)

    merged.sort(key=lambda x: x.get(key, ""))
    return merged

def save_merged_logs(file_path, merged_data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(merged_data, f, indent=4)


def resolve_strategy_conflicts(local_strategy, remote_strategy):
    """
    Keep the most recent values by timestamp for each setting.
    """
    merged = local_strategy.copy()
    for key, remote_val in remote_strategy.items():
        if key not in local_strategy or remote_val.get("timestamp", 0) > local_strategy[key].get("timestamp", 0):
            merged[key] = remote_val
    return merged
