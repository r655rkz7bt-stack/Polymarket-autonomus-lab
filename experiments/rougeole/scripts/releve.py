"""Marchés « Measles cases in U.S. by <date> ? » (seuils cumulés, compteur CDC) : événements réglés et leurs échanges réels."""
import gzip, json, sys, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "src")
import requests
from polymarket_agent.http_client import HttpClient
from polymarket_agent.idea_test import fetch_event_trades
H = {"User-Agent": "curl/8"}
D = Path("experiments/rougeole/releves/echanges"); D.mkdir(exist_ok=True, parents=True)
ev = {}
for q in ("Measles cases in U.S.", "Measles cases in U.S. by", "measles cases", "Measles"):
    for status in ("closed", "active"):
        for pg in (1, 2, 3):
            r = requests.get("https://gamma-api.polymarket.com/public-search", params={"q": q, "limit_per_type": 50, "page": pg, "events_status": status}, headers=H, timeout=30)
            if r.status_code != 200: break
            for e in r.json().get("events", []):
                if re.search(r"[Mm]easles cases", e["title"]): ev[e["id"]] = e["id"]
out = []
for eid in ev:
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=30).json()
    out.append({"id": e["id"], "title": e["title"], "closed": e["closed"], "end": e["endDate"], "description": e.get("description", "")[:600],
                "markets": [{"id": m["id"], "q": m["question"], "tokens": json.loads(m["clobTokenIds"]) if m.get("clobTokenIds") else [], "prices": m.get("outcomePrices"),
                             "closedTime": m.get("closedTime")} for m in e["markets"]]})
with gzip.open("experiments/rougeole/releves/evenements.json.gz", "wt") as f: json.dump(out, f)
http = HttpClient()
def go(e):
    try: return len(fetch_event_trades(http, D, e["id"]))
    except Exception as x: return str(x)[:60]
with ThreadPoolExecutor(6) as ex: res = list(ex.map(go, out))
print(len(out), "événements;", sorted((e["end"][:10], e["title"][:50], e["closed"]) for e in out)[:40], sum(r for r in res if isinstance(r, int)), "échanges")
