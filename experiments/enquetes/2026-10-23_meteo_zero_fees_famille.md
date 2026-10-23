# La météo passe en « zero_fees » et change de source : deux pannes silencieuses (23/10/2026, passage de l'après-midi)

Contrôle à la main, famille 6 (« ce qui ne tourne plus ») : `loterie_meteo` avait acheté 52 fois puis plus rien depuis le **20/10 à 16 h 27**, sans être
« muette » (le contrôle `muettes` ne regarde que les stratégies qui n'ont jamais acheté).

## Constat
- Abstentions du dernier cycle (`published/data.json`) : `loterie_meteo` voit 371 marchés et en écarte **371** pour « famille de marchés exclue ».
- `market_family` (`strategy_engine.py`) tire la famille du **barème de frais** de Gamma (`feeType` : `weather_fees` → weather, `politics_fees` → politics…).
  Relevé Gamma du 23/10, événements de température (`tag_id=84`) selon leur date de fin : `weather_fees` jusqu'au 18/10 (94 événements par jour), mélange le 19/10
  (19 `zero_fees`, 75 `weather_fees`), **`zero_fees` pour tous à partir du 20/10**. Le 23/10 : 595 marchés météo sur 600 sont en `zero_fees` (taux 0).
- Ce n'est pas la seule famille : sur les 600 marchés les plus actifs de chaque étiquette, `zero_fees` fait 471 de la politique (2 en `politics_fees`), 577 de la finance
  (5 `economics_fees`), 141 de la géopolitique ; la crypto (`crypto_fees_v2`) et le sport (`sports_fees_*`) ne bougent pas. Sur les 1 500 marchés les plus échangés :
  734 en `zero_fees`, 329 `sports_fees_v3`, 168 sans frais, 138 `crypto_fees_v2`.
- Effets :
  1. `loterie_meteo` (familles [weather]) : aveugle depuis le 20/10 ; 3 filtres `familles` qui nomment weather, politics, finance… ne voient plus ces marchés ;
  2. les stratégies `familles: [politics, sans_frais]` (`favori_politique*`, `parking_politique`, `nf_politique`…) ne gardent que les marchés sans frais et les 2 `politics_fees`
     (94 marchés sur 393 passent leur filtre) : leur univers a rétréci sans que personne le dise ;
  3. plafond de famille du principal (`max_famille`) : la météo, la politique et la finance forment désormais une seule famille « zero » ;
  4. **les frais de ces marchés valent 0** : le « −6 % aux prix payés » du test météo (`meteo_backtest.md`, frais 0,05 × p × (1 − p)) et les tests politiques ne
     décrivent plus les coûts d'aujourd'hui (les billets de loterie à 0,01 payaient ≈ 5 % de leur prix en frais).

## Cause
`market_family` suppose que le barème de frais nomme la famille. Gamma a regroupé des familles sous un barème à taux zéro (`feeType: zero_fees`, `rate: 0`).

## Correctif
- `market_family` : un marché `zero_fees` dont l'adresse d'événement commence par `highest-temperature`, `lowest-temperature`, `precipitation`, `where-will-it-rain`,
  `will-it-rain`, `rain-in-` ou `snow-in-` est de la famille **weather** (test `test_zero_fee_weather_markets_stay_in_the_weather_family`). Vérifié en direct :
  `loterie_meteo` reçoit de nouveau les marchés de température (cycle local).
- Contrôle `familles_vides` (`enquete.py`, test) : stratégie dont TOUS les marchés vus sont écartés par la famille ; il signale `loterie_meteo` sur les données publiées du 23/10.
  `scripts/enquete.py` lit désormais les raisons d'abstention dans `published/data.json`.

## Deuxième panne, même cause de fond : les lecteurs de station ne reconnaissent plus la source
Le statut publié du dernier cycle dit `meteo_metar : ok (0 observations)` et `meteo_prevision : ok (0 observations)` : « ok » cache une absence totale de relevés.
Les marchés de température citent maintenant `https://aviationweather.gov/api/data/metar?ids=EGLC&format=raw&…` comme source de résolution (**199 événements sur 255**, relevé
Gamma du 23/10 ; les 46 autres gardent `weather.gov/wrh/timeseries?site=…`), et `sources/weather.py:STATION` ne lit que la seconde forme : aucune station, aucun relevé METAR, aucune
prévision, aucune « valeur réelle » nouvelle pour l'étalonnage (`meteo_reel` : 828 valeurs, anciennes). Correctif : `STATION` accepte les deux formes (test sur le lien réel
d'EGLC, avec `ids` après d'autres paramètres, et refus d'un lien TAF) ; `resolution_sources.py` connaît le domaine `aviationweather.gov`.

## Reste ouvert (décision de recherche, pas un bug)
- La politique et la finance ne se reconnaissent pas à leur barème (pas d'étiquette dans la réponse Gamma `/markets`). Ajouter `zero` aux listes `familles` de `favori_politique*`
  élargirait leur univers à tous les marchés sans frais (Fed, culture, tech) : à décider avec une preuve sur le passé, pas à la volée.
- Refaire le test météo avec des frais nuls (données et scripts : `experiments/meteo_backtest/`, `experiments/ensemble_meteo/`) : 1,36 M$ échangés par jour sur ≈ 100 événements,
  sans frais ; le relevé en direct des ensembles Open-Meteo (`experiments/ensemble_meteo/releve.py`) prépare ce test.
