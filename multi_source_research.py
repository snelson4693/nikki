import os
import json
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import threading
from config_loader import load_config
from utils.helpers import log_message
import re

GITHUB_API_BASE = "https://api.github.com"
REPO = "snelson4693/nikki"  # Update this if your repo name changes
OUTPUT_FILE = "logs/github_analysis.json"

HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}

LOG_DIR = "logs"
SOURCE_FILE = os.path.join(LOG_DIR, "search_sources.json")
CACHE_FILE = os.path.join(LOG_DIR, "search_cache.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (NikkiBot)"}
INSIGHT_LOG_FILE = "logs/research_insights.json"

DEFAULT_SOURCES = [
    "https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={query}&site=stackoverflow",
    "https://www.reddit.com/search.json?q={query}&sort=relevance",
    "https://github.com/search?q={query}&type=code",
    "https://huggingface.co/search/full-text?q={query}",
    "https://dev.to/search?q={query}"
]

MAX_SOURCES = 50
FAILURE_THRESHOLD = 5
DISCOVERY_INTERVAL = 1800  # Every 30 minutes
CACHE_DURATION = 600  # 10 minutes

CODE_PATHS = ["."]  # Root-level scan — update as needed
PATTERN_LOG = "logs/patterns/code_patterns.json"

# Enhanced regex for function signatures (supports type hints and default values)
FUNCTION_REGEX = r"def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*[\w\[\], ]+)?\s*:"

# Handles single and triple-quoted docstrings
DOCSTRING_REGEX = r"\"\"\"(.*?)\"\"\"|\'\'\'(.*?)\'\'\'"

# Ensure log folder exists
os.makedirs("logs/patterns", exist_ok=True)

def ensure_log_directory():
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(SOURCE_FILE):
        with open(SOURCE_FILE, "w") as f:
            json.dump({url: {"score": 1.0, "last_used": None, "failures": 0} for url in DEFAULT_SOURCES}, f, indent=2)
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "w") as f:
            json.dump({}, f, indent=2)

def load_sources():
    with open(SOURCE_FILE, "r") as f:
        return json.load(f)

def save_sources(sources):
    filtered = {k: v for k, v in sources.items() if v.get("failures", 0) < FAILURE_THRESHOLD}
    sorted_sources = dict(sorted(filtered.items(), key=lambda x: x[1].get("score", 1), reverse=True))
    trimmed = dict(list(sorted_sources.items())[:MAX_SOURCES])
    with open(SOURCE_FILE, "w") as f:
        json.dump(trimmed, f, indent=2)

def score_source(meta, success):
    if success:
        meta["score"] = min(meta.get("score", 1.0) + 0.2, 5.0)
        meta["failures"] = 0
    else:
        meta["failures"] = meta.get("failures", 0) + 1
        meta["score"] = max(meta.get("score", 1.0) - 0.1 * meta["failures"], 0.1)
    meta["last_used"] = datetime.utcnow().isoformat()

def load_cache():
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def search_sources(query):
    sources = load_sources()
    cache = load_cache()
    now = time.time()
    if query in cache and now - cache[query].get("timestamp", 0) < CACHE_DURATION:
        return cache[query]["results"]

    ranked = sorted(sources.items(), key=lambda x: x[1].get("score", 1), reverse=True)
    results = []

    for url_template, meta in ranked:
        try:
            url = url_template.replace("{query}", requests.utils.quote(query))
            response = requests.get(url, headers=HEADERS, timeout=10)
            success = response.status_code == 200
            if success:
                results.append((url, response.text[:2000]))
            score_source(meta, success)
        except:
            score_source(meta, False)

    save_sources(sources)
    cache[query] = {"timestamp": now, "results": results}
    save_cache(cache)
    return results

def discover_new_sources(query):
    print("🌐 Discovering new sources dynamically via Google search...")
    try:
        search_url = f"https://www.google.com/search?q={requests.utils.quote(query + ' site:stackoverflow.com OR site:github.com OR site:dev.to OR site:medium.com')}"
        res = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True) if "url?q=" in a["href"] and "webcache" not in a["href"]]

        cleaned_links = []
        for link in links:
            start = link.find("url?q=") + 6
            end = link.find("&", start)
            if start != -1 and end != -1:
                actual_url = link[start:end]
                cleaned_links.append(actual_url)

        sources = load_sources()
        added = 0
        for link in cleaned_links:
            if "{query}" not in link and link not in sources:
                dynamic_template = link.replace(query, "{query}")
                sources[dynamic_template] = {"score": 1.0, "last_used": None, "failures": 0}
                added += 1

        save_sources(sources)
        print(f"🔍 Discovered and saved {added} new potential sources.")

    except Exception as e:
        print(f"❌ Error during dynamic discovery: {e}")

