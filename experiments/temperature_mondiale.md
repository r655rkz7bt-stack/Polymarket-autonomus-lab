# Température mondiale du mois : NASA GISTEMP prévue par ERA5 (piste n° 26, 11/11/2026) — ÉCARTÉE le jour même

Passage du chercheur du 11/11/2026, 16 h 20 UTC. Avantage de RÈGLE et d'INFORMATION : les marchés « <mois> 2026 Temperature Increase
(ºC) » (6 tranches) et « <mois> 1st, 2nd, or 3rd hottest on record? » se règlent sur la NASA GISTEMP (`GLB.Ts+dSST.txt`, base
**1951-1980**), publiée vers le 10-15 du mois suivant ; Copernicus publie ERA5 (Climate Pulse, chaque jour, 2 à 5 jours de retard ;
bulletin mensuel vers le 6) et la presse parle en « °C au-dessus du préindustriel » (octobre 2026 : « 1,75 °C »).

## Relation GISS − ERA5 (Climate Pulse, anomalie 1991-2020, `era5_daily_series_2t_global.csv`)
- 381 mois 1995-2026 : GISS = 0,613 + 0,936 × ERA5, écart-type du résidu 0,056 ; écart GISS − ERA5 moyen 0,605 (0,581 depuis 2018).
- 2026 : écart 0,57 (janvier) à 0,77 (mars), puis 0,568 / 0,574 / 0,561 en juillet, août, septembre.
- Octobre − moyenne juillet-septembre de l'écart : +0,046 ± 0,066 (1980-2025), +0,001 ± 0,048 (depuis 2010) ; années d'El Niño
  fort : 1997 +0,07, 2015 +0,06, 2023 −0,06.

## Octobre 2026 (marché 1108696, non publié par la NASA au 11/11 16 h UTC)
ERA5 d'octobre : **+0,904** (record ; 2023 : 0,850). GISS prévu **1,47 ± 0,05** (depuis 2010) à **1,52 ± 0,07** (1980-2025).

| Tranche | Chance (2 réglages) | Marché (milieu ; achat) |
|---|---|---|
| > 1,49 | 0,32-0,63 | 0,82 (vendeur 0,99, acheteur 0,65) |
| 1,45-1,49 | 0,23-0,39 | **0,036 (vendeur 0,068, 486 parts)** |
| 1,40-1,44 | 0,11-0,23 | 0,006 |
| < 1,40 | 0,03-0,06 | ~0,02 |

« 1st hottest » (record d'octobre 1,34) : 0,9885, juste. Lecture probable du marché : la base préindustrielle (1,75 °C) lue comme si
c'était la base de la NASA. **Conviction** `giss-octobre-2026-145-149` (OUI, 0,168 après rapprochement de moitié, borne 0,12, mise
2 % au plus, date limite le 12/11). Cycle local : 121,5 parts à 0,068. Étiquette `global-temp` (832) ajoutée au scanner : sans elle,
la stratégie de convictions ne voyait pas le marché.

## Novembre 2026 (marché 1283624)
ERA5 des 9 premiers jours : +1,064 (fin de mois − 9 premiers jours : −0,009 ± 0,094 sur 1995-2025) → GISS ≈ 1,63-1,68 ± 0,11 :
« > 1,54 » ≈ 0,83 contre 0,575 (vendeur 0,84) ; après rapprochement, rien d'achetable. À relire début décembre.

## Test sur le passé (16 h 30 UTC, même passage) : **écartée**

`temperature_mondiale/releve.py` (étiquette 832, `/events/keyset`) : 61 événements réglés, dont 27 mois « Temperature Increase »
(avril 2024 → septembre 2026, tranches réglées sur la première publication NASA). `temperature_mondiale/analyse.py <evenements> <csv
Climate Pulse> <GLB.Ts+dSST.txt> <jour> [écart-type] [décalage]` : GISS prévu = ERA5 du mois + écart GISS − ERA5 moyen des 3 mois
d'avant, loi normale (écart-type 0,05) ; prix de chaque tranche au jour J du mois suivant à 12 h UTC (`prices-history`).

| Jour de décision | Log-score de la tranche gagnante : calcul | marché | Achats simulés (chance − prix − 0,02 − frais ≥ 0,05) |
|---|---|---|---|
| 5 | −1,67 | **−0,57** | 65 paris, 15 gagnés pour 15,0 attendus (prix), 35,8 (calcul) ; −3,0 % |
| 2 | −1,67 | **−0,80** | 69 paris, 17 gagnés pour 20,2 attendus ; −18,4 % |

Le marché met souvent 0,75-0,93 sur la bonne tranche dès le 2-5 du mois, quand le calcul se trompe de 0,05 à 0,14 °C (mai 2026 :
prévu 1,24, publié 1,13). Le marché lit sans doute les entrées de GISTEMP (stations GHCN, océans ERSST, publiées vers le 3-8 du mois)
ou recalcule GISTEMP (code public) ; ERA5 n'est pas assez proche de l'arbitre. Réglages essayés : 3 (jour 5 et jour 2 avec un écart-type de 0,05 ; jour 2 avec 0,08 : −1,52 contre −0,80, 70 paris, −3,9 %), tous perdants. Regard vers le futur connu (GISS des mois d'avant lu après révision) : il ne favorise que le calcul.

**Conséquence** : la conviction `giss-octobre-2026-145-149` (écrite à 16 h 22) est abandonnée à 16 h 35 avant toute fusion (`abandon:
true`, gardée écrite) : le « 0,82 sur > 1,49 » n'était pas une confusion de base mais probablement la lecture de GHCN/ERSST d'octobre.
Leçon (carnet d'expériences, skill `prevoir-un-marche`) : contre un marché récurrent très sûr de lui, tester d'abord la même famille sur
ses mois réglés.

## Ce qui resterait (si un jour)
- Relire le règlement d'octobre (publication NASA attendue vers le 12-14/11) : la tranche gagnante dira qui avait raison.
- Seulement avec une source plus proche de l'arbitre (GHCN-m + ERSST, ou GISTEMP recalculé) : fantôme qui lit Climate Pulse chaque jour et chiffre chaque tranche (même calcul), avec le
  journal des prévisions dès le premier jour (`<nom>:histo`). Marchés réglés des mois passés : à relever (prix avant publication
  contre ce calcul) avant d'écrire la stratégie.
