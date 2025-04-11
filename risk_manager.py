def is_trade_allowed(data):
    print("🛡️ Running risk checks...")
    # Dummy rule: Only allow trades with high volume
    return data["volume"] > 100000
