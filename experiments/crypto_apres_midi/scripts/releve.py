"""27/10/2026 : échelles quotidiennes « Bitcoin/Ethereum/Solana/XRP above ___ on <date> ? » (étiquette multi-strikes 102516), réglées sur la bougie 1 minute de Binance de 12 h (Est).
Question : juste APRÈS midi, le résultat est connu (une bougie suffit) mais le règlement UMA prend des heures : le côté gagnant se paie-t-il encore moins de 0,97 ?
Relevé /events/keyset?tag_id=102516 (curseur), puis échanges réels de chaque événement (data-api, cache gzip). Sortie : donnees/echelles.jsonl, donnees/echanges/. Racine du dépôt."""
import json, sys, requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
OUT = Path("experiments/crypto_apres_midi/donnees"); (OUT / "echanges").mkdir(parents=True, exist_ok=True)
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
CH = ("id", "question", "outcomes", "outcomePrices", "clobTokenIds", "endDate", "startDate", "feeSchedule", "volumeNum", "closedTime", "groupItemTitle")
out, cur = {}, None
while True:
    p = {"tag_id": 102516, "closed": "true", "limit": 100, "order": "endDate", "ascending": "false"}
    if cur: p["after_cursor"] = cur
    d = s.get("https://gamma-api.polymarket.com/events/keyset", params=p, timeout=120).json()
    ev = d.get("events") or []
    if not ev: break
    for e in ev:
        if "above" in (e.get("title") or "").lower() and " on " in (e.get("title") or ""):
            out[e["id"]] = {"id": e["id"], "title": e["title"], "end": e.get("endDate"), "markets": [{k: m.get(k) for k in CH} for m in e.get("markets") or []]}
    cur = d.get("next_cursor")
    if not cur or (ev[-1].get("endDate") or "9")[:10] < "2026-03-01": break
print("événements", len(out), flush=True)
with open(OUT / "echelles.jsonl", "w") as f:
    for e in out.values(): f.write(json.dumps(e) + "\n")
http = HttpClient(min_interval=0.03)
def un(e): it.fetch_event_trades(http, OUT / "echanges", str(e["id"])); return 1
with ThreadPoolExecutor(16) as ex: print("échanges", sum(ex.map(un, out.values())), flush=True)
