"""Échanges (vrais prix payés) des événements « posts Truth Social » -> donnees/cache/echanges_<id>.json.gz (ignoré par Git)."""
import json, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
http = HttpClient(timeout=40, max_retries=3, backoff=2.0, min_interval=0.05, user_agent="curl/8")
cache = Path("experiments/truth_social/donnees/cache")
ev = json.load(open("experiments/truth_social/donnees/evenements.json"))
def un(e):
    n = len(it.fetch_event_trades(http, cache, str(e["id"])))
    return e["slug"][-26:], n
with ThreadPoolExecutor(6) as ex:
    for slug, n in ex.map(un, ev): print(slug, n, flush=True)
