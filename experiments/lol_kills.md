# Totaux de kills d'e-sport (« Total Kills Over/Under X in Game N ») : le « Over » est trop cher (27/10/2026)

**Verdict : INDICE** (pas « retenue » : le gain s'efface avec la profondeur et vient presque d'un seul jeu) → fantôme **`moins_de_kills`** (LoL, « Under », une ligne par partie, demi-Kelly).
**Résultat le plus net : n'acheter jamais le « Over »** (−10 à −12 %, z −5,4 sur LoL, même signe dans les quatre jeux).

## Pourquoi cette piste
Nouveau type de marché, que l'arène ne jouait pas. Inventaire des `sportsMarketType` des événements réglés (relevé `/events/keyset`, `experiments/bo3_coherence/releve_evenements.py lol dota2 cs2 val`) : LoL **25 659 marchés** `kill_over_under_game`
(16 M$ de volume, 3 à 6 lignes par partie, depuis janvier 2026), Dota 2 35 309 (4,4 M$), CS2 `round_over_under_game_N` 25 328 (manches, 0,75 M$ par carte), Valorant 8 301. Les « props » LoL (Baron, dragon, quadra…) : 7 490 marchés chacun mais ~34 $ de volume par marché : sans carnet.
Les Over réalisés par ligne sont monotones (17,5 : 71 % → 45,5 : 19 %), donc les lignes sont des échelles de la même variable.

## Données et méthode (`scripts/`)
- `releve_marches.py`, `releve_autres.py` : marchés réglés net (Over ou Under = 1) ou à 50-50 (payé 0,5), jetons, ligne, coup d'envoi (Gamma `gameStartTime`), taux de frais du marché (0 jusqu'en mars ; 3 % puis 5 % × p(1−p) ensuite).
- `releve_echanges.py` : vrais échanges des preneurs (data-api `trades?market=`), **25 659 marchés LoL, 6 708 Dota 2 (≥ 100 $), 1 709 CS2, 746 Valorant**.
- `analyse.py` : décision à T0 = coup d'envoi − h ; **prix payé = premier échange réel qui ACHÈTE le côté** (achat du côté, ou vente de l'autre à 1 − p) dans l'heure après T0, jamais après le coup d'envoi ; frais payés ; un pari par marché et par côté ; `idea_test.verdict` (paris liés par événement).
- `analyse2.py` : découpages (partie, ligne, mois, ligue) et **profondeur** (parts achetables à ≤ prix + 0,02 dans la fenêtre, leçon du 27/10 sur le NON crypto) ; `groupe.py` : quatre jeux ensemble, **un pari par partie** (la ligne payée la plus proche de 0,5 : les lignes d'une partie se gagnent ou se perdent ensemble) ;
  `echelle.py` : arbitrage entre lignes d'une même partie.
- Pas de contrôle du règlement par un score de partie (le prix de règlement Gamma 0/1 est la seule source relue ; les 684 règlements à 50-50 du LoL sont comptés 0,5).

## Résultats (`resultats_*.txt`)
| LoL, tous paris (plusieurs lignes par partie) | Over | Under |
|---|---|---|
| 1 h avant | −12,2 % (1 769 paris, 819 gagnés pour 931,5, z −5,45) | +5,1 % (1 535, 838 pour 788,7, z +2,53, t par événement 1,13) |
| 3 h avant | −8,1 % (764, z −2,43) | +8,6 % (647, 366 pour 332,8, z +2,65, t 2,44, 8 mois sur 9) |
| 6 h avant | −17,6 % (420, z −3,40) | +8,3 % (371, z +1,94, t 2,18) |
| 12 h avant | −20,4 % (196, z −2,81) | +12,1 % (202, z +1,76) |

**Un pari par partie, payé 0,35-0,65, quatre jeux** (`resultats_groupe_under.txt`) : Under à 1 h **+2,5 %** (1 241 paris, z +1,70, t 0,85), à 3 h **+9,5 %** (588 paris, 330 gagnés pour 297,3, z +2,72, t par événement 2,75, 8 mois sur 9),
à 6 h **+10,2 %** (322, z +2,31, t 2,16, 7 mois sur 9) ; Over à 3 h **−10,5 %** (675 paris, t −3,6, 2 mois sur 9). Par jeu (3 h) : LoL +10,1 % (487 paris), CS2 +2,6 % (62), Dota 2 et Valorant trop peu.
Autres jeux, tous paris, 1 h : CS2 (manches) Over −13,8 % (z −2,27), Under +3,7 % (z +0,8) ; Valorant Over −17,2 %, Under −2,1 % ; Dota 2 Over −14,0 %, Under −2,6 %. Même sens pour le « Over » dans les quatre jeux.
Par mois (LoL, 1 h) : avril −14,7 %, mai +18,5 %, juin −8,3 %, juillet +9,4 %, août +5,7 %, septembre +17,1 %, octobre +14,2 %. Par ligue : LCS +22,5 % (z +3,0), CBLOL +8,1 %, LEC +4,6 %, LCK +6 à 7 %, LPL −3,5 %.

**Profondeur (à lire avant de croire le gain)** : LoL Under 1 h, parts achetables à ≤ prix + 0,02 dans l'heure : ≥ 20 : +6,2 % ; ≥ 100 : +6,6 % ; ≥ 400 : **+4,2 %** (398 paris). À 3 h : ≥ 100 +6,2 %, ≥ 400 +4,0 % (123 paris) ; à 6 h : ≥ 100 **−3,5 %**.
Le gain tient en gros jusqu'à 100 parts, plus fragile au-delà : un fantôme à mises franches sera servi sur le carnet (25 % de la quantité au meilleur prix), l'arène mesurera ce que ces chiffres ne montrent pas.

**Arbitrage entre lignes** (`echelle.py`) : 226 paires de lignes d'une même partie comparables à 10 minutes près, 3 avec coût + frais < 0,99 : **écarté** (les lignes sont cohérentes entre elles).

## Limites et lecture
- **La plupart des échanges de ces marchés ont lieu PENDANT la partie** : la première transaction tombe en médiane 0,9 h après le coup d'envoi (marchés de 100 $ et plus) ; 14 % des 25 659 marchés LoL ont un échange avant le coup d'envoi, 9 % (2 324) dans l'heure juste avant. Les paris testés sont ceux de la minorité qui s'échange avant ; le carnet de la plupart des marchés est vide avant le match.
- ~15 découpages regardés (4 horizons, 5 types de découpage, 4 jeux) : le z de +2,7 survit à peine à une correction de ce nombre. Le « Over » (z −5,4, quatre jeux) est le seul résultat qui la survit largement.
- Pas d'explication vérifiée. Hypothèse : les parieurs aiment le « plus de kills » (parties spectaculaires), ce qui pousse le prix du Over ; le Under, acheté à l'ask, ne gagne que ce qui reste après frais et écart.
- Ces marchés n'existaient pas encore (au 27/10 à 11 h UTC) pour les matchs du 28/10 : ils sont créés dans la journée qui précède. Le fantôme les verra via `scanner.series_pages` (série 10311, type `kill_over_under_game`, ajouté aujourd'hui).

