from textblob import TextBlob
import json
import os
from global_news import collect_global_news
from datetime import datetime

GLOBAL_NEWS_FILE = "logs/global_headlines.json"
GLOBAL_SENTIMENT_FILE = "logs/global_sentiment.json"

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

def get_global_sentiment():
    try:
        # Try reading latest sentiment log first
        if os.path.exists(GLOBAL_SENTIMENT_FILE):
            with open(GLOBAL_SENTIMENT_FILE, "r") as f:
                logs = json.load(f)
                if logs:
                    return {
                        "positive": logs[-1]["positive"],
                        "negative": logs[-1]["negative"],
                        "neutral": logs[-1]["neutral"],
                        "mood_ratio": logs[-1]["mood_ratio"],
                        "mood_label": logs[-1]["mood_label"]
                    }

        # Fallback to headlines if no log exists
        if os.path.exists(GLOBAL_NEWS_FILE):
            with open(GLOBAL_NEWS_FILE, "r") as f:
                data = json.load(f)
                headlines = data.get("headlines", [])
                return summarize_sentiments(headlines)
        else:
            print("🌍 No global sentiment or headlines available.")
            return {"positive": 0, "negative": 0, "neutral": 0}

    except Exception as e:
        print(f"❌ Failed to retrieve global sentiment: {e}")
        return {"positive": 0, "negative": 0, "neutral": 0}


def log_global_sentiment():
    try:
        news_data = collect_global_news()
        headlines = news_data["bbc"] + news_data["reuters"] if news_data else []

        summary = summarize_sentiments(headlines)
        total = sum(summary.values())

        if total == 0:
            print("📭 No headlines to analyze.")
            return

        mood_ratio = (summary["positive"] - summary["negative"]) / total
        label = (
            "bullish" if mood_ratio > 0.5 else
            "slightly_optimistic" if mood_ratio > 0.2 else
            "neutral" if abs(mood_ratio) < 0.2 else
            "slightly_bearish" if mood_ratio < -0.2 else
            "bearish"
        )

        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "positive": summary["positive"],
            "negative": summary["negative"],
            "neutral": summary["neutral"],
            "mood_ratio": round(mood_ratio, 2),
            "mood_label": label
        }

        os.makedirs("logs", exist_ok=True)

        if os.path.exists(GLOBAL_SENTIMENT_FILE):
            with open(GLOBAL_SENTIMENT_FILE, "r") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        logs.append(log_entry)
        with open(GLOBAL_SENTIMENT_FILE, "w") as f:
            json.dump(logs[-100:], f, indent=2)

        print(f"🌍 Global sentiment logged → {label} ({summary})")

    except Exception as e:
        print(f"❌ Failed to log global sentiment: {e}")
if __name__ == "__main__":
    global_summary = get_global_sentiment()
    print("🌍 Global Sentiment Summary:", global_summary)
