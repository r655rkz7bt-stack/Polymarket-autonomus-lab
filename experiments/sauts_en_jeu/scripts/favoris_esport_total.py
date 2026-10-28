"""Favoris d'e-sport sur TOUT le relevé (février-octobre 2026) : bandes 0,55-0,65, 0,65-0,80, 0,80-0,90, 0,65-0,90 à H-1, H-3, H-6, H-12, par jeu. 28/10/2026."""
import sys, os, collections
from pathlib import Path
os.environ["COTE"] = "favoris"
sys.path.insert(0, "experiments/sauts_en_jeu/scripts"); sys.path.insert(0, "src")
import analyse as a
import outsiders_avant_match as o
groups = tuple((sys.argv[1] if len(sys.argv) > 1 else "cs2,lol,dota2,val").split(","))
MS = []
for d in ("experiments/sauts_en_jeu/donnees", "experiments/sauts_en_jeu/donnees/avant"):
    a.D = Path(d); MS += a.load(groups)
print(groups, len(MS), "matchs (février-octobre)", flush=True)
for delta in (1, 3, 6, 12):
    r = o.run(MS, delta)
    print(f"=== H-{delta}")
    for lo, hi in ((0.55, 0.65), (0.65, 0.80), (0.80, 0.90), (0.65, 0.90), (0.90, 0.97)):
        print(f"  {lo:.2f}-{hi:.2f}", o.fmt([x for x in r if lo <= x["cout"] < hi]), flush=True)
    b = [x for x in r if 0.65 <= x["cout"] < 0.90]
    for sp in groups: print(f"     0,65-0,90 {sp}", o.fmt([x for x in b if x["sport"] == sp]))
    bymois = collections.defaultdict(list)
    for x in b: bymois[x["mois"]].append(x)
    print("     par mois :", {m: round(100 * sum(y['gain'] for y in v) / len(v), 1) for m, v in sorted(bymois.items())})
