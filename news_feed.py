import requests
import praw


def get_reddit_headlines(query="crypto"):
    try:
        print(f"🔍 Pulling Reddit headlines for '{query}'...")
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://www.reddit.com/search.json?q={query}&sort=new&limit=10"

        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        posts = r.json()["data"]["children"]

        headlines = [post["data"]["title"] for post in posts if "title" in post["data"]]
        return {"source": "get_reddit_headlines", "headlines": headlines}

    except Exception as e:
        print(f"❌ Error pulling from Reddit: {e}")
        return {"source": "none", "headlines": []}

def get_headlines(coin="bitcoin"):
    print(f"🔍 Pulling Reddit headlines for '{coin}'...")

    try:
        import praw

        reddit = praw.Reddit(
            client_id="66w9dDpwDbkkUsycRK0_Rw",  # <- your app ID
            client_secret="o3A_daMkFb-q6jLLj_pWA7eLE7QT4w",  # <- your secret
            user_agent="nikki-news-bot"
        )
        reddit.read_only = True

        headlines = []
        for post in reddit.subreddit("CryptoCurrency").search(coin, sort="new", limit=10):
            headlines.append(post.title)

        return {"headlines": headlines}

    except Exception as e:
        print(f"❌ Error pulling headlines for {coin}: {e}")
        return {"headlines": []}


