# Architecture — Polymarket Autonomous Lab

Version 0.1, 14 octobre 2026. Résultat des étapes 1 (questions) et 2 (conception) avec Etienne.
Ces décisions sont validées : ne pas reposer les questions, construire à partir d'ici.

## 1. Décisions validées

| Sujet | Décision | Raison |
|---|---|---|
| Exécution | GitHub Actions, dépôt public, workflow `cycle.yml` déclenché par `workflow_dispatch` | Gratuit, sans carte bancaire, minutes illimitées en dépôt public |
| Déclencheur | cron-job.org (gratuit) appelle l'API GitHub toutes les 5 min | Le cron natif de GitHub est souvent retardé de 30 à 60 min |
| Plan B | Oracle Cloud Always Free (VM 24h/24) | Si GitHub juge l'usage abusif. Carte demandée pour vérification |
| Cerveau | 1 Routine Claude Code par jour (abonnement Pro) | Pro : 5 routines/jour max, intervalle minimal 1 h, quota partagé |
| IA dans le cycle | Aucune par défaut. Gemini gratuit en option, plafonné par jour | Économie de tokens |
| Données | API publiques Polymarket (Gamma, CLOB, Data) + sources gratuites | X désactivé : payant depuis février 2026 |
| Capital | 1 000 € virtuels | Choix d'Etienne |
| Mises | Liberté totale (décision du 15/10/2026). Taille par défaut : Kelly complet (×1), modifiable par chaque stratégie | Croissance maximale ; seule règle de risque : à 0 € tu meurs |
| Horizon | 30 minutes à 3 jours | Plus court n'a pas de sens avec un cycle de 5 min |
| Catégories | Toutes | Choix d'Etienne |
| Consultation | Page statique GitHub Pages + e-mails d'échec automatiques de GitHub | Zéro token |
| Objectif | Croissance logarithmique du capital, validée hors échantillon | Maximiser le gain espéré par pari mène à la faillite |
| Argent réel | Non implémenté | France interdite de passage d'ordres sur Polymarket |

## 2. Le cycle (≈ 1 min, toutes les 5 min)

1. Charger le journal comptable, vérifier signatures et chaîne. Si invalide : arrêt « CORROMPU ».
2. Vérifier le verrou de faillite. S'il existe : ne rien trader, mettre à jour le tableau de bord, sortir.
3. Scanner les marchés (Gamma, paginé) et mettre à jour la liste de surveillance.
4. Récupérer carnets d'ordres et prix pour la liste de surveillance (CLOB public).
5. Collecter les nouvelles observations des sources actives (mode dégradé si une source tombe).
6. Associer observations et marchés.
7. Estimer les probabilités (méthodes déterministes ; abstention si données insuffisantes).
8. Détecter les opportunités : avantage net des frais, du slippage et d'une marge d'incertitude.
9. Les stratégies produisent des propositions ; `safety_controller` les accepte ou les rejette.
10. Simuler l'exécution des propositions acceptées (re-lecture du carnet juste avant).
11. Écrire les écritures comptables signées, un battement de cœur signé, sauvegarder.
12. Vérifier les règlements de marchés résolus.
13. Toutes les 30 min : régénérer le tableau de bord.
14. Sortir proprement. Toute erreur réseau : nouvelles tentatives avec délais progressifs, puis abandon du cycle sans corrompre l'état.

Un seul cycle à la fois : `concurrency: group: cycle, cancel-in-progress: false`. Chaque opération a un identifiant unique (idempotence, pas de double comptabilisation).

## 3. Stockage

- **Journal comptable** (`ledger/ledger.jsonl`, branche `data`) : append-only, texte. Chaque ligne contient le hash de la précédente et une signature HMAC-SHA256 avec `LEDGER_KEY`. Solde, positions, gains réalisés et latents sont recalculés depuis le journal à chaque cycle. Un battement de cœur signé et horodaté est ajouté à chaque cycle : une troncature du journal est détectée par l'absence de battement récent. Toute anomalie déclenche l'arrêt « CORROMPU », jamais une réinitialisation.
- **Données de marché** (`state/market.sqlite`) : snapshots, estimations, décisions, observations. Base tournante plafonnée à 40 Mo. Proposition : branche orpheline `snapshots` écrasée à chaque sauvegarde, pour ne pas gonfler l'historique git. À valider pendant le prototype en mesurant la taille du dépôt ; alternative : artefacts GitHub Actions.
- **Historique pour les backtests** : `data/history/` (versionné, compressé), construit par `scripts/build_history.py` à partir de Gamma `/events/keyset` et du CLOB `prices-history`. Échantillon **non biaisé** : jours tirés au hasard, tous les marchés résolus, tirage uniforme de 40 % (voir §14).
- Toute observation stocke `published_at` et `collected_at`. Les backtests filtrent sur `collected_at <= instant de décision` (aucune fuite temporelle).

