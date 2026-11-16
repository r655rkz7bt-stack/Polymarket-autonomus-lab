"""Piste n° 66 : un tirage par événement. Meneur (tranche la plus chère) de chaque événement à J+d ; rendement brut
d'un achat au prix d'historique ; z = (gagnés − attendus) / sqrt(Σ p(1−p)) ; par mois de vote et par famille."""
import json, math, collections
from pathlib import Path
cas = json.loads((Path(__file__).parent / "donnees" / "cas.json").read_text())
ev = collections.defaultdict(list)
for r in cas:
    ev[r["event"]].append(r)
for d in ("1", "3", "7"):
    for lo, hi in ((0.3, 0.98), (0.5, 0.85), (0.5, 0.95), (0.85, 0.98)):
        g = a = v = 0; n = 0; ret = []; mois = collections.Counter(); moisg = collections.Counter()
        for e, rows in ev.items():
            rs = [r for r in rows if d in r["prix"]]
            if not rs: continue
            top = max(rs, key=lambda r: r["prix"][d]); p = top["prix"][d]
            if not (lo <= p < hi): continue
            n += 1; g += top["gagne"]; a += p; v += p * (1 - p); ret.append(top["gagne"] / p - 1)
            m = top["vote"][:7]; mois[m] += 1; moisg[m] += top["gagne"] / p - 1
        if n:
            z = (g - a) / math.sqrt(v) if v else 0
            print(f"J+{d} meneur {lo}-{hi}: {n} événements, gagnés {g} attendus {a:.1f}, z {z:+.2f}, rendement moyen {sum(ret)/n:+.1%}")
            if lo == 0.5 and hi == 0.95:
                print("     par mois:", {m: f"{mois[m]}:{moisg[m]/mois[m]:+.0%}" for m in sorted(mois)})
# exemples J+1
print()
for e, rows in list(ev.items()):
    rs = [r for r in rows if "1" in r["prix"]]
    if not rs: continue
    top = max(rs, key=lambda r: r["prix"]["1"])
    if 0.5 <= top["prix"]["1"] < 0.85:
        print(top["vote"][:10], top["title"][:55], "|", top["item"], top["prix"]["1"], "gagné" if top["gagne"] else "PERDU")
