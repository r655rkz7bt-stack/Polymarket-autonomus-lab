# `moins_de_cartes` en direct : confirmation hors échantillon (25/10/2026, nuit)

Suite de `experiments/pistes_sport_coherence.md` et du test du 25/10 midi (« Under » des totaux de cartes d'e-sport, refait avec les règlements 50-50 : indice, +7,7 %, t 2,0 sur 865 paris du passé).
Le fantôme `moins_de_cartes_v1.0.0` joue depuis le 23/10 à 0 h 26 UTC. Les paris réglés du journal signé (état du 25/10 à 20 h 47 UTC) sont HORS ÉCHANTILLON : la stratégie a été choisie sur le passé du 23/10, avant ces paris.

## Contrôles (script `experiments/moins_de_cartes_direct/confirme_25_10.py`)
- **Règlement relu** : les 54 paris réglés, relus un par un sur Gamma (`/markets/<id>`, `outcomePrices`, `umaResolutionStatus: resolved`) : **54 sur 54** conformes au paiement du journal (dont 6 règlements à 50-50, comptés 0,5).
- **Un pari par match** : 54 paris, 54 événements distincts (« Games Total: O/U 2.5 », Under) : pas de paris liés à regrouper.
- **Achats immédiats** (aucun ordre posé : pas de sélection adverse, voir `ordres_poses_en_jeu.md`), prix payés 0,51 à 0,68 (carnet réel + frais du marché).

## Résultat
| | paris | mis | gain | rendement | gagnés / attendus | z des prix | t par match |
|---|---|---|---|---|---|---|---|
| direct 23-25/10 | 54 | 367 € | +109 € | **+29,7 %** | 40,0 / 30,6 | **2,59** | **2,97** |
| sans les 3 meilleurs matchs | 51 | 314 € | +69 € | +22 % | | | |
| passé (midi, 865 paris) | 865 | | | +7,7 % | | 1,5 | 2,0 |

La mise est petite (7 € par pari en moyenne, 20 € au plus) : le gain en euros est modeste. Le rendement direct est 4 fois celui du passé : un effet de petit échantillon (54 paris, trois jours) autant qu'un signe ; la bonne lecture est « le signe tient, l'ampleur reste inconnue ».

## Verdict : indice qui se confirme (passé t 2,0 + direct t 3,0)
- Pas de changement de stratégie. Le principal la suit déjà (16 % du capital engagé, première des 5 championnes du 25/10 à 20 h 47 UTC), sans `validated_strategies`.
- À surveiller : si les 50 prochains paris donnent z < 0, c'est que le signe de 23-25/10 était la chance. Le fantôme `moins_de_cartes_lol` (LoL seul, +15 % sur le passé) et `moins_de_cartes_bo5` n'ont encore aucun pari réglé.
- Ne pas oublier : ce fantôme est l'un des ~60 de l'arène (contrôle `selection_multiple`) ; ce qui le distingue est qu'il a été choisi AVANT ces paris, sur un test du passé indépendant.

## Mécanisme : les cartes d'un match sont corrélées (26/10/2026, `experiments/bo3_coherence/correlation_manches.py`)
Question : pourquoi l'« Under 2,5 » gagne-t-il ? Si les cartes sont indépendantes (loi binomiale, modèle de `series.py`) un balayage 2-0 a la chance 1 − 2q(1 − q), où q est tiré du prix du vainqueur (q²(3 − 2q) = prix à T − 3 h).
Sur **577 BO3** (CS2, LoL, Dota 2, Valorant, janvier-octobre 2026, tirage de 2 755 matchs, vrais échanges) avec un total « 2,5 » échangé :
- balayages réels **63,6 %**, binomial **56,1 %** (+7,5 points, z ≈ +3,7), marché (prix payé de l'Under) **59,5 %** : le marché connaît à peu près la moitié de la corrélation ;
- écart réel − binomial positif dans les **5 tranches de force du favori** (+4,2 à +14,3 points), les **4 jeux** (+6,3 à +8,9) et les **2 périodes** (+7,2 puis +8,7) ; réel − marché : +4,1 points (z +2,07), de +0,6 à +7,6 selon la tranche.
- Lecture : un favori qui gagne la 1re carte en gagne plus souvent une 2e que ne le dit l'indépendance (équipe plus forte que son prix, même carte pool/forme du jour). L'Under vaut donc plus que sa valeur binomiale ; le marché en paie déjà une partie. Le décalage de 0,05 de la stratégie (`shift`) est du même ordre que l'écart réel − marché mesuré (+0,041).
- **Limite** : c'est le même échantillon que l'indice du 25/10 (+7,7 %, t 2,0) : cela explique le résultat, ça ne le confirme pas de façon indépendante ; la confirmation reste les paris en direct (`moins_de_cartes` : 57 paris, +26,7 %, z +2,33, par jeu : CS2 +23,5 %, Dota 2 +25,4 %, 3 Valorant, 1 LoL).
- **BO5 (Under 3,5 = balayage 3-0), même méthode** (`BO=5`, `resultats_correlation_manches_bo5.txt`) : 122 matchs (109 LoL), balayages réels **53,3 %** contre **33,9 %** par la loi binomiale (+19,4 points) et **38,9 %** pour le prix payé de l'Under : réel − marché **+14,4 points (z +3,4)**, positif dans 4 tranches de favori sur 5 (−9,9 en 0,6-0,7), les deux périodes (+15,2 puis +17,0). C'est la corrélation entre cartes à son plus fort (la meilleure équipe gagne 3-0 deux fois plus souvent que le dit l'indépendance) et le marché n'en paie qu'un quart. Même échantillon que la fille `moins_de_cartes_bo5` (qui n'a eu aucun pari : attend les barrages de Worlds) ; 122 cas, à lire comme un indice fort de mécanisme, pas comme une preuve du gain.
