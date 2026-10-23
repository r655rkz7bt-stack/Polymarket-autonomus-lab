# Deux camps d'un même match, mises géantes des fantômes (23/10/2026)

Demande d'Etienne : « il y a des anomalies qui ont été notées, regarde ce qu'il se passe et corrige ».
Source : enquête automatique du 22/10, 23 h 57 UTC (`published/rapports/enquete.md`).

## Constat
1. **Deux camps d'un même match** (contrôle `deux_camps`) : 11 fantômes, 12 marchés, **1 322 € misés**.
   Le défaut continue après les fiches du 20/10 : le 22/10, Mary Stoiana (04 h 32) puis Moyuka Uchijima
   (05 h 46) chez `nf_tennis_prix_bas`, `_vainqueur` et `nf_tennis_vainqueur` ; Belinda Bencic puis
   Katarzyna Kawa ; Tereza Krejcova puis Pavla Sviglerova. Le premier favori s'effondre en jeu,
   l'autre camp passe au-dessus de 0,80 et la même stratégie l'achète : la mise est doublée sur un seul
   match, et l'un des deux paris perd forcément.
2. **Mises géantes** (contrôle `mises`) : 12 mises de fantômes au-dessus de 25 % de leur capital,
   jusqu'à 53 % (`nf_court_prix_haut`, 489 €) et 45 % (`nf_sport_patiente`, 475 € sur Alex Michelsen).
   Cause déjà écrite le 22/10 : biais fixe +0,05, Kelly complet, mise ∝ 1/(1 − prix).
3. **Achats hors plage** (contrôle `filtre_prix`) : 7 achats, **tous du 20/10**, avant le correctif
   `prix_final` du 21/10 : rien à refaire.
4. Obligations (championne et `nf_tennis_prix_bas` sans avantage récent, gains concentrés sur un jour) :
   causes écrites dans `2026-10-22_championne_biais_et_mises.md` ; rien de neuf.

## Cause (1)
Aucun garde-fou : `NaiveFavorite` saute seulement le jeton déjà détenu (« position déjà ouverte »), pas
l'AUTRE jeton du même marché.

## Correctifs
- `main._opposite_side` (réglage `deux_camps.prix_min: 0.70`) : un portefeuille n'achète pas, au-dessus
  de 0,70, un jeton d'un marché où il tient déjà un autre jeton payé au-dessus de 0,70, ni deux camps
  proposés dans le même cycle. Raison d'abstention publiée : « camp opposé d'une position déjà prise ».
  Les jambes d'arbitrage et de tenue de marché (autour de 0,50, somme < 1) passent.
- `main._cap_ghost` (réglage `fantomes.max_mise: 0.25`) : une mise de fantôme ≤ 25 % de son capital
  estimé. Mêmes paris, taille seulement : la confiance de l'arène (rendement par mise) ne change pas.
- **Biais de la championne : laissé à 0,05.** À 0,02, l'estimation (milieu + 0,02 − incertitude 0,015)
  ne dépasse plus le prix de vente : elle deviendrait muette. Ses sœurs à 0,03
  (`nf_sport_patiente_biais_faible`) et 0,02 (`nf_court_prix_haut_biais_faible`) font la comparaison
  sur la même période ; le plafond de 25 % règle les mises géantes, et le principal mise déjà selon
  l'avantage MESURÉ (`mise_avantage_mesure`).

## Tests
`tests/test_deux_camps.py` : le cas Stoiana/Uchijima, deux camps dans le même cycle, jambes d'arbitrage
permises, mise de 489 € ramenée à 250 € sur 1 000 €.

## Contrôle automatique
Les contrôles `deux_camps` et `mises` existent déjà : ils doivent tomber à zéro sur les achats
postérieurs au 23/10.
