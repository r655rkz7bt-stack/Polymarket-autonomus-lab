"""Vague de volume, étape 2 : vrais échanges des preneurs (data-api, public, sans clé), marché par marché.

Usage : PYTHONPATH=src python experiments/vague_volume_backtest/releve_echanges.py [pages_max] [inverse]
Même format que `idea_test.fetch_event_trades` ([heure, jeton, côté, prix, parts]), deux différences :
- par marché (`market=<conditionId>`) et non par événement : un événement de 30 marchés atteint vite la
  limite de 11 pages ;
- on remonte le temps avec `end` (vérifié le 23/10/2026 : `end=X`, avec ou sans décalage, renvoie
  exactement les échanges d'horodatage ≤ X de la pagination) au lieu de s'arrêter à 11 pages, en partant
  de l'échéance réelle − 46 h (aucune décision après échéance − 48 h, achat au plus 2 h après).
Un marché est « tronqué » si `pages_max` pages (défaut 40) n'atteignent pas sa création : ses jours non
couverts sont écartés par l'analyse (champ `couvert_depuis`). Cache : donnees/echanges/<id>.json.gz."""
import concurrent.futures as cf
import gzip
import json
import sys
import threading
import time
from pathlib import Path

import requests

H = {"User-Agent": "curl/8"}
U = "https://data-api.polymarket.com/trades"
DIR = Path("experiments/vague_volume_backtest/donnees/echanges")
PAGES = int(sys.argv[1]) if len(sys.argv) > 1 else 40
markets = json.load(open("experiments/vague_volume_backtest/donnees/marches.json"))
if len(sys.argv) > 2 and sys.argv[2] == "inverse":  # second processus parallèle : part de la fin (cache partagé)
    markets.reverse()
DIR.mkdir(parents=True, exist_ok=True)
session = threading.local()


def get(params):
    s = getattr(session, "s", None) or requests.Session()
    session.s = s
    for attempt in range(5):
        try:
            r = s.get(U, headers=H, params=params, timeout=60)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 400:
                return None
        except (requests.RequestException, ValueError):
            pass
        time.sleep(2 ** attempt)
    raise RuntimeError("data-api muette")


def one(m):
    path = DIR / f"{m['market_id']}.json.gz"
    if path.exists():
        return "cache"
    x = m["extra"]
    end, rows, pages, done = x["deadline"] - 46 * 3600, [], 0, False
    while pages < PAGES and not done:
        chunk = []
        for off in range(0, 10001, 1000):
            b = get({"market": x["condition"], "limit": 1000, "offset": off, "end": end})
            pages += 1
            if not b:
                done = True; break
            chunk += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])]
                      for t in b if t.get("timestamp") and t.get("price") is not None]
            if len(b) < 1000:
                done = True; break
            if pages >= PAGES:
                break
        if not chunk:
            break
        if not done:  # on reprend à la plus vieille seconde vue, relue en entier
            oldest = min(r[0] for r in chunk)
            chunk = [r for r in chunk if r[0] > oldest]
            end = oldest
        rows += chunk
        if not done and oldest <= x["created"]:
            done = True
    covered = x["created"] if done else (min(r[0] for r in rows) if rows else end)
    path.write_bytes(gzip.compress(json.dumps({"couvert_depuis": covered, "complet": done, "pages": pages,
                                               "echanges": rows}).encode()))
    return "complet" if done else "tronqué"


from collections import Counter
c, t0 = Counter(), time.time()
with cf.ThreadPoolExecutor(6) as ex:
    for i, res in enumerate(ex.map(one, markets)):
        c[res] += 1
        if i % 1000 == 0:
            print(i, dict(c), round(time.time() - t0), "s", flush=True)
print("fini", dict(c))
