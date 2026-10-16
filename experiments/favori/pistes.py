"""Nouvelles pistes (16/10/2026) : mouvement récent du prix (suivre ou contrer), par famille.

Usage : python3 -I experiments/favori/pistes.py <dossier_de_travail>
Mêmes données et même règle que analyse.py (échéance ANNONCÉE, prix du dernier échange avant la
décision, jamais après). Pour chaque marché et instant : prix p de l'issue n°0 et prix p6 / p24
6 h et 24 h plus tôt. Signal « mouvement » = p − p6 (ou p − p24). Deux règles :
  suivre : acheter l'issue qui monte ; contrer : acheter l'issue qui baisse (au prix actuel).
"""
import bisect, glob, json, math, os, sys
from collections import defaultdict
from datetime import datetime

SP = sys.argv[1]
sys.path.insert(0, os.path.dirname(__file__))
from analyse_commun import family, fee_rate, ts  # noqa: E402

markets = {m["cid"]: m for m in json.load(open(f"{SP}/sm/markets.json"))}
HORIZONS = [2, 6, 24, 72]
rows = []  # (famille, h, p, p6, p24, gagnant0, frais, cid)
for path in glob.glob(f"{SP}/sm/trades/*.json"):
    cid = os.path.basename(path)[:-5]
    m = markets.get(cid)
    if not m:
        continue
    end, closed = ts(m.get("end")), ts(m.get("closed")) or ts(m.get("end"))
    if end is None or closed is None:
        continue
    pts = []
    for t in json.load(open(path)):
        try:
            p = float(t["price"])
            pts.append((int(t["timestamp"]), p if t["asset"] == m["tokens"][0] else 1 - p))
        except (KeyError, TypeError, ValueError):
            continue
    pts.sort()
    def at(when, max_age=3 * 3600):
        i = bisect.bisect_right(pts, (when, 2.0)) - 1
        return pts[i][1] if i >= 0 and when - pts[i][0] <= max_age else None
    for h in HORIZONS:
        when = end - h * 3600
        if when >= closed:
            continue
        p, p6, p24 = at(when, 1800), at(when - 6 * 3600), at(when - 24 * 3600)
        if p is None or not (0.03 <= p <= 0.97):
            continue
        rows.append((family(m), h, p, p6, p24, 1 if m["winner"] == m["tokens"][0] else 0, fee_rate(m["tags"]), cid))
print(len(rows), "cas")


def bet(r, side):  # side 0 : acheter l'issue n°0 au prix p ; 1 : l'issue n°1 à 1 − p
    price = r[2] if side == 0 else 1 - r[2]
    won = r[5] if side == 0 else 1 - r[5]
    cost = price + r[6] * price * (1 - price)
    return won - cost, cost


def report(title, sel_rule):
    print(f"\n### {title}\n| famille | paris | gagnés | rendement après frais |\n|---|---|---|---|")
    groups = defaultdict(list)
    for r in rows:
        side = sel_rule(r)
        if side is not None:
            groups[r[0]].append(bet(r, side) + (r[5] if side == 0 else 1 - r[5],))
            groups["TOUT"].append(groups[r[0]][-1])
    for f, v in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        if len(v) >= 40:
            g, c = sum(x[0] for x in v), sum(x[1] for x in v)
            print(f"| {f} | {len(v)} | {sum(x[2] for x in v) / len(v):.3f} | {100 * g / c:+.1f} % |")


for th in (0.05, 0.10):
    report(f"SUIVRE un mouvement de plus de {th} sur 6 h", lambda r, th=th: None if r[3] is None or abs(r[2] - r[3]) < th else (0 if r[2] > r[3] else 1))
    report(f"CONTRER un mouvement de plus de {th} sur 6 h", lambda r, th=th: None if r[3] is None or abs(r[2] - r[3]) < th else (1 if r[2] > r[3] else 0))
report("CONTRER un mouvement de plus de 0,10 sur 24 h", lambda r: None if r[4] is None or abs(r[2] - r[4]) < 0.10 else (1 if r[2] > r[4] else 0))
report("SUIVRE un mouvement de plus de 0,10 sur 24 h", lambda r: None if r[4] is None or abs(r[2] - r[4]) < 0.10 else (0 if r[2] > r[4] else 1))


# Stabilité : première moitié contre seconde moitié (date de clôture), par signal retenu.
def halves(title, fam_set, rule):
    out = []
    for name, keep in (("avant le 1/10", lambda d: d < "2026-10-01"), ("après le 1/10", lambda d: d >= "2026-10-01")):
        v = []
        for r in rows:
            d = (markets[r[7]].get("closed") or "")[:10]
            side = rule(r)
            if r[0] in fam_set and side is not None and keep(d):
                v.append(bet(r, side))
        g, c = sum(x[0] for x in v), sum(x[1] for x in v)
        out.append(f"{name} : {len(v)} paris, {100 * g / c:+.1f} %" if c else f"{name} : —")
    days = defaultdict(float)
    for r in rows:
        side = rule(r)
        if r[0] in fam_set and side is not None:
            days[(markets[r[7]].get("closed") or "")[:10]] += bet(r, side)[0]
    print(f"{title} : " + " | ".join(out) + f" | jours gagnants {sum(1 for v in days.values() if v > 0)}/{len(days)}")


print()
halves("Politique, SUIVRE > 0,05 sur 6 h", {"politique", "géopolitique"},
       lambda r: None if r[3] is None or abs(r[2] - r[3]) < 0.05 else (0 if r[2] > r[3] else 1))
halves("Crypto (seuils), CONTRER > 0,05 sur 6 h", {"crypto (seuils)"},
       lambda r: None if r[3] is None or abs(r[2] - r[3]) < 0.05 else (1 if r[2] > r[3] else 0))
halves("Crypto (seuils), CONTRER > 0,10 sur 24 h", {"crypto (seuils)"},
       lambda r: None if r[4] is None or abs(r[2] - r[4]) < 0.10 else (1 if r[2] > r[4] else 0))
halves("Crypto hausse/baisse, CONTRER > 0,05 sur 6 h", {"crypto hausse/baisse"},
       lambda r: None if r[3] is None or abs(r[2] - r[3]) < 0.05 else (1 if r[2] > r[3] else 0))
# Le contre-pari crypto : achète-t-il surtout l'issue bon marché (billet de loterie) ?
v = [(r, 1 if r[2] > r[3] else 0) for r in rows if r[0] == "crypto (seuils)" and r[3] is not None and abs(r[2] - r[3]) >= 0.05]
cheap = [x for x in v if (x[0][2] if x[1] == 0 else 1 - x[0][2]) < 0.3]
print(f"Crypto CONTRER : {len(cheap)} paris sur {len(v)} achètent une issue à moins de 0,30")
