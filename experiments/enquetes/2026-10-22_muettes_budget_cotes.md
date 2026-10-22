# Enquête du 22/10/2026 (2e, famille 6 : ce qui ne tourne plus) : stratégies muettes et budget des cotes

Méthode : pour chaque stratégie active, achats dans le journal signé du fantôme ; raisons d'abstention du dernier cycle de la
sauvegarde de production (table `kv`, clé `abstentions`, cycle 20261022T0000Z) ; compteur de crédits de The Odds API (`odds_api:credits:<jour>`).

## 1. La mère `naive_favorite` n'est pas sourde (question ouverte du 21/10 : « pourquoi n'achète-t-elle plus ? »)
Dernier achat le 18/10 à 03 h 28 UTC, 257 € disponibles. Cycle de 00 h UTC : 429 marchés vus, **279 « favori hors de la plage 0,80-0,95 »**,
**28 « avantage net insuffisant »**, 11 « position déjà ouverte ». Elle exige `min_net_edge 0,02` (borne basse = milieu + 0,035) : il faut donc
ask + frais ≤ milieu + 0,015, c'est-à-dire un carnet serré et peu de frais ; ses filles (`min_net_edge 0,01`, ordres posés) passent. **Cause : filtre trop serré
combiné à un biais fictif** (voir la fiche du matin), pas un défaut de code. Rien à corriger ; question close.

## 2. 12 stratégies actives sans aucun achat depuis 1,7 jour
`marches_jumeaux`, `implication_politique`, `paire_oui_non`, `coherence_match` : « paire cohérente : aucun écart après frais » (429, 33, 8, 2 marchés) :
les prix sont cohérents, elles se taisent à raison. `kalshi_reference`, `predictit_reference`, `manifold_reference`, `futurs_bookmakers`, `crypto_threshold_24_72h` :
« avantage net insuffisant » (20, 50, 4, 28, 16) : elles voient des références mais l'écart ne couvre pas frais et écart achat-vente. **`football_trois_issues`,
`cotes_tennis`, `mots_prononces_nfl` : aucune raison d'abstention (aucun marché candidat vu).** `mots_prononces_nfl` : pas de match de NFL à minuit UTC, normal.
Les deux autres dépendent des cotes de The Odds API.

## 3. Défaut : le budget quotidien de cotes est dépensé d'un coup (`sources/odds_api.py`)
Compteurs de production : `odds_api:credits:2026-10-20` = 12 (dernier appel 19 h 59 UTC), `…:2026-10-21` = 12 (dernier appel **12 h 57 UTC** : trois listes de champions, après la Ligue des champions à 11 h 22
et un tournoi de tennis à 12 h 23). Le budget de 12 (500 par mois gratuits) est donc épuisé en une demi-journée UTC : plus de cotes pour les matchs du soir
européen et américain (NBA, NHL, MLB, tennis de nuit), alors que `cotes_tennis` et `football_trois_issues` comparent justement « juste avant le match ».
Chiffre non prouvé : le nombre exact de matchs sans cote (les observations ne sont pas dans la sauvegarde publiée).

**Correctif** : `OddsApiSource.allowed_today(now)` : le budget se dépense au fil de la journée (`ceil(budget × (heure UTC + 4) / 24)` : 2 à 0 h, 8 à 12 h, 12 à 20 h).
Test `tests/test_odds_budget.py`. Le plafond de 12 par jour reste (les 500 crédits gratuits ne bougent pas).

## À surveiller
- La garde `muettes` ne signale ces stratégies qu'après 48 h : elles seront listées demain si elles sont toujours muettes.
- `football_trois_issues` et `cotes_tennis` : revoir dans 2 jours si elles achètent maintenant que les cotes du soir existent.
