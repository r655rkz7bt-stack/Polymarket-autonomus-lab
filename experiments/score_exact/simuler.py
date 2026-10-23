"""Piste n° 1 : paris simulés à partir de paris_<decal>_<fenetre>.json (analyse.py). Un pari = un marché-score, un côté.
Gain par euro misé = résultat / (prix payé + frais) − 1. usage : simuler.py FICHIER [ÉCART_min]"""
import json, sys, math, collections
sys.path.insert(0, "src")
from polymarket_agent import idea_test as it
rows = json.load(open(sys.argv[1]))
print(len(rows), "candidats,", len({r["match"] for r in rows}), "matchs")
def bet(r): 
    c = r["cout"] + r["fee"]
    return dict(gain=r["gain_brut"] / c - 1, evenement=r["match"], mois=r["mois"], cout=r["cout"])
print("\n== Calibrage brut : gagnés contre attendus par le prix payé, par côté et tranche ==")
for side in ("oui", "non"):
    b = collections.defaultdict(lambda: [0, 0, 0.0, 0.0])
    for r in rows:
        if r["side"] != side: continue
        k = "<0.03" if r["cout"] < 0.03 else "0.03-0.08" if r["cout"] < 0.08 else "0.08-0.15" if r["cout"] < 0.15 else "0.15-0.30" if r["cout"] < 0.30 else "0.30-0.70" if r["cout"] < 0.70 else "0.70-0.90" if r["cout"] < 0.90 else "0.90-0.97" if r["cout"] < 0.97 else ">=0.97"
        x = b[k]; x[0] += 1; x[1] += r["gain_brut"]; x[2] += r["cout"]; x[3] += (r["gain_brut"] / (r["cout"] + r["fee"]) - 1)
    for k in sorted(b):
        n, w, e, g = b[k]; print(f"{side:4s} {k:10s} n={n:5d} gagnés={w:6.0f} attendus={e:7.1f} rendement/mise={g/n:+.3f}")
print("\n== Modèle contre marché : on achète si modèle − (prix+frais) > écart ==")
for ecart in (0.02, 0.04, 0.06, 0.10):
    for side in ("oui", "non"):
        bets = [bet(r) for r in rows if r["side"] == side and 0.02 <= r["cout"] <= 0.98 and (r["modele"] - r["cout"] - r["fee"]) > ecart]
        if not bets: print(f"écart {ecart} {side}: aucun"); continue
        v = it.verdict(bets); print(f"écart {ecart:.2f} {side:3s}: n={v['paris']:5d} matchs={v['evenements']:4d} rend={v['rendement_moyen']:+.3f} t_ev={v['confiance_evenements']:+.2f} z_prix={v['z_prix']:+.2f} mois={v['mois_gagnants']} -> {v['verdict']}")

print("\n== Par score (côté OUI, prix payé 0,02-0,50) : gagnés contre attendus par le prix, et fréquence prévue par le modèle ==")
sc = collections.defaultdict(lambda: [0, 0, 0.0, 0.0])
for r in rows:
    if r["side"] != "oui" or not (0.02 <= r["cout"] <= 0.50): continue
    x = sc[r["score"]]; x[0] += 1; x[1] += r["gain_brut"]; x[2] += r["cout"]; x[3] += r["modele"]
for k, (n, w, e, mo) in sorted(sc.items(), key=lambda kv: -kv[1][0])[:12]:
    print(f"{k:6s} n={n:5d} gagnés={w:5.0f} prix={e:7.1f} modèle={mo:7.1f}")
