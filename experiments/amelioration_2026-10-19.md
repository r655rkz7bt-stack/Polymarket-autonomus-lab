# AMELIORATION du 19/10/2026 : recherche approfondie

Demande d'Etienne : « D'autres choses ? Fais une recherche plus profonde », puis « Tout ».
Données : journaux de la branche `data` (19/10, vers 11 h UTC), sauvegarde `essentiel.sqlite` (pour
les libellés), API publique Gamma (en direct). Script : `experiments/amelioration_2026-10-19/analyse.py`.

## 1. Bilan de toutes les opérations (1 549 opérations clôturées, tous fantômes)
- Total : **−3 416**. Paris gardés jusqu'au règlement : 681 gagnés pour 725 attendus d'après les prix
  payés, soit **−4,4 points par pari** (on achète trop cher en moyenne).
- Par famille (favoris à 0,70 et plus) :

| Famille | Mode d'achat | Paris | Rendement moyen | Gagnés / attendus |
|---|---|---|---|---|
| politique | immédiat | 24 | +2,3 % | 14 / 13,1 |
| sport | posé | 53 | +4,9 % | 47 / 44,6 |
| météo | immédiat / posé | 67 / 35 | ≈ 0 | 50 / 49,0 et 26 / 25,6 |
| sport | immédiat | 329 | −5,8 % | 266 / 281,8 |
| autres | immédiat | 78 | −9,2 % | 41 / 46,5 |

- Prix 0,50-0,70 : −15,4 % (81 gagnés pour 100,2 attendus). Horizon 12-24 h : z = −3,7.
- Reventes avant la fin : 524 ventes, −656, presque toutes par market_structure (déjà coupée).
- Achats posés, toutes familles : −4,1 points par pari (contre −4,4 en immédiat). Poser ses ordres
  ne suffit pas : c'est le CHOIX des paris qui coûte.

## 2. Ordres posés en sport (nf_sport_patiente)
- 23 paris en commun avec une stratégie qui achète tout de suite : économie moyenne **1,8 centime
  par part** (médiane 0), achat posé environ 2,3 h après l'achat immédiat.
- Gagnés / attendus par tranche de prix : 0-0,85 : 24 / 22,1 ; 0,85-0,90 : 14 / 12,2 ;
  0,90-0,95 : 13 / 13,0.
- Lecture : l'économie explique environ 2 des 4 à 5 points d'avance ; le reste est le choix des
  paris ou la chance (55 paris, z = 1,7). Ailleurs (politique, météo, crypto), l'ordre posé ne
  rapporte rien de mesurable : **pas d'extension**, les variantes du chercheur (#78-80) explorent.

## 3. Arbitrage sur les événements à plusieurs issues (Gamma, 19/10, 41 événements « negRisk »)
- 6 événements où la somme des prix vendeurs est sous 1 (ex. « Republican Presidential Nominee
  2028 » 0,82 ; « Prime Minister of Israel » 0,962). Mais ce sont des événements **augmentés** : des
  issues réservées (« Person H »…) peuvent être ajoutées plus tard et gagner, et « Other » change de
  sens à chaque ajout. Acheter toutes les issues actuelles ne garantit donc rien.
- Événements complets : « Bank of Canada » (acheteurs 1,008), « Likud # of seats » (1,019),
  « Senate pending oil » (vendeurs 0,993) : 0,7 à 1,9 % avant frais, sur peu de volume ;
  frais 4 à 5 % × p × (1 − p) par jambe → nul ou négatif. **Pas de stratégie** (cross_market reste
  pour les échelles de seuils).

## 4. Programmes de Polymarket (web, 19/10/2026)
- Récompense de détention : 4 %/an sur la valeur des positions des marchés éligibles (Gamma
  `holdingRewardsEnabled`) → estimée et comptée pour le classement (lot 2, ARCHITECTURE §43),
  stratégie parking_politique, proposition noyau `proposals/2026-10-19_detention_et_remises.md`.
- Frais preneur sur crypto (janvier 2026), sport (février), puis presque tout (mars, non confirmé) ;
  20 à 25 % reversés aux ordres posés exécutés (non compté, noyau : même proposition).
- Thèse de Princeton : le sport est le domaine le moins bien calibré sur Polymarket, la politique
  le mieux → les cotes des bookmakers en sport (cotes_bookmakers, réparée au lot 1) restent la
  piste d'information la plus prometteuse.

Sources : docs.polymarket.com (holding-rewards, maker-rebates-program), theblock.co (frais crypto
2026), pineanalytics.substack.com (déploiement des frais), theses-dissertations.princeton.edu
(calibration de Polymarket), arxiv.org/abs/2508.03474 (arbitrage sur Polymarket).
