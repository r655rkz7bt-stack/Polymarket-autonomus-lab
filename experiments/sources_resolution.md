# Sources de résolution des 1500 marchés actifs (échéance 30 min à 30 jours, 15/10/2026 20:06 UTC)

Chantier n°0 (`experiments/CHANTIERS.md`). Tableau produit par `resolution_sources.markdown()` à partir
de l'API Gamma (tous les marchés actifs lus par le scanner). Le cycle archive en continu la source de
résolution des marchés surveillés (table `market_rules`) et en affiche le résumé dans la console du
tableau de bord (`sources_resolution`). « Lecteur » = source du projet qui lit directement l'arbitre
(ou un équivalent officiel) ; « — » = rien encore (voir la remarque). Pour compléter : `CATALOG`
dans `src/polymarket_agent/resolution_sources.py`.

Étape suivante (point 3 du chantier, libre) : une stratégie qui compare la valeur lue à la source
(score, prix Binance) au seuil du marché et au temps restant. `crypto_threshold` le fait déjà pour
les prix crypto, désormais lus chez Binance (l'arbitre) ; les scores MLB / NHL / football arrivent
comme observations rattachées aux marchés (titres « Équipe A 2 - 3 Équipe B (terminé) »).

| domaine | marchés | organisme | lecteur | remarque |
|---|---|---|---|---|
| (aucun) | 245 |  | — | aucune source indiquée |
| binance.com | 234 | Binance (bourse crypto) | crypto_prices | bougies officielles via data-api.binance.vision (données de marché publiques) |
| weather.gov | 210 | NOAA (station d'aéroport citée) | meteo_metar | relevés METAR officiels via aviationweather.gov ; max METAR ≤ max officiel |
| nfl.com | 79 | National Football League | — | pas d'API publique officielle ; en complément : cotes des bookmakers (odds_api, ODDS_API_KEY) |
| x.com | 68 | X (Twitter) | — | API payante : interdit n°2 |
| pythdata.app | 63 | Pyth (oracle de prix) | — | hermes.pyth.network, API publique : à étudier |
| fec.gov | 57 |  | — | à étudier |
| ncaa.com | 48 | NCAA | — | pas d'API publique documentée |
| nhl.com | 28 | National Hockey League | nhl_stats | api-web.nhle.com, API publique de la ligue |
| laliga.com | 25 |  | — | à étudier |
| hltv.org | 24 | HLTV (esport CS) | — | pas d'API ; pages protégées contre les robots : on ne contourne pas |
| gol.gg | 23 | Games of Legends (esport LoL) | — | pas d'API publique |
| itftennis.com | 22 |  | — | à étudier |
| app.pyth.com | 22 | Pyth (oracle de prix) | — | hermes.pyth.network, API publique : à étudier |
| uefa.com | 21 | UEFA | football_data | pas d'API publique UEFA ; football-data.org (clé gratuite FOOTBALL_DATA_KEY) donne les scores |
| dotabuff.com | 20 | Dotabuff (esport Dota 2) | — | pas d'API ; api.opendota.com est l'équivalent ouvert (chantier n°15) |
| dadosabertos.tse.jus.br | 20 | Tribunal électoral du Brésil | — | données ouvertes officielles : à étudier |
| gov.il | 15 |  | — | à étudier |
| atptour.com | 14 | ATP (tennis) | — | pas d'API publique |
| nba.com | 14 | NBA | — | pas d'API publique officielle documentée ; en complément : odds_api |
| premierleague.com | 14 |  | — | à étudier |
| youtube.com | 14 |  | — | à étudier |
| ufc.com | 11 |  | — | à étudier |
| the-numbers.com | 10 |  | — | à étudier |
| conmebollibertadores.com | 9 |  | — | à étudier |
| predictionmarketodds.com | 9 |  | — | à étudier |
| wtatennis.com | 8 | WTA (tennis) | — | pas d'API publique |
| arena.ai | 8 | LMArena (classement des modèles d'IA) | — | chantier n°9 |
| weather.gov.hk | 8 |  | — | à étudier |
| mlb.com | 7 | Major League Baseball | mlb_stats | statsapi.mlb.com, API publique de la ligue |
