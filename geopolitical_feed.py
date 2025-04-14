import random
import time
from datetime import datetime
from utils.helpers import log_geopolitical_event

# Simulated geopolitical signals for now (replace later with API or RSS feed)
SIMULATED_EVENTS = [
    {"type": "sanction", "region": "Russia", "impact": "medium", "description": "New sanctions on Russian banks."},
    {"type": "election", "region": "USA", "impact": "high", "description": "Upcoming presidential election."},
    {"type": "conflict", "region": "Middle East", "impact": "high", "description": "Escalating tensions reported."},
    {"type": "regulation", "region": "EU", "impact": "medium", "description": "EU proposes new crypto regulations."},
    {"type": "summit", "region": "Global", "impact": "low", "description": "G20 summit underway with crypto talks."},
    {"type": "hack", "region": "Asia", "impact": "high", "description": "Major crypto exchange breach in South Korea."}
]

def get_recent_geopolitical_events():
    """Simulate fetching global macro events (to be replaced with real feed)."""
    event = random.choice(SIMULATED_EVENTS)
    event["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [event]

def monitor_geopolitical_signals():
    while True:
        events = get_recent_geopolitical_events()
        for e in events:
            log_geopolitical_event(e)
        time.sleep(300)  # Check every 5 minutes
