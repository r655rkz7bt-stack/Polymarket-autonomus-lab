# Météo : prévisions d'ensemble et Observatoire de Hong Kong (23/10/2026)

Chantiers n° 34 (Open-Meteo Ensemble) et Hong Kong Observatory de `experiments/CHANTIERS.md` / `experiments/veille_api_publiques.md`.
Scripts : `experiments/meteo_ensemble/` (données téléchargées dans `donnees/`, ignoré par Git).

## En bref, pour Etienne
- **Hong Kong** : un nouveau lecteur (`meteo_hko`) lit l'Observatoire de Hong Kong, l'arbitre des 8 marchés de température de
  Hong Kong. En le préparant, j'ai trouvé que ces marchés se règlent en **coupant** les décimales (31,9 °C → tranche « 31°C »),
  pas en arrondissant : 166 marchés réglés sur 166. Notre modèle météo supposait l'arrondi : sur Hong Kong, il se serait
  trompé d'un demi-degré. C'est corrigé et testé.
- **Ensemble** (une prévision faite de 82 scénarios au lieu de 2) : Open-Meteo **ne garde pas** les anciennes prévisions
  d'ensemble (3 jours seulement, et ce ne sont pas des prévisions faites la veille). On ne peut donc **pas** juger l'idée sur
  le passé aujourd'hui. J'ai mis en place un **relevé automatique** : toutes les 6 heures, le cycle note la probabilité de
  chaque tranche ET le prix du marché au même moment. Dans 5 à 7 jours, il y aura assez de marchés réglés pour le test.
- **Verdict : pas testable aujourd'hui.** Aucune stratégie pour le capital. Pas de fantôme non plus (raison au § 5).

