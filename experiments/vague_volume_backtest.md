# Vague de volume : test sur le passé aux prix réellement payés (23/10/2026)

Scripts et ordre de lancement : `experiments/vague_volume_backtest/README.md`. Chiffres bruts :
`experiments/vague_volume_backtest/resultats_0h.txt` (décision à 00:00 UTC) et `resultats_0h_12h.txt`
(00:00 et 12:00 UTC).

## La question

La stratégie `vague_volume` (fantômes `vague_volume_suivre` et `vague_volume_contrer`, idée reprise des
skills Polymarket publics) n'avait jamais été testée sur le passé. Question : quand un marché OUI/NON
s'échange au moins 3 fois plus que d'habitude et que son prix a bougé d'au moins 0,03 en 24 h, acheter le
côté qui a monté (**suivre**) ou l'autre côté (**contrer**) gagne-t-il plus souvent que son prix, après
frais, aux prix réellement payés ?

## Les données

- **Marchés** : tous les marchés OUI/NON réglés net à 1/0 (lecture `idea_test.parse_event_market`), dont
  l'échéance annoncée tombe entre le 10/07 et le 15/10/2026, avec au moins 20 000 $ échangés : 87 484
  marchés lus sur Gamma (`/markets`, une fenêtre par jour : `/events` dépasse 2 100 événements et 6 Mo par
  page un seul jour). Gardés : issues littéralement « Yes »/« No » (comme la règle en direct) et au moins
  une décision possible (âge ≥ 3 jours ET échéance réelle ≥ 48 h après) → **13 714 marchés, 5 939
  événements** (sport 8 958, crypto 2 278, politique 1 501, autres 977). Échéance réelle d'un match :
  `gameStartTime` (l'`endDate` d'un match est fictive).
- **Vrais échanges** (data-api, public, sans clé), marché par marché. Au lieu de s'arrêter à 11 pages
  (`fetch_event_trades`, qui garde les plus récents et perd justement les jours d'avant), on remonte le
  temps avec le paramètre `end`, en partant de l'échéance réelle − 46 h. Vérifié avant usage : sur un
  événement de 5 030 échanges, `end=X` (avec ou sans décalage) renvoie exactement les échanges ≤ X de la
  pagination. **57 marchés restent tronqués** à 40 pages (leurs jours non couverts sont écartés : 14 953
  instants de décision à 00:00 retirés pour cette raison) ; 1 901 marchés n'ont aucun échange avant
  l'échéance − 46 h (surtout des matchs de football, échangés seulement le jour même).
- **Période des décisions** : les marchés se règlent de juillet à octobre 2026, mais beaucoup vivaient
  depuis longtemps : les décisions vont de juillet 2025 à octobre 2026 (≈ 80 % depuis juillet 2026).

## Contrôle du règlement

Sur 400 marchés tirés au hasard (graine fixe), le dernier échange réel avant la clôture redonne le résultat
officiel **400 fois sur 400** (et ce prix est toujours ≥ 0,9 ou ≤ 0,1). Notre lecture des jetons OUI/NON et
des résultats est donc juste.

## La règle rejouée (sans regard vers le futur)

À chaque instant T (chaque jour à 00:00 UTC ; variante : 00:00 et 12:00), seulement avec les échanges
d'avant T : âge ≥ 3 jours, échéance réelle ≥ 48 h après T, marché pas encore clos ; référence = volume
moyen par jour des jours précédents (fenêtre min(7, âge) jours moins les dernières 24 h, divisée par
jours − 1, comme `VagueVolume._surge`) ≥ 500 $ ; rapport = volume des 24 h / référence ; mouvement = prix
du OUI au dernier échange avant T − prix au dernier échange avant T − 24 h. Plages : suivre achète le côté
qui a monté si son dernier prix est dans [0,55 ; 0,90], contrer achète l'autre côté s'il est dans
[0,10 ; 0,45]. **Prix payé = premier échange réel après T qui achète ce côté** (même définition que
`taker_cost(after=True)`, fenêtre 2 h, égalité vérifiée par 354 contrôles automatiques) ; pas d'échange =
pas de pari. Frais réels du marché (`fee_rate × p × (1 − p)`). Gain par euro = (gagné − coût − frais) / coût.
Au plus un pari par marché et par jour ; paris liés par événement dans `idea_test.verdict`.

**Réglages essayés : 36 par jeu d'heures** (vague ×2 / ×3 / ×5, mouvement 0,03 / 0,05 / 0,10, avec ou sans
plages, suivre et contrer), sur deux jeux d'heures (00:00 ; 00:00 + 12:00), soit **72**, plus 3 références
sans vague, le détail par famille et une variante « un seul pari par marché » (comme en direct, où la
position est gardée). Tous les chiffres sont dans les fichiers de résultats, pas seulement le meilleur.

## Résultats aux prix payés (réglage en direct : vague ×3, mouvement 0,03, plages)

