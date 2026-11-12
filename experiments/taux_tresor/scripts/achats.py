"""Achats simulés : premier jour où la chance du modèle (K) dépasse le prix + 0,02 d'écart + seuil, on achète ce côté au prix + 0,02
(un pari par marché, frais economics_fees ignorés : prix 0,05-0,95 seulement) ; rendement par mois et par sens."""
import json, os, sys, collections
D = os.path.join(os.path.dirname(__file__), "..", "donnees")
for K in sys.argv[1:]:
    o = json.load(open(os.path.join(D, f"obs_K{K}.json")))
    for seuil in (0.05, 0.10, 0.15):
        done, bets = set(), []
        for x in sorted(o, key=lambda x: x["jour"]):
            if x["id"] in done:
                continue
            for side, est, pr in ((1, x["p"], x["prix"] + 0.02), (0, 1 - x["p"], 1 - x["prix"] + 0.02)):
                if 0.05 <= pr <= 0.95 and est - pr >= seuil:
                    win = x["y"] if side == 1 else 1 - x["y"]
                    bets.append((x["mois"], x["sens"], side, pr, win, x["ev"])); done.add(x["id"]); break
        g = collections.defaultdict(list)
        for b in bets: g[b[0]].append(b)
        tot = sum(b[4] / b[3] - 1 for b in bets) / max(len(bets), 1)
        print(f"K={K} seuil {seuil}: {len(bets)} paris, gagnés {sum(b[4] for b in bets)} pour {sum(b[3] for b in bets):.1f} attendus, rendement {tot:+.1%} ;",
              " ; ".join(f"{m} {len(v)} paris {sum(b[4]/b[3]-1 for b in v)/len(v):+.0%} (OUI {sum(b[2] for b in v)})" for m, v in sorted(g.items())))
