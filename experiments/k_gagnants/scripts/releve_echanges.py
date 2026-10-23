"""Échanges réels (data-api, preneurs) des événements « k gagnants » : donnees/cache/echanges_<id>.json.gz."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from polymarket_agent import idea_test as it
from polymarket_agent.http_client import HttpClient
D = Path("experiments/k_gagnants/donnees")
evs = json.load(open(D / "evs.json"))
http = HttpClient(timeout=40, min_interval=0.0, user_agent="curl/8")
def go(e):
    try:
        return e["id"], len(it.fetch_event_trades(http, D / "cache", e["id"]))
    except Exception as ex:
        return e["id"], repr(ex)
with ThreadPoolExecutor(6) as ex:
    for i, r in ex.map(go, evs):
        print(i, r, flush=True)
