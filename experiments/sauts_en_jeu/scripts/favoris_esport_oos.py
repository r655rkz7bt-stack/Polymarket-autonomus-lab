"""Hors échantillon : favoris d'e-sport 0,65-0,80 à H-1, H-3, H-6, H-12, relevé de février à juillet (DONNEES=experiments/sauts_en_jeu/donnees/avant). 28/10/2026."""
import sys, os, collections
os.environ["COTE"] = "favoris"
sys.path.insert(0, "experiments/sauts_en_jeu/scripts"); sys.path.insert(0, "src")
import analyse as a
import outsiders_avant_match as o
groups = tuple((sys.argv[1] if len(sys.argv) > 1 else "cs2,lol,dota2,val").split(","))
MS = a.load(groups)
print(groups, len(MS), "matchs (février-juillet)", flush=True)
for delta in (1, 3, 6, 12):
    r = o.run(MS, delta)
    print(f"=== H-{delta}")
    for lo, hi in ((0.55, 0.65), (0.65, 0.80), (0.80, 0.90)):
        print(f"  {lo:.2f}-{hi:.2f}", o.fmt([x for x in r if lo <= x["cout"] < hi]), flush=True)
    b = [x for x in r if 0.65 <= x["cout"] < 0.80]
    for sp in groups: print(f"     0,65-0,80 {sp}", o.fmt([x for x in b if x["sport"] == sp]))
    bymois = collections.defaultdict(list)
    for x in b: bymois[x["mois"]].append(x)
    for m, v in sorted(bymois.items()): print(f"     0,65-0,80 mois {m}", o.fmt(v))
