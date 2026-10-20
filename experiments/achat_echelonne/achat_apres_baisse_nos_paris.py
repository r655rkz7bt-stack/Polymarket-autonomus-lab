"""Achat SEUL après une baisse : le favori qu'on détient (ou qu'on visait) perd d points ; on achète à ce moment."""
import json
import math
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime

D = "donnees/ech"
rows = [r for r in json.load(open(f"{D}/paths.json")) if len(r["chemin"]) > 3]
SPREAD, RATE = 0.01, 0.04
fee = lambda p: RATE * p * (1 - p)


def ts(x):
    return datetime.fromisoformat(x).timestamp()


def t_of(v):
    return st.mean(v) / st.stdev(v) * math.sqrt(len(v)) if len(v) > 2 and st.stdev(v) > 0 else 0


for d in (0.05, 0.10, 0.15, 0.20, 0.30):
    res, by_day, by_px = [], defaultdict(list), defaultdict(list)
    for r in rows:
        p0, t0 = r["prix"], ts(r["ouvert"])
        hit = next(((t, p) for t, p in r["chemin"] if t > t0 and p <= p0 - d), None)
        if not hit or not 0.05 < hit[1] < 0.95:
            continue
        c = hit[1] + SPREAD
        c += fee(c)
        g = (r["paiement"] - c) / c
        res.append((g, hit[1], r["paiement"]))
        by_day[r["ouvert"][:10]].append(g)
        by_px["< 0,5" if hit[1] < 0.5 else "0,5-0,7" if hit[1] < 0.7 else "≥ 0,7"].append(g)
    g = [x[0] for x in res]
    print(f"baisse de {d:.2f} : {len(g)} achats, prix moyen {st.mean(x[1] for x in res):.3f}, gagnés {st.mean(x[2] for x in res):.3f}, "
          f"rendement {st.mean(g):+.3f} (t {t_of(g):+.2f}) | jours {dict((k, round(st.mean(v), 2)) for k, v in sorted(by_day.items()))} "
          f"| prix {dict((k, (len(v), round(st.mean(v), 2))) for k, v in sorted(by_px.items()))}")