## 4. Modules (`src/polymarket_agent/`)

Structure du cahier des charges, avec ces ajouts :

- `ledger.py` (protégé) : journal signé, chaîne de hash, recalcul du capital, verrou de faillite.
- `safety_controller.py` (protégé) : contrôleur déterministe des propositions ; applique `risk_limits.yaml`.
- `fees.py` : frais par marché.
- `sources/` : un fichier par source (`polymarket_gamma.py`, `polymarket_clob.py`, `polymarket_comments.py`, `crypto_prices.py`, `gdelt.py`, `rss.py`, `bluesky.py`, `gemini.py`, `x_api.py`). Chaque source est activable séparément dans `config/settings.yaml`.

Séparation cerveau / garde-fous : les stratégies proposent (marché, sens, probabilité, prix max, taille, avantage net, sources, incertitude, conditions d'invalidation, durée, stratégie et version). Seul le contrôleur décide.

## 5. Sources de données

| Source | Coût | Clé | Défaut |
|---|---|---|---|
| Polymarket Gamma / Data / CLOB (lecture) | Gratuit | Non | Actif |
| Commentaires Polymarket (Gamma) | Gratuit | Non | Actif |
| Prix crypto publics (Coinbase, Kraken) | Gratuit | Non | Actif. Binance : souvent bloqué depuis les serveurs américains, à vérifier |
| GDELT (actualités mondiales) | Gratuit | Non | Actif |
| Flux RSS de médias et sources officielles | Gratuit | Non | Actif |
| Bluesky | Gratuit | Mot de passe d'application | Optionnel |
| Gemini (Google AI Studio) | Gratuit, quotas variables | Oui | Optionnel, plafond `llm.max_calls_per_day` |
| X | ≈ 0,005 $ par post lu | — | Désactivé |

Une source indisponible ne bloque jamais le cycle : l'analyse est marquée partielle et la confiance réduite. La viralité n'est jamais une preuve. L'absence d'information n'est pas un signal.

## 6. Simulation d'exécution et frais

- Par défaut, ordres « taker » : on parcourt le carnet relu juste avant l'exécution. Exécutions partielles si la profondeur manque. Un ordre non exécuté n'est jamais comptabilisé.
- Frais : taux par marché via `GET https://clob.polymarket.com/fee-rate?token_id=...`. Vérifier la formule en vigueur dans docs.polymarket.com/trading/fees avant de coder (structure 2026 : proportionnelle à `prix × (1 − prix)`, variable selon la catégorie ; géopolitique gratuite). Rien en dur. Les rebates « maker » ne sont pas comptés (prudence).
- Ordres limites « maker » : expérimentaux, exécutés seulement si des transactions ultérieures traversent la limite d'au moins un tick.
- Règlement à 1 ou 0 à la résolution ; marchés annulés ou invalides selon leurs règles.
- Tests de sensibilité : slippage ×1,5 et ×2.

## 7. Règles du jeu (`config/risk_limits.yaml`, protégé)

**Décision d'Etienne (15/10/2026) : liberté de trading totale.** Il n'y a plus aucune limite de
risque (taille, concentration, liquidités minimales, nombre de positions, pause après perte,
interdiction de renforcer une position perdante, avantage minimal, passage obligatoire en
fantôme). Les stratégies décident seules et le chercheur peut en créer et en lancer librement.

Restent, appliqués par du code déterministe :
1. **Règle n°1 : à 0 € tu meurs** (`ledger.py`, `safety_controller.py`).
2. **Règles du jeu**, qui rendent les gains simulés honnêtes : prix et carnets réels, frais
   officiels, carnet de moins de 120 s, données fiables, pas de dépense au-delà du solde
   disponible, pas de vente de parts non détenues, pas de doublon, journal signé.
3. **Interdits absolus de CLAUDE.md** (pas d'argent réel, pas de service payant, pas de secret exposé).

```yaml
initial_capital: 1000
max_book_age_seconds: 120
```

Taille par défaut : critère de Kelly **complet** (`kelly_fraction: 1` dans `strategies.yaml`),
qui maximise la croissance à long terme. Au-delà, la croissance diminue ; à partir de 2× Kelly
elle devient négative en moyenne. Chaque stratégie peut changer sa fraction.

## 8. Garde-fous et verrouillage

Principe : la protection repose sur les permissions GitHub et du code déterministe, jamais sur la confiance envers l'IA.
Attention : les Routines Claude Code poussent avec l'identité GitHub d'Etienne. Une règle qu'Etienne peut contourner ne bloque donc pas Claude : les rulesets ne doivent avoir **aucune liste de contournement**.

1. **Environnement GitHub `production`**, branche de déploiement autorisée : `main` uniquement. Il contient `LEDGER_KEY`, `RESET_CODE` et éventuellement `GEMINI_API_KEY`. Une branche de pull request ne peut pas lire ces secrets.
2. **Ruleset sur `main`** : pull request obligatoire, contrôles `guard` et `tests` obligatoires, pas de force push, pas de suppression, aucun contournement.
3. **Workflow `guard.yml`** sur `pull_request_target` : compare les fichiers modifiés par la PR à `PROTECTED_PATHS.txt` lu depuis `main`. Ne récupère et n'exécute jamais le code de la PR. Échoue si un fichier protégé est touché.
4. **Branche `data`** : techniquement modifiable, mais toute altération est détectée (signatures, chaîne, battement de cœur) et provoque l'arrêt « CORROMPU ». Aucune altération ne peut créer du capital.
5. **Réinitialisation** : workflow `reset-capital.yml` (`workflow_dispatch`, entrée `code`), job dans l'environnement `production`, comparaison à temps constant avec `RESET_CODE`, puis écriture signée d'une entrée RESET avec la raison.
6. **Fusion automatique** : une PR de branche `claude/` est fusionnée automatiquement si `guard`, `tests` et la non-régression de simulation passent. Une PR qui touche un fichier protégé reste ouverte pour Etienne.

Le verrouillage est activé à l'étape 8, avec Etienne qui fait les réglages GitHub guidé pas à pas.

## 9. Apprentissage et promotion (`config/promotion.yaml`, protégé)

- **Niveau 1, paramètres** : ajustement automatique dans les bornes, chaque changement documenté et évalué.
- **Niveau 2, stratégies** : walk-forward (entraînement, validation, période de test réservée et jamais utilisée pour choisir). Comparaison systématique à « ne rien faire » et à une stratégie naïve définie à l'avance.
- **Niveau 3, code** : uniquement par pull request (§8).
- **Promotion** : un challenger tourne en paper trading « fantôme » en parallèle du titulaire, sur un sous-journal séparé qui ne touche pas le capital principal. Valeurs par défaut, modifiables par Etienne : au moins 30 positions clôturées et 7 jours ; probabilité bootstrap ≥ 90 % que sa croissance logarithmique dépasse celle du titulaire ; drawdown pas plus de 1,5 fois pire ; Brier score égal ou meilleur.
- **Tests multiples** : compter les variantes essayées et pénaliser en conséquence (une stratégie n'est pas adoptée parce qu'elle est la meilleure de 200 essais).
- **Mesures** : profit net, rendement, espérance par opération, taux de réussite, drawdown, Sharpe si pertinent, Brier, log loss, calibration, par catégorie et par durée.

## 10. Plan de construction (sessions Claude Code)

| Étape | Contenu | Critère de fin |
|---|---|---|
| 3. Prototype | Scanner Gamma, carnets CLOB, SQLite, journal signé, une stratégie naïve, simulateur taker, tests capital et journal | Un cycle complet sur données réelles, tests verts |
| 4. Simulation complète | Portefeuille, frais réels, règlements, rapports | Tous les tests comptables du cahier des charges passent |
| 5. Sources | Commentaires, prix crypto, GDELT, RSS ; Gemini optionnel | Mode dégradé testé |
| 6. Laboratoire | Backtests sur l'historique de prix, walk-forward, promotion fantôme, 7 stratégies initiales | Test anti-fuite temporelle vert |
| 7. Tableau de bord | Page statique GitHub Pages | Page accessible en ligne |
| 8. Validation et verrouillage | Scénarios de panne, environnement `production`, rulesets, `guard` | Une PR touchant un fichier protégé est bloquée (test réel) |
| 9. Mise en service | `cycle.yml`, cron-job.org, Routine « chercheur », procédure d'arrêt et de reprise | 24 h de cycles sans erreur |

Les sessions Claude Code sur le web ont besoin d'accès réseau aux domaines Polymarket (environnement réglé en « Custom »).

## 11. Ce qu'Etienne configurera, guidé au moment voulu

- Environnement `production` et ses secrets (étape 8).
- Rulesets sur `main` (étape 8).
- GitHub Pages (étape 7).
- Compte cron-job.org et jeton GitHub à portée minimale, stocké uniquement dans cron-job.org (étape 9).
- Routine « chercheur » sur claude.ai/code/routines (étape 9).
- Optionnel : clé Google AI Studio, compte Bluesky.

## 12. Limites connues

- Conditions de GitHub : l'usage « paper trading = test du projet » est défendable mais pas garanti. Plan B : Oracle Cloud.
- Granularité de 5 minutes ; dépendance à cron-job.org (s'il tombe, pas de cycles, mais aucune perte).
- Dépôt public : stratégies et trades simulés visibles.
- Routines en « research preview » : limites susceptibles de changer ; quota Pro partagé avec l'usage normal d'Etienne.
- Frais et endpoints Polymarket évoluent : toujours vérifier la doc.
- Un backtest positif ne prouve pas qu'une stratégie est rentable.

## 13. Constats du prototype (étape 3, 14 octobre 2026)

Mesurés par appels réels depuis l'environnement Claude Code :

- **Gamma** `GET /markets` : 100 résultats maximum par page (`limit` + `offset`), filtres `end_date_min` / `end_date_max` fonctionnels. `outcomes`, `outcomePrices`, `clobTokenIds` sont des chaînes JSON. Environ 9 % des marchés n'ont pas de `bestBid` : ils sont exclus.
- **CLOB** `GET /book`, `POST /books` : les bids arrivent en ordre croissant et les asks en ordre décroissant ; on retrie, meilleur prix en premier.
- **Frais** : chaque marché Gamma porte `feesEnabled` et `feeSchedule = {rate, exponent, takerOnly, rebateRate}` (observé : sports 0,03–0,05, politique 0,04, crypto 0,07, exposant 1). Formule confirmée sur docs.polymarket.com/trading/fees : `frais = parts × taux × p × (1 − p)`, arrondis à 5 décimales. `GET /fee-rate` renvoie seulement `base_fee` (1000) : inutile pour le calcul.
- **Taille** : journal ≈ 0,3 Ko par battement de cœur (≈ 90 Ko/jour). Base SQLite ≈ 10 Mo/jour une fois le scan complet archivé toutes les 30 min seulement ; le plafond de 40 Mo garde donc environ 4 jours de snapshots (rotation automatique). L'historique long viendra de `prices-history` du CLOB.
- **Ancrage anti-troncature** : la base garde le dernier numéro et le hash du journal ; si le journal ne contient plus cette écriture, arrêt « CORROMPU ».
- **Création du capital** : seul `scripts/initialize.py` écrit le GENESIS, et il refuse s'il existe déjà un journal, un verrou ou un ancrage. Le cycle ne crée jamais de capital.

## 14. Étape 4 et premier travail de recherche (14 octobre 2026)

**Ajouté :** règlement des marchés résolus (1/0 et 50-50, seulement si `closed` et statut UMA
« resolved »), groupes de corrélation (actif crypto commun, sinon événement) plafonnés comme
un événement (15 %), capital total estimé dans chaque battement (courbe, drawdown), rapports
(`scripts/generate_report.py`), lecture des carnets des deux issues, exclusion des marchés à
l'issue quasi certaine (≥ 0,99), backtest passant par le vrai journal et le vrai contrôleur.

**Leçon majeure — biais de sélection.** Un premier historique filtré sur le *volume final*
(≥ 50 000) faisait apparaître des favoris surévalués de 5 points et une stratégie à +112 %
en validation. Un échantillon témoin sans filtre a montré que c'était un artefact : une
surprise génère du volume, donc ce filtre sur-représente les surprises. Règle permanente :
**aucune sélection de données sur une information connue après l'issue** (volume final,
clôture réelle…). Test de non-régression : `test_regression_final_volume_is_not_used_as_a_filter`.
Détails : `experiments/PROTOCOLE_v2.md`.

**Autres constats :**
- Du 05 au 25/03/2026, l'API Gamma renvoie un volume nul pour la plupart des marchés.
- Une journée compte de 1 000 à 8 000 marchés binaires résolus (beaucoup de paris sportifs
  annexes et de marchés crypto courts).
- Débit utilisé pour l'historique : environ 48 requêtes/s (limite documentée : 1 000 / 10 s).
- La copie de l'état du journal avant chaque écriture (`deepcopy`) rendait les backtests
  quadratiques : remplacée par `LedgerState.clone()`, testée équivalente.

**Décision au 14/10/2026** (`experiments/BILAN_2026-10-14.md`) : aucune stratégie n'est
prouvée rentable. Capital principal : « ne rien faire ». `reversion v1` tourne en
**portefeuille fantôme** : journal séparé `ledger/fantome/`, même marché, mêmes carnets réels,
mêmes garde-fous, sans jamais toucher le capital principal. Promotion selon
`config/promotion.yaml` ; le critère de drawdown relatif est inapplicable face à « ne rien
faire » (drawdown nul) : à trancher par Etienne avant l'étape 6.
