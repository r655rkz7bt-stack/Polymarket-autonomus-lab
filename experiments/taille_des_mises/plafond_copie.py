"""Rejeu (27/10/2026, demande d'Etienne « regarde ce qui marchait quand on était en croissance ») : la règle d'entrée en vigueur
au capital principal (12 opérations, 12 h, croissance ≥ 0,02, t ≥ 1,0), avec un plafond sur chaque mise copiée (part du capital
du fantôme). Même approximation que experiments/regle_confiance/rejouer.py (copie au prorata, sans frais ni carnet).

Usage : bash scripts/fetch_data.sh ; .venv/bin/python experiments/taille_des_mises/plafond_copie.py
"""
import sys
from datetime import timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "regle_confiance"))
import rejouer as r
ghosts = r.load()
def current_now(st, held, now):
    ok = {}
    for name, s in st.items():
        age = (now - s["start"]).total_seconds() / 3600 if s["start"] else 0
        if (s["n"] >= 12 and age >= 12 and s["growth"] >= 0.02 and s["t"] >= 1.0) or (name in held and s["growth"] >= 0 and s["t"] >= 0):
            ok[name] = s
    best = sorted(ok, key=lambda k: -ok[k]["growth"])[:5]
    total = sum(ok[k]["growth"] for k in best)
    if total <= 0: return {}
    return {k: min((0.5 / len(best) + 0.5 * ok[k]["growth"] / total) * (0.5 if ok[k]["n"] < 30 else 1.0), 0.7) for k in best}
first = min(g["start"] for g in ghosts.values() if g["start"]); end = max(t["close"] for g in ghosts.values() for t in g["trades"])
mid = first + (end - first) / 2
caps = [None, 0.10, 0.05, 0.03, 0.02]   # plafond de la mise COPIÉE, en part du capital du fantôme copié
res = {c: [0.0, 0.0, 0.0, 0.0] for c in caps}  # misé, résultat 1re moitié, 2e moitié, misé total
now = first.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1); held = set()
while now <= end:
    st = {}
    for name, g in ghosts.items():
        done = [t for t in g["trades"] if t["close"] <= now]
        if done: st[name] = dict(r.stats(done), start=g["start"])
    w = current_now(st, held, now); held = set(w)
    half = 1 if now < mid else 2
    for name, x in w.items():
        for t in ghosts[name]["trades"]:
            if now <= t["open"] < now + timedelta(hours=1):
                for c in caps:
                    stake = t["cost"] if c is None else min(t["cost"], c * 1000)
                    res[c][0] += x * stake; res[c][half] += x * stake * t["pnl"] / t["cost"]
    now += timedelta(hours=1)
for c in caps:
    s, a, b, _ = res[c]
    print(f"plafond {('aucun' if c is None else f'{c:.0%}'):6s}: misé {s:6.0f} €, 1re moitié {a:+5.0f} €, 2e moitié {b:+5.0f} €, total {a+b:+5.0f} € ({(a+b)/s*100:+.1f} % par euro)")
