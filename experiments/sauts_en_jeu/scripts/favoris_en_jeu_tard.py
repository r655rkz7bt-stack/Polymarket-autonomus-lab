"""Favoris acheté tard en match (T = coup d'envoi + 1, 2, 3 h), tennis et e-sport, tranches 0,65-0,80 / 0,80-0,90 / 0,90-0,97 (28/10/2026). Même méthode que outsiders_avant_match.py (delta négatif)."""
import sys, os
os.environ["COTE"] = "favoris"
sys.path.insert(0, "experiments/sauts_en_jeu/scripts"); sys.path.insert(0, "src")
import analyse as a
import outsiders_avant_match as o
for groupe in (("atp", "wta"), ("cs2", "lol", "dota2", "val")):
    MS = a.load(groupe); print(groupe, len(MS), "matchs", flush=True)
    for delta in (-0.5, -1, -2, -3):
        r = o.run(MS, delta)
        for lo, hi in ((0.65, 0.80), (0.80, 0.90), (0.90, 0.97)):
            print(f"  T = coup d'envoi + {-delta} h, prix {lo:.2f}-{hi:.2f}", o.fmt([x for x in r if lo <= x["cout"] < hi]), flush=True)
