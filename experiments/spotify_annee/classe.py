"""Classe les titres par écoutes hebdomadaires cumulées sur une fenêtre (somme des semaines kworb dont la date tombe dedans).
Usage : python classe.py 2025-01-02 2025-11-13 [global|us] [n]"""
import json, sys
from pathlib import Path
D = Path(__file__).parent / "donnees"
debut, fin = sys.argv[1], sys.argv[2]
col = 1 if len(sys.argv) > 3 and sys.argv[3] == "us" else 0
n = int(sys.argv[4]) if len(sys.argv) > 4 else 12
res = []
for l in open(D / "titres.jsonl"):
    t = json.loads(l)
    s = sum(v[col] for d, v in t["semaines"].items() if debut <= d <= fin)
    der = max((d for d in t["semaines"] if d <= fin), default=None)
    rythme = t["semaines"].get(der, [0, 0])[col] if der else 0
    res.append((s, t["titre"], rythme))
res.sort(reverse=True)
for i, (s, ti, r) in enumerate(res[:n], 1):
    print(f"{i:2d} {s/1e6:9.1f} M  (dernière semaine {r/1e6:6.1f} M)  {ti}")
