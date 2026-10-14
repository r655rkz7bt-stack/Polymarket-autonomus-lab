# Protocole v2 — calibration et reversion sur un historique non biaisé

Écrit le 14/10/2026 **avant** de voir les résultats sur ce nouvel historique.

## Pourquoi une v2 : la v1 est rejetée

Sur l'historique v1 (marchés au **volume final** ≥ 50 000), la stratégie « calibration v1 »
semblait gagner +112 % en validation en achetant des outsiders. Un échantillon témoin de
8 jours sans filtre de volume a montré que c'était un **biais de sélection** : une surprise
(l'outsider gagne) génère beaucoup d'échanges, donc filtrer sur le volume final, connu
seulement après l'issue, sur-représente les surprises.

| échantillon témoin, favori à 0,65–0,90, horizon ≥ 4 h | δ (victoires − prix) |
|---|---|
| tous les marchés | +0,015 [+0,004 ; +0,026] |
| seulement volume final ≥ 50 000 | −0,013 [−0,047 ; +0,019] |

Leçon (règle permanente) : **ne jamais sélectionner les données sur une variable connue
après l'issue** (volume final, date de clôture réelle, nombre de commentaires…).
« calibration v1 » n'est pas adoptée. L'historique v1 est retiré du dépôt.

## Données v2

- 40 jours d'échéance tirés au hasard (graine 20261014) entre le 14/10/2025 et le
  13/10/2026, listés dans `jours_v2.txt` (dont les 8 jours du témoin).
- **Tous** les marchés binaires résolus nettement (1/0) de ces jours, sans filtre de volume.
  Un marché sans aucun échange n'a pas d'historique de prix : il est absent (il n'aurait
  de toute façon pas pu être tradé).
- Prix horaires sur 72 h, horizon mesuré par rapport à l'échéance prévue.

## Filtre de liquidité connu à l'instant de décision (nouveau, fixé à l'avance)

En réel, le scanner écarte les marchés peu actifs. Pour reproduire cela sans tricher,
un échantillon n'est utilisé que si **le prix a changé au moins 4 fois sur les 24 points
horaires précédant la décision** (information disponible à l'instant T). La même règle
sera appliquée en réel avant toute proposition.

## Règles, découpage, critères

Inchangés par rapport à `PROTOCOLE_calibration_v1.md` et `PROTOCOLE_reversion_v1.md` :
même table (cases, k = 200, ≥ 150 événements), mêmes règles d'achat, même découpage
chronologique par événement 60/20/20, mêmes 5 critères d'adoption, demi-écart 0,01
testé ×1,5 et ×2. La table est réajustée sur l'entraînement v2 uniquement.

Si aucune stratégie ne passe : le bot s'abstient, et c'est le bon résultat.
