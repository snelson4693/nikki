from textblob import TextBlob

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    if polarity > 0.2:
        return "positive"
    elif polarity < -0.2:
        return "negative"
    else:
        return "neutral"

def summarize_sentiments(headlines):
    results = {"positive": 0, "negative": 0, "neutral": 0}

    for headline in headlines:
        sentiment = analyze_sentiment(headline)
        results[sentiment] += 1

    return results

if __name__ == "__main__":
    test = [
        "Bitcoin skyrockets to new all-time high",
        "Crypto market crashes amid regulation fears",
        "Ethereum price remains steady"
    ]

    print("🔍 Sentiment Summary:")
    print(summarize_sentiments(test))
