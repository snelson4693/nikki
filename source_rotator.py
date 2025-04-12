import requests
import random
import time

LAST_USED = {}

# Only using safer sources for now (Binance removed)
PRICE_SOURCES = [
    "coingecko",
    "coincap"
]

def rate_limit_wait(source):
    now = time.time()
    if source in LAST_USED:
        elapsed = now - LAST_USED[source]
        if elapsed < 20:  # Wait 20 seconds between requests to the same source
            wait_time = 20 - elapsed
            print(f"⏳ Waiting {wait_time:.1f}s to avoid spamming {source}...")
            time.sleep(wait_time)
    LAST_USED[source] = time.time()

def get_price_from_coingecko(coin):
    coin = coin.lower()
    rate_limit_wait("coingecko")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": coin,
            "vs_currencies": "usd",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        }
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        coin_data = data.get(coin)
        if not coin_data or "usd" not in coin_data:
            raise Exception("Coin data not available in CoinGecko response.")

        return {
            "price": coin_data["usd"],
            "volume": coin_data.get("usd_24h_vol", 0),
            "change_24h": coin_data.get("usd_24h_change", 0),
            "market_cap": coin_data.get("usd_market_cap", 0),
            "source": "coingecko"
        }
    except Exception as e:
        print(f"❌ CoinGecko failed: {e}")
        return None

def get_price_from_coincap(coin):
    coin = coin.lower()
    rate_limit_wait("coincap")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        url = f"https://api.coincap.io/v2/assets/{coin}"
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()["data"]
        return {
            "price": float(data["priceUsd"]),
            "volume": float(data["volumeUsd24Hr"]),
            "change_24h": float(data["changePercent24Hr"]),
            "market_cap": float(data["marketCapUsd"]),
            "source": "coincap"
        }
    except Exception as e:
        print(f"❌ CoinCap failed: {e}")
        return None

def get_price_data(coin):
    coin = coin.lower()
    for source in random.sample(PRICE_SOURCES, len(PRICE_SOURCES)):
        if source == "coingecko":
            result = get_price_from_coingecko(coin)
        elif source == "coincap":
            result = get_price_from_coincap(coin)
        else:
            continue

        if result:
            return result

    print("❌ All sources failed.")
    print("😴 Cooling off for 60s to avoid lockout...")
    time.sleep(60)
    return None
