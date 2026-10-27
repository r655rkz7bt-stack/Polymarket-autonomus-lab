"""27/10/2026 : relevé des événements politiques « à candidats » réglés (étiquette politics 2, negRisk, ≥ 5 marchés) depuis le 01/01/2026 et de leurs échanges réels, pour rejouer `outsiders_surcotes`
(somme des OUI > 1 : NON aux outsiders à 2-15 %). /events/keyset (curseur), data-api (cache gzip, 8 fils). Sortie : donnees/evenements.jsonl, donnees/echanges/. Racine du dépôt."""
import json, sys, requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
OUT = Path("experiments/outsiders_passe/donnees")
H = {"User-Agent": "curl/8"}
CH = ("id", "question", "outcomes", "outcomePrices", "clobTokenIds", "endDate", "startDate", "feeSchedule", "volumeNum", "closedTime", "groupItemTitle", "negRisk")
out, cur = {}, None
while True:
    p = {"tag_id": 2, "closed": "true", "limit": 100, "order": "endDate", "ascending": "false"}
    if cur: p["after_cursor"] = cur
    d = requests.get("https://gamma-api.polymarket.com/events/keyset", params=p, headers=H, timeout=120).json()
    ev = d.get("events") or []
    if not ev: break
    for e in ev:
        ms = e.get("markets") or []
        if e.get("negRisk") and len(ms) >= 5 and (e.get("endDate") or "9")[:10] >= "2026-01-01":
            out[e["id"]] = {"id": e["id"], "title": e.get("title"), "end": e.get("endDate"), "markets": [{k: m.get(k) for k in CH} for m in ms]}
    cur = d.get("next_cursor")
    if not cur or (ev[-1].get("endDate") or "9")[:10] < "2026-01-01": break
print("événements", len(out), "marchés", sum(len(e["markets"]) for e in out.values()), flush=True)
with open(OUT / "evenements.jsonl", "w") as f:
    for e in out.values(): f.write(json.dumps(e) + "\n")
http = HttpClient(min_interval=0.05)
def un(i): it.fetch_event_trades(http, OUT / "echanges", str(i)); return 1
with ThreadPoolExecutor(8) as ex: print("échanges", sum(ex.map(un, out)), flush=True)
