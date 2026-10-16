# Proposition (noyau) : compter la remise versée aux ordres posés (« maker rebate »)

Date : 16/10/2026. Fichiers du noyau concernés : `src/polymarket_agent/fees.py`,
`src/polymarket_agent/execution_simulator.py` (et `ledger.py` si on choisit l'option B).
Seul Etienne peut les modifier ; je ne les ai pas touchés.

## Ce que dit Polymarket (lu le 16/10/2026)
`https://docs.polymarket.com/programs/maker-rebates.md` et `https://docs.polymarket.com/trading/fees` :
- seuls les preneurs (« taker ») paient : `frais = C × feeRate × p × (1 − p)` ; les ordres posés
  (« maker ») ne paient rien — c'est déjà ce que fait le simulateur (`takerOnly: true`) ;
- une part des frais de chaque marché (`rebateRate` du barème Gamma : 15 % en sport, 20 % en
  crypto, 25 % ailleurs) est reversée **chaque jour** aux ordres posés qui ont été exécutés :
  `remise = (mon équivalent-frais / total des équivalents-frais du marché) × cagnotte`, avec
  `équivalent-frais = C × feeRate × p × (1 − p)` pour chaque exécution de mon ordre posé ;
- versement à partir de **1 $** de remise accumulée.

Chaque exécution a un preneur et un « poseur » au même prix et pour le même nombre de parts.
Le total des équivalents-frais des poseurs est donc égal au total des frais payés par les
preneurs, et la remise attendue d'une exécution posée vaut :
`remise ≈ C × feeRate × rebateRate × p × (1 − p)`.

## Ce que ça change pour nous (mesuré sur les journaux du 16/10/2026, branche `data`)
Estimation avec feeRate 0,05 et rebateRate 0,25 :

| Portefeuille | Ordres posés exécutés | Montant | Remise estimée |
|---|---|---|---|
| market_structure_patiente | 33 | 398 | ≈ 3,05 |
| meteo_prevision_patiente | 20 | 281 | ≈ 1,92 |
| news_momentum_patiente | 30 | 752 | ≈ 0,88 |
| crypto_threshold_patiente | 7 | 60 | ≈ 0,64 |

Cela représente **≈ 0,1 à 0,8 % du montant posé** : petit, mais gratuit et cumulatif pour les
variantes « patientes ». C'est l'avantage le plus modeste de la liste « AMELIORATION ». Le
gros gain des ordres posés — ne pas payer les frais de preneur — est déjà compté.

## Deux façons de le faire (au choix d'Etienne)
**A. Simple (recommandée)** : dans `fees.py`, ajouter
`maker_rebate(shares, price, schedule) = shares × rate × rebateRate × p × (1 − p)`, arrondi
**vers le bas**, et dans `execution_simulator._resting_fill`, enregistrer
`fee = −maker_rebate(...)` (frais négatif) pour une exécution posée. Plus test : remise nulle si
`rebateRate` est absent, si le marché est sans frais, ou pour un ordre preneur.
*Limite* : la remise est créditée tout de suite au lieu du lendemain, et sans le seuil de 1 $.
Sur nos montants, l'écart reste de l'ordre de quelques centimes par jour.

**B. Exacte** : une écriture `REBATE` dans le journal signé, une fois par jour (UTC), pour la
somme des remises accumulées la veille si elle atteint 1 $, sinon reportée. C'est plus fidèle,
mais il faut modifier `ledger.py` (règle n°1). Je le déconseille pour un gain aussi petit.

Dans les deux cas : pas de remise en dehors des marchés à frais, et pas de « taker rebate »
(programme à paliers selon le volume sur 30 jours, non modélisé par prudence).

## Ce qu'Etienne aurait à faire
Me dire « remise : option A » (ou B). Je préparerai alors la pull request du noyau avec ses tests,
et je te guiderai pour la fusion, comme pour l'audit des règlements (désactiver la règle
`protection-main`, fusionner, la réactiver).
