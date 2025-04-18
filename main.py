import time
import random
import json
import os
from datetime import datetime, timedelta
import threading
import subprocess
from auto_calibration import auto_calibrate_strategy
from data_feed import get_market_data
from trade_engine import evaluate_trade
from risk_manager import is_trade_allowed
from wallet import execute_trade, load_wallet
from utils.helpers import log_trade, log_message, adaptive_sleep, log_error
from portfolio import load_portfolio
from news_feed import get_headlines
from sentiment import summarize_sentiments
from pattern_tracker import save_market_snapshot
from prediction_engine import load_model, predict_price_movement
from smart_screener import run_screener
from strategy_optimizer import analyze_patterns
from config_loader import load_config
from model_mutator import retrain_model
from model_manager import should_retrain_model, update_model_history
from prediction_engine import train_and_save_model
from prediction_feedback import record_prediction_result
from config_loader import get_personality_profile
from sentiment import get_global_sentiment, log_global_sentiment 
from influencer_tracker import track_influencer_sentiment
from macro_tracker import log_macro_news
from reflective_journal import log_reflection
from self_reflection import reflect_on_decision
from self_feedback import load_trade_log, evaluate_performance
import shutil
from self_debugger import SelfDebugger
from self_patch import self_patch_loop
from device_identity import get_instance_id
from sync_utils import pull_latest_brain, push_brain_update
from log_merge_wiring import run_full_log_merge
from model_fusion import fuse_models
from wire_multi_source import start_multi_source_thread
from cross_asset_coordinator import cross_asset_coordinator_loop











LAST_SCREENED = None
SCREEN_INTERVAL_MINUTES = 30
MIN_USD_THRESHOLD = 10.0

def schedule_tasks(model, scaler, coins):
    log_message("📅 Task scheduler thread started.")
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Nikki is evaluating trade urgency...")

            high_priority = False
            observations = []

            for coin in coins:
                if coin.isupper():  # crude but works: assume all-uppercase means stock symbol
                    data = get_market_data(coin, asset_type="stock")
                else:
                    data = get_market_data(coin, asset_type="crypto")

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
                        observation = f"Urgent trade signal for {coin} detected → {signal['action']}"
                        observations.append(observation)
                        log_message(f"⚡ {observation}")
                        break

            if high_priority:
                reflect_on_decision(
                    context="Autonomous Task Scheduling",
                    observation="\n".join(observations),
                    suggestion="Prioritize trade threads for detected coins."
                )
            else:
                reflect_on_decision(
                    context="Autonomous Task Scheduling",
                    observation="No urgent signals detected during this evaluation cycle."
                )

            # Evaluate Nikki's trade performance and reflect
            trades = load_trade_log()
            performance = evaluate_performance(trades)
            if performance:
                reflect_on_decision(
                    context="Trade Performance",
                    observation=f"Average profit per trade: {performance['average_profit']:.4f}",
                    suggestion="Review risk thresholds if profit remains flat."
                )

        except Exception as e:
            log_message(f"❌ Error during scheduling logic: {e}")

        time.sleep(120)  # Evaluate every 2 minutes

def refresh_coin_list():
    global LAST_SCREENED
    if not LAST_SCREENED or (datetime.now() - LAST_SCREENED) > timedelta(minutes=SCREEN_INTERVAL_MINUTES):
        log_message("🔁 Refreshing screener list...")
        run_screener()
        LAST_SCREENED = datetime.now()
        time.sleep(random.uniform(3.0, 5.0))

def auto_sync_repos():
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔁 Auto-syncing Nikki's brain...")
            subprocess.run(["python", "brain_sync.py"], check=True)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Brain synced.")

            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔁 Auto-syncing Nikki's code...")
            subprocess.run(["python", "github_sync.py"], check=True)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Code synced.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Auto-sync error: {e}")
        time.sleep(1800)

def continuous_self_training():
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Continuous self-training started...")
        analyze_patterns()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Self-training complete.")
        time.sleep(150)

