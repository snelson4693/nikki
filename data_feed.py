import requests
import time
import random
from utils.helpers import log_message

COINCAP_URL = "https://api.coincap.io/v2/assets/{}"
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

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
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            log_message("❌ Coincap failed: 429 Too Many Requests")
            raise e
        raise
    except Exception as e:
        log_message(f"❌ Coincap failed: {e}")
        raise

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
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            log_message("❌ Coingecko failed: 429 Too Many Requests")
            raise e
        raise
    except Exception as e:
        log_message(f"❌ Coingecko failed: {e}")
        raise

def get_price_data(coin):
    try:
        return fetch_from_coincap(coin)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            time.sleep(30)  # Wait when rate limited
    except:
        pass

    try:
        return fetch_from_coingecko(coin)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            time.sleep(30)  # Wait when rate limited
    except:
        pass

    raise Exception("All price sources failed.")

def get_market_data(coin):
    try:
        data = get_price_data(coin)
        data["rsi"] = random.uniform(30, 70)  # Simulate RSI
        return data
    except Exception as e:
        log_message(f"❌ Error fetching or processing data: {e}")
        return None
