"""Profondeur des favoris d'e-sport à 0,65-0,80, H-3 / H-6 (28/10/2026) : parts achetées par des preneurs à <= prix + 2 centimes dans l'heure qui suit T."""
import sys, os, math
os.environ["COTE"] = "favoris"
sys.path.insert(0, "experiments/sauts_en_jeu/scripts"); sys.path.insert(0, "src")
import analyse as a
import outsiders_avant_match as o
from polymarket_agent import idea_test as it
groups = ("cs2", "lol", "dota2", "val")
MS = a.load(groups)
byid = {M["e"]["id"]: M for M in MS}
for delta in (3, 6):
    r = [x for x in o.run(MS, delta) if 0.65 <= x["cout"] < 0.80]
    for x in r:
        M = byid[x["evenement"]]; T = M["start"] - delta * 3600
        buy0 = a.price_at(M, T, fresh=3 * 3600) >= 0.5
        tok, oth = (M["toks"][0], M["toks"][1]) if buy0 else (M["toks"][1], M["toks"][0])
        lim = x["cout"] + 0.02
        x["depth"] = sum(t[4] for t in M["trades"] if T <= t[0] <= T + 3600 and ((t[1] == tok and t[2] == "BUY" and t[3] <= lim) or (t[1] == oth and t[2] == "SELL" and 1 - t[3] <= lim)))
    print(f"=== H-{delta} : 0,65-0,80, {len(r)} paris")
    for seuil in (0, 20, 100, 400, 1000):
        sub = [x for x in r if x["depth"] >= seuil]
        print(f"  parts achetables >= {seuil:5d}", o.fmt(sub), flush=True)
