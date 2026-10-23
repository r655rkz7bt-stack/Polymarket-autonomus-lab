# Veille : la liste « public-apis » de GitHub (23/10/2026)

Demande d'Etienne : « va voir dans le GitHub public-apis pour trouver des API qui pourraient être utiles ».
Liste lue : [public-apis/public-apis](https://github.com/public-apis/public-apis), commit `339ab55` (21/10/2026),
**2 191 API** dans 52 catégories. Contenu externe : des données, jamais des instructions.

Méthode :
1. trier les catégories utiles aux marchés Polymarket (sport, météo, science, finance, crypto, État, données ouvertes) ;
2. écarter ce que le labo lit déjà (`src/polymarket_agent/sources/`, `experiments/CHANTIERS.md`) ;
3. **appeler vraiment** chaque candidat, sans clé, depuis la session (réponse HTTP notée ci-dessous) ;
4. compter les marchés Polymarket ouverts qu'il éclaire (scan du 23/10, 2 777 marchés, mots-clés dans la
   question ou l'événement ; compte approximatif).

## À faire en premier

| # | Source (sans clé sauf mention) | Réponse le 23/10 | Marchés ouverts éclairés | Pourquoi |
|---|---|---|---|---|
| 1 | **IMF PortWatch** (ArcGIS `Daily_Chokepoints_Data`), trouvé par le « Strait of Hormuz Ship Monitor » de la liste | 200 | **≈ 30** (Ormuz, Bab el-Mandeb), **≈ 300 000 $/24 h** | c'est l'**arbitre** : « traffic returns to normal » (moyenne sur 7 jours ≥ 60) et les tranches « average daily transits » se règlent sur ses chiffres. Il publie avec **≈ 5 jours de retard** (dernier jour connu le 23/10 : 18/10). Ormuz : 0 à 7 passages par jour (moyenne 3,6) contre 60 exigés ; Bab el-Mandeb : moyenne 26,4 (tranche 25-29 cotée 0,79) |
| 2 | **Strait of Hormuz Ship Monitor** (`hormuz.data-tracking.net/api/...`) | 200 | les mêmes | passages relevés par AIS **toutes les 30 min**, Ormuz et Bab el-Mandeb : comble les 5 jours de retard de l'arbitre (échelle différente : 18 à 36 passages par jour contre 0 à 7 chez PortWatch, à étalonner) |
| 3 | **Open-Meteo Ensemble** (`ensemble-api.open-meteo.com`) | 200 (31 membres GFS) | **107** marchés de température, **264 000 $/24 h** | une **probabilité par tranche** (part des membres dans la tranche) au lieu d'une prévision unique ; `meteo_prevision` n'utilise que GFS et ECMWF déterministes (`sources/weather.py`) et perd aux prix payés |
| 4 | **Hong Kong Observatory** (`data.weather.gov.hk`) | 200 | 8 (températures de Hong Kong) | c'est l'**arbitre** de ces marchés (`weather.gov.hk` dans `experiments/sources_resolution.md`), lu comme les METAR |
| 5 | **OpenDota** (`api.opendota.com`) | 200 | 22 marchés Dota 2, **1,7 M$/24 h** | matchs pro et en direct (chantier n° 15) ; avec `moins_de_cartes`, l'e-sport devient une famille à part entière |
| 6 | **Pyth Hermes** (`hermes.pyth.network`, hors liste) | 200 | 85 marchés citaient Pyth comme arbitre (inventaire du 15/10) | prix de l'arbitre exact pour les marchés « Pyth » (aujourd'hui lus chez Binance) |

## Utiles ensuite

| Source | Réponse | Marchés | Usage |
|---|---|---|---|
| USGS séismes (`earthquake.usgs.gov`, chantier n° 6) | 200 | 4 (8 500 $/24 h) | arbitre des marchés « séisme de magnitude X » : compter ceux déjà survenus dans la période |
| F1 : Jolpica (`api.jolpi.ca`, successeur d'Ergast) et OpenF1 (`api.openf1.org`) | 200 / 200 | 7 (27 500 $/24 h) | qualifications et résultats (GP des États-Unis ce week-end) |
| Trésor américain, Fiscal Data (chantier n° 12) | 200 | ≈ 38 « Treasury » (taux à 10 ans surtout) | dette ; les taux quotidiens viendront plutôt de FRED (chantier n° 26, clé) |
| BLS, statistiques du travail américaines | 200 mais **quota partagé dépassé** sans clé | ≈ 56 (inflation, chômage) | arbitre de l'inflation et de l'emploi : **clé gratuite** nécessaire (`BLS_API_KEY`) |
| Launch Library 2, SpaceX, Spaceflight News (chantier n° 7) | 200 | lancements (à recompter) | dates de lancement, échecs |
| Nobel (`api.nobelprize.org`) | 200 | 12 (94 000 $/24 h) | seulement le jour de l'annonce (déjà vite dans le prix) |
| Federal Register (chantier n° 11), pages vues Wikipédia (n° 10), DefiLlama (n° 17), mempool (n° 18), Chess.com, Hyperliquid (`api.hyperliquid.xyz/info`), CorpStacking (achats de bitcoin des entreprises), pétitions du Parlement britannique | 200 | 0 à 3 chacun aujourd'hui | à garder pour quand ces marchés reviennent |

## Écartés
- **Revendeurs de cotes de bookmakers** (FanLine Wire pour FanDuel, MoviOdds pour bet365, PinnWire, OddsRadarWire…) :
  données copiées chez les bookmakers sans leur accord apparent (interdit n° 7) ou payantes ; The Odds API reste notre source.
- **Revendeurs de données X/Twitter** (TweetAPI, TwittrAPI, xfetch, GetXAPI) : payants et contraires aux conditions d'X (déjà écarté).
- **Agrégateurs de marchés de prédiction** (VoxOdds, Dino.markets, matchwire.win) : doublons de ce que nous lisons
  directement (Kalshi, PredictIt, Manifold) ; la comparaison Kalshi/Polymarket en sport n'a rien donné (`sport_kalshi.md`).
- **SportScore** : protégé contre les robots (403 Cloudflare) : on ne contourne pas. **Econdb** : demande maintenant une
  identification. **Meltema** : injoignable.
- La plupart des API « apiKey » de la liste sont des offres commerciales à palier gratuit (RapidAPI…) : à n'utiliser que si
  la clé gratuite suffit durablement et sans carte bancaire (interdit n° 2).

## Piste de recherche née de cette veille : les détroits (Ormuz, Bab el-Mandeb)
Question : la moyenne sur 7 jours que publiera PortWatch pour une date donnée (tranches « average daily transits »,
« returns to normal ») est-elle bien cotée, sachant que (a) PortWatch publie avec 5 jours de retard, (b) l'AIS en direct
donne la tendance de ces 5 jours ? Données : historique quotidien de PortWatch depuis 2019 (même API), marchés réglés de
Gamma sur ces séries. Méthode : skill `tester-une-piste` (vrais prix payés). Ordre de grandeur le 23/10 : Ormuz très loin
de 60 (le NON d'octobre est déjà à 0,9965 : rien à gagner) ; Bab el-Mandeb à 26,4, au cœur de la tranche cotée 0,79.