def trade_worker(coin, model, scaler):
    while True:
        try:
            if coin.isupper():  # crude but works: assume all-uppercase means stock symbol
                data = get_market_data(coin, asset_type="stock")
            else:
                data = get_market_data(coin, asset_type="crypto")

            if not data:
                log_message(f"❌ Failed to fetch data for {coin}")
                adaptive_sleep(coin)
                continue

            data["coin"] = coin
            log_message(f"📡 {coin.upper()}: ${data['price']} | Vol: {data['volume']} | 24h: {data['change_24h']}%")

            if not is_trade_allowed(data):
                log_message("⚠️ Risk conditions not met.")
                log_trade(data, None, status="risk_blocked")
                log_reflection(coin, data, None, {}, 0, executed=False)
                adaptive_sleep(coin)
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
            if not confident:
                log_message(f"🔮 Model says → Not confident ❌")
                log_trade(data, None, status="no_signal")
                log_reflection(coin, data, None, sentiment, data.get("confidence", 0), executed=False)
                adaptive_sleep(coin)
                continue

            log_message(f"🔮 Model says → Confident ✅")
            signal = evaluate_trade(data, sentiment)
            wallet = load_wallet()
            usd = wallet.get("usd_balance", 0)

            if not signal:
                log_message("🟡 No trade signal.")
                log_trade(data, None, status="no_signal")
                log_reflection(coin, data, signal, sentiment, data.get("confidence", 0), executed=False)
                adaptive_sleep(coin)
                continue

            # 🧠 Real-time prediction feedback logging (AFTER signal is known)
            expected = signal["action"]
            actual = "buy" if signal["action"] == "buy" else "sell"
            was_correct = expected == actual
            record_prediction_result(coin, was_correct, data.get("confidence", 0), expected, actual)

            if signal["action"] == "buy" and usd < MIN_USD_THRESHOLD:
                log_message(f"💰 Not enough USD (${usd:.2f}) to buy.")
                log_trade(data, None, status="insufficient_funds")
                log_reflection(coin, data, signal, sentiment, data.get("confidence", 0), executed=False)
                adaptive_sleep(coin)
                continue

            log_message(f"📈 Trade signal: {signal['action']} ${signal['amount']}")
            execute_trade(signal, data)
            log_trade(data, signal, status="executed")
            log_reflection(coin, data, signal, sentiment, data.get("confidence", 0), executed=True)
            save_market_snapshot(data, sentiment, signal)

            # 🔁 Train brain in background after each trade
            threading.Thread(target=lambda: os.system("python train_model_from_memory.py"), daemon=True).start()

        except Exception as e:
            log_message(f"❌ Error in thread for {coin}: {e}")
            log_error(str(e), context=f"trade_worker:{coin}")

        adaptive_sleep(coin)
def continuous_replay_testing():
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Running strategy replay test...")
        subprocess.run(["python", "replay_test.py"])
        time.sleep(150)
def auto_calibration_loop():
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Auto-calibrating strategy from simulation insights...")
        auto_calibrate_strategy()
        time.sleep(300)  # every 5 minutes
def brain_mutation_loop():
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔁 Attempting self-mutation...")
        retrain_model()
        time.sleep(3600)  # every hour
def mutation_thread():
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔁 Running mutation check...")
        try:
            from mutation_engine import mutate_strategy
            mutate_strategy()
        except Exception as e:
            print(f"❌ Mutation thread error: {e}")
        time.sleep(300)  # Every 5 minutes
