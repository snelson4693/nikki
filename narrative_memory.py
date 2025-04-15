import threading
import time
from datetime import datetime
import os
import json
from data_feed import get_market_data
from sentiment import summarize_sentiments, get_global_sentiment
from prediction_engine import predict_price_movement
from trade_engine import evaluate_trade
from risk_manager import is_trade_allowed
from utils.helpers import log_message, adaptive_sleep
from news_feed import get_headlines
from self_reflection import reflect_on_decision
from self_feedback import evaluate_performance, load_trade_log
from config_loader import get_personality_profile
from portfolio import load_portfolio

NARRATIVE_LOG = "logs/narrative_memory.json"

def log_narrative(entry):
    os.makedirs("logs", exist_ok=True)
    if os.path.exists(NARRATIVE_LOG):
        with open(NARRATIVE_LOG, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []
    logs.append(entry)
    with open(NARRATIVE_LOG, "w") as f:
        json.dump(logs[-200:], f, indent=2)

def detect_asset_type(symbol):
    if symbol.isalpha() and symbol.upper() == symbol and len(symbol) <= 5:
        return "stock"
    return "crypto"

def schedule_tasks(model, scaler, coins):
    log_message("📅 Narrative scheduler thread started.")
    while True:
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{now}] 🧠 Nikki is evaluating narrative context...")

            personality = get_personality_profile()
            narrative_style = personality.get("response_style", "professional")

            narrative = {
                "timestamp": now,
                "style": narrative_style,
                "events": []
            }

            for coin in coins:
                asset_type = detect_asset_type(coin)
                data = get_market_data(coin, asset_type=asset_type)
                if not data:
                    narrative["events"].append(f"No data for {coin}.")
                    continue

                if not is_trade_allowed(data):
                    narrative["events"].append(f"Trade blocked for {coin} due to risk profile.")
                    continue

                headlines = get_headlines(coin)
                coin_sentiment = summarize_sentiments(headlines["headlines"])
                global_sentiment = get_global_sentiment()

                sentiment = {
                    "positive": coin_sentiment["positive"] + global_sentiment["positive"],
                    "negative": coin_sentiment["negative"] + global_sentiment["negative"],
                    "neutral": coin_sentiment["neutral"] + global_sentiment["neutral"]
                }

                confident = predict_price_movement(model, scaler, data, sentiment)

                if confident:
                    signal = evaluate_trade(data, sentiment)
                    if signal:
                        msg = f"⚡ Nikki felt a confident urge to {signal['action']} {coin} based on price ${data['price']:.2f} and market tone."
                        log_message(msg)
                        narrative["events"].append(msg)
                    else:
                        narrative["events"].append(f"Confident prediction on {coin}, but no trade action met conditions.")
                else:
                    narrative["events"].append(f"Low confidence in prediction for {coin}. No action taken.")

            trades = load_trade_log()
            performance = evaluate_performance(trades)
            if performance:
                avg = performance['average_profit']
                total = performance['total_trades']
                narrative["performance"] = {
                    "summary": f"Nikki has made {total} successful trades with an average profit of {avg:.4f}.",
                    "insight": "Performance steady." if avg > 0 else "Performance may need recalibration."
                }
                reflect_on_decision("narrative_memory", narrative["performance"]["summary"], narrative["performance"]["insight"])
            else:
                narrative["performance"] = {"summary": "No trades to evaluate."}

            log_narrative(narrative)

        except Exception as e:
            log_message(f"❌ Narrative task error: {e}")

        time.sleep(180)  # Every 3 minutes

if __name__ == "__main__":
    from prediction_engine import load_model
    with open("active_coins.json", "r") as f:
        coins = json.load(f)
    model, scaler = load_model()
    schedule_tasks(model, scaler, coins)
