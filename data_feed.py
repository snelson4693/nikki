import requests
import time
import random
from utils.helpers import log_message
from pattern_tracker import save_market_snapshot  # Nikki learns from this

COINCAP_URL = "https://api.coincap.io/v2/assets/{}"
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
FINNHUB_API_KEY = "cvva24pr01qi0bq3ulagcvva24pr01qi0bq3ulb0"
FINNHUB_URL = f"https://finnhub.io/api/v1/quote?symbol={{}}&token={FINNHUB_API_KEY}"
YAHOO_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={}"
RSI_HISTORY = {}  # In-memory tracker for RSI history
RSI_PERIOD = 14  # RSI period window

# Known crypto identifiers
KNOWN_CRYPTO = {
    "bitcoin", "ethereum", "litecoin", "solana",
    "dogecoin", "cardano", "xrp", "polkadot",
    "shiba-inu", "tron", "avalanche"
}

# Determine if asset is a cryptocurrency
def is_crypto(symbol):
    lower_symbol = symbol.lower()
    return lower_symbol in KNOWN_CRYPTO or any(term in lower_symbol for term in ["coin", "token", "eth", "btc", "bnb"])

# Fetch crypto data from CoinCap
def fetch_from_coincap(coin):
    try:
        response = requests.get(COINCAP_URL.format(coin), timeout=10)
        response.raise_for_status()
        data = response.json()["data"]
        return {
            "price": float(data["priceUsd"]),
            "volume": float(data["volumeUsd24Hr"]),
            "change_24h": float(data["changePercent24Hr"])
        }
    except Exception as e:
        log_message(f"❌ Coincap error for {coin}: {e}")
        return None

# Fetch crypto data from Coingecko
def fetch_from_coingecko(coin):
    try:
        params = {
            "vs_currency": "usd",
            "ids": coin,
            "order": "market_cap_desc",
            "per_page": 1,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h"
        }
        response = requests.get(COINGECKO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()[0]
        return {
            "price": float(data["current_price"]),
            "volume": float(data["total_volume"]),
            "change_24h": float(data["price_change_percentage_24h"])
        }
    except Exception as e:
        log_message(f"❌ Coingecko error for {coin}: {e}")
        return None

# Fetch stock or crypto data from Finnhub
def fetch_from_finnhub(symbol):
    try:
        response = requests.get(FINNHUB_URL.format(symbol), timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "price": data.get("c", 0.0),
            "volume": data.get("v", 0),
            "change_24h": round(((data.get("c", 0) - data.get("pc", 0)) / data.get("pc", 1)) * 100, 2) if data.get("pc") else 0
        }
    except Exception as e:
        log_message(f"❌ Finnhub error for {symbol}: {e}")
        return None

# Fetch stock data from Yahoo Finance
def fetch_from_yahoo(symbol):
    try:
        response = requests.get(YAHOO_URL.format(symbol), timeout=10)
        response.raise_for_status()
        quote = response.json()["quoteResponse"]["result"][0]
        return {
            "price": quote.get("regularMarketPrice", 0.0),
            "volume": quote.get("regularMarketVolume", 0),
            "change_24h": quote.get("regularMarketChangePercent", 0.0)
        }
    except Exception as e:
        log_message(f"❌ Yahoo error for {symbol}: {e}")
        return None

# Smart cascading fetch logic (optimized and intelligent)
def get_price_data(symbol):
    attempts = []
    result = None
    is_coin = is_crypto(symbol)

    # Try Finnhub first since it's multi-purpose
    result = fetch_from_finnhub(symbol.upper())
    attempts.append("finnhub")

    # Fallback to Coingecko/CoinCap if it's crypto
    if not result and is_coin:
        for fetch_func in [fetch_from_coincap, fetch_from_coingecko]:
            result = fetch_func(symbol)
            attempts.append(fetch_func.__name__)
            if result:
                break

    # Fallback to Yahoo if it's a stock
    if not result and not is_coin:
        result = fetch_from_yahoo(symbol.upper())
        attempts.append("yahoo")

    if not result:
        raise Exception(f"All price sources failed for {symbol}. Attempts: {attempts}")

    return result

# Enhanced RSI calculator with memory
def calculate_real_rsi(price_data, symbol):
    close_price = price_data["price"]
    history = RSI_HISTORY.setdefault(symbol, [])

    history.append(close_price)
    if len(history) > RSI_PERIOD:
        history.pop(0)

    if len(history) < 2:
        return 50.0  # Neutral default if not enough data

    gains = [history[i] - history[i - 1] for i in range(1, len(history)) if history[i] > history[i - 1]]
    losses = [history[i - 1] - history[i] for i in range(1, len(history)) if history[i] < history[i - 1]]

    avg_gain = sum(gains) / RSI_PERIOD if gains else 0.01
    avg_loss = sum(losses) / RSI_PERIOD if losses else 0.01

    rs = avg_gain / avg_loss if avg_loss != 0 else 1
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

# Unified interface for market data (and Nikki learns here)
def get_market_data(symbol, asset_type="crypto"):
    try:
        data = get_price_data(symbol, asset_type=asset_type)
        data["rsi"] = calculate_real_rsi(data, symbol)

        # Let Nikki learn from every market data pull
        enriched_data = {
            "symbol": symbol,
            "price": data["price"],
            "volume": data["volume"],
            "rsi": data["rsi"],
            "change_24h": data["change_24h"],
            "timestamp": time.time(),
            "source": "market_pull"
        }
        save_market_snapshot(enriched_data)

        return data
    except Exception as e:
        log_message(f"❌ Failed to get {asset_type} market data for {symbol}: {e}")
        return None

    except Exception as e:
        log_message(f"❌ Failed to get {asset_type} market data for {symbol}: {e}")
        return None
