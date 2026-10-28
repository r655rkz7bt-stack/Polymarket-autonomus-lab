"""Favoris d'e-sport à 0,65-0,80, 3 à 6 h avant le coup d'envoi (28/10/2026) : robustesse (mois, jeu, 50-50 comptés, bornes de prix, profondeur)."""
import sys, math, os, collections
os.environ["COTE"] = "favoris"
sys.path.insert(0, "experiments/sauts_en_jeu/scripts"); sys.path.insert(0, "src")
import analyse as a
import outsiders_avant_match as o
from polymarket_agent import idea_test as it
MS = a.load(("cs2", "lol", "dota2", "val"))
def show(titre, r):
    print(f"{titre:44s}", o.fmt(r), flush=True)
for delta in (3, 6):
    print(f"=== H-{delta}")
    r = o.run(MS, delta)
    base = [x for x in r if 0.65 <= x["cout"] < 0.80]
    show("0,65-0,80", base)
    for sp in ("cs2", "lol", "dota2", "val"): show(f"  jeu {sp}", [x for x in base if x["sport"] == sp])
    bymois = collections.defaultdict(list)
    for x in base: bymois[x["mois"]].append(x)
    for m, v in sorted(bymois.items()): show(f"  mois {m}", v)
    for lo, hi in ((0.60, 0.75), (0.62, 0.78), (0.67, 0.82), (0.70, 0.85), (0.65, 0.72), (0.72, 0.80)):
        show(f"  bande {lo:.2f}-{hi:.2f}", [x for x in r if lo <= x["cout"] < hi])
    # moitiés par date
    srt = sorted(base, key=lambda x: x["mois"]); h = len(srt) // 2
    show("  1re moitié (dates)", srt[:h]); show("  2e moitié (dates)", srt[h:])
o.INCL = True
print("=== 50-50 comptés à 0,5")
for delta in (3, 6):
    r = o.run(MS, delta); show(f"H-{delta} 0,65-0,80 (50-50 inclus)", [x for x in r if 0.65 <= x["cout"] < 0.80])
