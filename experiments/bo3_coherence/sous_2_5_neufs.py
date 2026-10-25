"""Contrôle du 25/10 : « Under » des totaux de cartes (h=3, fenêtre 6 h, AVEC 50-50) sur les matchs du nouveau tirage qui n'étaient PAS
dans le tirage du 23/10 (celui qui a servi à trouver et régler l'idée) : un vrai échantillon neuf, même règle, aucun réglage.
Usage : python experiments/bo3_coherence/sous_2_5_neufs.py <ancien_echantillon.json>"""
import json
import runpy
import sys
from pathlib import Path

ancien = set(json.loads(Path(sys.argv[1]).read_text()))
HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0]]
g = runpy.run_path(str(HERE / "sous_2_5_50_50.py"), run_name="importe")  # imprime aussi la table complète (ignorée ici)
cas, paris, resume = g["cas_list"], g["paris"], g["resume"]
neufs = {c["event"] for c in cas} - ancien
print(f"\n# {len(neufs)} matchs neufs sur {len(cas)}")
for h, fen in ((3, 6), (3, 2), (1, 2), (6, 2)):
    b = [x for x in paris(h, fen) if x["evenement"] in neufs]
    print(resume(b, f"NEUFS, AVEC 50-50, h={h} fen={fen}h"))
b = [x for x in paris(3, 6) if x["evenement"] in neufs]
for key in ("serie", "bo"):
    from collections import defaultdict
    d = defaultdict(list)
    for x in b:
        d[x[key]].append(x)
    for k, v in sorted(d.items()):
        print(resume(v, f"NEUFS, h=3 fen=6h, {key} = {k}"))
