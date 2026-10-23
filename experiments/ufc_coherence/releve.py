"""Piste n° 6 (ufc_coherence, 23/10/2026) : relevé des combats UFC réglés (Gamma, série 38) et de leurs échanges réels.
Écrit donnees/combats.json (un combat par événement : marchés par type, jetons, résultat) et le cache d'échanges.
À lancer depuis experiments/ufc_coherence/ avec PYTHONPATH=../../src."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test

D = Path("donnees")
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
http = HttpClient()
events, off = [], 0
while True:
    r = S.get("https://gamma-api.polymarket.com/events", params={"series_id": 38, "closed": "true", "limit": 100, "offset": off,
                                                                 "order": "endDate", "ascending": "false"}, timeout=60).json()
    if not r:
        break
    events += r; off += 100
    print(off, len(events), events[-1]["endDate"], flush=True)
    if off >= 3000:
        break

def one(e):
    ms = []
    for m in e.get("markets") or []:
        tok = json.loads(m.get("clobTokenIds") or "[]")
        if len(tok) != 2:
            continue
        ms.append({"q": m["question"], "type": m.get("sportsMarketType"), "yes": tok[0], "no": tok[1], "final": m.get("outcomePrices"),
                   "frais": m.get("feeSchedule"), "ligne": m.get("line"), "debut": m.get("gameStartTime"), "id": m["id"]})
    tr = idea_test.fetch_event_trades(http, D / "cache", str(e["id"]))
    return {"slug": e["slug"], "titre": e["title"], "id": e["id"], "fin": e.get("endDate"), "marches": ms, "echanges": len(tr)}

with ThreadPoolExecutor(6) as pool:
    out = list(pool.map(one, events))
json.dump(out, open(D / "combats.json", "w"))
print(len(out), "combats", sum(o["echanges"] for o in out), "échanges")
