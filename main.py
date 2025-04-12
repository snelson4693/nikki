import time
import random
import json
import os
from datetime import datetime, timedelta

from data_feed import get_market_data
from trade_engine import evaluate_trade
from risk_manager import is_trade_allowed
from wallet import execute_trade, load_wallet
from utils.helpers import log_trade, log_message, adaptive_sleep
from portfolio import load_portfolio
from news_feed import get_headlines
from sentiment import summarize_sentiments
from pattern_tracker import save_market_snapshot
from prediction_engine import load_model, predict_price_movement
from smart_screener import run_screener
from strategy_optimizer import analyze_patterns  # 🧠 New import

LAST_SCREENED = None
SCREEN_INTERVAL_MINUTES = 30
MIN_USD_THRESHOLD = 10.0  # Don't buy if below this

def refresh_coin_list():
    global LAST_SCREENED
    if not LAST_SCREENED or (datetime.now() - LAST_SCREENED) > timedelta(minutes=SCREEN_INTERVAL_MINUTES):
        log_message("🔁 Refreshing screener list...")
        run_screener()
        LAST_SCREENED = datetime.now()
        time.sleep(random.uniform(3.0, 5.0))  # 3–5s delay to be polite to APIs

def main():
    log_message("🚀 Nikki is starting...")

    os.system("git -C model pull")
    os.system("copy model\\model.pkl brain_repo\\model.pkl >nul 2>&1")
    os.system("copy model\\scaler.pkl brain_repo\\scaler.pkl >nul 2>&1")
    log_message("✅ Brain synced.")

    refresh_coin_list()

    # 🧠 Self-learn from past patterns before making trades
    analyze_patterns()

    try:
        with open("active_coins.json", "r") as f:
            coins_to_trade = json.load(f)
    except:
        coins_to_trade = ["bitcoin"]

    model, scaler = load_model()

    for coin in coins_to_trade:
        data = get_market_data(coin)
        wallet = load_wallet()
        usd_balance = wallet.get("usd_balance", 0)
        if not data:
            log_message(f"❌ Failed to fetch data for {coin}")
            continue

        data["coin"] = coin  # Ensure coin name is included in log
        log_message(f"📡 Market data for {coin.upper()}: ${data['price']} | Vol: {data['volume']} | 24h: {data['change_24h']}%")

        if not is_trade_allowed(data):
            log_message("⚠️ Risk conditions not met. Trade skipped.")
            log_trade(data, None, status="risk_blocked")
            adaptive_sleep(coin)
            continue

        headlines_data = get_headlines(coin)
        sentiment_summary = summarize_sentiments(headlines_data["headlines"])

        confident = predict_price_movement(model, scaler, data, sentiment_summary)
        if not confident:
            log_message(f"🔮 Model says → Not confident ❌")
            log_message(f"🟡 No strong trade signal for {coin.upper()}.")
            log_trade(data, None, status="no_signal")
            adaptive_sleep(coin)
            continue

        log_message(f"🔮 Model says → Confident ✅")
        trade_signal = evaluate_trade(data, sentiment_summary)

        if not trade_signal:
            log_message(f"🟡 No strong trade signal for {coin.upper()}.")
            log_trade(data, None, status="no_signal")
            adaptive_sleep(coin)
            continue

        if trade_signal["action"] == "buy" and usd_balance < MIN_USD_THRESHOLD:
            log_message(f"💰 USD balance too low (${usd_balance:.2f}). Skipping buy and looking to sell.")
            log_trade(data, None, status="insufficient_funds")
            adaptive_sleep(coin)
            continue

        log_message(f"📈 Trade signal: {trade_signal['action']} ${trade_signal['amount']}")
        execute_trade(trade_signal, data)
        log_trade(data, trade_signal, status="executed")

        save_market_snapshot(data, sentiment_summary, trade_signal)
        wallet = load_wallet()
        usd_balance = wallet.get("usd_balance", 0)

        adaptive_sleep(coin)

    portfolio = load_portfolio()
    print(portfolio)

while True:
    if __name__ == "__main__":
        main()