def autonomous_research(query):
    ensure_log_directory()
    discover_new_sources(query)
    return search_sources(query)

def background_discovery_loop():
    ensure_log_directory()
    while True:
        discover_new_sources("python bug fix")
        time.sleep(DISCOVERY_INTERVAL)
def summarize_and_store_insights(query, results):
    """
    Summarizes and stores insights from a multi-source search.
    Stores metadata about source and relevance for later learning.
    """
    if not os.path.exists("logs"):
        os.makedirs("logs")

    insights = []
    for url, content in results:
        snippet = content.strip().replace("\n", " ").replace("\r", " ")[:500]
        insights.append({
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "source": url,
            "summary": snippet,
            "length": len(content)
        })

    if os.path.exists(INSIGHT_LOG_FILE):
        try:
            with open(INSIGHT_LOG_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.extend(insights)

    with open(INSIGHT_LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Stored {len(insights)} insights for query: {query}")
def analyze_github_codebase():
    """
    Pulls recent code from GitHub repo, searches for complexity or patterns,
    and stores insights in a local log.
    """
    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")

        config = load_config()
        token = config.get("github_token")  # Optional: For higher rate limits
        if token:
            HEADERS["Authorization"] = f"token {token}"

        files = []
        page = 1

        while True:
            url = f"{GITHUB_API_BASE}/repos/{REPO}/contents?ref=main&page={page}"
            res = requests.get(url, headers=HEADERS)
            if res.status_code != 200:
                log_message(f"❌ GitHub fetch error: {res.status_code}")
                break

            content = res.json()
            if not content:
                break

            files.extend(content)
            page += 1

        insights = []

        for file in files:
            if file["type"] != "file" or not file["name"].endswith(".py"):
                continue

            raw_url = file.get("download_url")
            res = requests.get(raw_url)
            if res.status_code == 200:
                code = res.text
                line_count = len(code.split("\n"))
                func_count = code.count("def ")
                class_count = code.count("class ")

                insights.append({
                    "filename": file["name"],
                    "lines": line_count,
                    "functions": func_count,
                    "classes": class_count,
                    "download_url": raw_url
                })

        with open(OUTPUT_FILE, "w") as f:
            json.dump(insights, f, indent=2)

        log_message("✅ GitHub codebase analysis complete.")

    except Exception as e:
        log_message(f"❌ analyze_github_codebase error: {e}")
def extract_code_patterns():
    patterns = []
    stats = {"functions": 0, "docstrings": 0, "files_scanned": 0}

    for path in CODE_PATHS:
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py") and not file.startswith("_") and "site-packages" not in root:
                    full_path = os.path.join(root, file)
                    stats["files_scanned"] += 1
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()

                            # Function extraction
                            funcs = re.findall(FUNCTION_REGEX, content)
                            for func_name, args in funcs:
                                patterns.append({
                                    "type": "function",
                                    "name": func_name,
                                    "args": args,
                                    "file": full_path
                                })
                            stats["functions"] += len(funcs)

                            # Docstring extraction
                            docs = re.findall(DOCSTRING_REGEX, content, re.DOTALL)
                            for doc1, doc2 in docs:
                                doc = doc1 or doc2
                                if doc.strip():
                                    patterns.append({
                                        "type": "docstring",
                                        "content": doc.strip()[:300],
                                        "file": full_path
                                    })
                                    stats["docstrings"] += 1

                    except Exception as e:
                        print(f"❌ Failed to read {full_path}: {e}")

    # Final pattern log with timestamp and stats
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "stats": stats,
        "patterns": patterns
    }

    try:
        if os.path.exists(PATTERN_LOG):
            with open(PATTERN_LOG, "r") as f:
                existing = json.load(f)
        else:
            existing = []

        existing.append(log_entry)

        with open(PATTERN_LOG, "w") as f:
            json.dump(existing, f, indent=2)

        print(f"✅ Code pattern extraction complete. Scanned {stats['files_scanned']} files.")

    except Exception as e:
        print(f"❌ Failed to write code pattern log: {e}")
if __name__ == "__main__":
    threading.Thread(target=background_discovery_loop, daemon=True).start()
    q = input("🔎 Enter your query: ")
    results = autonomous_research(q)
    print("\n🔍 Top results:")
    for url, snippet in results[:3]:
        print(f"\nFrom {url}\n{'-'*40}\n{snippet[:300]}\n...")
