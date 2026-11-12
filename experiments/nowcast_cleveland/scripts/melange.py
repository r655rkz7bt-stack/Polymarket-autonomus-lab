"""Mélange géométrique marché^(1-w) × modèle^w (normalisé par événement), log-score et achats simulés au prix + 1 centime."""
import math, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from analyse import lignes

def blend(rows, w):
    evs = {}
    for r in rows:
        evs.setdefault(r["ev"], []).append(r)
    for rs in evs.values():
        sx = sum(max(r["px"], 0.001) for r in rs)
        z = [(max(r["px"], 0.001) / sx) ** (1 - w) * r["pm"] ** w for r in rs]
        s = sum(z)
        for r, v in zip(rs, z):
            r["pb"] = v / s
    return evs

for k in (1, 2, 4):
    rows = [r for r in lignes(k) if r["px"] is not None]
    print(f"\nk = {k}")
    for w in (0.0, 0.2, 0.35, 0.5):
        evs = blend(rows, w)
        ls = [math.log([r for r in rs if r["win"]][0]["pb"]) for rs in evs.values() if sum(r["win"] for r in rs) == 1]
        line = f"  w={w:.2f} log-score {sum(ls)/len(ls):+.3f}"
        if w > 0:
            for seuil in (0.05, 0.10, 0.15):
                bets = [r for rs in evs.values() for r in rs if r["pb"] - (r["px"] + 0.01) > seuil and 0.03 <= r["px"] <= 0.9]
                cost = sum(r["px"] + 0.01 for r in bets); gain = sum(r["win"] for r in bets)
                exp = sum(r["px"] for r in bets)
                nev = len({r["ev"] for r in bets})
                line += f" | >{seuil:.2f}: {len(bets)} paris ({nev} év.), {gain} gagnés / {exp:.1f} att., rendement {gain/cost-1 if cost else 0:+.0%}"
        print(line)
