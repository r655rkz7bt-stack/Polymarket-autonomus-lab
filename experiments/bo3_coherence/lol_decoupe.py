"""LoL seul, « Under » des totaux (h=3, fenêtre 6 h, AVEC 50-50) : par BO, par mois, par tranche de prix payé. Usage : python experiments/bo3_coherence/lol_decoupe.py"""
import runpy
import sys
from collections import defaultdict
from pathlib import Path

sys.argv = [sys.argv[0]]
g = runpy.run_path(str(Path(__file__).resolve().parent / "sous_2_5_50_50.py"), run_name="importe")
paris, resume = g["paris"], g["resume"]
lol = [x for x in paris(3, 6) if x["serie"] == "lol"]
print("\n# LoL seul :", len(lol), "paris")
for key, f in (("bo", lambda x: f"BO{x['bo']}"), ("mois", lambda x: x["mois"]),
               ("prix", lambda x: "<0,45" if x["cout"] < 0.45 else "0,45-0,55" if x["cout"] < 0.55 else "0,55-0,70" if x["cout"] < 0.70 else ">=0,70")):
    d = defaultdict(list)
    for x in lol:
        d[f(x)].append(x)
    for k, v in sorted(d.items()):
        print(resume(v, f"LoL, {key} = {k}"))
