# Piste n° 40 : les marchés annuels de séismes contre la fréquence de base de l'USGS (12/11/2026, passage de 11 h)

**Marchés** (étiquette `earthquakes` 103038, frais `weather_fees` ou aucun) : « How many 7.0 or above earthquakes in 2026? »
(événement 134977, **1,55 M$** de volume, tranches < 5 … 20+), « Highest earthquake magnitude in 2026? » (870991, 29 k$, 7,9 ou moins …
9,0 ou plus), « Will California experience a 7.0 or above magnitude earthquake in 2026? » (744604, 8 k$). Tous réglés sur l'USGS
(compte annuel, magnitude préférée, Californie et ses eaux territoriales), comme les marchés du jour et de la semaine que joue déjà
`seismes_marche` (testés : `experiments/seismes.md`).

**Données** (USGS ComCat, sans clé ; `seismes_annee/scripts/frequences.py` → `seismes_annee/frequences.json`) :
- séismes ≥ 7,0 par an, 2000-2025 : moyenne **14,88**, variance 15,8 (Poisson suffit : pas de surdispersion annuelle) ;
- séismes ≥ 8,0 / 8,2 / 8,4 / 8,6 / 8,8 / 9,0 par an, 1950-2025 : 0,816 / 0,421 / 0,197 / 0,158 / 0,092 / 0,066 ;
- Californie ≥ 7,0, 1950-2025 : 8 lignes dont 4 au large (153 km de Big Lagoon, 121 km de Ferndale…) : **0,105 par an** en les comptant
  (surestime le OUI : la règle ne compte que l'État et ses eaux territoriales).

## Le 12/11/2026 à 11 h UTC (49 jours restants)

13 séismes ≥ 7,0 au catalogue (le dernier : 7,0 au Tibet le 22/10), maximum 7,8 (Philippines 07/06, Indonésie 14/08).

| Marché | Chance calculée | Prix (acheteur / vendeur) |
|---|---|---|
| 11-13 | 0,132 | 0,046 (0,004 / 0,088) |
| 14-16 | 0,721 | 0,68 (0,63 / 0,73) |
| 17-19 | 0,143 | 0,25 (0,18 / 0,32) |
| 20+ | 0,005 | 0,06 (0,01 / 0,11) |
| maximum 7,9 ou moins | 0,879 | 0,845 (0,80 / 0,89) |
| maximum 8,0-8,1 | 0,055 | 0,07 |
| maximum 9,0 ou plus | 0,010 | 0,046 (0,013 / 0,079) |
| Californie ≥ 7,0 | **0,014** | **0,093** (0,081 / 0,105) |

Le marché le plus suivi (le compte, 1,55 M$) est le plus proche ; les queues minces sont payées 3 à 7 fois leur fréquence. Côtés
achetables avec une marge : NON Californie (0,986 pour 0,919), OUI « 11-13 » (0,13 pour 0,088), NON « 17-19 » (0,857 pour 0,82).
Convictions : non (le rapprochement de moitié vers le prix de la méthode `prevoir-un-marche` les ramène sous le seuil de 5 points).

## Ce qui est lancé

**Fantôme `seismes_annee`** (`seismes_annee.py`, source `usgs_annee` toutes les 30 min, séismes ≥ 6,8 depuis le 1er janvier, heure
de l'Est ; Kelly entier sur chance − 0,02, avantage net ≥ 0,04). Aucun test sur le passé possible (un marché annuel par an) : la
mécanique est celle des semaines, testée. Limite connue : pas de témoin EMSC (un ≥ 7,0 vu par l'EMSC et pas encore par l'USGS n'est pas
compté ; `seismes_marche` s'abstient dans ce cas) ; une magnitude « 7,0 » révisée en 6,9 changerait le compte (Tibet, 22/10).

**Cycle local (12/11, 11 h 33 UTC, deux cycles)** : 12 marchés rattachés, 1 proposition (NON Californie), refusée « carnet périmé
(124 s > 120 s) » (carnet calme : `proposals/2026-11-11_carnet_calme_juge_perime.md`, en attente chez Etienne). Elle visait
271 parts ≈ 250 € (Kelly entier sur 0,966 contre 0,919, coupé par le plafond général de 25 %) : paramètre **`mise_max_pari`**
ajouté à `_buy` (facultatif, sans effet ailleurs), 5 % pour `seismes_annee` et `el_nino_cpc` (règle « audace » : 2 à 5 % par pari).
