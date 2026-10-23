"""Vague de volume, contrôle du règlement : le dernier échange réel avant la clôture redonne-t-il le résultat
officiel (Gamma outcomePrices) ? Échantillon tiré au hasard (graine fixe) parmi les marchés relevés.

Usage : PYTHONPATH=src python experiments/vague_volume_backtest/controle_reglement.py [taille]
Lecture : prix du OUI au dernier échange avant `closedTime` (data-api, plus récents d'abord, 1 page) ;
« lisible » si ce prix est ≥ 0,9 ou ≤ 0,1 ; « d'accord » si (prix > 0,5) = OUI gagné."""
import json
import random
import sys
import time
from collections import Counter

import requests

N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
markets = json.load(open("experiments/vague_volume_backtest/donnees/marches.json"))
random.seed(23)
sample = random.sample(markets, min(N, len(markets)))
c = Counter()
bad = []
for m in sample:
    x = m["extra"]
    for attempt in range(5):
        try:
            b = requests.get("https://data-api.polymarket.com/trades", headers={"User-Agent": "curl/8"}, timeout=60,
                             params={"market": x["condition"], "limit": 500, "end": x["closed"]}).json()
        except (requests.RequestException, ValueError):
            b = None
        if isinstance(b, list):
            break
        time.sleep(2 ** attempt)
    else:
        c["erreur_api"] += 1
        continue
    if not b:
        c["sans_echange"] += 1
        continue
    t = max(b, key=lambda t: int(t["timestamp"]))
    p = float(t["price"]) if t["asset"] == m["yes_token"] else 1 - float(t["price"])
    c["lus"] += 1
    c["lisible"] += p >= 0.9 or p <= 0.1
    ok = (p > 0.5) == bool(m["won"])
    c["d_accord"] += ok
    c["d_accord_lisibles"] += ok and (p >= 0.9 or p <= 0.1)
    if not ok:
        bad.append((m["market_id"], m["question"][:70], round(p, 3), m["won"]))
print(dict(c))
print("désaccords :", bad[:15])
json.dump({"compte": dict(c), "desaccords": bad},
          open("experiments/vague_volume_backtest/donnees/controle_reglement.json", "w"), ensure_ascii=False)
