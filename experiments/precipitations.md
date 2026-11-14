# Précipitations du mois : cumul observé + climatologie contre le prix (12/11/2026, piste n° 32 : NYC ÉCARTÉE aux vrais échanges ; 14/11 : Hong Kong, climatologie seule non concluante, fantôme `pluie_hk` avec ensemble ECMWF)

Passage du chercheur de 1 h (12/11/2026), issu de l'inventaire des sources officielles (`sources_officielles.md`).
Marchés « Precipitation in <ville> in <mois>? » (NYC Central Park, Seattle, Londres Heathrow, Hong Kong, Séoul ; 6-7 tranches,
1-4 k$ de liquidité par événement ; 45 mois réglés de janvier à octobre 2026). Règle NYC : total du mois à Central Park,
« Monthly summarized data » de weather.gov (NOAA) ; valeur pile sur une borne → tranche du dessus.

## Modèle (`precipitations/scripts/`)

Chance d'une tranche = cumul observé du 1er au jour J − 1 (ACIS `data.rcc-acis.org`, sans clé, Central Park = sid 94728) + reste
du mois tiré des mêmes dates de 1951 à 2025 (75 ans). Aucune prévision météo (à ajouter : NWS à 7 jours).

## En direct, 12/11/2026 (NYC novembre, `nyc_novembre.py`)

Cumul du 1er au 10/11 : 0,91" (0,09 le 5, 0,82 le 6 ; le 11 pas encore publié). Modèle : < 2" 0,12 ; 2-3" 0,32 ; 3-3,5" 0,107 ;
3,5-4,25" 0,213 ; 4,25-5,75" 0,147 ; > 5,75" 0,093. Marché (milieu) : 0,15 / 0,21 / 0,195 / 0,225 / 0,215 / 0,125 (carnets
0,08-0,34 d'écart). Écart le plus net : « 2-3" » 0,32 contre 0,21 (vendeur 0,22) ; rapproché de moitié 0,265, borne basse ≈ 0,21 :
**sous le seuil d'une conviction**.

## Test sur le passé, NYC janvier → octobre 2026 (`test_nyc.py`)

Le 11 de chaque mois à 12 h UTC (cumul du 1er au 10 seulement), 10 mois, 60 tranches :
- log-score moyen : **modèle −0,370, marché −0,395** (le modèle fait un peu mieux) ;
- achats simulés quand chance − (prix + 0,02) ≥ 0,08 : **22 paris, 15 gagnés pour 12,5 attendus par les prix (16,3 par le
  modèle), +38 % par mise** ; mois perdants : janvier et février (−3 paris), gagnants : avril à octobre.

**Réserves (ne pas croire ce chiffre en l'état)** : (1) prix = milieu horaire du CLOB sur des carnets de 300-700 $ : le défaut
du 22/10 (« prix milieu sans échange réel ») a déjà transformé +9 à +31 % en −1 à +2 % ; (2) 10 mois seulement, paris d'un même
mois liés (un seul tirage par mois : t par mois à calculer) ; (3) un seul réglage (jour 11, seuil 0,08) ; (4) frais `weather_fees`
non comptés ; (5) une seule ville.

## Aux vrais échanges, même passage (`test_nyc_echanges.py 0.08 11`)

Premier échange réel du jeton dans les 72 h après le 11 à 12 h UTC, à un prix ≤ chance − 0,08 (Data API v2, 1 232 échanges en
octobre, quelques centaines les autres mois) :
- tous les échanges : **28 paris, 13 gagnés pour 9,8 attendus, +108 % par mise, t par mois 0,99 (8 mois)** ; mais le gain vient
  d'échanges de 1 à 5 parts à des prix extrêmes (juillet : NON « 5-6" » à 0,07 pour 9,9 parts, les deux côtés de 4 tranches
  achetés à 0,02-0,07 et 0,38-0,68) ;
- échanges d'au moins 10 parts : **13 paris, 6 gagnés, −23 % par mise**.

**Verdict NYC : écartée** (le gain s'efface dès qu'on demande 10 parts ; même leçon que le NON crypto à 0,10-0,20 du 27/10, règle
« profondeur à tester avant d'écrire exécutable »). Le log-score un peu meilleur que le marché (−0,370 contre −0,395) dit que la
climatologie lit bien le cumul, mais les carnets sont trop minces pour en vivre. Deux réglages regardés (prix milieu, échanges ;
seuil 0,08, jour 11).

## À faire (si on reprend)

1. Refaire aux **vrais échanges** (`data_api.lire` v2, `trades` par marché) : premier échange réel après le 11 à ≤ prix + 2
   centimes, profondeur (parts) ; frais du marché (`feeSchedule`).
2. Seattle (règle : « Seattle City Area », vérifier le sid ACIS), Londres (Met Office `heathrowdata.txt`, mensuel seulement :
   il faut un relevé quotidien, à chercher), Hong Kong (HKO, quotidien), Séoul (KMA).
3. Plusieurs jours de décision (5, 11, 18, 25) et seuils (0,05-0,15) ; t par mois ; `idea_test.verdict`.
4. Si l'indice tient : fantôme (source ACIS quotidienne, étiquette Gamma des précipitations).

## Hong Kong (14/11/2026, passage de 6 h, `precipitations/hk/`)

**Pourquoi Hong Kong** : l'événement le plus liquide de la famille (« Precipitation in Hong Kong in November? », 8,5 k$ de liquidité,
195 échanges en 3 jours, 7 tranches de « < 5 mm » à « 95 mm+ »). Règle : « Total Rainfall (mm) » du Daily Extract de l'Observatoire
(`www.weather.gov.hk/cis/dailyExtract/dailyExtract_AAAAMM.xml`, JSON, sans clé), valeur pile sur une borne → tranche du dessus.

