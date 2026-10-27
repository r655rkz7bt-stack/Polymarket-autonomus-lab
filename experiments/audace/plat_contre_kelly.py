"""Les grosses mises des fantômes sont-elles les mauvaises ? (27/10/2026, experiments/audace.md)

Pour chaque stratégie (≥ 15 opérations) : rendement moyen à mise plate contre rendement pondéré par la mise réelle ; puis,
toutes stratégies confondues, les paris classés par mise relative (mise / mise médiane de sa stratégie), en cinq paquets.
Et le rendement par famille (mère et filles) contre ses prix.

Usage : bash scripts/fetch_data.sh ; .venv/bin/python experiments/audace/plat_contre_kelly.py
"""

from __future__ import annotations

from collections import defaultdict

from commun import SANS, bilan, charger

from polymarket_agent.arena import family_map


def main() -> None:
    g = charger()
    pire = mieux = 0
    ecarts, paris = [], []
    for nom, x in g.items():
        t = x["trades"]
        if len(t) < 15:
            continue
        b = bilan(t)
        ecarts.append(b["par_euro"] - b["plat"])
        pire, mieux = pire + (b["par_euro"] < b["plat"]), mieux + (b["par_euro"] >= b["plat"])
        mediane = sorted(a["cost"] for a in t)[len(t) // 2]
        paris += [dict(a, rel=a["cost"] / mediane) for a in t]
    print(f"Pondérer par la mise fait PIRE que la mise plate chez {pire} stratégies, mieux chez {mieux} ; "
          f"écart moyen {sum(ecarts) / len(ecarts) * 100:+.1f} points")
    paris.sort(key=lambda a: a["rel"])
    k = len(paris) // 5
    for i in range(5):
        lot = paris[i * k:(i + 1) * k] if i < 4 else paris[4 * k:]
        b = bilan(lot)
        print(f"  mises relatives {lot[0]['rel']:.2f}-{lot[-1]['rel']:.2f} : {b['n']} paris, rendement moyen {b['plat'] * 100:+5.1f} %, "
              f"gagnés {b['gagnes']} / attendus {b['attendus']:.0f}, z {b['z']:+.2f}")
    fam = family_map()
    par = defaultdict(list)
    for nom, x in g.items():
        base = nom.rsplit("_v", 1)[0]
        par[fam.get(base, base)] += [dict(a, s=base) for a in x["trades"]]
    print("\nPar famille (mère et filles), 30 paris ou plus :")
    for f, lot in sorted(par.items(), key=lambda kv: -len(kv[1])):
        if len(lot) < 30 or f.startswith(SANS):
            continue
        b = bilan(lot)
        print(f"  {f:30s} {len({a['s'] for a in lot}):3d} stratégies, {b['n']:5d} paris, écart "
              f"{100 * (b['gagnes'] - b['attendus']) / b['n']:+6.2f} points par pari, z {b['z']:+6.2f}, {b['euros']:+7.0f} €")


if __name__ == "__main__":
    main()