## 1. Hong Kong : qu'est-ce qui tranche, exactement ?
Description Gamma d'un marché (« Will the highest temperature in Hong Kong be 31°C on October 24? ») : « the highest temperature
recorded by the Hong Kong Observatory […] specifically the "Absolute Daily Max (deg. C)" […] in the relevant "Daily Extract"
(https://www.weather.gov.hk/en/cis/climat.htm) […] measures temperatures in Celsius to one decimal place ». Le minimum : « Absolute
Daily Min ». Le jour est le jour local (heure de Hong Kong, UTC+8, sans heure d'été). Fin Gamma : 12 h UTC (20 h locales) du jour ;
le marché reste ouvert jusqu'à la publication.

**Contrôle du règlement** (`hk_reglement.py`, résultats dans `resultats_hk_reglement.txt`) :

| Relevé officiel | Marchés réglés relus | Tranche = troncature | Tranche = arrondi |
|---|---|---|---|
| CLMMAXT / CLMMINT (open data HKO, station HKO), août-septembre | 122 | **122 / 122** | 61 / 122 |
| bulletin du lendemain RYES (`HKOReadingsMaxTemp` / `MinTemp`, « provisoire »), 1er-22 octobre | 44 | **44 / 44** | — |

Donc la tranche « 27°C » contient 27,0 à 27,9 °C. Les marchés NOAA (METAR en degrés entiers) gardent leur lecture.
Correctifs : `weather_model.truncated(q)` (tranche décalée de +0,5) et `certain_side(..., truncation=True)` (règle « tranche déjà
dépassée » ; sans lui, 31,6 °C « dépassait » la tranche 31 °C avec une marge de 0,5). `temperature_floor` passe la règle lue dans
le relevé (`regle: troncature`).

**Le lecteur** (`src/polymarket_agent/sources/hko.py`, réglage `meteo_hko` : `enabled`, `every_minutes: 15`, `veille`) :
- `latest_since_midnight_maxmin.csv` (open data, sans clé) : maximum et minimum **depuis minuit**, au dixième, ligne « HK Observatory »,
  mis à jour toutes les 10 minutes. Vérifié en vrai le 24/10 à 02 h 20 locales : max 28,3 °C, min 27,0 °C ;
- bulletin RYES de la veille (≈ 00 h 15 locales) : la valeur qui tranchera le marché d'hier (le 23/10 : min 23,8 °C ; le marché
  « 23°C » était coté 0,998, cohérent avec la troncature) ;
- rattaché aux marchés dont la description cite l'Observatoire (`intel_pipeline.weather_station`), au même format que `meteo_metar`
  (`jour_local`, `max_jour_c`, plus `min_jour_c`) : la logique « tranche déjà dépassée » les couvre ;
- mode dégradé : panne ou réponse illisible → « indisponible », le cycle continue ; aucun marché de Hong Kong → aucun appel.
- 2 appels par passage (96 + 96 par jour). Tests : `tests/test_hko.py` (réponses simulées reprises des vraies).

Limite : le « depuis minuit » vient de la station automatique de l'Observatoire ; la valeur qui tranche est celle du Daily Extract.
Pas encore comparés jour par jour (le bulletin RYES, lui, a redonné 44 règlements sur 44).

## 2. Existe-t-il des prévisions d'ensemble passées, gratuites ?
Toutes les URL ont été appelées le 23/10/2026 (`sonde_historique.py`, `sonde_runs.py`, réponses dans `resultats_sonde_historique.txt`).
Lieu d'essai : Londres City (EGLC).

| Essai | URL (paramètres principaux) | Réponse |
|---|---|---|
| dates passées | `ensemble-api.open-meteo.com/v1/ensemble?models=gfs025&start_date=2026-10-01&end_date=2026-10-03` | 200, 31 séries… **toutes vides** |
| dates lointaines | idem, `start_date=2026-07-01` | 400 « allowed range from 2026-07-22 to 2026-11-27 » (la fenêtre existe, pas les valeurs) |
| `past_days=30` / `92` | `ensemble-api…&past_days=30` | 200, 744 heures demandées, **seules les 96 dernières remplies** (20/10 → 23/10) |
| variable « veille » | `ensemble-api…&hourly=temperature_2m_previous_day1` | 200, 31 séries `previous_day1_memberNN`, **toutes vides** |
| un passage précis | `ensemble-api…&run=2026-10-10T00:00`, et `run=` du 19, 22, 23/10 (00 h et 12 h) | 400 « The requested model run is not available » (GEFS et ECMWF) |
| « single runs » | `single-runs-api.open-meteo.com/v1/forecast?models=ncep_gefs025&run=…` | 400 « run is not available » (ou 429) |
| « previous runs », « historical forecast » avec un modèle d'ensemble | `previous-runs-api…&models=ncep_gefs025`, `historical-forecast-api…&models=ncep_gefs025` | 429 « Daily API request limit exceeded » depuis la session (pas de réponse sur le fond) |
| sous-domaine « ensemble single runs » | `ensemble-single-runs-api.open-meteo.com` | n'existe pas (échec de connexion) |

La documentation de l'API d'ensemble le dit : « You can retrieve up to **three days** of historical data. Additionally, we store
ensemble means and spreads with a longer retention period. » Et les 3 jours passés sont recollés à partir des passages les plus
récents (échéance de quelques heures) : ce ne sont **pas** des prévisions faites la veille. S'en servir pour un test serait regarder
vers le futur.

**Hors d'Open-Meteo, il existe des archives brutes gratuites** (vérifiées, HTTP 200) :
- NOAA GEFS sur AWS (`noaa-gefs-pds.s3.amazonaws.com/gefs.20261001/00/atmos/pgrb2ap5/gep01.t00z.pgrb2a.0p50.f024`) : un fichier
  GRIB2 de 15 Mo par membre et par échéance, avec index ; on peut ne télécharger que `TMAX` / `TMIN` à 2 m (max / min sur 6 h) :
  **139 Ko en 0,37 s** par champ. Pour 20 jours de marchés : ≈ 31 membres × 10 échéances × 2 champs × 20 jours ≈ 12 400
  téléchargements partiels, ≈ 1,7 Go, et un décodeur GRIB2 (pygrib ou eccodes, absent ici : environnement `.venv-recherche`) ;
- ECMWF (données ouvertes) sur AWS (`ecmwf-forecasts.s3.eu-central-1.amazonaws.com/20261001/00z/ifs/0p25/enfo/`) : un fichier de
  6 Go par échéance (tous les membres), avec index pour ne prendre que la température.
C'est un vrai historique, mais c'est un chantier d'un passage entier ; pas fait aujourd'hui.

## 3. Ce qui est en place : lecteur d'ensemble et relevé quotidien
- `sources/weather.py` → `EnsembleSource` (`meteo_ensemble`) : `models=gfs025,ecmwf_ifs025`, `forecast_days=3`, `timezone=auto`,
  10 stations par appel, délai de 60 s (15 s ne suffisaient pas : 3 délais dépassés au cycle local) ; pour chaque jour LOCAL, le
  maximum et le minimum de **chaque** membre (31 GEFS + 51 ECMWF, témoins compris ; l'ancien `experiments/ensemble_meteo/releve.py`
  en oubliait les 2 témoins).
- Réglage `meteo_ensemble` (`config/settings.yaml`) : `every_minutes: 360`, `tous_les_marches: true` (relit sur Gamma TOUS les
  marchés de température ouverts qui finissent dans `heures: 48`, pas seulement les marchés surveillés) ; coordonnées des stations
  METAR inconnues demandées une fois à aviationweather.gov, celles de l'Observatoire fixées.
- `weather_ensemble.py` : probabilité d'une tranche = **part des membres** dont la valeur, dans l'unité du marché (°C ou °F),
  tombe dans [bas ; haut[ de la tranche, avec la règle du marché (arrondi ou troncature). À chaque passage de la source, le cycle
  écrit dans la base :
  - `meteo_ensemble_releves` : instant, marché, événement, station, jour, type, règle, heures avant minuit local, p GEFS, p ECMWF,
    p de l'ensemble, nombre de membres, meilleur acheteur, meilleur vendeur, dernier prix, jeton OUI ;
  - `meteo_ensemble_membres` : les membres eux-mêmes (pour régler un biais de station après coup, sans regard vers le futur).
  Ces tables sont gardées par la sauvegarde quotidienne de la base (branche `data`, `backup/essentiel.sqlite.gz`).
- Les marchés reçoivent aussi l'ensemble de leur station (`market.weather["ensemble"]`) : prêt pour une stratégie, aucune ne s'en sert.
- Mode dégradé et tests : `tests/test_weather_ensemble.py` (format réel, °F, troncature, panne, aucune station).

**Coût en appels** (règle de la page tarifs d'Open-Meteo, relue le 23/10 : au-delà de 10 variables, un appel en vaut plusieurs ;
la page de l'API d'ensemble compte 40 membres pour 4,0 appels, donc **chaque membre compte comme une variable**) :
82 membres = **8,2 appels par station**. Réglage `every_minutes: 360` (les ensembles changent toutes les 6 h) : 50 stations ×
8,2 × 4 ≈ **1 640 appels par jour**, ≈ 410 en une minute à chaque passage. Avec `meteo_prevision` (≈ 1 200 par jour) : ≈ 2 900 par
jour pour une limite gratuite non commerciale de 10 000 par jour, 5 000 par heure, 600 par minute et 300 000 par mois (≈ 87 000).
Raisonnable. Attention : depuis la session, les API « previous runs », « historical forecast » et « single runs » répondaient déjà
« Daily API request limit exceeded » (adresse partagée) ; en production, l'adresse change à chaque cycle.

## 4. Le test, quand le relevé aura des marchés réglés
`experiments/meteo_ensemble/evaluer_releve.py --base <market.sqlite>` (base de production : `bash scripts/fetch_data.sh`, puis
`gunzip -c published_data/backup/essentiel.sqlite.gz > /tmp/base.sqlite`), protocole `tester-une-piste` :
0. décisions prises AVANT le début du jour local (`--avance-min 0 --avance-max 48`, heures entre T0 et minuit local) : l'ensemble
   ignore ce que la station a déjà relevé, comparer pendant la journée serait injuste pour lui ;
1. règlement relu sur Gamma (`/markets/<id>`), contrôle « une tranche gagnante par événement » ;
2. biais de chaque station réglé sur la **1re moitié des jours** (valeur réelle = centre de la tranche gagnante, selon la règle) ;
3. marchés **sans vrai échange dans les 2 h avant T0 écartés** (règle du 22/10) ;
4. log-score du modèle contre le milieu du carnet relevé ; puis achats au **premier vrai échange dans les 2 h après T0**
   (`fetch_event_trades` + `taker_cost(after=True)`), frais du marché (0 depuis le 20/10 : `zero_fees`) ;
5. `idea_test.verdict` pour 3 flous (σ 0,3 / 0,6 / 1,0 °C) × 3 écarts (0,05 / 0,10 / 0,15) = **9 réglages** (à dire dans le verdict).
Il faut au moins 4 jours réglés (2 pour régler, 2 pour juger) ; mieux : 7 à 10 jours (≈ 300 marchés par jour relevés 4 fois).

## 5. Ce que montrent les relevés déjà pris
- **Relevé manuel du 23/10, 15 h 23 UTC** (session précédente, `experiments/ensemble_meteo/releves/`) : 1 012 marchés, 48 stations,
  92 événements. Relu à 18 h 45 UTC avec `evaluer_releve.py --releves …` : **0 marché réglé** (ceux du 23-24/10 ne sont pas encore
  tranchés sur Gamma). Rien à juger (`resultats_essai_releve_23oct.txt`).
- **Relevé du nouveau lecteur, en vrai** (copie de la base locale, 23/10 vers 18 h 50 UTC) : statut « ok (2068 tranches relevées) »,
  **49 stations, 188 événements, en 4 secondes** (≈ 49 × 8,2 ≈ 400 appels pondérés). Avance : de −7,9 h (jour local déjà commencé,
  Asie) à +36 h. Dans le cycle local complet, la liste surveillée ne contenait que **3** marchés de température et aucun de Hong
  Kong (aucune stratégie météo ne demande ses marchés) : d'où la relecture de tous les marchés par le relevé lui-même.
- Premier coup d'œil (pas une preuve) : à Hong Kong, pour le 24/10, les deux ensembles bruts ne sont pas d'accord entre eux
  (GEFS : 65 % sur « 32°C », 0 % sur « 30°C » ; ECMWF : 73 % sur « 30°C », 0 % sur « 32°C ») alors que le marché cote « 31°C » 0,42 et
  « 32°C » 0,45. Le point de grille du modèle (22,5 N ; 114,25 E) n'est pas la station : **sans correction du biais de chaque
  station, la part des membres ne vaut rien contre le marché.** C'est pour cela que l'évaluation apprend ce biais sur la 1re moitié
  des jours et que les membres sont gardés.

Pas de fantôme : la règle du labo veut un relevé en direct qui le justifie ; aucun marché relevé n'est encore réglé, rien ne le
justifie. L'arène gaspillerait des paris sur une idée qui, en version « deux prévisions », a déjà coûté −52 € au capital principal.

## Ce qui reste
1. Dans 5 à 7 jours : `evaluer_releve.py --base …` sur la base de production ; verdict avec les 9 réglages ; si « indice » ou
   « retenue » : variante de `meteo_prevision` qui lit `market.weather["ensemble"]` (et `weather_model.truncated` pour Hong Kong).
2. Historique GEFS (NOAA, AWS) : test sur octobre entier, `TMAX`/`TMIN` par plages d'octets, pygrib dans `.venv-recherche`.
3. Comparer le maximum « depuis minuit » de l'Observatoire (relevé du soir) au bulletin RYES du lendemain, jour par jour.
4. `meteo_prevision` (deux prévisions) et `temperature_floor` sont hors de l'arène ; si l'une revient, Hong Kong est couvert
   (troncature lue dans le relevé), mais `MeteoForecast` ne le sait pas encore (elle ne voit que les stations METAR).
