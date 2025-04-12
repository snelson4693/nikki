from coin_discovery import get_trending_coins
from trend_analyzer import analyze_coin_sentiment
import json

def run_screener(min_score=2):
    print("🧠 Running smart screener...")

    selected = []
    trending = get_trending_coins()

    for coin in trending:
        _, score = analyze_coin_sentiment(coin)
        if score >= min_score:
            print(f"✅ Added {coin} (score: {score})")
            selected.append(coin)
        else:
            print(f"❌ Skipped {coin} (score: {score})")

    # Save to a JSON file Nikki can use in main loop
    with open("active_coins.json", "w") as f:
        json.dump(selected, f, indent=2)

    print(f"🗂️ Final selected coins: {len(selected)}")
    return selected

# Optional: test it
if __name__ == "__main__":
    run_screener()
