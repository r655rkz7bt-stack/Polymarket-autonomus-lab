"""Le NON à 0,10-0,30 vient-il d'événements dont la somme des prix OUI dépasse 1 (surcote d'ensemble) ? Somme des OUI des candidats
relevés à H jours (prix horaire connu à l'instant) ; on sépare les événements par cette somme et on retire « Uniswap Cup »."""
import json, collections
from polymarket_agent.idea_test import fee, verdict
ev = {e["id"]: e for e in json.load(open("donnees/evenements.json"))}
mk = {m["id"]: (m, e) for e in ev.values() for m in e["markets"]}
P = collections.defaultdict(dict)
for l in open("donnees/prix.jsonl"):
    r = json.loads(l)
    pts = [p for p in r["hist"] if p[0] <= r["t"]]
    if pts and r["t"] - pts[-1][0] <= 43200: P[(mk[r["id"]][1]["id"], r["h"])][r["id"]] = pts[-1][1]
for h in (7, 14):
    for name, ok in (("tous", lambda s, t: True), ("sans Uniswap Cup", lambda s, t: "Uniswap" not in t), ("somme OUI ≤ 1,15", lambda s, t: s <= 1.15), ("somme OUI > 1,15", lambda s, t: s > 1.15)):
        b = []
        for (eid, hh), d in P.items():
            if hh != h: continue
            s = sum(d.values()); t = ev[eid]["title"]
            if not ok(s, t): continue
            for mid, p in d.items():
                if not 0.10 <= p < 0.30: continue
                m = mk[mid][0]; pay = 1 - p + 0.01; c = pay + fee(pay, float(m["fee"] or 0))
                b.append({"gain": ((0 if m["yes_won"] else 1) - c) / c, "evenement": eid, "mois": "x", "cout": pay, "win": not m["yes_won"]})
        if len(b) < 15: print(h, name, "n =", len(b)); continue
        v = verdict(b)
        print(f"H={h:>2} {name:20} n={len(b)} ev={len({x['evenement'] for x in b})} gagnés {sum(x['win'] for x in b)}/{sum(x['cout'] for x in b):.1f} rend {v['rendement_moyen']:+.3f} t_ev {v['confiance_evenements']:+.2f}")
