"""28/10/2026 : lit donnees/snaps.json (écrit par modele.py) et répond : (1) le modèle sans drift (volatilité réalisée) bat-il le prix du OUI au log-score ?
(2) parmi les NON payés 0,10-0,45 (un pari par marché : le plus ancien instant de décision où le NON est dans la plage et acheté dans l'heure), le gain dépend-il
de l'écart modèle − prix ? Usage : PYTHONPATH=src python analyse.py"""
import json, math, sys
from collections import defaultdict
from polymarket_agent import idea_test as it
S = json.load(open("experiments/crypto_pourquoi/donnees/snaps.json"))
EPS = 1e-3
def ls(p, y): p = min(max(p, EPS), 1 - EPS); return math.log(p if y else 1 - p)
print(f"{len(S)} instants, {len({s['id'] for s in S})} marchés, {len({s['ev'] for s in S})} événements")
print("\n== (1) log-score du modèle contre le prix (OUI), instants où le prix du OUI est entre 0,05 et 0,95 ==")
for kind in ("above", "below", "reach", "dip", None):
    for h in (3, 6, 12, 24):
        rows = [s for s in S if s["h"] == h and (kind is None or s["kind"] == kind) and 0.05 <= s["pyes"] <= 0.95]
        if len(rows) < 30: continue
        for v in ("0.8", "1.0", "1.25"):
            d = [ls(r["pm"][v], r["won"]) - ls(r["pyes"], r["won"]) for r in rows]
            ev = defaultdict(list)
            for r, x in zip(rows, d): ev[r["ev"]].append(x)
            m = [sum(x) / len(x) for x in ev.values()]; mu = sum(m) / len(m); sd = math.sqrt(sum((x - mu) ** 2 for x in m) / max(len(m) - 1, 1))
            print(f"{str(kind):6s} h={h:2d} vol×{v:4s} n={len(rows):5d} modèle − prix = {sum(d)/len(d):+.4f} (t par événement {mu / (sd / math.sqrt(len(m))) if sd else 0:+.2f})  "
                  f"OUI réel {sum(r['won'] for r in rows)/len(rows):.3f} prix moyen {sum(r['pyes'] for r in rows)/len(rows):.3f} modèle moyen {sum(r['pm'][v] for r in rows)/len(rows):.3f}")
print("\n== (2) NON payé 0,10-0,45, un pari par marché, selon l'écart modèle − prix (vol ×1,0) ==")
by_m = defaultdict(list)
for s in S:
    if s["paid"] is not None and 0.10 <= s["paid"] <= 0.45: by_m[s["id"]].append(s)
bets = []
for k, v in by_m.items():
    s = max(v, key=lambda x: x["h"])   # le plus ancien instant
    fee = s["rate"] * s["paid"] * (1 - s["paid"])
    won = 1 - s["won"]
    bets.append(dict(gain=(won - s["paid"] - fee) / s["paid"], cout=s["paid"], evenement=s["ev"], mois=s["mois"], gagne=won, h=s["h"], kind=s["kind"], a=s["a"],
                     edge={v_: (1 - s["pm"][v_]) - s["paid"] for v_ in s["pm"]}, pmn=1 - s["pm"]["1.0"]))
def show(label, b):
    if len(b) < 10: print(f"| {label} | {len(b)} |"); return
    v = it.verdict(b); g = sum(x["gagne"] for x in b); a = sum(x["cout"] for x in b)
    print(f"| {label} | {v['paris']} | {v['evenements']} | {v['rendement_moyen']:+.1%} | t évén. {v['confiance_evenements']:+.2f} | gagnés {g} / attendus {a:.1f} (z {v['z_prix']:+.2f}) | modèle attend {sum(x['pmn'] for x in b):.1f} | {v['verdict']} |")
show("tous", bets)
for v_ in ("0.8", "1.0", "1.25"):
    for lo, hi in ((-9, 0), (0, 0.05), (0.05, 0.10), (0.10, 9)):
        show(f"vol ×{v_}, écart modèle−prix du NON {lo}..{hi}", [b for b in bets if lo <= b["edge"][v_] < hi])
for kind in ("above", "below", "reach", "dip"): show(f"genre {kind}", [b for b in bets if b["kind"] == kind])
for a in ("BTC", "ETH", "SOL", "XRP", "DOGE", "BNB"): show(f"actif {a}", [b for b in bets if b["a"] == a])
for lo, hi in ((0.10, 0.20), (0.20, 0.30), (0.30, 0.45)): show(f"payé {lo}-{hi}", [b for b in bets if lo <= b["cout"] < hi])
for h in (3, 6, 12, 24): show(f"instant h={h}", [b for b in bets if b["h"] == h])
for mo in sorted({b["mois"] for b in bets}): show(f"mois {mo}", [b for b in bets if b["mois"] == mo])
