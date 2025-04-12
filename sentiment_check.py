from news_feed import get_headlines
from sentiment import summarize_sentiments

def run_sentiment_check():
    result = get_headlines()

    print(f"📰 Source: {result['source']}")
    for h in result['headlines']:
        print(f" - {h}")

    print("\n🔍 Sentiment Summary:")
    summary = summarize_sentiments(result["headlines"])
    for sentiment, count in summary.items():
        print(f" {sentiment.title()}: {count}")

if __name__ == "__main__":
    run_sentiment_check()
