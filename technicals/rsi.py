import pandas as pd
import numpy as np

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50  # neutral if not enough data

    prices = pd.Series(prices)
    delta = prices.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean().iloc[-1]
    avg_loss = loss.rolling(window=period, min_periods=period).mean().iloc[-1]

    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
