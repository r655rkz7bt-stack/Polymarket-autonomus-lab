"""Robustesse des paris de test_passe.py : par détroit et par côté, première / seconde moitié des dates cibles,
sans les 3 meilleurs paris, sans le meilleur événement. Usage : python analyse_paris.py [paris.json]"""
import collections
import json
import sys

sys.path.insert(0, "src")
from polymarket_agent import idea_test as it  # noqa: E402

path = sys.argv[1] if len(sys.argv) > 1 else "experiments/detroits/donnees/paris.json"
data = json.load(open(path))


def court(v):
    if v.get("paris", 0) == 0:
        return "aucun pari"
    return (f"{v['paris']} paris, {v.get('evenements')} év., rendement {v.get('rendement_moyen', 0):+.3f}, "
            f"t év. {v.get('confiance_evenements')}, z {v.get('z_prix')}, mois {v.get('mois_gagnants')} → {v['verdict']}")


for nom, d in data.items():
    bets = d["paris"]
    if not bets:
        continue
    print(f"\n=== {nom} : {court(d['verdict'])}")
    for det in sorted({b["detroit"] for b in bets}):
        sub = [b for b in bets if b["detroit"] == det]
        print(f"  {det:10s} {court(it.verdict(sub, min_bets=1))}")
    evs = sorted({b["mois"] + b["evenement"] for b in bets})
    jours = sorted({b["jour"] for b in bets})
    cut = jours[len(jours) // 2]
    print(f"  1re moitié (avant {cut}) : {court(it.verdict([b for b in bets if b['jour'] < cut], min_bets=1))}")
    print(f"  2e moitié               : {court(it.verdict([b for b in bets if b['jour'] >= cut], min_bets=1))}")
    top = sorted(bets, key=lambda b: -b["gain"])[3:]
    print(f"  sans les 3 meilleurs    : {court(it.verdict(top, min_bets=1))}")
    par_ev = collections.defaultdict(float)
    for b in bets:
        par_ev[b["evenement"]] += b["gain"]
    best = max(par_ev, key=par_ev.get)
    print(f"  sans le meilleur év. ({best}) : {court(it.verdict([b for b in bets if b['evenement'] != best], min_bets=1))}")
    for cote in ("OUI", "NON"):
        sub = [b for b in bets if b["cote"] == cote]
        if sub:
            print(f"  {cote} : {court(it.verdict(sub, min_bets=1))} ; prix payé moyen {sum(b['cout'] for b in sub) / len(sub):.3f}")
    hs = collections.defaultdict(list)
    for b in bets:
        hs["h ≤ 7" if b["h"] <= 7 else "h 8-13" if b["h"] <= 13 else "h ≥ 14"].append(b["gain"])
    print("  par horizon :", {k: (len(v), round(sum(v) / len(v), 3)) for k, v in sorted(hs.items())})
