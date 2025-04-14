import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from sentiment import summarize_sentiments

INFLUENCERS = [
    "Elon Musk",
    "CZ Binance",
    "Vitalik Buterin",
    "Michael Saylor",
    "Cathie Wood"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

LOG_FILE = "logs/influencer_sentiment.json"

def fetch_headlines(query):
    try:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=nws"
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = [tag.text for tag in soup.find_all("div", class_="BNeawe vvjwJb AP7Wnd")]
        return headlines[:5]  # limit to 5 per influencer
    except Exception as e:
        print(f"❌ Error fetching headlines for {query}: {e}")
        return []

def track_influencer_sentiment():
    results = []

    for person in INFLUENCERS:
        print(f"🔍 Checking sentiment for: {person}")
        headlines = fetch_headlines(person)
        if not headlines:
            continue
        sentiment_summary = summarize_sentiments(headlines)
        results.append({
            "influencer": person,
            "headlines": headlines,
            "sentiment": sentiment_summary
        })

        time.sleep(2)

    log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "results": results
    }

    try:
        with open(LOG_FILE, "w") as f:
            json.dump(log, f, indent=2)
        print("✅ Influencer sentiment log updated.")
    except Exception as e:
        print(f"❌ Failed to write influencer sentiment log: {e}")

if __name__ == "__main__":
    track_influencer_sentiment()
