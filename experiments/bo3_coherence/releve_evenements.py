"""Pistes n° 4 (bo3_coherence) et n° 5 (tennis_sets_coherence), étape 1 : relève les événements RÉGLÉS d'une
série Gamma (e-sport ou tennis) avec tous leurs marchés (vainqueur, carte / set 1, handicap, total).

Gamma refuse les décalages au-delà de 5 000 (/events) : on lit /events/keyset (curseur `after_cursor`).
Usage (depuis la racine du dépôt) :
    python experiments/bo3_coherence/releve_evenements.py cs2 lol dota2 val     (e-sport)
    python experiments/bo3_coherence/releve_evenements.py atp wta               (tennis)
    -> experiments/bo3_coherence/donnees/evenements_<série>.json.gz (ignoré par Git)"""
import gzip
import json
import sys
import time
from pathlib import Path

import requests

D = Path(__file__).resolve().parent / "donnees"
D.mkdir(exist_ok=True)
SERIES = {"cs2": 10310, "lol": 10311, "dota2": 10309, "val": 10369, "atp": 10365, "wta": 10366, "itf": 11634}
S = requests.Session()
S.headers["User-Agent"] = "polymarket-autonomous-lab"
CHAMPS = ("id", "conditionId", "question", "endDate", "gameStartTime", "closedTime", "outcomes", "outcomePrices",
          "clobTokenIds", "volumeNum", "feesEnabled", "feeSchedule", "umaResolutionStatus", "groupItemTitle",
          "sportsMarketType", "line")


def get(params):
    for k in range(6):
        try:
            r = S.get("https://gamma-api.polymarket.com/events/keyset", params=params, timeout=120)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(2 ** k)
    raise SystemExit(f"Gamma ne répond pas ({params})")


for nom in sys.argv[1:]:
    out, cursor, pages = [], None, 0
    while True:
        p = {"series_id": SERIES[nom], "closed": "true", "limit": 100}
        if cursor:
            p["after_cursor"] = cursor
        d = get(p)
        for e in d.get("events") or []:
            out.append({"id": e.get("id"), "slug": e.get("slug"), "title": e.get("title"), "startDate": e.get("startDate"),
                        "endDate": e.get("endDate"), "serie": nom,
                        "markets": [{k: m.get(k) for k in CHAMPS} for m in e.get("markets") or []]})
        pages += 1
        cursor = d.get("next_cursor")
        if pages % 10 == 0:
            print(nom, pages, "pages,", len(out), "événements", flush=True)
        if not cursor or not d.get("events"):
            break
    path = D / f"evenements_{nom}.json.gz"
    path.write_bytes(gzip.compress(json.dumps(out).encode()))
    print(nom, "total", len(out), "événements ->", path, flush=True)
