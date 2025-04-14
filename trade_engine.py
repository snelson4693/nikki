from prediction_engine import load_model, predict_price_movement
from config_loader import load_config, get_personality_profile

def evaluate_trade(data, sentiment_summary):
    try:
        config = load_config()
        strategy = config["strategy"]
        personality = get_personality_profile()

        sell_threshold = float(strategy["sell_rsi_threshold"])
        buy_threshold = float(strategy["buy_rsi_threshold"])
        sentiment_bias = strategy.get("sentiment_bias", 0)

        if sentiment_bias and sentiment_summary:
            sentiment_score = sentiment_summary["positive"] - sentiment_summary["negative"]
            total = sum(sentiment_summary.values())
            if total > 0:
                mood_ratio = sentiment_score / total

                if mood_ratio > 0.4:
                    buy_threshold -= 2
                    sell_threshold += 2
                    print("🌍 Global optimism detected → Nikki is more assertive.")
                elif mood_ratio < -0.4:
                    buy_threshold += 3
                    sell_threshold -= 3
                    print("🌍 Global pessimism detected → Nikki becomes cautious.")


        # 🔧 Apply personality risk bias
        if personality["risk_profile"] == "aggressive":
            buy_threshold += -2
            sell_threshold += 2
        elif personality["risk_profile"] == "cautious":
            buy_threshold += 3
            sell_threshold -= 3

        model_data = load_model()
        if not model_data:
            print("⚠️ No model available — skipping prediction.")
            return None

        model, scaler = model_data
        price_rising = predict_price_movement(model, scaler, data, sentiment_summary)

        # 🧠 Style confidence message based on tone
        confidence = round(data.get("confidence", 0), 3)
        tone = personality["confidence_tone"]
        if tone == "assertive":
            print(f"🧠 Nikki is certain → Confidence: {confidence}")
        elif tone == "cautious":
            print(f"🔍 Nikki is cautiously optimistic → Confidence: {confidence}")
        else:
            print(f"📈 Nikki's confidence: {confidence}")

        print("📊 Strategy thresholds → Buy RSI <", buy_threshold, "| Sell RSI >", sell_threshold)
        print("🔮 Model says →", "Price Rising ✅" if price_rising else "Not confident ❌")

        trade_amount = config.get("trade_amount", 10)

        try:
            rsi_value = float(data.get("rsi", 50))
        except (ValueError, TypeError):
            print(f"❌ Invalid RSI value → {data.get('rsi')} — skipping trade.")
            return None

        if rsi_value < buy_threshold and price_rising:
            return {"action": "buy", "amount": trade_amount}
        elif rsi_value > sell_threshold and not price_rising:
            return {"action": "sell", "amount": trade_amount}

        return None

    except Exception as e:
        print(f"❌ Trade evaluation error: {e}")
        return None
