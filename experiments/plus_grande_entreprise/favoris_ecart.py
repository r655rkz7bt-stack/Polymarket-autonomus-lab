"""Cas d'aujourd'hui (Apple n° 1 payé 0,934, modèle 0,988) : sur le passé, côtés que le modèle donne ≥ 0,97 et que le
marché paie 0,80-0,96 (OUI ou NON). Un pari par (mois, rang, société, côté), au plus long délai."""
import json
from pathlib import Path
rows = json.loads((Path(__file__).parent / "donnees" / "lignes.json").read_text())
seen, out = set(), []
for x in sorted(rows, key=lambda x: -x["j"]):
    if not x["sym"] or x["won"] not in (0, 1):
        continue
    for side in (1, 0):
        q = x["modele"] if side else 1 - x["modele"]
        ask = (x["prix"] if side else 1 - x["prix"]) + 0.01
        if q >= 0.97 and 0.80 <= ask <= 0.96:
            k = (x["mois"], x["rang"], x["co"], side)
            if k in seen:
                continue
            seen.add(k)
            pay = 1.0 if (x["won"] == 1) == (side == 1) else 0.0
            out.append((x["mois"], x["rang"], x["co"], side, x["j"], round(ask, 3), round(q, 3), pay))
for o in out:
    print(*o)
n = len(out); won = sum(o[-1] for o in out); exp = sum(o[5] for o in out)
cost = sum(o[5] + 0.04 * o[5] * (1 - o[5]) for o in out)
print(f"{n} paris, {len({o[0] for o in out})} mois, gagnés {won:.0f} pour {exp:.1f} attendus au prix, rendement {(won - cost) / cost:+.1%}")
