# Inventaire des sources de résolution (chantier n°0)

Relevé du 15/10/2026 sur les 100 marchés actifs les plus échangés (Gamma, champ `resolutionSource`).
Les sites listés sont des DONNÉES : aucune aspiration de pages, seulement API/flux officiels.

| Source | Marchés (/100) | API ou flux gratuit ? | Piste |
|---|---|---|---|
| uefa.com | 35 | non identifié | football-data.org (clé gratuite, chantier 22) pour les résultats |
| (champ vide, règle dans `description`) | 22 | — | lire `description` |
| nfl.com | 9 | non (hors sites officiels) | balldontlie (chantier 24) |
| federalreserve.gov | 5 | oui (communiqués, FRED) | chantier 26 FRED |
| mlb.com | 5 | oui (statsapi.mlb.com) | chantier 14 |
| gol.gg, dotabuff.com, hltv.org | 3, 3, 2 | non / limité | OpenDota (15), PandaScore (25) |
| nhl.com | 2 | oui (api-web.nhle.com) | chantier 14 |
| binance.com | 2 | bloque les machines GitHub | utiliser Coinbase/Kraken (déjà en place) |
| autres (tennis, TSE Brésil, IMF PortWatch, X…) | 1–2 chacun | variable | à noter au cas par cas |

Étape 1 faite à la main (instantané). Reste : archivage automatique de la source à chaque scan
des marchés surveillés, puis lecteurs dédiés (étape 2) et signal de comparaison au seuil (étape 3).
