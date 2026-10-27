"""Étape 4 bis (2e tour, 12 réglages de plus) : un GROS compte neuf et concentré suffit-il ? Ballon d'Or 2026 : 15 766 $,
123 420 $, 182 450 $ par compte. Même protocole que test_grappes.py, avec K = 1 ou 2, S de 5 000 à 20 000 $, au plus 10
marchés, et le prix payé en les suivant (tous, ou seulement ≥ 0,30 : les initiés du Ballon d'Or achetaient à 0,54-0,76).

Usage : .venv/bin/python experiments/inities/scripts/test_gros_comptes.py
"""

from __future__ import annotations

import test_grappes as tg
from commun import DONNEES, lire_gz


def main() -> None:
    evs = tg.charger_tout()
    profils = lire_gz(DONNEES / "portefeuilles.json.gz") or {}
    essais = 0
    for prix_min in (0.0, 0.30):
        for k, s in ((1, 5000), (1, 10000), (1, 20000), (2, 5000), (2, 10000), (2, 20000)):
            essais += 1
            bets = [b for b in tg.paris(evs, profils, (7, 10), k, s, 900) if b["cout"] >= prix_min]
            tg.resume(f"K={k} S={s} marchés≤10 âge≤7 j, prix payé ≥ {prix_min:.2f}", bets)
    print(f"\n{essais} réglages de plus (48 en tout avec test_grappes.py)")
    best = tg.paris(evs, profils, (7, 10), 1, 10000, 900)
    print("\nK=1, S=10 000 : paris un par un")
    for b in sorted(best, key=lambda b: b["mois"]):
        print(f"  {b['mois']} {b['famille']:18s} {'GAGNÉ' if b['gagne'] else 'perdu'} à {b['cout']:.2f}, {b['heures_avant_public']:6.1f} h avant, "
              f"{b['dollars']:7.0f} $ | {b['titre'][:45]} | {b['question'][:50]}")


if __name__ == "__main__":
    main()
