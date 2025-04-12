import json
import os
from datetime import datetime

PORTFOLIO_FILE = "logs/portfolio.json"

# Default portfolio setup
default_portfolio = {
    "usd_balance": 100.0,     # Starting with $100
    "btc_balance": 0.0,
    "last_trade_price": 0.0,
    "trade_history": []
}

def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        save_portfolio(default_portfolio)
    with open(PORTFOLIO_FILE, "r") as f:
        return json.load(f)

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=4)

def execute_paper_trade(signal, market_data):
    portfolio = load_portfolio()
    price = market_data['price']
    action = signal["action"]
    amount_usd = signal["amount"]

    if action == "buy" and portfolio["usd_balance"] >= amount_usd:
        btc_bought = amount_usd / price
        portfolio["usd_balance"] -= amount_usd
        portfolio["btc_balance"] += btc_bought
        portfolio["last_trade_price"] = price

    elif action == "sell" and portfolio["btc_balance"] > 0:
        btc_to_sell = min(amount_usd / price, portfolio["btc_balance"])
        usd_gained = btc_to_sell * price
        portfolio["btc_balance"] -= btc_to_sell
        portfolio["usd_balance"] += usd_gained
        portfolio["last_trade_price"] = price

    portfolio["trade_history"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "price": price,
        "usd": round(portfolio["usd_balance"], 2),
        "btc": round(portfolio["btc_balance"], 6)
    })

    save_portfolio(portfolio)
    return portfolio