**Données** : série quotidienne complète de l'Observatoire depuis 1884 (`data.weather.gov.hk/weatherAPI/cis/csvfile/HKO/ALL/daily_HKO_RF_ALL.csv`,
« *** » = manquant) ; bulletin de la veille (`opendata.php?dataType=RYES&date=AAAAMMJJ&lang=en&rformat=json`, champ
`HKOReadingsRainfall`, publié vers 00 h 15 HKT) ; pluie de l'heure passée par station (`hourlyRainfall.php`, station RF023 « Hong Kong
Observatory », observation à hh:45) ; prévision à 9 jours (`weather.php?dataType=fnd`, PSR) ; ensemble ECMWF 51 membres (Open-Meteo).

**Contrôle du règlement : 8 mois sur 8** (mars 154,4 « 150-160 » ; avril 160,4 « 160-170 » ; mai 227,2
« 220-230 » ; juin 600,5 « 500+ » ; juillet 790,3 « 600+ » ; août 380,0 « < 425 » ; septembre 94,3 « < 275 » ; octobre 81,0 « 70-120 ») ;
le script `test_hk_echanges.py` le revérifie tranche par tranche (`assert`).

**Le piège du jour (enquête, `enquetes/2026-11-14_matin_secheresse_disparue_et_pluie_du_jour.md`)** : au 14/11 06 h UTC, le Daily
Extract s'arrêtait au 12/11 (3,2 mm) ; « < 5 mm » et « 5-10 mm » se vendaient 0,02-0,05 et la climatologie leur donnait 0,37-0,84.
En réalité 7,9 mm le 13/11 (RYES) et une nuit d'averses fortes (METAR VHHH, +SHRA de 01 h à 06 h HKT ; ECMWF et GFS annonçaient
87-103 mm sur la grille) : le marché le savait (OUI « 95 mm+ » acheté 0,66 pour 151 parts à 00 h 20 UTC). Pas de conviction : la
pluie du 14/11 à la station n'est pas connue avant le bulletin du 15/11.

**Test sur le passé, climatologie seule, aux VRAIS échanges** (`test_hk_echanges.py <seuil> <jour> <parts>`) : cumul des jours 1 à
J − 1 + reste du mois tiré des mêmes dates 1947-2025 ; premier achat réel (côté preneur) dans les 72 h à ≤ chance − seuil :

| réglage | paris | gagnés | attendus (prix) | attendus (modèle) | rendement | t par mois |
|---|---|---|---|---|---|---|
| seuil 0,08, jour 11, tous | 17 | 9 | 6,4 | 9,9 | +121 % | 1,18 |
| seuil 0,08, jour 11, ≥ 10 parts | 14 | 7 | 4,3 | 7,5 | +151 % | 1,23 |
| seuil 0,12, jour 11, ≥ 10 parts | 12 | 6 | 3,5 | 6,4 | +183 % | 1,31 |
| seuil 0,05, jour 11, ≥ 10 parts | 14 | 7 | 4,3 | 7,5 | +151 % | 1,23 |
| seuil 0,08, jour 11, ≥ 50 parts | 9 | 3 | 2,6 | 4,4 | −22 % | −0,37 |
| seuil 0,08, jour 5, ≥ 10 parts | 9 | 5 | 4,1 | 5,3 | +7 % | 0,17 |
| seuil 0,08, jour 18, ≥ 10 parts | 14 | 7 | 6,6 | 9,0 | −26 % | −1,42 |
| seuil 0,08, jour 25, ≥ 10 parts | 12 | 6 | 5,0 | 8,0 | −31 % | −1,20 |

8 réglages. Le jour 11 gagne grâce à deux billets (OUI « 600 mm+ » à 0,06 en juillet, OUI « 500 mm+ » à 0,13 en juin) ; plus tard dans
le mois et en grosses quantités, rien. Le modèle annonce toujours plus de gains qu'il n'en fait (7,5-9,9 attendus par lui pour 6-9) :
la climatologie seule est trop sûre d'elle. **Verdict climatologie seule : écartée** (pas d'avantage robuste ; même conclusion que NYC).

**Fantôme `pluie_hk` (expérience audacieuse, `src/polymarket_agent/pluie_hk.py`)** : ce que le test ne contient pas, c'est
l'information du jour : pluie des jours finis (Daily Extract + RYES), pluie du jour additionnée heure par heure (journal
`pluie_hk:heures`, source relue toutes les 20 min), reste du mois moitié ensemble ECMWF 51 membres (la valeur du jour en cours est
remplacée par la climatologie : l'ensemble y met la pluie déjà tombée), moitié climatologie. Aucune chance sans toutes les heures du
jour. Écart minimal 0,08 + incertitude 0,05 (le modèle est trop sûr de lui au test), Kelly entier, 4 % du fantôme au plus par pari.
Cycle local : 7 tranches rattachées (dès que le journal des heures est complet). L'ensemble n'a pas d'archive : c'est lui qu'on teste
en direct. Prochain contrôle : le bulletin RYES du 14/11 (pluie de la nuit à la station) contre la prévision de la grille (87-103 mm).
