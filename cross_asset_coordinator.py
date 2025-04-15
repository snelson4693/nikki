import time
from data_feed import get_market_data
from wallet import load_wallet, execute_trade, get_asset_balance
from config_loader import load_config, update_strategy
from utils.helpers import log_message

DEFAULT_MIN_PROFIT_THRESHOLD = 0.25
DEFAULT_ADAPTIVE_WINDOW = 7
DEFAULT_CONFIDENCE_MARGIN = 1.1

def detect_asset_type(symbol):
    return "crypto" if symbol.lower() in ["bitcoin", "ethereum", "solana", "bnb"] else "stock"

def evaluate_opportunity(asset_from, asset_to, threshold, confidence_margin):
    from_type = detect_asset_type(asset_from)
    to_type = detect_asset_type(asset_to)

    from_data = get_market_data(asset_from, asset_type=from_type)
    to_data = get_market_data(asset_to, asset_type=to_type)

    if not from_data or not to_data:
        return None

    from_price = from_data["price"]
    to_price = to_data["price"]
    from_change = from_data.get("change_24h", 0)
    to_change = to_data.get("change_24h", 0)

    projected_diff = (to_change - from_change) * confidence_margin
    potential_gain = projected_diff * to_price / 100

    log_message(f"🔀 Evaluating {asset_from} → {asset_to} | ΔProjected Gain: ${potential_gain:.4f}")

    if potential_gain > threshold:
        return {
            "from": asset_from,
            "to": asset_to,
            "gain": potential_gain,
            "timestamp": time.time(),
            "confidence": confidence_margin,
            "rsi_from": from_data.get("rsi"),
            "rsi_to": to_data.get("rsi")
        }

    return None

def auto_adjust_threshold(history):
    if len(history) < DEFAULT_ADAPTIVE_WINDOW:
        return DEFAULT_MIN_PROFIT_THRESHOLD

    recent = history[-DEFAULT_ADAPTIVE_WINDOW:]
    avg_gain = sum(recent) / len(recent)
    adjusted = max(0.05, min(2.0, avg_gain * 0.85))
    return round(adjusted, 4)

def auto_adjust_confidence_margin(history):
    if not history:
        return DEFAULT_CONFIDENCE_MARGIN

    volatility = max(history) - min(history)
    margin = 1.0 + min(0.5, volatility / 100)
    return round(margin, 4)

def adjust_asset_scope(history):
    if not history:
        return ["bitcoin", "ethereum", "solana"], ["AAPL", "TSLA", "NVDA"]

    average_gain = sum(history[-DEFAULT_ADAPTIVE_WINDOW:]) / len(history[-DEFAULT_ADAPTIVE_WINDOW:])
    if average_gain > 1:
        return ["bitcoin", "ethereum", "solana", "bnb"], ["AAPL", "TSLA", "NVDA", "MSFT"]
    return ["bitcoin", "ethereum"], ["AAPL", "TSLA"]

def smart_asset_rotation():
    config = load_config()
    wallet = load_wallet()
    history = config.get("strategy", {}).get("profit_rotation_log", [])
    min_profit_threshold = auto_adjust_threshold(history)
    confidence_margin = auto_adjust_confidence_margin(history)

    cryptos, stocks = adjust_asset_scope(history)
    all_assets = cryptos + stocks

    trade_candidates = []
    for from_asset in all_assets:
        balance = get_asset_balance(from_asset, wallet)
        if balance <= 0:
            continue

        for to_asset in all_assets:
            if from_asset == to_asset:
                continue

            opportunity = evaluate_opportunity(from_asset, to_asset, min_profit_threshold, confidence_margin)
            if opportunity:
                opportunity["balance"] = balance
                trade_candidates.append(opportunity)

    trade_candidates.sort(key=lambda x: x["gain"], reverse=True)

    for candidate in trade_candidates:
        from_asset = candidate["from"]
        to_asset = candidate["to"]
        balance = candidate["balance"]
        gain = candidate["gain"]

        from_type = detect_asset_type(from_asset)
        to_type = detect_asset_type(to_asset)

        from_data = get_market_data(from_asset, asset_type=from_type)
        from_price = from_data["price"]
        usd_value = balance * from_price

        execute_trade({
            "action": "sell",
            "amount": round(balance, 6),
            "symbol": from_asset
        }, from_data)

        to_data = get_market_data(to_asset, asset_type=to_type)
        to_price = to_data["price"]
        to_amount = usd_value / to_price

        execute_trade({
            "action": "buy",
            "amount": round(to_amount, 6),
            "symbol": to_asset
        }, to_data)

        log_message(f"💱 Rebalanced: Sold {balance:.6f} {from_asset} → Bought {to_amount:.6f} {to_asset}")

        history.append(gain)
        update_strategy({"profit_rotation_log": history[-DEFAULT_ADAPTIVE_WINDOW * 2:]})

        break

def cross_asset_coordinator_loop():
    while True:
        try:
            smart_asset_rotation()
        except Exception as e:
            log_message(f"❌ Cross-asset coordinator error: {e}")
        time.sleep(600)

