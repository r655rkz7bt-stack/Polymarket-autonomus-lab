"""Relevé des événements « Opening Weekend Box Office » de Polymarket (réglés) et de leurs échanges réels (versionnés : le passage suivant repart d'un clone neuf)."""
import gzip, json, sys, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "src")
import requests
from polymarket_agent.http_client import HttpClient
from polymarket_agent.idea_test import fetch_event_trades
H = {"User-Agent": "curl/8"}
R = Path("experiments/box_office/releves"); D = R / "echanges"; D.mkdir(exist_ok=True, parents=True)
ev = {}
for q in ["Opening Weekend Box Office", "Box Office", "Opening Weekend", "5-day Opening Weekend", "Box Office Higher Brackets", "Box Office lower strikes"]:
    for st in ("closed", "active"):
        for pg in range(1, 12):
            r = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=60,
                             params={"q": q, "limit_per_type": 50, "page": pg, "events_status": st})
            if r.status_code != 200: break
            es = r.json().get("events", [])
            if not es: break
            for e in es:
                if re.search(r"box office", e["title"], re.I): ev[e["id"]] = e
print(len(ev), "événements", file=sys.stderr)
keep = []
for e in ev.values():
    full = requests.get(f"https://gamma-api.polymarket.com/events/{e['id']}", headers=H, timeout=60).json()
    keep.append({"id": full["id"], "title": full["title"], "closed": full["closed"], "end": full.get("endDate"), "start": full.get("startDate"),
                 "desc": (full.get("description") or "")[:600],
                 "markets": [{"id": m["id"], "q": m["question"], "tokens": json.loads(m["clobTokenIds"]) if m.get("clobTokenIds") else [],
                              "prices": m.get("outcomePrices"), "closedTime": m.get("closedTime"), "end": m.get("endDate"),
                              "git": m.get("groupItemTitle"), "fee": m.get("feeSchedule") or m.get("feeType")} for m in full["markets"]]})
with gzip.open(R / "evenements.json.gz", "wt") as f: json.dump(keep, f)
http = HttpClient(user_agent="curl/8") if "user_agent" in HttpClient.__init__.__code__.co_varnames else HttpClient()
def go(e):
    try: return len(fetch_event_trades(http, D, e["id"]))
    except Exception as x: return str(x)[:80]
with ThreadPoolExecutor(6) as ex: res = list(ex.map(go, [e for e in keep if e["closed"]]))
print(sum(r for r in res if isinstance(r, int)), "échanges;", [r for r in res if not isinstance(r, int)][:3])
