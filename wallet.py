import json
import os
from datetime import datetime

WALLET_FILE = "wallet.json"
TRADE_LOG = "logs/trade_history.json"

def load_wallet():
    if not os.path.exists(WALLET_FILE):
        return {
            "usd_balance": 100.0,
            "balances": {
                "bitcoin": 0.0,
                "ethereum": 0.0,
                "litecoin": 0.0
            },
            "last_trade_price": 0.0,
            "trade_history": []
        }

    with open(WALLET_FILE, "r") as f:
        return json.load(f)

def save_wallet(wallet):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallet, f, indent=4)

def execute_trade(trade, data):
    wallet = load_wallet()
    coin = data["coin"]
    price = data["price"]

    # Initialize coin entry if it doesn't exist
    if coin not in wallet["balances"]:
        wallet["balances"][coin] = 0.0

    timestamp = data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if trade["action"] == "buy":
        usd_amount = trade["amount"]
        if wallet["usd_balance"] >= usd_amount:
            coin_amount = usd_amount / price
            wallet["usd_balance"] -= usd_amount
            wallet["balances"][coin] += coin_amount
            wallet["last_trade_price"] = price

            wallet["trade_history"].append({
                "timestamp": timestamp,
                "coin": coin,
                "action": "buy",
                "price": price,
                "amount": coin_amount,
                "usd_spent": usd_amount
            })
        else:
            print("❌ Not enough USD balance to buy.")
            return  # Exit early, don't save

    elif trade["action"] == "sell":
        coin_amount = trade["amount"]
        if wallet["balances"].get(coin, 0.0) >= coin_amount:
            usd_gained = coin_amount * price
            wallet["usd_balance"] += usd_gained
            wallet["balances"][coin] -= coin_amount
            wallet["last_trade_price"] = price

            wallet["trade_history"].append({
                "timestamp": timestamp,
                "coin": coin,
                "action": "sell",
                "price": price,
                "amount": coin_amount,
                "usd_gained": usd_gained
            })
        else:
            print("❌ Not enough coin balance to sell.")
            return  # Exit early, don't save

    save_wallet(wallet)