| | paris | événements | rendement moyen | confiance par événement | z_prix | mois gagnants | verdict automatique |
|---|---|---|---|---|---|---|---|
| suivre, 00:00 | 468 | 254 | **+1,4 %** | 1,31 | 1,14 | 10/15 | indice |
| suivre, 00:00 + 12:00 | 823 | 341 | **+2,2 %** | 2,38 | 1,66 | 12/15 | retenue |
| suivre, 00:00 + 12:00, sans vague (rapport < 1,5, mêmes plages) | 2 144 | 528 | +1,3 % | −0,94 | 1,73 | 9/17 | écartée |
| contrer, 00:00 | 413 | 223 | **−9,1 %** | −1,63 | −0,20 | 7/16 | écartée |
| contrer, 00:00 + 12:00 | 750 | 321 | **−16,9 %** | −3,53 | −1,65 | 6/16 | écartée |

Ce qu'on apprend :

1. **Contrer perd partout** : les 36 réglages de contrer (18 par jeu d’heures) sont négatifs (−9 % à −23 %), dans
   toutes les familles, avant comme après juillet 2026, avec ou sans vague (sans vague : −18 %, z_prix
   −3,4). Acheter le côté qui vient de baisser, entre 0,10 et 0,45, c'est surtout acheter des billets
   perdants.
2. **Suivre gagne un peu, mais pas grâce à la vague.** Sans les plages de prix, les 18 réglages de suivre
   perdent (−1,6 % à −8,6 %) ; avec les plages, les 18 sont positifs (+1 % à +7 %). Le gain vient d'acheter le
   **favori qui monte, entre 0,55 et 0,90** (tranche ≥ 0,70 : +3,5 % ; tranche 0,30-0,70 : −0,7 %), et la
   même règle **sans vague** fait presque pareil (+1,3 %, z_prix 1,73). Une vague plus forte fait un peu
   mieux (×5 : +5,3 %, z_prix 2,1 sur 390 paris), mais c'est un réglage parmi 72.
3. **Le « retenue » ne tient pas sur la période récente.** Pour suivre (00:00 + 12:00), les décisions
   d'avant juillet 2026 (158 paris, marchés à longue vie) font +10,9 % ; celles de juillet à octobre 2026
   (665 paris, 279 événements) font **+0,1 %** (z_prix 0,65, 2 mois gagnants sur 4). Sans les 3 meilleurs
   paris : +1,8 %. Avec un seul pari par marché (comme en direct) : +1,7 %, z_prix 1,14 → « indice ».
4. **Par famille** (suivre, 00:00 + 12:00) : sport +8,4 % (139 paris, 67 événements, z_prix 1,88),
   politique +2,6 % (368 paris), crypto +2,2 % (114 paris), autres −3,0 % (202 paris). Seul le sport
   ressort, sur peu d'événements.

## Verdict

- **vague_volume_suivre : indice** (et non « retenue »). Le verdict automatique dit « retenue » pour
  2 jeux de réglages sur 72, mais : le gain (+1 à +2 %) tient aux plages de prix et non à la vague (même
  gain sans vague), il disparaît sur les 4 derniers mois (+0,1 %), et le nombre de réglages essayés rend un
  z de 1,7-2,4 attendu par hasard. Gagne à peine plus souvent que ses prix (z_prix 1,1 à 1,7).
- **vague_volume_contrer : écartée.** Perd dans les 36 réglages, toutes familles, toutes périodes
  (réglage en direct : −9 % à −17 % par euro, confiance par événement −1,6 à −3,5).

## Recommandation pour les deux fantômes

- **vague_volume_contrer : retirer** (`enabled: false`) : rien sur 3 mois de marchés réglés ne la soutient.
- **vague_volume_suivre : garder comme fantôme, sans réglage changé et sans entrée dans
  `validated_strategies`**. Si l'on veut un réglage chiffré à suivre en parallèle : une fille avec
  `surge_min: 5.0` (+5,3 %, z_prix 2,1, 12 mois gagnants sur 13, 390 paris) et/ou limitée au sport, en
  sachant que c'est le meilleur de 72 réglages ; l'arène dira s'il tient en direct.

## Limites

- Le prix servant aux plages est le dernier échange avant T (en direct : le milieu du carnet) ; le
  mouvement est calculé sur les derniers échanges (Gamma `oneDayPriceChange` peut différer un peu).
- Le volume de data-api compte les échanges des preneurs (taille × prix) ; Gamma `volume24hr` peut compter
  autrement : le rapport est comparable, le seuil de 500 $ un peu moins.
- Seuls les marchés à ≥ 20 000 $ échangés au total et réglés entre juillet et octobre 2026 ; les marchés
  non réglés (encore ouverts) manquent, ce qui sous-représente les marchés à très longue échéance.
- Un pari = une part au premier prix échangé ; la profondeur du carnet n'est pas simulée.
