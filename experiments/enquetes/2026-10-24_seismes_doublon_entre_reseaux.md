# 2026-10-24 (après-midi, 2e enquête) : un séisme compté deux fois dans le catalogue USGS (famille 3 : la donnée n'est pas celle qu'on croit)

Relecture à la main des derniers achats des fantômes à source propre (séismes, détroits, tweets, mots). Un achat ne tenait pas : `seismes_marche`, 13 h 22 UTC, **NON « exactement 2 séismes de 6,5 ou plus »**
(semaine du 19 au 25/10, marché 5775544) acheté **0,259 pour 106 parts, chance estimée 0,97**, alors que le marché cote le OUI de « exactement 2 » à 0,76 (écart 0,74-0,79, 8 353 $ de volume).

## Constat
- Catalogue USGS (requête `minmagnitude=6.0`, du 19/10 04 h UTC) : 6,0 (19/10), **6,6 « Mi » réseau `pt`** (20/10 04:20), **6,3 « mww » réseau `us`** (20/10 04:20), 7,0 (22/10), 6,9 (24/10), 6,3 (24/10).
  Les deux événements du 20/10 sont **le même séisme** (Vanuatu, 195 et 197 km au nord-ouest de Port-Olry, même minute) listé par le centre d'alerte du Pacifique (`pt26293000`) et par le NEIC (`us6000u3jl`).
- Notre relevé compte donc 3 séismes ≥ 6,5 (6,6 ; 7,0 ; 6,9) et 14 séismes ≥ 5,5 ; **sans le doublon : 2 et 13**. Le marché cote exactement ces deux nombres : « exactement 2 » 0,76 (6,5 ou plus) et « plus de 13 » 0,80 (5,5 ou plus).
- Selon que le règlement compte le doublon ou non (association des deux événements par l'USGS avant la fermeture, le 26/10, ou 48 h après), le NON acheté gagne (3) ou perd (2). Le passage du 24/10 (matin) notait que le marché
  compte « un séisme de plus » que le catalogue d'aujourd'hui dans 10 semaines sur 57 : même famille de cause (les entrées de réseaux secondaires apparaissent puis disparaissent du catalogue ; le règlement lit le catalogue **au moment du règlement**).
- Exposition du fantôme : NON « exactement 2 » 27,5 € (0,259 × 106) et OUI « exactement 3 » 3 € (0,21 × 15), tous deux justes si le compte est 3, perdus si 2 ; le fantôme prend une chance estimée à 0,97 sur une donnée incertaine.

## Cause
`seismes.py` (`weekly_count`, `daily_cdf`) compte chaque ligne du flux USGS sans regarder si deux lignes de réseaux différents décrivent le même séisme. Le plafond de certitude (0,97) ne couvre pas un compte ambigu.

## Correctif
- `seismes.dedup_rows` : retire l'événement d'un autre réseau qui a un événement `us…` à moins de 120 secondes (le NEIC est la référence).
- `attach_seismes` pose `p` (avec doublons) **et** `p_dedup` (sans) ; `SeismesMarche` ne propose rien quand les deux diffèrent de plus de `max_ecart_doublon` (0,15) : « doublon possible entre réseaux USGS (compte incertain) ».
- Tests : `tests/test_seismes.py::test_dedup_rows_drops_the_other_network_copy_of_the_same_quake_only` (cas réel du 20/10 : 5 contre 4, `p` 0 contre > 0,2) et
  `test_strategy_abstains_when_the_duplicate_changes_the_count`.

## À vérifier au prochain passage (reste ouvert)
Lire le règlement du marché 5775544 (« exactement 2 » ≥ 6,5, semaine du 19/10) et de 5775534/« plus de 13 » (≥ 5,5) : le compte final est-il avec ou sans le doublon `pt26293000` ? Si le règlement compte
sans doublon, l'écart « le marché compte un de plus » s'explique à l'envers par des doublons qui restent listés jusqu'au règlement : refaire alors la comparaison des 57 semaines avec `dedup_rows` sur un relevé qui garde les identifiants de réseau
(le relevé `experiments/seismes/releves/usgs_m5.json.gz` garde les identifiants).

## Contrôle automatique
Pas ajouté à `enquete.py` : le relevé publié (`published/data.json`) ne contient pas les identifiants USGS ; le correctif agit dans la stratégie. À reprendre si les observations du cycle gardent les lignes USGS.