## Suite
- Premier jugement du fantôme `moins_de_kills` : 30 paris réglés (gagnés contre attendus ; par partie). Pas de capital principal avant.
- Si le fantôme confirme, tester la même règle sur les manches de CS2 (carte 1, `round_over_under_game_1`) en fantôme à part.
- Contrôle à faire quand le fantôme a acheté : prix payé réel contre l'échange du test, et nombre de parties où il n'a pas trouvé de carnet.

## Complément : hors échantillon dans le temps (LoL, 3 h, un pari par partie, payé 0,35-0,65)
487 paris, +10,1 % ; première moitié des mois (fév.-mai) +13,7 % (177 paris), seconde (juin-oct.) **+8,1 %** (310) : l'effet existe encore dans les derniers mois. `idea_test.verdict` dit « retenue » ; je garde « indice » à cause de la profondeur (+4 % à ≥ 400 parts), des ~15 découpages regardés et du fait que 9 % seulement des marchés ont un carnet avant le match.

## Complément : le biais existe au prix médian (pas seulement l'écart achat-vente)
LoL, lignes payées 0,35-0,65, prix médian des échanges de la fenêtre exprimé en prix du « Over » : à 1 h 2 088 marchés, prix moyen 0,506, Over réalisé **0,458** ; à 3 h 998 marchés, 0,504 contre **0,462** ; à 6 h 597 marchés, 0,504 contre **0,434**. Le « Over » est surcoté de 4 à 7 points au milieu du prix (marchés d'une même partie corrélés : lecture par marché, pas par partie).
