from prediction_engine import load_model, predict_price_movement
from config_loader import load_config

def evaluate_trade(data, sentiment_summary):
    config = load_config()
    strategy = config["strategy"]

    sell_threshold = strategy["sell_rsi_threshold"]
    buy_threshold = strategy["buy_rsi_threshold"]
    sentiment_bias = strategy["sentiment_bias"]

    if sentiment_bias and sentiment_summary:
        sentiment_score = sentiment_summary["positive"] - sentiment_summary["negative"]
        if sentiment_score > 0:
            buy_threshold += 5
        elif sentiment_score < 0:
            sell_threshold -= 5

    model_data = load_model()
    if not model_data:
        print("⚠️ No model available — skipping prediction.")
        return None

    model, scaler = model_data
    price_rising = predict_price_movement(model, scaler, data, sentiment_summary)

    print("📊 Strategy thresholds → Buy RSI <", buy_threshold, "| Sell RSI >", sell_threshold)
    print("🔮 Model says →", "Price Rising ✅" if price_rising else "Not confident ❌")

    if data["rsi"] < buy_threshold and price_rising:
        return {"action": "buy", "amount": config["trade_amount"]}
    elif data["rsi"] > sell_threshold and not price_rising:
        return {"action": "sell", "amount": config["trade_amount"]}

    return None