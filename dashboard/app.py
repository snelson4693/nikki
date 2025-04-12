import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from flask import Flask, render_template, request,jsonify
from wallet import load_wallet
from config_loader import load_config
from pattern_tracker import save_market_snapshot
import json

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    wallet = load_wallet()
    config = load_config()
    usd_balance = wallet.get("usd_balance", 0)
    balances = wallet.get("balances", {})
    trade_amount = config["strategy"].get("trade_amount", 10)

    total_value = usd_balance  # you could expand to add BTC x price, etc.

    user_message = ""
    response = ""

    if request.method == "POST":
        user_message = request.form.get("user_message")
        response = generate_response(user_message)

    return render_template(
        "dashboard.html",
        usd_balance=usd_balance,
        balances=balances,
        trade_amount=trade_amount,
        total_value=round(total_value, 2),
        user_message=user_message,
        response=response
    )
def generate_response(user_message):
    """Basic rule-based response engine"""
    if not user_message:
        return "Sorry, I didn't catch that."

    message = user_message.lower()
    if "balance" in message:
        return f"Your current USD balance is ${load_wallet().get('usd_balance', 0):.2f}."
    elif "holdings" in message or "coins" in message:
        wallet = load_wallet()
        return "You're holding: " + ", ".join(f"{k}: {v}" for k, v in wallet.get("balances", {}).items() if v > 0)
    elif "profit" in message or "portfolio" in message:
        from portfolio import load_portfolio
        p = load_portfolio()
        return f"Total portfolio value is ${p.get('usd_balance', 0) + p.get('btc_balance', 0) * 85000:.2f}"  # assume BTC for example
    elif "hi" in message or "hello" in message:
        return "Hi! I’m Nikki, your autonomous crypto AI assistant. How can I help today?"
    elif "help" in message:
        return "You can ask me about your balance, holdings, portfolio, or say hello!"
    else:
        return "I'm still learning — try asking me about your balance or portfolio!"
@app.route('/api/wallet')
def get_wallet():
    wallet = load_wallet()
    return jsonify(wallet)

@app.route('/api/config')
def get_config():
    config = load_config()
    return jsonify(config)

@app.route('/api/trade-history')
def get_trade_history():
    try:
        with open("wallet.json", "r") as f:
            data = json.load(f)
        return jsonify(data.get("trade_history", []))
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/logs')
def get_logs():
    try:
        with open("logs/pattern_learning.json", "r") as f:
            data = json.load(f)
        return jsonify(data[-20:])  # Send last 20 pattern logs
    except Exception as e:
        return jsonify({"error": str(e)})
if __name__ == "__main__":
    app.run(debug=True, port=5000)