def continuous_replay_testing():
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Running replay accuracy test...")
            subprocess.run(["python", "replay_test.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Replay accuracy test failed: {e}")
        time.sleep(300)  # Run every 5 minutes
def continuous_brain_training():
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Retraining Nikki's brain from memory...")
            subprocess.run(["python", "train_model_from_memory.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Brain training error: {e}")
        time.sleep(600)  # every 10 minutes
def simulated_clone_loop():
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧪 Running clone simulation...")
            subprocess.run(["python", "clone_engine.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Clone simulation error: {e}")
        time.sleep(600)  # every 10 minutes
def global_sentiment_loop():
    while True:
        log_global_sentiment()
        time.sleep(900)  # Every 15 minutes
def influencer_sentiment_loop():
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Scanning influencer sentiment...")
            track_influencer_sentiment()
        except Exception as e:
            log_error(str(e), context="influencer_sentiment_loop")
        time.sleep(900)  # every 15 minutes
def macro_insight_loop():
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌍 Pulling macroeconomic data...")
            log_macro_news()
        except Exception as e:
            print(f"❌ Macro loop error: {e}")
        time.sleep(3600)  # Once per hour
def model_fusion_loop():
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧬 Running model fusion...")
            fuse_models()
        except Exception as e:
            print(f"❌ Model fusion error: {e}")
        time.sleep(1800)  # Every 30 minutes

def main():
    personality = get_personality_profile()
    style = personality.get("response_style", "professional")

    if style == "playful":
        log_message("💃 Nikki's clocked in and ready to move markets!")
    elif style == "serious":
        log_message("🔒 Initializing Nikki AI Trading Core...")
    else:
        log_message("🚀 Nikki is starting...")
        pull_latest_brain()
        log_message("🧠 Pulled latest brain from GitHub.")

    # 🔁 Merge logs across devices before loading brain
    run_full_log_merge()


    os.system("git -C model pull")
    shutil.copy("model/model.pkl", "brain_repo/model.pkl")
    shutil.copy("model/scaler.pkl", "brain_repo/scaler.pkl")
    log_message("✅ Brain synced.")
    try:
        with open("active_coins.json", "r") as f:
            coins = json.load(f)
    except:
        coins = ["bitcoin", "ethereum", "litecoin"]
    try:
        model, scaler = load_model()
        if model is None or scaler is None:
            raise ValueError("🚨 Model or scaler is not loaded correctly.")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return  # prevent running if model fails
    

    
    scheduling_thread = threading.Thread(target=schedule_tasks, args=(model, scaler, coins), daemon=True)
    scheduling_thread.start()

    sync_thread = threading.Thread(target=auto_sync_repos, daemon=True)
    sync_thread.start()

    training_thread = threading.Thread(target=continuous_self_training, daemon=True)
    training_thread.start()

    replay_thread = threading.Thread(target=continuous_replay_testing, daemon=True)
    replay_thread.start()

    calibration_thread = threading.Thread(target=auto_calibration_loop, daemon=True)
    calibration_thread.start()

    # Start the thread for brain mutation logic
    brain_mutation_thread = threading.Thread(target=brain_mutation_loop, daemon=True)
    brain_mutation_thread.start()

    # Start the thread for the mutation engine
    mutation_engine_thread = threading.Thread(target=mutation_thread, daemon=True)
    mutation_engine_thread.start()



    # Replay-based accuracy tuning
    replay_thread = threading.Thread(target=continuous_replay_testing, daemon=True)
    replay_thread.start()

    # Live brain training thread
    brain_train_thread = threading.Thread(target=continuous_brain_training, daemon=True)
    brain_train_thread.start()
    
    fusion_thread = threading.Thread(target=model_fusion_loop, daemon=True)
    fusion_thread.start()

    
    # Clone simulation thread
    clone_sim_thread = threading.Thread(target=simulated_clone_loop, daemon=True)
    clone_sim_thread.start()

    global_sentiment_thread = threading.Thread(target=global_sentiment_loop, daemon=True)
    global_sentiment_thread.start()

    # Influencer sentiment thread
    influencer_thread = threading.Thread(target=influencer_sentiment_loop, daemon=True)
    influencer_thread.start()
    
    macro_thread = threading.Thread(target=macro_insight_loop, daemon=True)
    macro_thread.start()

    # Start self-patching engine in the background
    threading.Thread(target=self_patch_loop, daemon=True).start()
 

    cross_asset_coordinator_loop()
    start_multi_source_thread()



    
    analyze_patterns()
    # Auto-retrain model if needed
    if should_retrain_model():
        train_and_save_model()
        update_model_history()
    





    for coin in coins:
        thread = threading.Thread(target=trade_worker, args=(coin, model, scaler), daemon=True)
        thread.start()
        time.sleep(1.5)
    push_brain_update()
    log_message("🧠 Pushed brain update from this instance.")

    while True:
        time.sleep(60)

if __name__ == "__main__":
    SelfDebugger()
    main()
    refresh_coin_list()
