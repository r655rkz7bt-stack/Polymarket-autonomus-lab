"""28/10/2026 : règle « avant le fix de 12 h (Est) » sur les tranches « between » : (R1) NON de la tranche centrale (OUI coté 0,55-0,97) et (R2) OUI des tranches de queue (payé 0,02-0,25), à 3 h et 6 h
avant le règlement. Un pari par marché (le plus ancien instant H dans la liste où le côté est acheté dans l'heure), vrais échanges, frais payés ; paris liés = un événement (un actif un jour).
Jugement idea_test.verdict, par mois, par actif, par moitié (janvier-mai / juin-octobre), nombre de réglages essayés ; profondeur : parts achetables. Lit donnees/snaps_saison.json.
Usage : PYTHONPATH=src python regle_fix.py"""
import json, math, os, datetime as dt
from collections import defaultdict
from polymarket_agent import idea_test as it
S = json.load(open("experiments/crypto_pourquoi/donnees/" + ("snaps_saison_2025.json" if os.environ.get("HOLDOUT") == "1" else "snaps_saison.json")))
def paris(cote, lo, hi, heures, genre="between"):
    par = defaultdict(list)
    for s in S:
        if s["kind"] != genre or s["h"] not in heures: continue
        p = s["pn"] if cote == "non" else s["py"]
        if p is not None and lo <= p <= hi: par[s["id"]].append((s, p))
    out = []
    for k, v in par.items():
        s, p = max(v, key=lambda x: x[0]["h"])
        w = (1 - s["won"]) if cote == "non" else s["won"]
        out.append(dict(gain=(w - p - s["rate"] * p * (1 - p)) / p, cout=p, evenement=s["ev"], mois=s["mois"], gagne=w, a=s["a"], h=s["h"], pyes=s["pyes"]))
    return out
def show(label, b):
    if len(b) < 15: print(f"| {label} | {len(b)} |"); return
    v = it.verdict(b); g = sum(x["gagne"] for x in b); a = sum(x["cout"] for x in b)
    print(f"| {label} | {v['paris']} | {v['evenements']} | {v['rendement_moyen']:+.1%} | t évén. {v['confiance_evenements']:+.2f} | {g:g} / {a:.1f} (z {v['z_prix']:+.2f}) | {v['mois_gagnants']} mois | {v['verdict']} |")
    return v
print("| règle | paris | évén. | rendement | t | gagnés/attendus | mois | verdict |")
for nom, cote, lo, hi in (("R1 NON tranche centrale (NON payé 0,03-0,45)", "non", 0.03, 0.45), ("R2 OUI queues (payé 0,02-0,25)", "oui", 0.02, 0.25)):
    for heures in ((3,), (6,), (3, 6), (4,), (2, 3, 4, 6)):
        show(f"{nom}, H−{'/'.join(map(str, heures))}", paris(cote, lo, hi, heures))
print("\n== détail R1 (H−3/6) et R2 (H−3/6) ==")
for nom, cote, lo, hi in (("R1", "non", 0.03, 0.45), ("R2", "oui", 0.02, 0.25)):
    b = paris(cote, lo, hi, (3, 6))
    for mo in sorted({x["mois"] for x in b}): show(f"{nom} mois {mo}", [x for x in b if x["mois"] == mo])
    for a in ("BTC", "ETH", "SOL", "XRP"): show(f"{nom} actif {a}", [x for x in b if x["a"] == a])
    show(f"{nom} janvier-mai", [x for x in b if x["mois"] <= "2026-05"]); show(f"{nom} juin-octobre", [x for x in b if x["mois"] >= "2026-06"])
    for lo2, hi2 in ((0.03, 0.10), (0.10, 0.25), (0.25, 0.45)) if nom == "R1" else ((0.02, 0.06), (0.06, 0.12), (0.12, 0.25)):
        show(f"{nom} payé {lo2}-{hi2}", [x for x in b if lo2 <= x["cout"] < hi2])
    # sans les 5 meilleurs jours
    by = defaultdict(list)
    for x in b: by[x["evenement"]].append(x)
    top = sorted(by, key=lambda e: -sum(y["gain"] for y in by[e]))[:10]
    show(f"{nom} sans ses 10 meilleurs événements", [x for e, v in by.items() if e not in top for x in v])
