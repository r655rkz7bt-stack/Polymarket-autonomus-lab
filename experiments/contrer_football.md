# Piste n° 13 `contrer_football_en_jeu` : après un but, le prix dépasse-t-il sa juste valeur ? (22/10/2026)

**Question** : pendant un match de football, après un gros saut de prix du marché « X gagne » (but, carton rouge), le prix va-t-il trop loin puis revient-il ?
Si oui, acheter le contraire du saut (NON de X après une hausse, OUI après une baisse) rapporte ; sinon, le suiveur (acheter dans le sens du saut) non plus.

**Données** : 1 110 matchs de football (événement 1X2 : marchés « X gagne » et « Y gagne »), du 15/09 au 22/10/2026, volume de l'événement « exact score » ≥ 5 000 $,
**échanges réels** (data-api, par événement ; équivalent « OUI de X » = achat de OUI ou vente de NON). Scripts : `experiments/contrer_football/` (`releve.py`,
`analyse.py`, `detail.py`, `resultats.txt`).
**Contrôle du règlement** : le dernier prix échangé de chaque marché va dans le sens du résultat 2 206 fois sur 2 207 (hors prix entre 0,2 et 0,8).

**Méthode** : à chaque minute après le coup d'envoi (jusqu'à 125 min), un saut = variation ≥ J du prix de « X gagne » en 2 ou 5 minutes (prix de moins de 4 min).
**Un seul saut par match** (le premier : paris indépendants). Entrée = prix du premier échange de preneur 1 ou 3 min après le saut (fenêtre de 5 min, prix 0,03-0,97),
plus les frais du marché (`feeSchedule`, taux 0,03 si absent). Aucun regard vers le futur.

## Résultats (28 réglages : 4 seuils J × 3 regards/délais × 2 sens, plus 4 de détail)
- **Contrarien** : J = 0,08 / 0,12 / 0,18 : −0,4 % à −4,8 % (z entre −0,43 et +0,53), 770-900 matchs. J = 0,25 : +2,4 % à +6,7 % (z +1,0 à +1,9, 650-720 matchs).
  **J = 0,35 : −8,8 % / −10,6 %** (z −0,8 / −1,2). Le sens change avec le seuil : pas de motif.
- **Suiveur** : −0,6 % à −1,2 % pour J ≤ 0,18 (z ≈ 0), −4,7 % à −6,0 % pour J = 0,25 (z −1,4 à −2,0) : ce sont les mêmes sauts, vus dans l'autre sens.
- Le « bon » réglage (J = 0,25, contrarien) : septembre −0,4 % / +2,8 %, octobre +8,7 % / +9,3 % ; minutes 45-70 négatives (−8,6 % / −13,4 %) ; prix 0,6-0,85 négatifs à un
  délai, positifs à l'autre. Rien de régulier.
- Le marché suit le but et ne revient pas : buts et cartons rouges sont de vraies informations, pas des excès.

**Verdict : écartée.** Un seul réglage sur 28 donne z ≈ +1,9 (ce que le hasard donne sur 28 réglages corrélés) et il s'inverse à J = 0,35. À ne pas refaire sans idée nouvelle
(par exemple séparer buts et cartons rouges : l'historique des événements du match n'est pas gratuit).
