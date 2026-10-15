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
- **Données de marché** (`state/market.sqlite`) : snapshots, estimations, décisions, observations. Base tournante plafonnée à 40 Mo. En production : **cache GitHub Actions** (décision de l'étape 9, au lieu d'une branche `snapshots`), recréée si elle est perdue (le capital n'en dépend pas).
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

## 9. Apprentissage et promotion (`config/promotion.yaml`, libre depuis le 15/10/2026)

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

## 15. Arène, cliquet et innovation obligatoire (décision d'Etienne, 15/10/2026)

- **Cliquet** : objectif = 1,5 × capital initial, puis 1,5 × le palier précédent. Chaque palier
  franchi par le capital **réalisé** (solde + coût des positions, aucun gain latent) est inscrit
  dans le journal signé (`MILESTONE`), avec le temps mis. Impossible d'inscrire un palier non atteint.
- **Arène** (`arena.py`) : chaque stratégie active trade dans son portefeuille fantôme (1 000,
  vrais carnets). Classement par croissance logarithmique du capital réalisé.
- **Champion** : le meilleur avec ≥ 20 opérations clôturées, qui bat « ne rien faire » et le
  champion en titre. Le capital principal suit ses décisions (`PROMOTION` signée). Un nouveau
  champion n'est jugé qu'après 20 opérations ; déchu s'il passe sous « ne rien faire ».
- **Élimination** : une fois par semaine, la pire stratégie éligible (≥ 20 opérations, ≥ 7 jours,
  jamais le champion) est éliminée (`ELIMINATION` signée) et ne trade plus.
- **Innovation obligatoire** (`brief.py`, `scripts/research_brief.py`) : ≥ 3 idées en test,
  remplacer les éliminées, idée radicale après 7 jours sans palier. Lu par le chercheur en début
  de session (CLAUDE.md).
- Toutes les ressources gratuites sont disponibles dès le départ ; X reste désactivé (payant).

## 16. Étape 5 — sources d'information (15 octobre 2026)

| module | rôle |
|---|---|
| `sources/polymarket_comments.py` | commentaires des événements (format vérifié par appel réel) |
| `sources/crypto_prices.py` | prix et volatilité horaire (Coinbase, repli Kraken) |
| `sources/gdelt.py` | actualités mondiales (GDELT DOC 2.0) |
| `sources/rss.py` | 10 flux RSS/Atom (médias FR/EN, Fed, BCE, Maison-Blanche), analyse en bibliothèque standard |
| `sources/bluesky.py` | publications Bluesky (compte optionnel) |
| `sources/gemini.py` | classement optionnel (gratuit, plafond quotidien, texte encadré comme donnée) |
| `sources/x_api.py` | X : désactivé (payant) |
| `observations.py` | observation complète : dates, délai, fiabilité, incertitude, type, sentiment, doublons |
| `data_collector.py` | fréquence par source, mode dégradé, enregistrement, dédoublonnage |
| `social_intelligence.py` | rattachement aux marchés, volumes 1 h / 24 h, pic, sources indépendantes, signal |
| `intel_pipeline.py` | assemblage pour le cycle (étape 6 bis) |
| `crypto_model.py` + stratégie `crypto_threshold` | probabilité indépendante pour les marchés crypto à seuil |

Règles appliquées par construction : la viralité n'entre dans aucun signal ; un message isolé
n'est jamais un signal (≥ 2 domaines indépendants, copies exclues) ; l'absence d'information
n'est pas un signal ; une source en panne attend sa fréquence normale et ne bloque rien ;
analyse toujours marquée partielle (X absent). Une date de publication dans le futur est
signalée comme suspecte.

**Vérifié par appels réels le 15/10/2026** (après ouverture des domaines par Etienne) :
- Coinbase : bougies horaires conformes, 5 actifs OK (BTC, ETH, SOL, XRP, DOGE) ; Kraken conforme.
- RSS : 10 flux sur 10 OK (≈ 255 articles). Corrigé : BOM UTF-8 du flux de la Fed (test de
  non-régression) ; France Info a déménagé sur `www.franceinfo.fr` (domaine autorisé, vérifié : 30 articles).
- GDELT : refuse systématiquement (429, « une requête toutes les 5 s ») depuis l'adresse IP
  partagée du proxy. Source conservée « au mieux » : en cas de refus, elle attend 15 min.
- Bluesky : la recherche sans compte est refusée (403). Compte optionnel nécessaire
  (`BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`, dans l'environnement `production`).
- `crypto_threshold` : les 48 questions crypto du moment sont toutes correctement comprises ;
  le modèle colle aux prix du marché, mais sous-estime les queues : intervalle élargi (σ × 0,75 à × 1,5).
- Gemini s'active avec la clé `GEMINI_API_KEY` (environnement `production`, étape 8).

## 17. Étape 6 — laboratoire de stratégies (15 octobre 2026)

**Les 7 familles du cahier des charges sont dans l'arène** (9 stratégies, chacune dans son fantôme) :

| # cahier | stratégie | idée | état |
|---|---|---|---|
| 1 | `reversion` | surréaction après un mouvement ≥ 0,10 en 6 h | active |
| 2 | `news_momentum` | actualité confirmée + mouvement amorcé → continuation | active (attend des actualités confirmées) |
| 3 | `information_advantage` | annonce officielle fraîche non intégrée | inerte sans Gemini (direction inconnue) |
| 4 | `calibration`, `crypto_threshold` | probabilité indépendante vs prix | actives |
| 5 | `market_structure` | déséquilibre du carnet, sorties objectif/stop/durée | active |
| 6 | `social_sentiment` | emballement social non confirmé → pari contraire | inerte sans Gemini |
| 7 | `cross_market` | incohérences d'échelles de seuils → arbitrage sans risque | active |
| — | `naive_favorite` | référence naïve définie à l'avance | active (repère) |

**Nouveaux mécanismes :** ventes (sorties) passant par relecture du carnet, contrôleur et journal
signé ; marchés supplémentaires demandés par les stratégies ; moteur d'apprentissage
(`learning_engine.py`) avec verdicts par stratégie ; walk-forward (`backtest.walk_forward`, test
anti-fuite : l'ajustement ne voit que le passé à chaque pli) ; laboratoire (`scripts/lab.py`) qui
adapte les paramètres dans leurs bornes avec un score pénalisé pour les essais multiples
(`deflated_score`) ; règles de l'arène dans `config/promotion.yaml` (protégé à l'époque, libre depuis l'étape 9).

**Constats du laboratoire (walk-forward 4 plis, 111 528 marchés) :**
- `naive_favorite` perd sur toutes les variantes ;
- `calibration` : certaines variantes gagnent, aucune ne bat la configuration actuelle une fois la
  pénalité des essais multiples appliquée ;
- `reversion` : gains invraisemblables (≈ ×16 par pli), artefact déjà diagnostiqué (prix
  historiques non exécutables) : l'arène sur vrais carnets tranche ;
- avec Kelly complet sans plafond, une stratégie à l'avantage surestimé s'effondre vite
  (calibration : −46 % en validation, drawdown 72 %). Leçon pour le chercheur : réduire
  `kelly_fraction` quand l'avantage est incertain.

**Défauts corrigés (avec tests de non-régression) :** section arène perdue lors d'une édition
de settings.yaml (règles désormais obligatoires) ; prix crypto absent entre deux collectes.

## 18. Étape 7 — tableau de bord (15 octobre 2026)

**Ce que c'est :** une page HTML statique et autonome (`site/index.html` + `site/data.json`),
sans aucune bibliothèque externe, lisible en mode clair, sombre et sur téléphone. Générée par
`src/polymarket_agent/dashboard.py` à partir du gabarit `dashboard_template.html`.

**Contenu :** solde disponible, capital total estimé, gains réalisés et latents (jamais comptés
comme liquidités), palier suivant avec barre de progression, champion ; courbe du capital
principal (survol / flèches du clavier, table des valeurs) ; arène classée avec mini-courbe et
verdict du moteur d'apprentissage ; positions ouvertes de tous les portefeuilles avec prévision et
intervalle ; opérations clôturées ; décisions récentes et raisons de refus ; marchés surveillés ;
état du bot (dernier battement, cycles 24 h, erreurs) ; état de chaque source (dernier résultat
réel, pas « pas encore ») ; expériences et propositions ; tests ; coûts (0 €, appels IA / plafond).

**Fonctionnement :**
- `scripts/run_simulation.py` régénère la page après le cycle si elle a plus de 30 minutes
  (`config/settings.yaml` → `dashboard`). Un échec n'interrompt jamais le cycle ; un journal
  illisible n'est jamais affiché.
- `scripts/build_dashboard.py` force une génération (option `--fragment` pour un aperçu).
- Les journaux sont relus et vérifiés (signatures, chaîne) avant affichage.
- L'état des sources est maintenant conservé dans le résumé de chaque cycle (table `cycles`).

**Sécurité de l'affichage :** tout texte venu de l'extérieur (questions de marchés, raisons,
messages d'erreur) est inséré avec `textContent`, jamais comme du HTML ; le JSON embarqué
échappe `</` ; un test interdit `innerHTML`, `document.write`, `eval` et les scripts externes.

**Pas encore fait :** la publication sur GitHub Pages (étape 9 : le workflow du cycle poussera
`site/` ; Etienne activera Pages, une étape à la fois). `site/` est ignoré par Git sur `main`.

## 19. Étape 8 — validation et verrouillage (15 octobre 2026)

**Scénarios de panne vérifiés (tests) :** API Polymarket en panne (mode dégradé), source
d'information en panne, collecte entièrement en échec, carnet périmé ou modifié avant exécution,
journal absent / corrompu / tronqué / mauvaise clé / ligne partielle / horodatage antidaté,
journal fantôme corrompu, faillite (aucun redémarrage), panne imprévue en plein cycle puis
reprise propre, deux cycles simultanés (verrou), verrou laissé par un cycle tué (libéré après
15 min), échec du tableau de bord, et **base SQLite illisible**.

**Défaut trouvé et corrigé :** une base SQLite illisible faisait planter tous les cycles,
indéfiniment. Elle est maintenant mise de côté (`*.corrompue-<date>`, jamais effacée) et
remplacée ; le cycle le signale. Le capital n'en dépend pas ; seul l'ancrage anti-troncature est
perdu jusqu'au cycle suivant (test de non-régression).

**Verrouillage (code prêt, réglages GitHub à faire par Etienne : `docs/VERROUILLAGE.md`) :**
- `tests.yml` : tests sur chaque pull request, sans aucun secret ;
- `guard.yml` (`pull_request_target`) : exécute le code de `main`, lit seulement la liste des
  fichiers modifiés via l'API (anciens noms des renommages compris, liste incomplète refusée),
  comparaison insensible à la casse et aux `./` `..` ; logique dans `scripts/guard_check.py` ;
- `automerge.yml` : fusion automatique des PR `claude/` après `guard` et `tests` ; jamais pour
  une PR qui touche un fichier protégé ;
- `reset-capital.yml` : environnement `production`, code lu dans le fichier de l'événement et
  masqué (jamais interpolé, jamais affiché), comparaison à temps constant dans `ledger.py`,
  écriture RESET signée sur la branche `data` (convention reprise à l'étape 9 :
  `data` contient `ledger/` et `state/market.sqlite`) ;
- actions épinglées par commit ; nouveaux fichiers protégés : `scripts/guard_check.py`,
  `scripts/reset_capital.py`, `tests/test_guard.py`.

**Vérification réelle sur GitHub (15/10/2026) :**
- PR n°1 (étapes 3 à 8) : contrôle `tests` vert sur GitHub (233 tests), fusionnée par Etienne ;
- environnement `production` créé (déploiement limité à `main`), secrets `LEDGER_KEY` et
  `RESET_CODE` ajoutés par Etienne (fabriqués sur son iPad, jamais vus par Claude) ;
- PR n°2 de test (ligne ajoutée dans `config/risk_limits.yaml`) : `guard` en échec
  (« BLOQUÉ … config/risk_limits.yaml »), `automerge` a refusé la fusion automatique, puis,
  ruleset `protection-main` actif (aucun contournement), fusion **bloquée** (état `blocked`
  confirmé par l'API). Fermée sans fusion. **Critère de fin de l'étape 8 atteint.**
- fusion automatique autorisée ; cette mise à jour de la documentation sert de test du circuit
  complet (PR `claude/` → `guard` et `tests` verts → fusion sans intervention).
- non testé : une poussée directe sur `main` (Claude n'a pas le droit de pousser sur `main`) ;
  le ruleset l'interdit par construction (pull request obligatoire).

**Limites honnêtes :**
- le code non protégé qui tourne avec `LEDGER_KEY` (le cycle) pourrait en théorie écrire des
  écritures fausses ; la défense est la validation de `ledger.py` (protégé), les règles de
  CLAUDE.md et l'historique public des pull requests. Piste : un vérificateur protégé qui
  recontrôle les règlements auprès de Gamma ;
- `reset-capital.yml` ne pourra être essayé en réel qu'avec la branche `data` (étape 9) ;
- le code saisi au lancement d'un workflow reste dans l'événement GitHub : d'où la consigne de
  changer `RESET_CODE` après chaque utilisation.

## 20. Étape 9 — mise en service (15 octobre 2026)

**Fonctionnement en production :**
- `cycle.yml` : `workflow_dispatch` appelé toutes les 5 min par cron-job.org, plus un
  déclencheur horaire de secours (minute 7). Environnement `production`, branche `main`
  seulement, jamais sur une pull request, un seul cycle à la fois (groupe `cycle`, partagé
  avec `initialize` et `reset-capital`).
- Journal : branche `data` (`ledger/`), un commit par cycle, jamais réécrit (ruleset
  `protection-data`). Sauvegardé aussi après un cycle en erreur (code 1) ; jamais quand le
  journal est illisible (code 2), et le workflow échoue alors (e-mail de GitHub).
- Base d'analyse : cache GitHub Actions. Tableau de bord, rapports et feuille de mission :
  branche `gh-pages` (un seul commit remplacé), GitHub Pages, toutes les 30 min.
- `initialize.yml` : GENESIS de production avec `LEDGER_KEY`, une seule fois (refus si `data`
  existe). Le journal de développement local n'est jamais utilisé en production.
- Routine « chercheur » (une par jour) : n'a pas la clé du journal ; lit la feuille de mission
  publiée par le cycle (`scripts/fetch_published.sh`), travaille sur une branche `claude/`,
  PR fusionnée automatiquement si `guard` et `tests` passent (`docs/ROUTINE_CHERCHEUR.md`).
- Démarrage, arrêt, reprise, incidents : `docs/EXPLOITATION.md`.

**Vérifié avant mise en service :** simulation locale complète des workflows (dépôt factice) :
initialisation puis refus d'une 2ᵉ initialisation ; deux cycles réels sur Polymarket ; journaux
principal et fantômes relus et vérifiés depuis `data` ; tableau de bord publié au 1er cycle et
pas au 2ᵉ (moins de 30 min) ; récupération des rapports publiés par la routine.

**Liberté du chercheur (décision d'Etienne, 15/10/2026) :** routine 5 fois par jour ; le
chercheur peut modifier tout le fonctionnement et créer des workflows `labo-*.yml`, sauf le
**noyau** (`PROTECTED_PATHS.txt`) : règle n°1, règles du jeu (simulateur, frais), mots de passe
(workflows qui les reçoivent, réinitialisation isolée), gardien. `config/promotion.yaml` (règles
de l'arène) devient libre ; la méthode passe dans `docs/METHODE.md` (libre). `guard` vérifie le
texte des workflows libres (ni secret, ni environnement, ni écriture, ni déclenchement sur
PR/push, ni nom de contrôle exigé). Limite : le cycle exécute du code libre avec `LEDGER_KEY`.

**Critère de fin :** 24 h de cycles sans erreur sur GitHub (à constater après la mise en service).


## 21. Ordres à cours limité posés (point 6, 15 octobre 2026)

Décision d'Etienne : liberté maximale, y compris des ordres posés dans le carnet. Proposition :
`proposals/2026-10-15_ordres_limites.md`.

- Noyau : `execution_simulator.simulate_resting_buy/sell` (règle du passage au travers, au prix
  posé, carnet relu après la pose, toucher insuffisant) et `maker_fee` (0 seulement si le barème
  dit « taker seulement »).
- Cycle : étape 5 bis exécute les ordres posés aux cycles précédents avec les carnets du cycle
  (contrôleur + journal comme un ordre taker) ; les stratégies posent leurs nouveaux ordres
  (carnet relu au moment de la pose, réservation du solde, 30 ordres ouverts au plus, 6 h au
  plus, un ordre par jeton et par sens : le nouveau remplace l'ancien). Un ordre déjà exécutable
  part dans le circuit taker. Expiré / marché fermé / position vendue / stratégie éliminée → fin.
- Stratégies : `limit_orders` dans `StrategyOutput` ; `limit_ticks` dans `strategies.yaml` ;
  variantes `class:`. Première variante : `calibration_patiente`.
