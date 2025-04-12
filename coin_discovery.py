import requests

def get_trending_coins():
    print("🧠 Discovering trending coins...")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        # Using CoinGecko's top 100 coins by market cap
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h"
        }

        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()

        # Filter coins based on custom strategy
        discovered = []
        for coin in data:
            if coin["total_volume"] > 100000000 and abs(coin["price_change_percentage_24h_in_currency"]) > 2:
                discovered.append(coin["id"])

        print(f"🪙 Discovered {len(discovered)} coins worth watching.")
        return discovered

    except Exception as e:
        print(f"❌ Error discovering coins: {e}")
        return []
if __name__ == "__main__":
    coins = get_trending_coins()
    print("🔍 Trending Coins:", coins)