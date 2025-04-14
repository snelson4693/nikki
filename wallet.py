import json
import os
import time
from datetime import datetime
from logs.trade_outcome_logger import log_trade_outcome
from data_feed import get_market_data  # ✅ To fetch new price post-trade

WALLET_FILE = "wallet.json"
INFLUENCE_LOG = "logs/influence_log.json"

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

def log_influence(coin, action, pre_price):
    try:
        time.sleep(10)  # 🕒 Wait 10 seconds to simulate short-term market reaction
        new_data = get_market_data(coin)
        if not new_data:
            return

        new_price = float(new_data["price"])
        delta = round(new_price - pre_price, 6)
        percent_change = round((delta / pre_price) * 100, 4) if pre_price else 0

        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "coin": coin,
            "action": action,
            "before_price": pre_price,
            "after_price": new_price,
            "delta": delta,
            "percent_change": percent_change
        }

        os.makedirs("logs", exist_ok=True)

        if os.path.exists(INFLUENCE_LOG):
            with open(INFLUENCE_LOG, "r") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        logs.append(log_entry)
        with open(INFLUENCE_LOG, "w") as f:
            json.dump(logs[-100:], f, indent=2)

        print(f"🌐 Influence logged: {coin.upper()} {action} → Δ {percent_change}%")

    except Exception as e:
        print(f"❌ Influence tracking error: {e}")

def execute_trade(trade, data):
    try:
        wallet = load_wallet()
        coin = data["coin"]
        price = float(data["price"])
        confidence = data.get("confidence", 0)
        rsi = float(data.get("rsi", 50))
        timestamp = data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if coin not in wallet["balances"]:
            wallet["balances"][coin] = 0.0

        emotion = "neutral"

        if trade["action"] == "buy":
            usd_amount = float(trade["amount"])
            if wallet["usd_balance"] >= usd_amount:
                coin_amount = usd_amount / price
                wallet["usd_balance"] -= usd_amount
                wallet["balances"][coin] += coin_amount
                wallet["last_trade_price"] = price
                if confidence > 0.85:
                    emotion = "confident"
                elif rsi > 70:
                    emotion = "nervous"

                wallet["trade_history"].append({
                    "timestamp": timestamp,
                    "coin": coin,
                    "action": "buy",
                    "price": price,
                    "amount": coin_amount,
                    "usd_spent": usd_amount,
                    "emotion": emotion
                })

                log_trade_outcome(coin, "buy", coin_amount, buy_price=price)
                # ✅ Log influence after buy
                log_influence(coin, "buy", price)
            else:
                print("❌ Not enough USD balance to buy.")
                return

        elif trade["action"] == "sell":
            coin_amount = float(trade["amount"])
            if wallet["balances"].get(coin, 0.0) >= coin_amount:
                usd_gained = coin_amount * price
                buy_price = wallet.get("last_trade_price", price)
                profit = usd_gained - (coin_amount * buy_price)

                if profit < 0:
                    emotion = "regret"
                elif confidence > 0.85:
                    emotion = "decisive"

                wallet["usd_balance"] += usd_gained
                wallet["balances"][coin] -= coin_amount
                wallet["last_trade_price"] = price
                wallet["trade_history"].append({
                    "timestamp": timestamp,
                    "coin": coin,
                    "action": "sell",
                    "price": price,
                    "amount": coin_amount,
                    "usd_gained": usd_gained,
                    "emotion": emotion
                })

                log_trade_outcome(coin, "sell", coin_amount, buy_price=buy_price, sell_price=price)
                # ✅ Log influence after sell
                log_influence(coin, "sell", price)
            else:
                print("❌ Not enough coin balance to sell.")
                return

        save_wallet(wallet)

    except Exception as e:
        print(f"❌ Wallet execution error: {e}")
