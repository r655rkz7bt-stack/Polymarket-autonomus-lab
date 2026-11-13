"""Log-score du modèle contre le prix, puis achats simulés (vendeur = prix horaire + demi-écart, frais finance 0,04·p(1−p))."""
import json, math, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from polymarket_agent import idea_test

rows = json.loads((Path(__file__).parent / "donnees" / "lignes.json").read_text())
EPS = 0.005
ls = lambda p, y: math.log(max(EPS, min(1 - EPS, p)) if y == 1 else max(EPS, min(1 - EPS, 1 - p)))
print("délai  n   log-score modèle  marché")
for j in (14, 10, 7, 5, 3, 2, 1):
    r = [x for x in rows if x["j"] == j and x["won"] in (0, 1) and x["sym"]]
    print(j, len(r), round(sum(ls(x["modele"], x["won"]) for x in r) / len(r), 4), round(sum(ls(x["prix"], x["won"]) for x in r) / len(r), 4))

def achats(seuil, demi, jours, pmin=0.0, pmax=1.0):
    bets = []
    for x in rows:
        if x["j"] not in jours or not x["sym"] or x["won"] not in (0, 1):
            continue
        for side in (1, 0):
            q = x["modele"] if side else 1 - x["modele"]
            ask = (x["prix"] if side else 1 - x["prix"]) + demi
            if not (pmin <= ask <= pmax) or ask >= 0.995:
                continue
            fee = 0.04 * ask * (1 - ask)
            if q - ask - fee > seuil:
                pay = 1.0 if (x["won"] == 1) == (side == 1) else 0.0
                bets.append({"event": f'{x["event"]}', "month": x["mois"], "price": ask, "cost": ask + fee, "payout": pay,
                             "q": q, "co": x["co"], "rang": x["rang"], "j": x["j"], "side": side})
    return bets

for seuil in (0.02, 0.04, 0.06, 0.10):
    for jours in ((14, 10, 7), (5, 3, 2), (14, 10, 7, 5, 3, 2, 1)):
        b = achats(seuil, 0.01, jours)
        if not b:
            continue
        # un pari par (événement, société, côté) : le premier délai seulement (paris liés)
        seen, bb = set(), []
        for x in sorted(b, key=lambda x: -x["j"]):
            k = (x["event"], x["co"], x["side"])
            if k not in seen:
                seen.add(k); bb.append(x)
        ret = sum(x["payout"] - x["cost"] for x in bb) / sum(x["cost"] for x in bb)
        won = sum(x["payout"] for x in bb); exp = sum(x["price"] for x in bb); expm = sum(x["q"] for x in bb)
        print(f"seuil {seuil} délais {jours}: {len(bb)} paris, {len({x['event'] for x in bb})} événements, gagnés {won:.0f} pour {exp:.1f} attendus au prix ({expm:.1f} au modèle), rendement {ret:+.1%}")
b = achats(0.04, 0.01, (14, 10, 7, 5, 3, 2, 1))
seen, bb = set(), []
for x in sorted(b, key=lambda x: -x["j"]):
    k = (x["event"], x["co"], x["side"])
    if k not in seen:
        seen.add(k); bb.append(x)
for x in bb:
    x.update(gain=(x["payout"] - x["cost"]) / x["cost"], evenement=x["month"], mois=x["month"], cout=x["price"])
print(json.dumps(idea_test.verdict(bb), ensure_ascii=False, default=str)[:1500])
for x in bb:
    print(x["month"], x["rang"], x["co"], "OUI" if x["side"] else "NON", "j-", x["j"], "payé", round(x["price"], 3), "modèle", round(x["q"], 3), "→", x["payout"])
