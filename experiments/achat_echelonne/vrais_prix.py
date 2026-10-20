"""Outsiders de tennis et favoris d'e-sport aux prix RÉELLEMENT payés par les preneurs."""
import json
import math
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime

sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict  # noqa: E402

D = "donnees/ech"
paths = {r["slug"]: r["chemin"] for r in json.load(open(f"{D}/univers.json"))}
rows = [r for r in json.load(open(f"{D}/trades.json")) if r.get("echanges") and len(r.get("toks") or []) == 2]
LEAD = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0  # heures avant le début


def at(path, when):
    last = None
    for t, p in path:
        if t > when:
            break
        last = p
    return last


def paid(trades, token, other, t0, t1):
    """Premier prix payé par un preneur pour acheter `token` entre t0 et t1 (achat du jeton, ou vente
    de l'autre issue à p = jeton à 1 − p) : le prix qu'on aurait payé en achetant à t0."""
    pts = sorted((t[0], t[3] if t[1] == token else 1 - t[3]) for t in trades
                 if t0 <= t[0] <= t1 and ((t[1] == token and t[2] == "BUY") or (t[1] == other and t[2] == "SELL")))
    return pts[0][1] if pts else None


for side, fams, lo, hi in (("outsider", ("itf", "atp", "wta"), 0.05, 0.30), ("favori", ("cs2", "lol", "dota2"), 0.70, 0.95),
                           ("favori", ("itf", "atp", "wta"), 0.70, 0.95)):
    groups = defaultdict(list)
    missing = 0
    for r in rows:
        if r["sport"] not in fams or r["slug"] not in paths:
            continue
        start = datetime.fromisoformat(r["debut"]).timestamp()
        t0 = start - LEAD * 3600
        p = at(paths[r["slug"]], t0)
        if p is None:
            continue
        fav = 0 if p >= 0.5 else 1
        pick = fav if side == "favori" else 1 - fav
        ref = p if pick == 0 else 1 - p
        if not lo <= ref <= hi:
            continue
        token, other = r["toks"][pick], r["toks"][1 - pick]
        c = paid(r["echanges"], token, other, t0, start)
        if c is None or not 0.01 < c < 0.99:
            missing += 1
            continue
        c_fee = c + float(r["taux"] or 0.05) * c * (1 - c)
        won = (r["gagne0"] if pick == 0 else not r["gagne0"])
        g = ((1 if won else 0) - c_fee) / c_fee
        groups[r["sport"]].append({"gain": g, "evenement": r["slug"], "mois": datetime.fromtimestamp(start).strftime("%G-S%V"),
                                   "cout": c, "ref": ref, "won": won})
    print(f"\n== {side} {fams} {lo}-{hi}, acheté {LEAD} h avant au premier vrai prix payé (sans échange : {missing})")
    everything = [b for v in groups.values() for b in v]
    for name, bets in sorted(groups.items()) + [("ensemble", everything)]:
        if not bets:
            continue
        v = verdict(bets, min_bets=20)
        print(f"  {name:9} {v['paris']:4} paris, prix payé {st.mean(b['cout'] for b in bets):.3f} (historique {st.mean(b['ref'] for b in bets):.3f}), "
              f"gagnés {st.mean(b['won'] for b in bets):.3f}, rendement {v['rendement_moyen']:+.3f}, confiance {v['confiance_paris']:+.2f}, "
              f"semaines {v['mois_gagnants']} {v['mois']} → {v['verdict']}")
        if name in ("itf", "ensemble") and side == "outsider":
            print("            par prix :", v["par_prix"])
