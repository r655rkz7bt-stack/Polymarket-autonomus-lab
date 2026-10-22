"""Piste n° 11 : NON des OUI à 2-15 % longtemps avant la fin (prix du CLOB ; les prix payés sont dans prix_payes.py)."""
import json, sys, bisect, math, datetime as dt
sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict
S = json.load(open("experiments/non_aux_drames/donnees/selection.json"))
P = json.load(open("experiments/non_aux_drames/donnees/prix.json"))
# contrôle du règlement : le dernier prix doit être du bon côté
ok = bad = 0
for m in S:
    h = P[m["id"]]
    if not h: continue
    last = h[-1][1]
    if (last > 0.5) == bool(m["won_yes"]): ok += 1
    else: bad += 1
print("contrôle du règlement (dernier prix du bon côté) :", ok, "/", ok + bad)
def price_at(h, t):
    i = bisect.bisect_right([x[0] for x in h], t) - 1
    return h[i][1] if i >= 0 else None
def run(days, lo, hi, minvol=5000, spread=0.01, label=""):
    bets = []
    for m in S:
        h = P[m["id"]]
        if not h or m["vol"] < minvol: continue
        t0 = m["t_close"] - days * 86400
        if t0 < m["t_start"] + 2 * 86400: continue
        y = price_at(h, t0)
        if y is None or not lo <= y <= hi: continue
        cost = min(0.999, 1 - y + spread)
        rate = float((m["fs"] or {}).get("rate") or 0) if m["fees"] else 0.0
        fee = rate * cost * (1 - cost)
        gain = ((1 if not m["won_yes"] else 0) - cost - fee) / (cost + fee)
        bets.append(dict(gain=gain, evenement=m["ev"], mois=dt.datetime.utcfromtimestamp(t0).strftime("%Y-%m"), cout=cost))
    v = verdict(bets) if bets else {"paris": 0}
    return v
rows = []
for days in (7, 14, 30, 60):
    for lo, hi in ((0.02, 0.05), (0.05, 0.10), (0.10, 0.15), (0.02, 0.15)):
        v = run(days, lo, hi)
        rows.append((days, lo, hi, v))
        if v["paris"]:
            print(f"T-{days:>2} j, OUI {lo:.2f}-{hi:.2f} : {v['paris']:>3} paris, rendement NON {v['rendement_moyen']:+.3f}, t événements {v['confiance_evenements']:+.2f}, z prix {v['z_prix']:+.2f}, mois gagnants {v['mois_gagnants']}, {v['verdict']}")
print("--- robustesse (T-60 j et T-30 j, OUI 0,02-0,15) : volume et écart achat-vente")
for days in (30, 60):
    for minvol in (5000, 20000, 100000):
        for sp in (0.01, 0.02):
            v = run(days, 0.02, 0.15, minvol, sp)
            if v["paris"]:
                print(f"T-{days} j, volume ≥ {minvol:>6}, écart {sp}: {v['paris']:>3} paris, rendement {v['rendement_moyen']:+.3f}, t événements {v['confiance_evenements']:+.2f}, z prix {v['z_prix']:+.2f}, {v['verdict']}")
