"""Gagnant de saison : le OUI d'un candidat gagne-t-il aussi souvent que son prix, à H jours de la fin ?
Achats simulés (écart 0,01 + frais rate·p·(1−p)) : NON des candidats par tranche de prix, OUI des favoris.
Usage depuis experiments/saison_sport : PYTHONPATH=../../src python scripts/analyse.py"""
import json, math, sys, collections
from datetime import datetime, timezone
from polymarket_agent.idea_test import verdict, fee
ev = {e["id"]: e for e in json.load(open("donnees/evenements.json"))}
mk = {m["id"]: (m, e) for e in ev.values() for m in e["markets"]}
rows = [json.loads(l) for l in open("donnees/prix.jsonl")]
SP = float(sys.argv[1]) if len(sys.argv) > 1 else 0.01
BANDS = [(0.02, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 0.50), (0.50, 0.80), (0.80, 0.97)]
def dec(r):
    pts = [p for p in r["hist"] if p[0] <= r["t"]]
    if not pts or r["t"] - pts[-1][0] > 43200: return None
    return pts[-1][1]
cases = []
for r in rows:
    p = dec(r)
    if p is None: continue
    m, e = mk[r["id"]]
    cases.append({"h": r["h"], "p": p, "yes": m["yes_won"], "ev": e["id"], "rate": float(m["fee"] or 0),
                  "mois": datetime.fromtimestamp(r["t"], timezone.utc).strftime("%Y-%m")})
print("cas", len(cases), "événements", len({c["ev"] for c in cases}), "écart", SP)
def bets(sel, side):
    out = []
    for c in sel:
        pr = c["p"] if side == "yes" else 1 - c["p"]
        pay = min(0.99, pr + SP)
        cost = pay + fee(pay, c["rate"])
        win = c["yes"] if side == "yes" else not c["yes"]
        out.append({"gain": ((1.0 if win else 0.0) - cost) / cost, "evenement": c["ev"], "mois": c["mois"], "cout": pay, "win": win, "pr": pr})
    return out
for h in (3, 7, 14, 30, 60):
    for lo, hi in BANDS:
        sel = [c for c in cases if c["h"] == h and lo <= c["p"] < hi]
        if len(sel) < 30: continue
        row = []
        for side in ("yes", "no"):
            b = bets(sel, side)
            v = verdict(b)
            row.append(f"{side.upper()}: gagnés {sum(x['win'] for x in b)}/{sum(x['pr'] for x in b):.1f} rend {v['rendement_moyen']:+.3f} t_ev {v['confiance_evenements']:+.2f}")
        print(f"H={h:>2} j  p_oui {lo:.2f}-{hi:.2f}  n={len(sel):>4}  " + " | ".join(row))
