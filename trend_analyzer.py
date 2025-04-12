from news_feed import get_reddit_headlines
from sentiment import analyze_sentiment

def analyze_coin_sentiment(coin_id):
    print(f"🧠 Analyzing sentiment for: {coin_id}...")
    
    try:
        # Fetch headlines related to this coin
        headlines_data = get_reddit_headlines(coin_id)
        headlines = headlines_data.get("headlines", [])

        if not headlines:
            print("⚠️ No headlines found.")
            return {"positive": 0, "negative": 0, "neutral": 0}, 0

        # Analyze sentiment on each headline
        summary = {"positive": 0, "negative": 0, "neutral": 0}
        total_score = 0

        for headline in headlines:
            sentiment = analyze_sentiment(headline)
            summary[sentiment] += 1

            if sentiment == "positive":
                total_score += 1
            elif sentiment == "negative":
                total_score -= 1

        print(f"📊 Sentiment for {coin_id}: {summary} (score: {total_score})")
        return summary, total_score

    except Exception as e:
        print(f"❌ Failed sentiment analysis for {coin_id}: {e}")
        return {"positive": 0, "negative": 0, "neutral": 0}, 0

# Optional: quick test
if __name__ == "__main__":
    _, score = analyze_coin_sentiment("bitcoin")
    print("🧪 Score:", score)
