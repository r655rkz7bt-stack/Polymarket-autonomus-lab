"""28/10/2026 : le NON bon marché (pari à la baisse) peut-il être couvert par le OUI bon marché (pari à la hausse) ? Pour les marchés « above » (et « less than »),
un pari par marché et par côté (le plus ancien instant de décision où le côté, payé 0,10-0,45, est acheté dans l'heure) ; rendement hebdomadaire de chaque côté
contre le rendement de la semaine du Bitcoin (barres Binance), puis du panier à parts égales. Usage : PYTHONPATH=src python analyse_couverture.py"""
import json, math, datetime as dt
from collections import defaultdict
from polymarket_agent import idea_test as it
S = json.load(open("experiments/crypto_pourquoi/donnees/snaps.json"))
spot = json.load(open("experiments/crypto_pourquoi/donnees/spot_BTC.json")); ts = [r[0] for r in spot]
import bisect
def px(t): return spot[max(bisect.bisect_right(ts, t) - 1, 0)][4]
def semaine(t):
    d = dt.datetime.utcfromtimestamp(t); lundi = (d - dt.timedelta(days=d.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    return int(lundi.timestamp())
def paris(cote):
    par = defaultdict(list)
    for s in S:
        p = s["paid"] if cote == "non" else s["paid_yes"]
        if s["kind"] in ("above", "below") and p is not None and 0.10 <= p <= 0.45: par[s["id"]].append((s, p))
    out = []
    for k, v in par.items():
        s, p = max(v, key=lambda x: x[0]["h"]); fee = s["rate"] * p * (1 - p)
        won = (1 - s["won"]) if cote == "non" else s["won"]
        out.append(dict(gain=(won - p - fee) / p, cout=p, evenement=s["ev"], mois=s["mois"], gagne=won, T=s["T"], sem=semaine(s["T"]), kind=s["kind"]))
    return out
def show(label, b):
    if len(b) < 10: print(f"| {label} | {len(b)} |"); return None
    v = it.verdict(b); g = sum(x["gagne"] for x in b); a = sum(x["cout"] for x in b)
    print(f"| {label} | {v['paris']} | {v['evenements']} | {v['rendement_moyen']:+.1%} | t évén. {v['confiance_evenements']:+.2f} | gagnés {g} / attendus {a:.1f} (z {v['z_prix']:+.2f}) | {v['verdict']} |"); return v
B = {c: paris(c) for c in ("non", "oui")}
for c in B:
    for kind in ("above", "below"): show(f"{c.upper()} payé 0,10-0,45, genre {kind}", [b for b in B[c] if b["kind"] == kind])
    show(f"{c.upper()} payé 0,10-0,45, tous", B[c])
def hebdo(b):
    w = defaultdict(list)
    for x in b: w[x["sem"]].append(x["gain"])
    return {k: sum(v) / len(v) for k, v in w.items() if len(v) >= 3}
H = {c: hebdo(B[c]) for c in B}
def corr(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n; sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else float("nan")
def ols(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n; b = sum((a - mx) * (d - my) for a, d in zip(x, y)) / sum((a - mx) ** 2 for a in x); return my - b * mx, b
print("\n== rendement hebdomadaire (semaines avec ≥ 3 paris du côté) contre le rendement de la semaine du Bitcoin ==")
for c in ("non", "oui"):
    ks = sorted(H[c]); x = [(px(k + 7 * 86400) / px(k) - 1) * 100 for k in ks]; y = [H[c][k] * 100 for k in ks]
    a, b = ols(x, y)
    print(f"{c.upper()} : {len(ks)} semaines, corrélation {corr(x, y):+.2f}, pente {b:+.2f}, rendement à cours stable {a:+.1f} %, rendement moyen {sum(y)/len(y):+.1f} %")
ks = sorted(set(H["non"]) & set(H["oui"]))
if len(ks) >= 5:
    x = [(px(k + 7 * 86400) / px(k) - 1) * 100 for k in ks]; yp = [50 * (H["non"][k] + H["oui"][k]) for k in ks]
    a, b = ols(x, yp)
    print(f"PANIER 50/50 : {len(ks)} semaines communes, corrélation {corr(x, yp):+.2f}, pente {b:+.2f}, rendement à cours stable {a:+.1f} %, moyen {sum(yp)/len(yp):+.1f} %, écart-type {math.sqrt(sum((v - sum(yp)/len(yp))**2 for v in yp)/(len(yp)-1)):.1f}")
    yn = [100 * H["non"][k] for k in ks]; print(f"NON seul sur les mêmes semaines : moyen {sum(yn)/len(yn):+.1f} %, écart-type {math.sqrt(sum((v - sum(yn)/len(yn))**2 for v in yn)/(len(yn)-1)):.1f}")
