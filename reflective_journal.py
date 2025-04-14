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

def schedule_tasks(model, scaler, coins):
    log_message("📅 Task scheduler thread started.")
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Nikki is evaluating trade urgency...")

            high_priority = False

            for coin in coins:
                data = get_market_data(coin)
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
