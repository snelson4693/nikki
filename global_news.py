import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

NEWS_OUTPUT = "logs/global_news.json"

def fetch_bbc_headlines():
    url = "https://www.bbc.com/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    headlines = []
    for item in soup.select("a.gs-c-promo-heading"):
        title = item.get_text(strip=True)
        if title and title not in headlines:
            headlines.append(title)
    
    return headlines[:10]  # limit to top 10

def fetch_reuters_headlines():
    url = "https://www.reuters.com/world/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    headlines = []
    for item in soup.select("a.story-title, h2.story-title, h3.story-title"):
        title = item.get_text(strip=True)
        if title and title not in headlines:
            headlines.append(title)
    
    # fallback: scan common article containers
    if not headlines:
        for tag in soup.find_all(["h2", "h3"]):
            if tag.get_text(strip=True) and len(tag.get_text(strip=True)) > 40:
                headlines.append(tag.get_text(strip=True))
    
    return headlines[:10]

def collect_global_news():
    try:
        print("🌍 Fetching BBC headlines...")
        bbc = fetch_bbc_headlines()

        print("📰 Fetching Reuters headlines...")
        reuters = fetch_reuters_headlines()

        all_news = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "bbc": bbc,
            "reuters": reuters
        }

        os.makedirs("logs", exist_ok=True)
        with open(NEWS_OUTPUT, "w") as f:
            json.dump(all_news, f, indent=2)
        
        print(f"✅ Global news saved to {NEWS_OUTPUT}")
        return all_news
    except Exception as e:
        print(f"❌ Error fetching global news: {e}")
        return None

if __name__ == "__main__":
    collect_global_news()
