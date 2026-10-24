"""NON des candidats de primaires cotés LO-HI à J-d (prix = dernier point horaire ; écart d'achat supposé SPREAD ; frais du marché). À lancer depuis experiments/primaires/."""
import json, bisect, os, sys
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import fee, verdict
rows = [json.loads(l) for l in open("donnees/prix.jsonl")]
SPREAD = float(os.environ.get("SPREAD", 0.015))
def price_at(r, d):
    T = r["endts"] - d * 86400; ts = [p[0] for p in r["h"]]
    i = bisect.bisect_right(ts, T) - 1
    return (r["h"][i][1], ts[i]) if i >= 0 and T - ts[i] <= 12 * 3600 else (None, None)
for LO, HI in ((0.05, 0.15), (0.10, 0.30), (0.15, 0.40), (0.05, 0.40)):
    print(f"== NON, candidats cotés {LO}-{HI}")
    for d in (3, 7, 14, 21, 30):
        bets = []
        for r in rows:
            p, t = price_at(r, d)
            if p is None or not LO <= p <= HI: continue
            cost = 1 - p + SPREAD
            if cost >= 0.995: continue
            g = ((1 - r["won"]) - cost - fee(1 - p, r["rate"])) / cost
            bets.append({"evenement": r["event"], "cout": cost, "gain": g, "mois": __import__("datetime").datetime.fromtimestamp(r["endts"]).strftime("%Y-%m"), "won": 1 - r["won"]})
        if len(bets) < 20: print(f" J-{d}: {len(bets)} paris"); continue
        v = verdict(bets, min_bets=30)
        wins = sum(b["won"] for b in bets); exp = sum(b["cout"] for b in bets)
        print(f" J-{d}: {len(bets)} paris ({len({b['evenement'] for b in bets})} événements), NON gagné {wins} / {exp:.1f} attendus, rendement {sum(b['gain'] for b in bets)/len(bets)*100:+.1f} %, t événement {v['confiance_evenements']}, z prix {v['z_prix']}, verdict {v['verdict']}")
