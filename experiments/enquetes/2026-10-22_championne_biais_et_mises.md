# Enquête du 22/10/2026 : la championne gagne-t-elle par avantage, ou parce que ses mises grossissent avec le prix ?

Déclencheurs : trois obligations de la feuille de mission (`champion_sans_avantage`, `chance` : 3 paris = 98 % du gain,
`chance` : le 18/10 = 192 % du gain) sur `nf_sport_patiente` (copiée par le principal). Famille du jour : 22 % 6 + 1 = 5
(comparaisons faussées), puis 2 (la mesure récompense la chance). Scripts : `scripts/champion_22_10.py`, `scripts/biais_par_prix_22_10.py`.

## Constat (journal signé du fantôme, 105 paris clôturés, +125,9 €, 8 776 € misés)
- **Sans ses 3 meilleurs paris : +2,2 €** (0,03 %) ; sans les 5 meilleurs : −48,5 € ; sans les 10 meilleurs : −163,9 € (−2,3 %).
- Gagnés **95 pour 90,8 attendus par les prix** (z +1,22) ; moyenne par événement +5,5 % (t +1,7, 100 événements).
- Par jour d'ouverture : 17/10 −72, 18/10 **+242**, 19/10 +16, 20/10 +145, 21/10 **−230**. Comptant +230 € (+4,2 %), ordres posés −104 € (−3,1 %).
- Par prix payé : 0,80-0,90 : +9,8 % (89 paris) ; **0,925-0,95 : −426 € et −96 €** (25 paris, 4 pertes de 113 à 223 €).
- Mise moyenne : 74 € à 0,80-0,85, **101 € à 0,90, 111 € à 0,95** ; le plus gros pari (289 €) a gagné.

## Cause (`strategy_engine.NaiveFavorite.propose`, `portfolio_manager.size_buy`)
La probabilité estimée est `milieu du carnet + bias` avec `bias = 0,05` **fixe**, quel que soit le prix. L'avantage annoncé
est donc toujours ≈ 3,5 points ; le Kelly complet mise `(prob_basse − prix) / (1 − prix)` du capital : 19 % à 0,82,
**50 % à 0,93, 70 % à 0,95**. La mise grossit comme 1/(1 − prix) pour un avantage qui, lui, n'existe pas.

Mesure sur toute l'arène (un jeton = un pari, le plus ancien ; 530 favoris de sport 0,70-0,95 réglés, toutes variantes
`nf_*`/`naive_favorite*` hors football et hors-sport) : **459 gagnés pour 460,9 attendus par les prix** (rendement −0,7 % par unité).
Par tranche (écart gagnés − prix, en points) : 0,80-0,85 : +0,9 ; 0,85-0,875 : +2,7 ; 0,875-0,90 : −4,2 ; 0,90-0,925 : +0,1 ;
0,925-0,95 : −0,8 (110 paris). Aucune tranche ne montre l'écart de +5 points que la stratégie suppose (estimation moyenne
0,87 à 0,98 contre 0,81 à 0,94 gagnés). Toutes stratégies confondues (1 227 jetons, tous types de marchés) : 827 gagnés pour
938,8 annoncés par les estimations, 857,4 attendus par les prix (z −9,7 contre les estimations).

Conclusion : le gain de la championne n'est pas un avantage de prix. C'est le même schéma que le 18/10 (PR #77) et le 20/10
(sélection du meilleur de 35) : des mises énormes sur un « avantage » inventé, dont le résultat dépend de 3 paris et d'un jour.
La part de la championne qui garde un indice est le tennis (voir `experiments/tennis.md` : favori en jeu 0,80-0,95, +3,1 %).

## Correctif
- Nouveau contrôle `estimation_gonflee` dans `src/polymarket_agent/enquete.py` (un jeton = un pari, z des gagnés contre les
  estimations) + test `test_declared_probabilities_far_above_the_results_are_flagged_once_per_token`. Il signale déjà l'arène (z −9,7).
- **Pas de changement de la championne** ce passage : l'écart gagnés − prix est trop petit pour distinguer −1 % de +3 %
  (530 paris, z prix −0,3), et retirer la championne couperait aussi sa part tennis. À trancher par Etienne : mettre
  `bias` à 0,02 sur les sports (mises ≈ 3× plus petites à 0,93, plus aucun achat sans avantage net) ou garder le Kelly à biais fixe.
  Les paris posés sous 0,80 (déjà bloqués le 21/10) et ≥ 0,925 sont les deux tranches à surveiller.
