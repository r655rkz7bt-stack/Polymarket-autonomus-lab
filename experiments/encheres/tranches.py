"""Chance de chaque tranche Polymarket à partir des rapports prix/estimation basse des gros lots passés (analyse.gros_lots).

Lot garanti : pas d'invendu (vendu au garant), seulement un risque de retrait `p_retrait` (tranche la plus basse).
"""
import sys
from analyse import gros_lots

LOTS = {  # estimation basse (M$), bornes des tranches (M$), garanti, prix vendeur du OUI par tranche (carnets du 12/11 21 h UTC)
    "Kandinsky": (60, [60, 75, 90, 105], True, [0.13, 0.35, 0.29, 0.18, 0.108]),
    "Klimt": (60, [60, 75, 90, 105], True, [0.20, 0.25, 0.36, 0.29, 0.102]),
    "Picasso": (40, [40, 50, 60, 70], True, [0.101, 0.334, 0.37, 0.19, 0.164]),
    "Basquiat": (30, [30, 40, 50, 60], True, [0.059, 0.52, 0.29, 0.18, 0.10]),
}


def chances(low, bornes, garanti, ratios, n_invendus, p_retrait=0.02):
    n = len(ratios) + (0 if garanti else n_invendus)
    p = [0.0] * (len(bornes) + 1)
    for r in ratios:
        prix = r * low
        k = sum(prix >= b for b in bornes)
        p[k] += 1 / n
    if not garanti:
        p[0] += n_invendus / n
    p = [x * (1 - p_retrait) for x in p]
    p[0] += p_retrait
    return p


if __name__ == "__main__":
    seuil = float(sys.argv[1]) if len(sys.argv) > 1 else 10e6
    L = gros_lots(seuil)
    ratios = [x["ratio"] for x in L if x["prix"]]
    inv = sum(1 for x in L if not x["prix"])
    print(f"{len(ratios)} vendus, {inv} invendus (estimation basse >= {seuil/1e6:.0f} M$)")
    for nom, (low, bornes, garanti, asks) in LOTS.items():
        p = chances(low, bornes, garanti, ratios, inv)
        print(nom.ljust(10), " ".join(f"{x:.2f}/{a:.2f}" for x, a in zip(p, asks)), "  (chance/prix vendeur du OUI)")
