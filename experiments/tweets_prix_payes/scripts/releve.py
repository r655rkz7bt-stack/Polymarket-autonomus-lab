"""Relevé pour re-juger `compteur_tweets_non` aux PRIX DES VRAIS ÉCHANGES (25/10/2026) : événements réglés des comptes XTracker, messages XTracker, échanges.
Usage : releve.py  ->  donnees/evenements_<compte>.json, donnees/messages_<compte>.json, donnees/cache/echanges_<id>.json.gz"""
import json, sys, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
D = Path("experiments/tweets_prix_payes/donnees"); D.mkdir(parents=True, exist_ok=True)
H = {"User-Agent": "curl/8"}
COMPTES = {"ZelenskyyUa": ("zelenskyy-of-tweets-", ["Zelenskyy tweets"]),
           "tedcruz": ("ted-cruz-of-tweets-", ["Ted Cruz tweets"]),
           "WhiteHouse": ("white-house-of-", ["White House posts", "White House tweets"]),
           "cz_binance": ("cz-binance-of-tweets-", ["CZ tweets", "CZ binance tweets"])}
http = HttpClient(timeout=40, max_retries=3, backoff=2.0, min_interval=0.05, user_agent="curl/8")
for handle, (prefix, queries) in COMPTES.items():
    ev = {}
    for q in queries:
        for page in range(1, 8):
            d = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=40,
                             params={"q": q, "events_status": "closed", "limit_per_type": 50, "page": page}).json()
            for e in d.get("events", []):
                if e["slug"].startswith(prefix): ev[e["id"]] = e
            if not d.get("pagination", {}).get("hasMore"): break
    evs = sorted(ev.values(), key=lambda e: e["endDate"])
    json.dump(evs, open(D / f"evenements_{handle}.json", "w"))
    posts = requests.get(f"https://xtracker.polymarket.com/api/users/{handle}/posts", headers=H, timeout=120,
                         params={"startDate": "2025-01-01T00:00:00Z", "endDate": "2026-10-26T00:00:00Z"}).json().get("data") or []
    json.dump(sorted(p["createdAt"] for p in posts if p.get("createdAt")), open(D / f"messages_{handle}.json", "w"))
    print(handle, len(evs), "événements", len(posts), "messages", flush=True)
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(lambda e: it.fetch_event_trades(http, D / "cache", str(e["id"])), evs))
