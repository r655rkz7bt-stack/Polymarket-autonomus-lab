import sys, re, statistics as st
sys.path.insert(0, "experiments/box_office/scripts"); sys.path.insert(0, "src")
from favori import *
title = {c["e"]["id"]: re.sub(r"\s*\(.*?\)|Opening Weekend Box Office.*|5-day|\bCont\.", "", c["e"]["title"]).strip(" '\"") + c["e"]["end"][:10] for c in C}
def dedup(bets):  # un seul pari par film (le premier événement rencontré)
    seen, out = set(), []
    for b in bets:
        k = title[b["evenement"]]
        if k in seen: continue
        seen.add(k); out.append(b)
    return out
for h, lo, hi in ((24, .5, 1), (36, .5, 1), (48, .5, 1), (12, .5, 1), (24, .6, .9), (36, .8, 1)):
    b = run(h, lo, hi); d = dedup(b)
    d.sort(key=lambda x: x["mois"]); half = len(d) // 2
    g = sorted((x["gain"] for x in d), reverse=True)
    v = verdict(d)
    print(f"h={h} {lo}-{hi}: bruts {len(b)} films {len(d)} rendement {v['rendement_moyen']:+.3f} t {v['confiance_evenements']:+.2f} | 1re moitié {sum(x['gain'] for x in d[:half])/half:+.3f} 2e {sum(x['gain'] for x in d[half:])/(len(d)-half):+.3f} | sans 3 meilleurs {sum(g[3:])/(len(g)-3):+.3f} | gagnés {sum(1 for x in d if x['gain']>0)}/{len(d)} attendus {sum(x['cout'] for x in d):.1f}")
