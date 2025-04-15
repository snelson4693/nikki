from config_loader import load_config, get_personality_profile
from utils.helpers import log_message
from wallet import load_wallet, get_asset_balance
from prediction_engine import load_model, predict_price_movement
from pattern_tracker import was_recent_trade
from datetime import datetime
import math
import random

RSI_BUY_DEFAULT = 30
RSI_SELL_DEFAULT = 70

# ⚙️ Ultra-intelligent trade evaluation logic

def evaluate_trade(data, sentiment):
    symbol = data.get("coin") or data.get("symbol")
    price = data.get("price")
    rsi = float(data.get("rsi", 50))
    confidence = float(data.get("confidence", 0.5))
    volume = data.get("volume", 0)
    change = data.get("change_24h", 0.0)

    config = load_config()
    strategy = config.get("strategy", {})
    min_conf = config.get("settings", {}).get("min_confidence", 0.6)
    min_amt = config.get("settings", {}).get("min_trade_amount", 0.01)
    max_amt = config.get("settings", {}).get("max_trade_amount", 10)

    buy_rsi = strategy.get("buy_rsi_threshold", RSI_BUY_DEFAULT)
    sell_rsi = strategy.get("sell_rsi_threshold", RSI_SELL_DEFAULT)
    bias = strategy.get("sentiment_bias", 0)

    personality = get_personality_profile()
    risk_profile = personality.get("risk_profile", "balanced")

    # 🎭 Adjust thresholds based on personality
    if risk_profile == "aggressive":
        buy_rsi -= 3
        sell_rsi += 3
    elif risk_profile == "cautious":
        buy_rsi += 3
        sell_rsi -= 3

    # 📊 Calculate sentiment influence
    sentiment_score = (sentiment["positive"] - sentiment["negative"] + bias)
    sentiment_total = max(sum(sentiment.values()), 1)
    signal_strength = sentiment_score / sentiment_total

    log_message(f"📊 {symbol.upper()} | RSI: {rsi:.2f} | Sentiment: {signal_strength:.2f} | Confidence: {confidence:.2f} | Δ24h: {change:.2f}%")

    # 🔮 Load and evaluate model prediction
    model_data = load_model()
    if not model_data:
        log_message("⚠️ No model available — skipping prediction.")
        return None

    model, scaler = model_data
    price_rising = predict_price_movement(model, scaler, data, sentiment)

    wallet = load_wallet()
    usd_balance = wallet.get("usd_balance", 0.0)
    asset_balance = get_asset_balance(symbol, wallet)

    # 📈 Factor in volume-based urgency and liquidity
    liquidity_factor = min(2.0, max(volume / 1e6, 0.05))
    urgency = 1.5 if abs(change) > 4 else 1.0

    # 🔁 Avoid redundant trades on recently traded assets
    if was_recent_trade(symbol):
        log_message(f"⏱️ {symbol} was recently traded — skipping to avoid overtrading.")
        return None

    # 🎨 Creative Intelligence Override Check
    creative_signal = creative_override(data, sentiment, confidence)
    if creative_signal:
        log_message(f"🧠 Creative override → {creative_signal['reason']}")
        return creative_signal

    # 💸 Buy condition logic
    if confidence >= min_conf and rsi <= buy_rsi and signal_strength > 0 and price_rising and usd_balance > min_amt:
        smart_amt = max(min_amt, min(max_amt, usd_balance * 0.15 * liquidity_factor * urgency))
        return {
            "action": "buy",
            "amount": round(smart_amt, 2),
            "reason": "📈 Strong buy signal from adaptive strategy"
        }

    # 📉 Sell condition logic
    if asset_balance * price > min_amt:
        if rsi >= sell_rsi and (signal_strength < 0 or not price_rising):
            sell_amt = max(min_amt / price, min(asset_balance, max_amt / price))
            return {
                "action": "sell",
                "amount": round(sell_amt, 6),
                "reason": "📉 Strategy-triggered sell condition met"
            }

        elif not price_rising:
            fallback_amt = min(asset_balance, max_amt / price)
            return {
                "action": "sell",
                "amount": round(fallback_amt, 6),
                "reason": "🛡️ Defensive fallback to prevent unrealized losses"
            }

    return None
def creative_override(data, sentiment, confidence):
    """
    Adds artistic, opponent-style, or emotionally-inspired overrides to Nikki's trade logic.
    This supplements logic in evaluate_trade() with creativity-based decisions.
    """
    symbol = data.get("coin") or data.get("symbol")
    rsi = float(data.get("rsi", 50))
    volume = data.get("volume", 0)
    change = data.get("change_24h", 0.0)

    # 🎭 Recognize unusual behavior (unusual volume + RSI divergence)
    if volume > 10_000_000 and rsi < 35 and change > 3:
        return {
            "action": "buy",
            "amount": round(random.uniform(5, 10), 2),
            "reason": "🎨 Creative: Unusual recovery pattern detected (volume + RSI)"
        }

    # 🔮 Opponent strategy mimicry
    if rsi > 70 and change > 5 and sentiment["positive"] > sentiment["negative"] * 1.5:
        return {
            "action": "sell",
            "amount": round(random.uniform(3, 7), 2),
            "reason": "🎭 Creative: Mimicking likely profit-taking breakout"
        }

    # ❤️ Emotion-inspired trade: sentiment surges
    sentiment_score = sentiment["positive"] - sentiment["negative"]
    if sentiment_score > 5 and confidence > 0.65 and rsi < 40:
        return {
            "action": "buy",
            "amount": round(random.uniform(1.5, 3.5), 2),
            "reason": "💡 Creative: Emotionally driven buy due to high positive sentiment surge"
        }

    return None