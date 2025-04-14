import os
import json
from datetime import datetime

WALLET_FILE = "wallet.json"
HIVE_TRADE_LOG = "logs/hive_trades.json"

def export_trade_history_to_hive():
    if not os.path.exists(WALLET_FILE):
        print("⚠️ No wallet file found to extract history.")
        return

    try:
        with open(WALLET_FILE, "r") as f:
            wallet = json.load(f)
        trade_history = wallet.get("trade_history", [])

        if not trade_history:
            print("📭 No trade history found in wallet.")
            return

        hive_entries = []
        for trade in trade_history:
            hive_entries.append({
                "timestamp": trade.get("timestamp"),
                "coin": trade.get("coin"),
                "action": trade.get("action"),
                "price": trade.get("price"),
                "amount": trade.get("amount"),
                "emotion": trade.get("emotion", "neutral")
            })

        os.makedirs("logs", exist_ok=True)
        with open(HIVE_TRADE_LOG, "w") as f:
            json.dump(hive_entries, f, indent=2)

        print(f"🐝 Hive trade log exported to {HIVE_TRADE_LOG} ({len(hive_entries)} trades).")

    except Exception as e:
        print(f"❌ Failed to export hive memory: {e}")

if __name__ == "__main__":
    export_trade_history_to_hive()
