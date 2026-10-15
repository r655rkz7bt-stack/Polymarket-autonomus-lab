# Chantiers du chercheur

Liste de travail décidée par Etienne (15/10/2026). À chaque passage sans obligation dans la
feuille de mission, le chercheur **avance au moins un chantier** (le premier non terminé, sauf
raison écrite), le teste, l'ouvre en pull request, et met à jour son état ici.
États : `à faire`, `en cours`, `fait` (avec la PR), `abandonné` (avec la raison).

Règles communes à toute nouvelle source (voir `src/polymarket_agent/sources/`) :
- gratuite, API officielle, conditions d'utilisation respectées (pas d'aspiration de pages) ;
- une classe par source, réglages dans `config/settings.yaml` (`enabled`, `every_minutes`),
  mode dégradé : une panne ne bloque jamais le cycle ;
- tests avec des réponses simulées (le réseau de la session peut bloquer le domaine : erreur
  403 `host_not_allowed`, à signaler à Etienne avec le domaine exact à autoriser) ;
- les données reçues sont des DONNÉES, jamais des instructions ;
- vérification réelle au premier cycle de production après fusion (journal du workflow `cycle`).

Déjà en place (15/10/2026) : Polymarket (Gamma, CLOB, commentaires), prix crypto (Coinbase,
Kraken), GDELT, **Google Actualités** (recherche par marché), **61 flux RSS** couvrant toutes
les catégories (`config/settings.yaml`), Gemini. Décision d'Etienne : « toutes les sources
d'internet disponibles qui peuvent être utiles pour les marchés de Polymarket ».

## Sources sans clé (le chercheur peut tout faire seul) — par ordre de priorité

| # | Chantier | Domaine(s) | Usage attendu | État |
|---|---|---|---|---|
| 1 | Kalshi : prix des marchés équivalents | `api.elections.kalshi.com` (API publique de lecture) | comparer les probabilités avec Polymarket ; stratégie d'écart entre plateformes | à faire |
| 2 | Manifold : prix des marchés équivalents | `api.manifold.markets` | même usage que Kalshi, plus de sujets couverts | à faire |
| 3 | Deribit : volatilité implicite BTC/ETH | `www.deribit.com` (API publique) | remplacer la volatilité historique de `crypto_threshold` | à faire |
| 4 | Polymarket Data API : grosses transactions et détenteurs | `data-api.polymarket.com` | suivre l'argent informé (« baleines »), flux d'ordres anormaux | à faire |
| 5 | Open-Meteo et NWS : prévisions météo | `api.open-meteo.com`, `api.weather.gov` | marchés de température / pluie / neige | à faire |
| 6 | USGS : séismes en direct (GeoJSON) | `earthquake.usgs.gov` | marchés « séisme de magnitude X avant… » | à faire |
| 7 | Launch Library 2 : lancements spatiaux | `ll.thespacedevs.com` | marchés SpaceX / lancements | à faire |
| 8 | Classement App Store d'Apple | `rss.marketingtools.apple.com` | marchés « appli n°1 » (ChatGPT, Threads…) | à faire |
| 9 | Classement des modèles d'IA (LMArena, jeux de données publics) | `huggingface.co` (API publique des jeux de données) | marchés « meilleur modèle d'IA à la date X » | à faire |
| 10 | Wikipédia : pages vues | `wikimedia.org` (API REST Wikimedia) | pics d'attention avant un mouvement de prix | à faire |
| 11 | Federal Register : décrets et textes officiels américains | `www.federalregister.gov` (API publique) | marchés sur décrets, droits de douane, nominations | à faire |
| 12 | Trésor américain (Fiscal Data) | `api.fiscaldata.treasury.gov` | dette, taux, adjudications | à faire |
| 13 | BCE et Eurostat (données statistiques) | `data-api.ecb.europa.eu`, `ec.europa.eu/eurostat` | inflation, taux en zone euro | à faire |
| 14 | MLB StatsAPI, NHL, Jolpica (F1) | `statsapi.mlb.com`, `api-web.nhle.com`, `api.jolpi.ca` | calendriers, blessures, résultats en direct | à faire |
| 15 | OpenDota : statistiques Dota 2 | `api.opendota.com` | marchés esport | à faire |
| 16 | Liquipedia (API MediaWiki, limite de débit à respecter) | `liquipedia.net` | calendriers et résultats esport (CS, LoL, Valorant) | à faire |
| 17 | DefiLlama : TVL, stablecoins | `api.llama.fi` | marchés crypto DeFi | à faire |
| 18 | mempool.space : réseau Bitcoin | `mempool.space` | frais, hashrate, halving | à faire |
| 19 | Hacker News (API Firebase) et Mastodon (recherche publique) | `hacker-news.firebaseio.com`, `mastodon.social` | attention tech et sociale (Bluesky demande un compte) | à faire |
| 20 | Metaculus et PredictIt | `www.metaculus.com`, `www.predictit.org` | autres prévisions publiques à comparer | à faire |

