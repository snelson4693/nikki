import json
import os
from datetime import datetime

PORTFOLIO_FILE = "logs/portfolio.json"

# Default portfolio setup
default_portfolio = {
    "usd_balance": 100.0,
    "balances": {},
    "last_trade_price": {},
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
    coin = market_data['coin']
    action = signal["action"]
    amount_usd = signal["amount"]

    # Initialize balances if not present
    if "balances" not in portfolio:
        portfolio["balances"] = {}
    if coin not in portfolio["balances"]:
        portfolio["balances"][coin] = 0.0

    if action == "buy" and portfolio["usd_balance"] >= amount_usd:
        coin_bought = amount_usd / price
        portfolio["usd_balance"] -= amount_usd
        portfolio["balances"][coin] += coin_bought
        portfolio["last_trade_price"][coin] = price

    elif action == "sell" and portfolio["balances"].get(coin, 0.0) > 0:
        coin_to_sell = min(amount_usd / price, portfolio["balances"][coin])
        usd_gained = coin_to_sell * price
        portfolio["balances"][coin] -= coin_to_sell
        portfolio["usd_balance"] += usd_gained
        portfolio["last_trade_price"][coin] = price

    portfolio["trade_history"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "coin": coin,
        "action": action,
        "price": price,
        "usd_balance": round(portfolio["usd_balance"], 2),
        "coin_balance": round(portfolio["balances"][coin], 6)
    })

    save_portfolio(portfolio)
    return portfolio
