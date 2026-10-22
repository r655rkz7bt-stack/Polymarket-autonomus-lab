# Piste n° 2 `toucher_avant_fin` : « touche X dans la journée » contre « au-dessus de X à midi » (22/10/2026)

**Question** : le marché « Le Bitcoin touchera-t-il X aujourd'hui ? » vaut au moins « sera-t-il au-dessus de X à midi (ET) ? »
(principe de réflexion). Si les deux prix s'écartent, on achète le côté le moins cher (arbitrage garanti : touche OUI + au-dessus
NON pour les barres ↑, touche OUI + au-dessus OUI pour les barres ↓ rapportent au moins 1 dans tous les cas).

**Données** : Gamma, 952 événements crypto (avril-octobre) ; 24 jours de « What price will Bitcoin/Ethereum/Solana hit on <jour> » (barres
↑ et ↓ tous les 1 000 $) appariés aux « above on <jour> » du même jour : **433 couples de barres identiques**, historique CLOB à 10 min
de 04 h à 16 h UTC (12 h ET). Scripts : `experiments/toucher_avant_fin/` (`releve.py`, `appariement.py`, `analyse_appar.py`, `resultats_appar.txt`).

## Résultats
- **Cohérence** : 27 561 points comparés. Coût du couple (au milieu des prix) inférieur à 1 − 0,01 : **5 points (0,02 %)**, 4 couples ;
  inférieur à 1 − 0,02 : **1 point** (Solana 80 $, 08/07 : 0,295 contre 0,355). Au prix du milieu, avant écart achat-vente (≥ 1 cent par jambe)
  et temps d'exécution : **aucune marge exploitable**. Les marchés sont cohérents.
- **Calibration du « touche » à 12 h UTC** (172 marchés) : prix moyen 0,027 → touchés 1,5 % ; 0,087 → 3,3 % ; 0,258 → 20 % ; 0,528 → 65 % ;
  ≥ 0,70 → 100 %. Le NON du « touche » à 2-15 % : +1,6 % (écart 0,01) puis +0,6 % (écart 0,02), t par jour +0,55 / +0,11 ; 5-40 % : +6,7 % / +5,3 %,
  t par jour +0,74 / +0,55. 6 réglages, 24 jours seulement, Bitcoin/Ethereum/Solana corrélés le même jour, prix de 10 minutes (pas de vrais échanges).

**Verdict : écartée.** Cohérence parfaite (pas d'arbitrage) ; le biais « touche trop cher » est dans le sens attendu (longshot) mais pas
significatif (t par jour < 1) et le sens opposé a été mesuré sur le marché voisin (`haut_ou_bas_crypto` −16 %, robots). Ne pas refaire sans
plus de jours (les « hit-on » n'existent que depuis mars 2026) ou sans vrais échanges.
