import os
import json
import threading
import time
from datetime import datetime
from data_feed import get_market_data
from sentiment import summarize_sentiments, get_global_sentiment
from prediction_engine import predict_price_movement
from trade_engine import evaluate_trade
from risk_manager import is_trade_allowed
from utils.helpers import log_message, adaptive_sleep
from news_feed import get_headlines

JOURNAL_LOG = "logs/reflective_journal.json"

def detect_asset_type(symbol):
    """Infer asset type from symbol name."""
    if symbol.isalpha() and symbol.upper() == symbol and len(symbol) <= 5:
        return "stock"
    return "crypto"

def schedule_tasks(model, scaler, coins):
    log_message("📅 Task scheduler thread started.")
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Nikki is evaluating trade urgency...")

            high_priority = False

            for coin in coins:
                asset_type = detect_asset_type(coin)
                data = get_market_data(coin, asset_type=asset_type)
                if not data or not is_trade_allowed(data):
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
                        high_priority = True
                        log_message(f"⚡ Trade signal found for {coin}: {signal['action']}")
                        break

            if high_priority:
                log_message("⚡ Prioritizing trade execution based on signal.")
            else:
                log_message("📊 No urgent signals found. Background tasks continue as normal.")

        except Exception as e:
            log_message(f"❌ Error during scheduling logic: {e}")

        time.sleep(120)  # Evaluate every 2 minutes

def log_reflection(source, message, signal=None, sentiment=None, confidence=0.0, executed=False, insight=None):
    os.makedirs("logs", exist_ok=True)

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "message": message,
        "insight": insight or "none",
        "signal": signal,
        "sentiment": sentiment,
        "confidence": confidence,
        "executed": executed
    }

    if os.path.exists(JOURNAL_LOG):
        try:
            with open(JOURNAL_LOG, "r") as f:
                journal = json.load(f)
        except json.JSONDecodeError:
            journal = []
    else:
        journal = []

    journal.append(entry)

    with open(JOURNAL_LOG, "w") as f:
        json.dump(journal[-200:], f, indent=2)

    print(f"📘 Reflection added from {source}: {message}")
