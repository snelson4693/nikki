import json
import os
from datetime import datetime

LOCAL_HIVE_FILE = "logs/hive_trades.json"
REMOTE_NODE_FILE = "logs/remote_node.json"

def simulate_node_relay():
    if not os.path.exists(LOCAL_HIVE_FILE):
        print("⚠️ Local hive memory not found.")
        return

    try:
        with open(LOCAL_HIVE_FILE, "r") as f:
            local_trades = json.load(f)

        os.makedirs("logs", exist_ok=True)
        relay_packet = {
            "node_id": "nikki_pi_node_001",
            "sync_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "trades": local_trades
        }

        with open(REMOTE_NODE_FILE, "w") as f:
            json.dump(relay_packet, f, indent=2)

        print(f"📡 Nikki successfully relayed {len(local_trades)} trades to remote node!")

    except Exception as e:
        print(f"❌ Node relay failed: {e}")

if __name__ == "__main__":
    simulate_node_relay()
