import random
from datetime import datetime
from config_loader import load_config

def is_trade_allowed(data):
    try:
        config = load_config()
        min_volume = config.get("min_volume", 100000)

        rsi = float(data.get("rsi", 50))
        volume = float(data.get("volume", 0))
        change_24h = float(data.get("change_24h", 0))

        if abs(change_24h) > 15 and not (30 <= rsi <= 70):
            print("⚠️ Skipping high volatility due to uncertain RSI.")
            return False

        if volume < min_volume:
            print("⚠️ Skipping low volume coin.")
            return False

        risk_factor = random.random()
        if -1 < change_24h < 1 and risk_factor < 0.5:
            print("🛑 Skipping stagnant market.")
            return False

        hour = datetime.utcnow().hour
        if 2 <= hour <= 4 and random.random() < 0.4:
            print("🌙 Quiet hours filter triggered. Skipping.")
            return False

        return True

    except Exception as e:
        print(f"❌ Risk check error: {e}")
        return False
