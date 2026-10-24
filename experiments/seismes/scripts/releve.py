"""Relevé des événements « séismes » de Polymarket (réglés) et de leurs échanges réels."""
import gzip, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "src")
import requests
from polymarket_agent.http_client import HttpClient
from polymarket_agent.idea_test import fetch_event_trades
H = {"User-Agent": "curl/8"}
D = Path("experiments/seismes/releves/echanges"); D.mkdir(exist_ok=True, parents=True)  # versionné (1,2 Mo) : le passage suivant repart d'un clone neuf
ev = {}
for closed in ("true", "false"):
    for off in range(0, 2000, 100):
        r = requests.get("https://gamma-api.polymarket.com/events", headers=H, timeout=60,
                         params=dict(closed=closed, limit=100, offset=off, order="endDate", ascending="false", tag_slug="earthquakes"))
        js = r.json()
        if not js: break
        for e in js: ev[e["id"]] = e
print(len(ev), "événements", file=sys.stderr)
keep = []
for e in ev.values():
    keep.append({"id": e["id"], "title": e["title"], "closed": e["closed"], "end": e["endDate"], "start": e.get("startDate"),
                 "markets": [{"id": m["id"], "q": m["question"], "tokens": json.loads(m["clobTokenIds"]) if m.get("clobTokenIds") else [],
                              "prices": m.get("outcomePrices"), "closedTime": m.get("closedTime"), "end": m.get("endDate"),
                              "git": m.get("groupItemTitle")} for e2 in [e] for m in e2["markets"]]})
Path("experiments/seismes/releves").mkdir(exist_ok=True, parents=True)
with gzip.open("experiments/seismes/releves/evenements.json.gz", "wt") as f: json.dump(keep, f)
http = HttpClient(user_agent="curl/8") if "user_agent" in HttpClient.__init__.__code__.co_varnames else HttpClient()
def go(e):
    try: return len(fetch_event_trades(http, D, e["id"]))
    except Exception as x: return str(x)[:80]
with ThreadPoolExecutor(6) as ex: res = list(ex.map(go, [e for e in keep if e["closed"]]))
print(sum(r for r in res if isinstance(r, int)), "échanges;", [r for r in res if not isinstance(r, int)][:3])
