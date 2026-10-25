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
