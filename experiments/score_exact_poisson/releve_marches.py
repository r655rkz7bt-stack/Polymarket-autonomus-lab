"""Piste n° 1 (score_exact_poisson), étape 1 : relève TOUS les marchés « score exact » réglés de Gamma.

Gamma refuse les décalages au-delà de 2 000 (/markets) : on lit /markets/keyset (curseur `after_cursor`),
filtré sur le type sportif `soccer_exact_score`. On ne garde que les champs utiles (petit fichier).
Usage (depuis la racine du dépôt) :
    python experiments/score_exact_poisson/releve_marches.py
    -> experiments/score_exact_poisson/donnees/marches_score_exact.json.gz (ignoré par Git)"""
import gzip
import json
import sys
import time
from pathlib import Path

import requests

D = Path(__file__).resolve().parent / "donnees"
D.mkdir(exist_ok=True)
TYPE = sys.argv[1] if len(sys.argv) > 1 else "soccer_exact_score"
OUT = D / f"marches_{'score_exact' if TYPE == 'soccer_exact_score' else TYPE}.json.gz"
S = requests.Session()
S.headers["User-Agent"] = "polymarket-autonomous-lab"
CHAMPS = ("id", "conditionId", "question", "slug", "endDate", "gameStartTime", "closedTime", "outcomes", "outcomePrices",
          "clobTokenIds", "volumeNum", "feesEnabled", "feeSchedule", "umaResolutionStatus", "negRisk", "groupItemTitle",
          "sportsMarketType", "line", "lastTradePrice")


def get(params):
    for k in range(6):
        try:
            r = S.get("https://gamma-api.polymarket.com/markets/keyset", params=params, timeout=90)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(2 ** k)
    raise SystemExit(f"Gamma ne répond pas ({params})")


rows, cursor, pages = [], None, 0
while True:
    p = {"sports_market_types": TYPE, "closed": "true", "limit": 100}
    if cursor:
        p["after_cursor"] = cursor
    d = get(p)
    for m in d.get("markets") or []:
        row = {k: m.get(k) for k in CHAMPS}
        ev = (m.get("events") or [{}])[0]
        row["event_id"], row["event_slug"], row["event_title"] = ev.get("id"), ev.get("slug"), ev.get("title")
        rows.append(row)
    pages += 1
    cursor = d.get("next_cursor")
    if pages % 20 == 0:
        print(pages, "pages,", len(rows), "marchés", flush=True)
    if not cursor or not d.get("markets"):
        break
OUT.write_bytes(gzip.compress(json.dumps(rows).encode()))
print("total", len(rows), "marchés,", len({r["event_id"] for r in rows}), "événements ->", OUT)
