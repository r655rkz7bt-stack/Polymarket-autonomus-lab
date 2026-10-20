"""Tennis : acheter l'OUTSIDER avant le match (le favori est trop cher). Univers du 22/09 au 19/10."""
import json, math, statistics as st, sys
from collections import defaultdict
from datetime import datetime
D = "donnees/ech"
rows = [r for r in json.load(open(f"{D}/univers.json")) if len(r["chemin"]) > 30]
def t_of(v): return st.mean(v) / st.stdev(v) * math.sqrt(len(v)) if len(v) > 2 and st.stdev(v) > 0 else 0
def at(path, when):
    last = None
    for t, p in path:
        if t > when: break
        last = p
    return last
FAM = {"itf": "tennis", "atp": "tennis", "wta": "tennis", "cs2": "esport", "lol": "esport", "dota2": "esport", "val": "esport", "r6siege": "esport"}
for fam_name in ("tennis", "esport", "autres"):
  for label, delta in (("2 h 30", 9000), ("1 h", 3600), ("5 min", 300)):
    for mode, sp in (("preneur", 0.01), ("posé", -0.01)):
        res = defaultdict(list); band = defaultdict(list); tour = defaultdict(list); allg = []
        for r in rows:
            if FAM.get(r["sport"], "autres") != fam_name: continue
            start = datetime.fromisoformat(r["debut"]).timestamp()
            p = at(r["chemin"], start - delta)
            if p is None: continue
            dog = 1 if p >= 0.5 else 0
            pd = 1 - p if dog == 1 else p
            if not 0.05 <= pd <= 0.30: continue
            won = (not r["gagne0"]) if dog == 1 else r["gagne0"]
            c = pd + sp
            if sp > 0: c += float(r["taux"] or 0.04) * c * (1 - c)
            g = ((1 if won else 0) - c) / c
            allg.append((g, pd, won)); res[datetime.fromtimestamp(start).strftime("%V")].append(g)
            band["0,05-0,15" if pd < 0.15 else "0,15-0,30"].append(g); tour[r["sport"]].append(g)
        if not allg: continue
        g = [x[0] for x in allg]
        print(f"{fam_name:6} {label:6} {mode:7}: {len(g):4} outsiders, prix {st.mean(x[1] for x in allg):.3f} gagnés {st.mean(x[2] for x in allg):.3f} "
              f"rendement {st.mean(g):+.3f} t {t_of(g):+.2f} | sem " + " ".join(f"{k}:{st.mean(v):+.2f}" for k, v in sorted(res.items()))
              + " | " + " ".join(f"{k}:{len(v)}/{st.mean(v):+.2f}" for k, v in sorted(band.items()))
              + (" | " + " ".join(f"{k}:{len(v)}/{st.mean(v):+.2f}" for k, v in sorted(tour.items(), key=lambda kv: -len(kv[1]))[:4]) if fam_name != "autres" else ""))
