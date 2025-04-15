import os
import json
from datetime import datetime
from utils.file_utils import read_file_lines, write_file_lines

LOG_DIR = "logs"

# ✅ Central list of JSON logs to merge (excluding device-specific files like portfolio.json)
MERGEABLE_LOGS = [
    "strategy_updates.json",
    "reflective_journal.json",
    "global_news.json",
    "hive_trades.json",
    "influencer_sentiment.json",
    "macro_insights.json",
    "model_history.json",
    "pattern_frequency.json",
    "prediction_feedback.json",
    "replay_results.json",
    "replay_accuracy_log.json",
    "simulation_results.json",
    "self_improvement_log.json",
    "self_reflection.json",
    "trade_outcome_log.json"
]

def merge_json_logs():
    """
    Merges list-based JSON logs from both local and remote brain_repo locations.
    Deduplicates entries using JSON string keys and sorts by timestamp if present.
    """
    for log_file in MERGEABLE_LOGS:
        path = os.path.join(LOG_DIR, log_file)
        remote_path = os.path.join("brain_repo", LOG_DIR, log_file)

        # Load local log
        try:
            with open(path, "r") as f:
                local_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            local_data = []

        # Load remote log
        try:
            with open(remote_path, "r") as f:
                remote_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            remote_data = []

        # Skip non-list files
        if not isinstance(local_data, list):
            print(f"⚠️ Skipped {log_file} (not a list format)")
            continue

        # 🔄 Merge entries using serialized JSON key
        merged = {json.dumps(entry, sort_keys=True): entry for entry in local_data}
        for entry in remote_data:
            key = json.dumps(entry, sort_keys=True)
            merged[key] = entry

        # ✅ Sort by timestamp if available
        merged_list = list(merged.values())
        merged_list.sort(key=lambda x: x.get("timestamp", ""))

        # Write to both local + brain_repo
        try:
            with open(path, "w") as f:
                json.dump(merged_list, f, indent=4)
            with open(remote_path, "w") as f:
                json.dump(merged_list, f, indent=4)
            print(f"✅ Merged {log_file} successfully.")
        except Exception as e:
            print(f"❌ Error writing {log_file}: {e}")

def merge_trade_log_csv():
    """
    Merges CSV-format trade logs between local and remote versions.
    Uses line-based deduplication and preserves header.
    """
    trade_log = os.path.join(LOG_DIR, "trade_log.csv")
    brain_log = os.path.join("brain_repo", LOG_DIR, "trade_log.csv")

    local_lines = read_file_lines(trade_log)
    remote_lines = read_file_lines(brain_log)

    # Remove duplicates
    merged = set(local_lines + remote_lines)
    header = "timestamp,coin,price,volume,confidence,action,amount,status"

    if header in merged:
        merged.remove(header)

    final_lines = [header] + sorted(merged)

    # Write both local and remote
    try:
        write_file_lines(trade_log, final_lines)
        write_file_lines(brain_log, final_lines)
        print("✅ Merged trade_log.csv successfully.")
    except Exception as e:
        print(f"❌ Error writing trade_log.csv: {e}")

def run_full_log_merge():
    """
    🔁 Full-cycle merger for all logs — JSON + CSV — across all devices.
    Ensures conflict-resistant log updates for singular intelligence behavior.
    """
    print("🔄 Merging all Nikki logs...")
    try:
        merge_json_logs()
        merge_trade_log_csv()
        print("✅ All logs merged and synced.")
    except Exception as e:
        print(f"❌ Error during log merge: {e}")

if __name__ == "__main__":
    run_full_log_merge()
