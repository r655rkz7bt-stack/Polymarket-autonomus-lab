"""Sonde : combien de marchés réglés d'un type sportif (Gamma `sportsMarketType`) existent ?
Recherche par dichotomie du dernier décalage qui renvoie encore des marchés (sans tout télécharger).
Usage : python experiments/score_exact_poisson/sonde_compte.py soccer_exact_score [volume_min]"""
import sys

import requests

S = requests.Session()
S.headers["User-Agent"] = "polymarket-autonomous-lab"
TYPE = sys.argv[1]
VMIN = sys.argv[2] if len(sys.argv) > 2 else None


def n_at(offset: int) -> int:
    p = {"sports_market_types": TYPE, "closed": "true", "limit": 1, "offset": offset}
    if VMIN:
        p["volume_num_min"] = VMIN
    d = S.get("https://gamma-api.polymarket.com/markets", params=p, timeout=60).json()
    return len(d) if isinstance(d, list) else 0


lo, hi = 0, 1
while n_at(hi):
    lo, hi = hi, hi * 2
    if hi > 2_000_000:
        break
while hi - lo > 1:
    mid = (lo + hi) // 2
    if n_at(mid):
        lo = mid
    else:
        hi = mid
print(TYPE, "volume_min", VMIN, "marchés réglés ≈", lo + 1)
