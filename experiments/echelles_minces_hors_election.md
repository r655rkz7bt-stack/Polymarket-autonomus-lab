# Piste 17 — échelles minces contre leurs composants (hors élections), relevé du 04/11/2026

Question : une échelle à tranches (« combien de baisses de taux », « combien de pays frappés ») cote-t-elle à l'achat
(carnet, pas `outcomePrices`) autre chose que ce que disent les marchés qui la composent ? Même mécanisme que
`sieges_coherence`, mais hors élections. Relevé aux carnets CLOB le 04/11 vers 16 h 30 UTC.

## Fed (événement 51456, 13 tranches, contre 770450 « Fed Decision in December »)
- Il ne reste qu'une réunion en 2026 (décembre, fin du marché 10/12). La tranche « 0 baisse » cote 0,976 / 0,977 (acheteur / vendeur).
- Le marché de la réunion cote une baisse de 25 pb à 0,004-0,005 et de 50 pb ou plus à 0,002-0,003, soit environ 0,7 % de baisse ;
  l'échelle laisse 2,35 % à « au moins une baisse ». Écart de 1,6 point.
- Acheter « 0 baisse » à 0,977 rend +1,6 % brut si rien ne bouge, capital bloqué jusqu'au 01/01/2027 (58 jours) : c'est un favori
  ordinaire (aucun avantage mesurable sur un seul événement, pas de passé à rejouer). **Écartée.**

## Israël (événement 79926, 16 tranches « combien de pays »)
- Les tranches 0 à 3 sont déjà réglées « Non » : le compte est d'au moins 4. Il reste « exactement 4 » à 0,70 / 0,77 (écart de 6 points)
  contre « 5 ou plus » ≈ 0,26. Aucun marché par pays ne permet de recomposer la somme, et la probabilité d'un 5e pays en 57 jours
  n'a pas de base de comparaison dans nos données. **Non testable aujourd'hui** ; on y revient si un pays est ajouté (le prix d'une
  tranche doit alors bouger d'un coup, ce qu'on peut mesurer).

## SpaceX
Non relevé ce passage (le compteur du mois est déjà suivi par `spacex_cumul`).

Verdict : aucune stratégie. Les échelles minces ont des écarts achat-vente de 1 à 7 points, supérieurs à l'écart mesurable.
