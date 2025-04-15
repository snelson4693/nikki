import threading
import time
import random
import json
import os
from datetime import datetime
from multi_source_research import discover_new_sources, summarize_and_store_insights, analyze_github_codebase, extract_code_patterns
from utils.helpers import log_message
from config_loader import load_config



# Interval between research runs (in seconds)
DISCOVERY_INTERVAL = 1800  # 30 minutes for rapid iteration

# List of default rotating queries for broader research
DEFAULT_QUERIES = [
    "python bug fix",
    "AI optimization",
    "strategy logic",
    "trading script",
    "machine learning model improvement",
    "financial forecasting algorithms",
    "auto-patching logic",
    "real-time data scraping",
    "error handling techniques",
    "neural network training tips",
    "github code enhancement patterns",
    "multi-device AI sync optimization",
    "self-healing AI methods"
]

# Memory to avoid repeating recent queries
recent_queries = []
MAX_RECENT_QUERIES = 25

SEARCH_KEYWORDS_FILE = "logs/search_keywords.json"

# Ensure search_keywords.json exists
if not os.path.exists("logs"):
    os.makedirs("logs")

if not os.path.exists(SEARCH_KEYWORDS_FILE):
    with open(SEARCH_KEYWORDS_FILE, "w") as f:
        json.dump(DEFAULT_QUERIES, f, indent=2)

def extract_dynamic_queries():
    """
    Pull insights from Nikki's logs and errors to create intelligent dynamic queries.
    Adds reflection-based reasoning for improved adaptive querying.
    """
    logs = []
    try:
        with open("logs/bug_reports.txt", "r") as f:
            logs += f.readlines()
    except:
        pass

    try:
        with open("brain_repo/logs/error_pool.json", "r") as f:
            errors = json.load(f)
            logs += [entry.get("error", "") for entry in errors if isinstance(entry, dict)]
    except:
        pass

    try:
        with open("logs/reflective_journal.json", "r") as f:
            reflections = json.load(f)
            for entry in reflections:
                logs.append(entry.get("observation", ""))
                logs.append(entry.get("suggestion", ""))
    except:
        pass

    # Load previous search keywords
    try:
        with open(SEARCH_KEYWORDS_FILE, "r") as f:
            previous = set(json.load(f))
    except:
        previous = set()

    keywords = set(previous)
    for entry in logs:
        entry = entry.lower()
        if "keyerror" in entry: keywords.add("fix keyerror in python")
        if "indexerror" in entry: keywords.add("resolve indexerror")
        if "strategy" in entry: keywords.add("strategy tuning ai trading")
        if "patch" in entry: keywords.add("intelligent bug patching")
        if "trade" in entry: keywords.add("autonomous trade algorithm")
        if "accuracy" in entry: keywords.add("model accuracy improvement techniques")
        if "scraper" in entry: keywords.add("robust scraping methods")
        if "confidence" in entry: keywords.add("boost prediction confidence")
        if "merge conflict" in entry: keywords.add("git auto conflict resolution")
        if "sandbox" in entry: keywords.add("python sandbox testing environment best practices")

    # Save updated keywords
    with open(SEARCH_KEYWORDS_FILE, "w") as f:
        json.dump(list(keywords), f, indent=2)

    return list(keywords)

def select_smart_query(dynamic_queries):
    """
    Selects a non-recent, highly intelligent query from the pool.
    """
    global recent_queries
    pool = list(set(DEFAULT_QUERIES + dynamic_queries))
    attempts = 0
    while attempts < 10:
        query = random.choice(pool)
        if query not in recent_queries:
            recent_queries.append(query)
            if len(recent_queries) > MAX_RECENT_QUERIES:
                recent_queries.pop(0)
            return query
        attempts += 1
    return random.choice(pool)

def background_multi_source_learning():
    """
    Background thread for autonomous source discovery.
    Uses Nikki’s past errors, logs, and reflections to inform research queries.
    Learns from results and evolves its own source bank and intelligence model.
    Also analyzes Nikki's own GitHub repo codebase for improvements.
    """
    while True:
        try:
            log_queries = extract_dynamic_queries()
            query = select_smart_query(log_queries)
            log_message(f"🔍 Nikki is researching: '{query}'")

            results = discover_new_sources(query)
            summarize_and_store_insights(query, results)
            log_message("✅ Research insights stored and cycle complete.")

            log_message("🔎 Scanning Nikki's GitHub codebase for optimization opportunities...")
            analyze_github_codebase()

            log_message("🧬 Extracting reusable patterns from discovered insights...")
            extract_code_patterns()

        except Exception as e:
            log_message(f"❌ Multi-source discovery failed: {e}")

        time.sleep(DISCOVERY_INTERVAL)

def start_multi_source_thread():
    """
    Initializes the multi-source research engine in a daemon thread.
    """
    thread = threading.Thread(target=background_multi_source_learning, daemon=True)
    thread.start()
    print("🧠 Multi-source research engine started.")