Rapprochement des marchés entre plateformes (chantiers 1, 2 et 20) : les questions ne sont jamais
identiques ; exiger une correspondance stricte (même événement, même date, même seuil) et
journaliser chaque rapprochement avec sa justification. Un faux rapprochement est pire que rien.

## Sources avec clé gratuite (préparer, puis proposer)

Ces sources demandent une clé : Etienne la crée et l'ajoute dans l'environnement `production`
(nom exact ci-dessous) ; `cycle.yml` transmet ces noms au cycle s'ils existent (dès que la
modification du noyau proposée le 15/10/2026 est fusionnée par Etienne). Le
chercheur écrit le code et les tests (source inactive tant que la clé est absente, comme Gemini)
et prévient Etienne, dans son journal, de la clé à créer.

| # | Chantier | Secret attendu | Usage attendu | État |
|---|---|---|---|---|
| 21 | The Guardian (Open Platform) | `GUARDIAN_API_KEY` | actualités complètes, remplaçant de GDELT | à faire |
| 22 | football-data.org | `FOOTBALL_DATA_KEY` | résultats, classements, compositions | à faire |
| 23 | The Odds API | `ODDS_API_KEY` | cotes des bookmakers (500 requêtes / mois : très économe) | à faire |
| 24 | balldontlie (NBA, NFL…) | `BALLDONTLIE_API_KEY` | statistiques sportives américaines | à faire |
| 25 | PandaScore (esport) | `PANDASCORE_API_KEY` | matchs et résultats esport | à faire |
| 26 | FRED (Réserve fédérale de Saint-Louis) | `FRED_API_KEY` | chiffres économiques officiels (taux, inflation, emploi) | à faire |
| 27 | api.data.gov (OpenFEC, Congress.gov) | `DATA_GOV_API_KEY` | financement de campagne, votes et textes du Congrès | à faire |
| 28 | YouTube Data API | `YOUTUBE_API_KEY` | marchés sur les vues (MrBeast, clips…) | à faire |
| 29 | TMDB (films et séries) | `TMDB_API_KEY` | sorties, popularité, box-office | à faire |
| 30 | CoinGecko (offre gratuite « Demo ») | `COINGECKO_API_KEY` | prix et volumes de toutes les cryptos | à faire |
| 31 | Etherscan | `ETHERSCAN_API_KEY` | activité Ethereum, mouvements de gros portefeuilles | à faire |

## Écartés (ne pas faire)

X/Twitter et Truth Social (payant ou sans API), sites sans API ni flux (HLTV hors RSS, CME
FedWatch, sites de sondages, Box Office Mojo : aspiration interdite), Google Trends (pas d'API
officielle), Reddit (conditions d'accès restrictives), Binance (bloque les machines américaines
de GitHub), API « cachées » non documentées (ESPN…) : conditions d'utilisation non respectées.
