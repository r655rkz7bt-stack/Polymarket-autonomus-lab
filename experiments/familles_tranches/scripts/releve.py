"""Familles d'événements « tranches » répétitifs autres que le box-office : relevé des événements réglés et de leurs échanges (versionnés)."""
import gzip, json, sys, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "src")
import requests
from polymarket_agent.http_client import HttpClient
from polymarket_agent.idea_test import fetch_event_trades
H = {"User-Agent": "curl/8"}
R = Path("experiments/familles_tranches/releves"); D = R / "echanges"; D.mkdir(exist_ok=True, parents=True)
FAM = {"rotten": ["Rotten Tomatoes Score"], "tesla": ["Tesla deliveries"], "netflix": ["top US Netflix show this week", "Netflix show this week"],
       "spotify": ["Top Spotify artist in", "#2 Spotify Artist"], "vues": ["# of views of", "views on day 1", "views of next MrBeast"],
       "followers": ["Twitter followers", "followers by"], "earnings": ["quarterly earnings"], "kpi": ["growth (constant", "payments volume growth"]}
ev = {}
for fam, qs in FAM.items():
    for q in qs:
        for pg in range(1, 10):
            r = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=60,
                             params={"q": q, "limit_per_type": 50, "page": pg, "events_status": "closed"})
            if r.status_code != 200: break
            es = r.json().get("events", [])
            if not es: break
            for e in es: ev.setdefault(e["id"], dict(e, fam=fam))
print(len(ev), "événements trouvés", file=sys.stderr)
def full(e):
    f = requests.get(f"https://gamma-api.polymarket.com/events/{e['id']}", headers=H, timeout=60).json()
    return {"id": f["id"], "fam": e["fam"], "title": f["title"], "closed": f["closed"], "end": f.get("endDate"),
            "markets": [{"id": m["id"], "q": m["question"], "tokens": json.loads(m["clobTokenIds"]) if m.get("clobTokenIds") else [],
                         "prices": m.get("outcomePrices"), "git": m.get("groupItemTitle")} for m in f["markets"]]}
with ThreadPoolExecutor(6) as ex: keep = [k for k in ex.map(full, ev.values()) if k["closed"] and len(k["markets"]) >= 3]
with gzip.open(R / "evenements.json.gz", "wt") as f: json.dump(keep, f)
http = HttpClient(user_agent="curl/8") if "user_agent" in HttpClient.__init__.__code__.co_varnames else HttpClient()
def go(e):
    try: return len(fetch_event_trades(http, D, e["id"]))
    except Exception as x: return str(x)[:80]
with ThreadPoolExecutor(6) as ex: res = list(ex.map(go, keep))
import collections
print(collections.Counter(k["fam"] for k in keep), sum(r for r in res if isinstance(r, int)), "échanges")
