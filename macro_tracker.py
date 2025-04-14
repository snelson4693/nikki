import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

MACRO_LOG = "logs/macro_insights.json"

def fetch_imf_headlines():
    url = "https://www.imf.org/en/News"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = [tag.text.strip() for tag in soup.select(".news-article-title a")][:5]
        return headlines
    except Exception as e:
        print(f"❌ IMF scrape error: {e}")
        return []

def fetch_world_bank_headlines():
    url = "https://www.worldbank.org/en/news"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = [tag.text.strip() for tag in soup.select(".title a")][:5]
        return headlines
    except Exception as e:
        print(f"❌ World Bank scrape error: {e}")
        return []

def fetch_fed_headlines():
    url = "https://www.federalreserve.gov/newsevents.htm"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = [tag.text.strip() for tag in soup.select(".item_title a")][:5]
        return headlines
    except Exception as e:
        print(f"❌ Federal Reserve scrape error: {e}")
        return []

def log_macro_news():
    imf = fetch_imf_headlines()
    wb = fetch_world_bank_headlines()
    fed = fetch_fed_headlines()

    snapshot = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "IMF": imf,
        "World Bank": wb,
        "Federal Reserve": fed
    }

    os.makedirs("logs", exist_ok=True)

    try:
        if os.path.exists(MACRO_LOG):
            with open(MACRO_LOG, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append(snapshot)
        with open(MACRO_LOG, "w") as f:
            json.dump(history[-100:], f, indent=2)

        print("📊 Macroeconomic news logged.")
    except Exception as e:
        print(f"❌ Logging error: {e}")

if __name__ == "__main__":
    log_macro_news()
