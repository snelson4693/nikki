def evaluate_trade(data):
    print("📈 Evaluating trade signal...")
    # Very basic logic
    if data["rsi"] < 30:
        return {"action": "buy", "amount": 10}
    elif data["rsi"] > 70:
        return {"action": "sell", "amount": 10}
    return None
