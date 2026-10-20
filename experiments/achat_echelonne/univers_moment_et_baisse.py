"""Univers large (tous les matchs à deux issues, 22/09-19/10) : acheter le favori d'avant-match après
une baisse de d points PENDANT le match, contre l'acheter avant le match (et à quel moment)."""
import json
import math
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime

D = "donnees/ech"
rows = [r for r in json.load(open(f"{D}/univers.json")) if len(r["chemin"]) > 30]
SPREAD = float(sys.argv[1]) if len(sys.argv) > 1 else 0.01
LO, HI = 0.70, 0.95


def t_of(v):
    return st.mean(v) / st.stdev(v) * math.sqrt(len(v)) if len(v) > 2 and st.stdev(v) > 0 else 0


def at(path, when):
    last = None
    for t, p in path:
        if t > when:
            break
        last = p
    return last


def cost(p, rate):
    c = min(p + SPREAD, 0.995)
    return c + rate * c * (1 - c)


games = []
for r in rows:
    start = datetime.fromisoformat(r["debut"]).timestamp()
    p = at(r["chemin"], start - 300)
    if p is None:
        continue
    fav = 0 if p >= 0.5 else 1
    pf = p if fav == 0 else 1 - p
    if not LO <= pf <= HI:
        continue
    won = r["gagne0"] if fav == 0 else not r["gagne0"]
    path = [(t, q if fav == 0 else 1 - q) for t, q in r["chemin"]]
    games.append({"r": r, "start": start, "pf": pf, "won": won, "path": path, "rate": float(r["taux"] or 0.04),
                  "week": datetime.fromtimestamp(start).strftime("%G-S%V"), "sport": r["sport"]})
print(f"{len(rows)} matchs relevés ; {len(games)} avec un favori à {LO}-{HI} juste avant le début ; écart {SPREAD}")

# 1. Moment d'achat avant le match (achat échelonné dans le temps)
for label, delta in (("2 h 30 avant", 9000), ("1 h avant", 3600), ("5 min avant", 300)):
    g = []
    for x in games:
        q = at(x["path"], x["start"] - delta)
        if q is not None and 0.5 <= q < 0.99:
            c = cost(q, x["rate"])
            g.append(((1 if x["won"] else 0) - c) / c)
    if g: print(f"favori acheté {label:12}: {len(g)} achats, rendement {st.mean(g):+.4f} (t {t_of(g):+.2f})")

# 2. Achat après une baisse pendant le match
print()
for d in (0.05, 0.10, 0.15, 0.20, 0.30):
    res = []
    for x in games:
        hit = next(((t, q) for t, q in x["path"] if t >= x["start"] and q <= x["pf"] - d), None)
        if not hit or not 0.05 < hit[1] < 0.95:
            continue
        c = cost(hit[1], x["rate"])
        res.append({"g": ((1 if x["won"] else 0) - c) / c, "p": hit[1], "won": x["won"], "week": x["week"], "sport": x["sport"],
                    "pf": x["pf"]})
    g = [y["g"] for y in res]
    weeks = defaultdict(list)
    sports = defaultdict(list)
    bands = defaultdict(list)
    for y in res:
        weeks[y["week"]].append(y["g"])
        sports[y["sport"]].append(y["g"])
        bands["< 0,5" if y["p"] < 0.5 else "0,5-0,7" if y["p"] < 0.7 else "≥ 0,7"].append(y["g"])
    print(f"baisse ≥ {d:.2f} : {len(g)} achats, prix {st.mean(y['p'] for y in res):.3f}, gagnés {st.mean(y['won'] for y in res):.3f}, "
          f"rendement {st.mean(g):+.4f} (t {t_of(g):+.2f})")
    print("    semaines", {k: (len(v), round(st.mean(v), 3)) for k, v in sorted(weeks.items())})
    print("    prix    ", {k: (len(v), round(st.mean(v), 3)) for k, v in sorted(bands.items())})
    top = sorted(sports.items(), key=lambda kv: -len(kv[1]))[:8]
    print("    sports  ", {k: (len(v), round(st.mean(v), 3)) for k, v in top})
