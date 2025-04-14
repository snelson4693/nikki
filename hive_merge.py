import json
import os
from datetime import datetime

LOCAL_HIVE_FILE = "logs/hive_trades.json"
REMOTE_NODE_FILE = "logs/remote_node.json"

def merge_hive_memory():
    if not os.path.exists(REMOTE_NODE_FILE):
        print("⚠️ No remote memory to merge.")
        return

    try:
        with open(LOCAL_HIVE_FILE, "r") as f:
            local_trades = json.load(f) if os.path.getsize(LOCAL_HIVE_FILE) > 0 else []

        with open(REMOTE_NODE_FILE, "r") as f:
            remote_data = json.load(f)
            remote_trades = remote_data.get("trades", [])

        existing = {json.dumps(t, sort_keys=True) for t in local_trades}
        new_trades = [t for t in remote_trades if json.dumps(t, sort_keys=True) not in existing]

        if new_trades:
            local_trades.extend(new_trades)
            with open(LOCAL_HIVE_FILE, "w") as f:
                json.dump(local_trades, f, indent=2)
            print(f"🧠 Merged {len(new_trades)} new trades from remote node.")
        else:
            print("🟡 No new trades to merge from remote node.")

    except Exception as e:
        print(f"❌ Merge failed: {e}")

if __name__ == "__main__":
    merge_hive_memory()
