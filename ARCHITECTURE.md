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
- **Champion** (seuils dans `config/promotion.yaml`, libres) : seuil d'ENTRÉE = ≥ 20 opérations
  clôturées, ≥ 24 h d'ancienneté et ≥ +2 % de croissance ; il doit battre le champion en titre de
  +1 %. Seuil de MAINTIEN plus bas (au-dessus de « ne rien faire ») : pas de va-et-vient sur du
  bruit (durci le 15/10/2026 après une promotion à +0,02 % destituée 10 minutes plus tard). Le
  capital principal se répartit entre les stratégies qui passent l'entrée (et le champion tant
  qu'il tient le maintien). `PROMOTION` signée. Une stratégie retirée garde la main sur les
  ventes de ses positions du principal, sans racheter.
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

**Critère de fin :** 24 h de cycles sans erreur sur GitHub — **atteint le 16/10/2026 à 12:17 UTC.**

**Bilan des 24 premières heures (15/10 12:17 → 16/10 12:17 UTC, constaté sur la branche `data`) :**
- 287 cycles, tous terminés avec le code 0 (aucune erreur, aucun journal illisible) ; écart médian
  entre deux cycles 5,0 min ; un seul trou de 38 min, au tout début (réglage de cron-job.org) ;
  tableau de bord publié sur `gh-pages` toutes les 10 min.
- Audit indépendant (job `audit`, depuis le 15/10 ~19:50) : 1 039 exécutions vérifiées contre
  l'historique public des prix, 22 règlements conformes à la résolution officielle, 0 anomalie.
- Routine « chercheur » : 5 passages notés dans `experiments/journal_recherche.md`, 5 pull
  requests fusionnées (#6, #10, #26, #32, #35) ; aucune ne touchait le noyau.
- Capital principal : 994,06 (−0,59 %), aucune championne : aucune stratégie n'a encore assez
  d'opérations clôturées et une croissance suffisante (règles : `config/promotion.yaml`).
- Limites constatées : le workflow `labo-alerte-coeur` (programmé toutes les heures) n'a tourné
  que 3 fois, GitHub retardant ou sautant les déclenchements programmés ; le cycle exécute
  toujours du code libre avec `LEDGER_KEY` (le « notaire » n'est pas fait, option A choisie :
  `proposals/2026-10-15_notaire_et_audit_des_reglements.md`) ; `reset-capital` n'a pas été
  essayé en production (aucune faillite).


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

## 22. Surveillance et justesse de Gemini (15 octobre 2026)

- Alerte : `labo-alerte.yml` (libre, lecture seule) lit la branche `data` toutes les heures et
  échoue si le cœur s'arrête, si cron-job.org semble arrêté ou en faillite (e-mail de GitHub).
- Justesse de Gemini : `stance_eval.py` interroge chaque heure jusqu'à 10 marchés classés par
  Gemini, enregistre leur résultat quand ils sont réglés (table `stance_outcomes`) et compare les
  avis « oui » / « non » au résultat réel (justesse brute et pondérée par la confiance). Statut
  `justesse_gemini` dans le cycle et le tableau de bord. Le chercheur s'en sert pour décider du
  poids à donner à Gemini dans les stratégies.

## 23. Audit indépendant, sauvegarde, réalisme, clés (15 octobre 2026)

Proposition : `proposals/2026-10-15_audit_sauvegarde_realisme_cles.md`.
- Job `audit` du workflow `cycle` (machine neuve, `scripts/audit_fills.py` protégé, `python -I -S`) :
  chaque achat / vente comparé à l'historique public des prix ; anomalies dans `audit/etat.json`
  (branche data), sur le tableau de bord et par e-mail.
- Sauvegarde quotidienne de l'essentiel de la base dans `backup/` (branche data), restaurée si le
  cache disparaît.
- Simulateur : 25 % du meilleur niveau, 50 % des suivants ; liquidité partagée entre les ordres d'un
  même portefeuille pendant un cycle (pas entre fantômes, scénarios indépendants).
- `cycle.yml` transmet 11 clés optionnelles de sources gratuites.

## 24. Santé des stratégies (15 octobre 2026)

`strategy_health.py` (libre) : prévisions des fantômes jugées sur les marchés réglés (table
`forecast_outcomes`, 15 marchés par heure), score de Brier contre le prix payé, dérive des prix
depuis l'achat ; mise prudente (½ Kelly tant que moins de 20 prévisions jugées, ×1 si meilleure
que le marché, ×¼ sinon) appliquée aux fantômes et au principal ; suspension d'une stratégie
gagnante avant frais mais perdante après (≥ 20 opérations clôturées). Réglages : section
`sante_strategies` de `config/settings.yaml`.

## 25. Sources de résolution, scores officiels, sources à clé (15 octobre 2026)

- `resolution_sources.py` : `resolutionSource` et `description` de Gamma (nouveaux champs de
  `MarketInfo`) archivés une fois par heure pour les marchés surveillés (table `market_rules`) ;
  `CATALOG` relie chaque domaine à son lecteur ; résumé `sources_resolution` dans la console.
- Lecteurs : `crypto_prices` lit Binance d'abord (`data-api.binance.vision`, arbitre des marchés
  crypto), puis Coinbase, Kraken ; `meteo_metar` (aviationweather.gov, relevés METAR des stations
  citées par les marchés de température, maximum prudent du jour local estimé) ; `mlb_stats`,
  `nhl_stats` (API des ligues) ; avec clé : `football_data`, `odds_api` (probabilités implicites
  des bookmakers), `guardian`. Sans clé : « désactivée (pas de clé …) », aucun appel.
- `HttpClient.get_json(..., headers=)` : en-têtes propres à une requête. Le jeton Bluesky n'est
  plus mis dans la session partagée (il partait vers toutes les autres sources).
- Rattachement des articles (`social_intelligence.match`) : au moins un mot du marché dans le
  titre, mots rares pondérés (idf), au plus 5 marchés par article.

## 26. « Aujourd'hui » et historique de l'arène (15 octobre 2026)

- `today.py` : les dernières 24 h en phrases simples, écrites par du code (capital, championne,
  opérations, meilleure et pire opération, arène, cycles, audit, sources) ; section
  « Aujourd'hui » du tableau de bord, juste sous le résumé.
- `arena_history.py` : une photo du classement par heure (table `arena_history`, réglage
  `dashboard.arena_history_minutes`), graphique « classement dans le temps » sous l'arène
  (survol : nom, rang, capital ; vue tableau) et « plus forte remontée / chute depuis hier ».

## 27. Audit des règlements (15 octobre 2026, option A du lot D)

`scripts/audit_fills.py` (protégé) vérifie aussi chaque règlement (`SETTLE`) contre l'API publique
Gamma : marché clos, jeton présent, paiement égal au prix final officiel de l'issue (1, 0 ou 0,5).
Résolution pas encore définitive : réessayée, anomalie après 3 jours. Curseur à part
(`dernier_seq_reglements`) : les règlements antérieurs sont vérifiés aussi. Compteur
`reglements_verifies` dans `audit/etat.json`, affiché dans la console et dans « Aujourd'hui ».
Le notaire (signature réservée à une machine protégée) n'est pas fait :
`proposals/2026-10-15_notaire_et_audit_des_reglements.md`.

## 28. Stratégie météo (16 octobre 2026)

- `weather_model.py` : lecture des questions de température (tranche, °C / °F, jour), probabilité
  d'une tranche à partir des prévisions floutées (σ, biais) et du relevé du jour.
- Sources : `meteo_metar` garde les coordonnées des stations (kv `station:XXXX`) ;
  `meteo_prevision` (Open-Meteo, toutes les heures) donne le maximum et le minimum du jour local
  prévus par GFS et ECMWF ; `intel_pipeline.latest_weather` les attache à `MarketInfo.weather`.
- Stratégie `meteo_prevision` (strategies_v2.py) : demande jusqu'à 100 marchés de température
  (`candidates`, `scanner.max_extra_markets` passé à 140), parie NON seulement, réglages issus du
  test sur le passé (`experiments/meteo_backtest.md`, scripts dans `experiments/meteo_backtest/`).

## 29. Outil de test sur le passé et météo étalonnée par station (16 octobre 2026)

- `idea_test.py` : outil générique pour juger une idée AVANT l'arène. `fetch_resolved` (marchés
  résolus d'une famille Gamma, cache gzip), `PriceCache.price_at` (prix du « Oui » à un instant,
  jamais un point postérieur, cache SQLite), `evaluate` (Brier, log loss, simulation 1 part par
  pari avec frais réels et écart simulé, jugée sur la seconde moitié des dates).
- `weather_calibration.py` : biais et flou propres à chaque station. Tables `meteo_previsions`
  (dernière prévision faite avant le début du jour local ; rattrapage unique par station depuis
  l'archive Open-Meteo `previous-runs`) et `meteo_reel` (valeur réelle = tranche gagnante des
  marchés météo résolus, source `meteo_reel` toutes les 3 h). La prévision collectée porte
  `data["erreurs"]` (7 dernières erreurs de la station) ; `meteo_prevision` en tire biais et flou,
  tirés vers le réglage global (`calibration_shrink` jours fictifs), plancher `sigma_floor`.
  Test sur le passé : Brier 0,090 au lieu de 0,097. **Aux prix réellement payés, aucun avantage**
  (−6 % des mises, 0 jour gagnant sur 8 ; `experiments/meteo_backtest.md`, « Vérification ») : le
  +28 % de l'historique « 10 minutes » venait de marchés sans échange.
- Arène (`arena.py`, `config/promotion.yaml` → `validated_strategies`) : une stratégie validée sur
  le passé AUX PRIX RÉELLEMENT PAYÉS entre au capital principal avec des seuils plus bas ; elle doit
  toujours battre « ne rien faire » en direct. Liste vide le 16/10/2026 (météo retirée).
- `idea_test.fetch_event_trades` / `taker_cost` : prix réellement payés par les preneurs
  (data-api, public). Leçon du 16/10/2026 (météo, crypto) : l'historique « 10 minutes » du CLOB
  invente des gains sur les marchés sans échange (carnets vides, prix périmés).

## 30. Tenue de marché (16 octobre 2026)

Décision d'Etienne après la veille (`experiments/veille_bots/Bots Polymarket et leurs gains.md`) :
orienter le labo vers la tenue de marché, sans arrêter ce qui tourne déjà.
- Stratégie `market_maker` (`strategies_v2.MarketMaker`, variantes `market_maker` et
  `market_maker_serre`) : à chaque cycle, achat du OUI et achat du NON POSÉS au meilleur acheteur
  de chaque côté (paire payée au plus 1 − `min_pair_margin`), sur des marchés calmes (milieu
  0,15-0,85, prix stable sur 6 h, échéance ≥ 3 jours, ni sport ni crypto : `rebateRate` < 0,25),
  avec une cagnotte de récompense ≥ 5 $/jour. Le stock détenu est revendu au meilleur vendeur ;
  stock net plafonné (`max_net_quotes`) ; coupe-perte (`stop_loss`, vente immédiate). Cotes de
  12 min renouvelées à chaque cycle. Exemptée de la « mise prudente » (elle ne prédit rien :
  attribut `forecasting = False`), pas de la suspension.
- `liquidity_rewards.py` : récompenses de liquidité ESTIMÉES (formule officielle, carnet du NON =
  miroir du OUI, concurrents comptés une fois), table `recompenses_estimees`, jamais dans le
  journal ni dans le capital (proposition au noyau si la piste se confirme).
- `markout.py` : sélection adverse des ordres posés (écart avec le milieu à 5 min, 1 h, 6 h,
  24 h et à la résolution), ordres servis contre ordres manqués, pour tous les portefeuilles qui
  posent des ordres (tenue de marché et variantes « patientes »). Section « Ordres posés » du
  tableau de bord.
- Gamma : `rewardsMinSize`, `rewardsMaxSpread`, `clobRewards[].rewardsDailyRate` →
  `MarketInfo.rewards_*` ; `feeSchedule.rebateRate` → `FeeSchedule.rebate_rate`.
- Limites : photo du carnet toutes les 5 min (Polymarket : chaque minute) ; file d'attente
  inconnue (règle d'exécution prudente du simulateur : seulement si le prix est traversé) ;
  un ordre du capital principal réduit à sa part peut passer sous la taille récompensée.

## 31. Le favori, raison par raison (16 octobre 2026)

Étude `experiments/favori.md` (script `experiments/favori/analyse.py`, prix réellement payés,
échéance ANNONCÉE comme référence de temps) : le favori est trop cher en moyenne, sauf en politique
et géopolitique (+5,7 % après frais, stable) ; la fin de partie est un piège ailleurs.
- `NaiveFavorite` (strategy_engine.py) gagne des options, sans changer l'originale : `familles`
  (YAML, liste ; `market_family` d'après le barème de frais : politics, sports, crypto, economics…,
  sans frais = sans_frais (surtout géopolitique)), `min_hours` / `max_hours` (avant l'échéance, ou avant le coup d'envoi
  `MarketInfo.game_start` = Gamma `gameStartTime`), `underdog` (acheter l'outsider), `shrink`
  (estimation = milieu + shrink × (1 − milieu)), `max_candidates` (marchés demandés au scanner).
- Variantes : `favori_politique`, `favori_politique_patiente`, `naive_favorite_sans_fin`,
  `outsider_sport_patiente`. `scanner.max_extra_markets` passé à 260.
- `strategies_v2.PriceMove` (mouvement de prix sur 6 h, `direction` 1 suivre / −1 contrer) :
  `suivre_politique`, `contrer_crypto` (+ patiente). Autres variantes : `favori_politique_quasi_certain`,
  `loterie_meteo`. YAML `exclure_mots` (question contenant un mot → marché exclu).

## 32. Tableau de bord réglé par le chercheur (17 octobre 2026)

Décision d'Etienne : le chercheur améliore le tableau de bord (ordre, tri, suppression du superflu).
- `config/dashboard.yaml` (libre) : `ordre` des blocs, `masquer`, `a_la_une` (5 points au plus) ;
  lu par `dashboard.layout` (garde-fous : identifiants connus seulement, `resume` et `capital`
  jamais cachés, textes bornés) ; appliqué dans le gabarit (blocs et menu réordonnés, encadré
  « À la une » en tête du résumé, texte inséré par `textContent`).
- `scripts/apercu_dashboard.py` : page reconstruite avec les données publiées et le gabarit du
  dépôt, photos téléphone / ordinateur (Node + Playwright), erreurs JavaScript et débordements.
- Méthode, garde-fous, évaluation de départ de chaque bloc : `docs/TABLEAU_DE_BORD.md`.

## 33. Entonnoir : mères, filles et phrases simples (17 octobre 2026)

- `strategy_engine.Filtered` (YAML `filtres`) : une « fille » joue la stratégie mère sur un morceau
  des marchés (`familles`, `heures_min`/`heures_max`, `prix_min`/`prix_max`, `issue` oui/non/autre).
  Filtres de marché avant la mère, filtres d'issue après ; ventes jamais filtrées.
- 17 filles : 11 de `naive_favorite` (`nf_*`), 6 de `news_momentum` (`nm_*`).
- YAML `explication` (phrase simple pour Etienne, sous chaque nom dans l'arène), `mere`, `morceau` ;
  `dashboard.strategy_info`, `dashboard.funnel` (fille comparée à la mère depuis sa naissance,
  d'après la courbe de capital de la mère) ; bloc « Entonnoir » du tableau de bord.
- Dissection des paris déjà faits : `experiments/dissection/dissequer.py`, `experiments/dissection.md`.

## 34. « AMELIORATION » du 17/10/2026 (réponse d'Etienne : « Tout »)

- Gemini : plafond du jour réparti heure par heure (`GeminiClassifier._budget_left`) : les 500 appels
  partaient avant 10 h UTC.
- Entonnoir, étage 2 : `nf_sport_prix_haut`, `nf_sport_sans_fin`, `nf_prix_haut_sans_fin` ; taille des
  mises : `nf_demi_mise`, `nf_quart_mise`, `nm_demi_mise` ; heure de la journée (filtre `heure_utc`) :
  `favori_politique_nuit`, `outsider_sport_apres_midi` (`experiments/favori/heure.py`).
- Coupées (servies quand elles ont tort ou perdantes) : `market_structure_patiente`, `reversion`,
  `naive_favorite_patiente` ; règle : ordres posés seulement pour la tenue de marché (METHODE.md).
- Capital principal plafonné (`settings.yaml` → `principal`) : 10 % du capital par achat, 40 % par
  famille de marchés (`main._cap_main`) ; fantômes non plafonnés.
- Ménage : retrait des stratégies sans opération ni position après 3 jours (`arena.retire_inactive`,
  `promotion.yaml`), sans toucher au compteur de l'élimination hebdomadaire.
- Tenue de marché élargie : 25 marchés, 3 % du capital par marché et par côté, 60 ordres posés au plus.
- Proposition noyau : `proposals/2026-10-17_recompenses_au_capital.md` (récompenses dans le journal).


## 35. Récompenses de liquidité : classement de l'arène (17 octobre 2026, option A d'Etienne)
- Les récompenses ESTIMÉES d'une stratégie qui pose des ordres (journées terminées d'au moins 1 $,
  chaque marché plafonné à sa cagnotte, × prudence 0,5 : `liquidity_rewards.ranking_bonus`)
  s'ajoutent à son capital réalisé pour calculer la croissance JUGÉE par l'arène (champion, parts
  du capital principal). Le capital du fantôme, lui, ne change jamais. Réglage :
  `settings.yaml → recompenses` (`classement_arene`, `prudence`).
- Le versement au capital PUBLIC (et à lui seul) attend le noyau (écriture `REWARD` dans
  `ledger.py`, contrôle par l'audit) : `proposals/2026-10-17_recompenses_au_capital.md`.
- Limite : les entrées de l'arène exigent toujours 20 opérations clôturées ; une tenue de marché
  peu servie peut attendre longtemps avant d'être jugée.

## 36. « AMELIORATION » du 17/10/2026 au soir (réponse d'Etienne : « Tout »)
- **Promotion** (`arena.py`, `config/promotion.yaml`) : score de confiance `min_t_stat` (t de
  Student des résultats par opération), période d'essai (`essai` → `arena.exposure`, appliquée
  par `main.py` à chaque part), modes `juger_sur_recompenses` (tenue de marché) et
  `juger_sur_valeur` (favori politique) avec `part_max`. Compte rendu : `experiments/promotion.md`.
- **Sport** : `sports_link.py` relie un marché « A vs. B » à son match (scores officiels) et à ses
  cotes (The Odds API) → `market.sport`. `cotes_bookmakers` (avant le match, Polymarket nettement
  moins cher que les bookmakers) joue dans l'arène ; `fin_de_match` est écrite mais COUPÉE : sur
  175 matchs MLB, le gagnant ne se vend plus sous 0,999 au-delà de 1 à 2 min après la fin
  (`experiments/fin_de_match/`).
- **Sortie météo** : `meteo_prevision` revend un NON quand le marché le rachète plus cher que la
  probabilité du modèle + `exit_margin` (vaut aussi pour les positions du principal).
- **Ménage** : stratégies coupées marquées « retirée » et rangées en bas de l'arène ; GDELT toutes
  les 3 h (HTTP 429) ; Gemini « en pause » (budget de l'heure) n'est plus compté comme une panne.

## 37. « Vague d'opinion » (idée d'Etienne, 18/10/2026)
- Idée : sur un marché long, acheter au début d'une vague d'attention (réseaux, presse) et
  revendre quand elle est passée, sans attendre le règlement. Stratégie `vague_opinion`
  (`strategies_v2.OpinionWave`) : entrée sur pic de mentions + sources indépendantes + sens (IA ou
  prix qui démarre), aller-retour (écart + frais aux deux bouts) vérifié, sorties objectif / stop /
  vague retombée / durée maximale.
- Test sur le passé (`experiments/vague_opinion/`, 140 marchés, fichiers GDELT GKG, prix des vrais
  échanges) : après une vague, le prix revient en arrière ; suivre −9,1 %, contrer −4,6 % par
  opération après coûts ; 0 réglage gagnant sur 384. COUPÉE. Ce que la vague annonce : de
  l'agitation (+32 % de mouvement) — piste : s'en servir comme alarme pour la tenue de marché.

## 38. Plusieurs championnes (décision d'Etienne, 18/10/2026)
- Plus de marge de +1 % (`promotion_margin: null`) : toute stratégie qualifiée reçoit une part du
  capital principal ; le titre de « champion » du journal signé reste à la doyenne tant qu'elle
  est qualifiée (pas de va-et-vient d'écritures).
- Parts (`arena.allocation`) : moitié à égalité, moitié selon les gains (`repartition.merite`
  0,5) ; une seule place par famille (`arena.family_map`, champ `mere` de strategies.yaml ;
  remplacé par la mesure des doublons, §39) ; au
  plus 50 % du capital par stratégie (`part_max_par_strategie`, dans `arena.exposure`), en plus de
  la période d'essai et des plafonds des modes.
- `main._steady_shares` : parts recalculées au plus une fois par heure (une entrée ou une sortie
  s'applique tout de suite), gardées en base sous `repartition_principal` ; le tableau de bord
  affiche chaque championne et sa part, et la phrase du haut les cite toutes.

## 39. Doublons mesurés au lieu d'« une place par famille » (décision d'Etienne, 18/10/2026, option B)
- Constat : nf_sport (qualifiée, confiance 5,6) n'avait aucune part parce que nf_court, sa sœur,
  avait la place de la famille naive_favorite ; à quelques dixièmes de pour cent près, la place
  passait de l'une à l'autre.
- Règle (`arena.allocation`, `_twins`, `overlap`) : on compare les événements (matchs…) réellement
  achetés par deux qualifiées depuis le début de leur époque (`Standing.events`,
  `bought_events`). Si plus de `chevauchement_max` (0,5, config/promotion.yaml) des paris de la
  plus petite sont communs, ce sont des doublons : seule la meilleure prend une place, même entre
  familles différentes. En dessous, chacune a la sienne, même une mère et sa fille. Sans achat à
  comparer, ou si `chevauchement_max` est absent, la règle de la famille s'applique.
- Mesure du 18/10 (journaux de production) : nf_sport partage 79 % de ses matchs avec nf_court
  (doublon) ; nf_sport_patiente 17 % ; nf_sport_prix_haut 41 %.
- `run_arena` renvoie `doublons` ({nom: {comme, chevauchement}}), gardé en base
  (`doublons_principal`) ; le tableau de bord marque ces stratégies « doublon » et dit pourquoi.
- Garde-fou du principal (`main._execute`) : si deux stratégies veulent le même marché dans le
  même cycle, seule la première l'achète (les stratégies sautent déjà les positions ouvertes ;
  sans ce filtre, le test montrait un double achat).

## 40. Copie fidèle : le principal refait les paris de ses championnes (AMELIORATION du 18/10/2026 au soir)
- Constat (journaux de production, 18/10 à 21 h) : capital principal à 897 (réalisé 914) pendant
  que nf_sport (+13 %) et nf_court (+11 %) gagnaient. Depuis 06:28, hors météo, le principal a
  perdu 89 sur 12 opérations (−23 % des mises) quand les fantômes copiés perdaient 2 à 4 % de leurs
  mises sur la même période. Cause : le principal relançait la stratégie sur SON état (son argent,
  ses positions) ; il ne prenait donc pas les paris jugés par l'arène. À la promotion il achetait
  d'un coup des positions que le fantôme tenait depuis des heures (Titans −55 : acheté par le
  fantôme la veille), et ses mises étaient 1,5 à 3 fois plus grosses en proportion (Bitcoin −48 :
  51 parts contre 17 pour le fantôme).
- Règle (`main.Weighted`, `source`) : les fantômes tradent d'abord ; chaque pari exécuté (et
  chaque ordre posé) est noté (`Portfolio.copied`) ; le principal refait ces paris dans le même
  cycle, mêmes marchés, mise × (part × capital du principal / capital du fantôme). Il ne rachète
  jamais une position que le fantôme tenait déjà avant la promotion. Les sorties restent celles de
  la stratégie (`exits`) sur les positions du principal ; les reventes posées de la tenue de marché
  sont copiées dans la limite du stock détenu. Plafonds inchangés : budget par stratégie
  (part × capital), `_cap_main`, un seul achat par marché et par cycle.
- Estimation sur les mêmes journaux : la copie aurait fait ≈ −5 au lieu de −89 depuis 06:28.
- Limite connue : à petite part, une copie peut tomber sous le minimum d'un marché (5 parts) ; elle
  est alors refusée par le contrôleur, comme tout ordre trop petit.

## 41. Les favoris ne gagnent pas plus que leur prix : confiance sur le rendement (18/10/2026)
- Mesure en direct (`experiments/favori.md` §6) : 160 paris sur favoris réglés dans les fantômes de
  la famille naive_favorite (dédoublonnés) ; gagnés 86,9 % pour un coût moyen de 0,893 par part
  (frais compris) ; estimation des stratégies 0,92 à 0,98 (prix + 5 points) : trop optimiste
  d'environ 6 points, comme le test sur le passé (7 600 paris, favori surpayé de 1 à 2 points).
- Le score de confiance de l'arène était calculé sur les résultats en euros : avec des mises Kelly
  très inégales, il mesurait la taille des mises gagnantes. nf_sport : 2,7 (qualifiée) avec 24
  gagnés pour 23,4 attendus ; nf_court : 1,2 en gagnant moins souvent que ses prix.
- Désormais (`arena.trade_returns`) : t de Student des rendements (résultat / mise). Sur les mêmes
  journaux : nf_sport 0,4, nf_court −0,7, naive_favorite −0,7 ; nf_sport_patiente 2,75 (40 gagnés
  pour 36,2 attendus : ses ordres posés achètent moins cher) ; la météo reste à −1,2.
- Rejeu (`experiments/promotion/rejouer.py`, copie de portefeuille, 15 → 18/10) : règle actuelle
  (t ≥ 1,5 + essai) −15 ; même règle sur le rendement +74 (nf_sport_patiente seule). Attention :
  mesure faite sur les journaux qui ont inspiré la règle ; c'est le principe (la taille des mises
  ne prouve rien) qui justifie le changement, pas le chiffre du rejeu.
- Maintien : la championne garde sa place tant que sa croissance reste positive ET que son score
  de confiance reste ≥ `keep_t_stat` (0). Sans ce seuil, nf_court (−0,7) serait restée championne.
  Simulation avec les journaux du 18/10 à 21 h : nf_sport_patiente devient championne, 50 % du
  capital principal ; nf_court et nf_sport sortent (leurs positions vont à leur terme).

## 42. AMELIORATION du 19/10/2026 (réponse d'Etienne : « Tout »), lot 1
- Constat d'ensemble (1 549 opérations clôturées de tous les fantômes) : −3 416 au total ; les
  paris gardés jusqu'au règlement gagnent 4,4 points de moins que leur prix ; seules poches non
  négatives : favori politique (+2,3 %), favori sportif posé (+4,9 %), favori météo (≈ 0).
- cotes_bookmakers : 17 de ses 20 achats étaient des HANDICAPS (« Spread: Colts (-7.5) ») auxquels
  elle appliquait les cotes du vainqueur. `sports_link.winner_market` : seul le pari « vainqueur »
  est rattaché (Gamma `sportsMarketType == "moneyline"`, sinon le libellé) ; garde-fou `max_gap`
  (25 points d'écart avec les bookmakers = mauvais rattachement). `MarketInfo` lit aussi
  `sportsMarketType` et `holdingRewardsEnabled` (récompense de détention, lot 2).
- Ménage (`arena.retire_hopeless`, `retirer_perdantes` dans promotion.yaml) : confiance ≤ −1,5
  après 20 opérations → retrait immédiat (journal signé, hors compteur hebdomadaire ; jamais le
  champion, ni les modes de jugement). Le 19/10 : news_momentum, news_momentum_patiente,
  meteo_prevision.
- Reventes immédiates : −656 sur 524 ventes, mais presque toutes par market_structure (déjà
  coupée) ; les stratégies actives ne revendent plus qu'avec des ordres posés (tenue de marché)
  ou rarement (météo : 3 ventes, +15). Rien à changer.

## 43. Récompense de détention et parking politique (19/10/2026, lot 2)
- Polymarket verse un taux annuel (4 % le 19/10, variable) sur la valeur des positions des marchés
  éligibles (Gamma `holdingRewardsEnabled`, lu dans `MarketInfo.holding_rewards`).
- `holding_rewards.py` : à chaque cycle, valeur de chaque position éligible au meilleur acheteur ×
  taux (`recompenses.detention_taux_annuel`) × durée du cycle → table `recompenses_detention`.
  Comptée pour le classement de l'arène (× prudence, comme les récompenses de liquidité), jamais
  dans le capital d'un fantôme ; celle du principal est affichée à part (« hors capital »).
  Versement au capital public : proposals/2026-10-19_detention_et_remises.md (noyau).
- `parking_politique` (naive_favorite, `holding_only`) : favoris politiques 0,93-0,99, au moins 2
  semaines avant la fin, marchés éligibles seulement ; l'avantage et la mise comptent la
  récompense attendue (`holding_rate` × années, au plus `holding_years_max`), pas les
  probabilités déclarées (vérifiées par le contrôleur). Jugée sur la valeur (part max 30 %).
- Pas encore de « placement de l'argent qui dort » dans le principal : tant que la récompense
  n'est pas versée au journal signé, il ne gagnerait que le mouvement des prix (≈ 0) pour un
  risque de plus ; l'arène mesure d'abord parking_politique.

## 44. Cotes fraîches avant les matchs et cycles plus rapides (19-20/10/2026)
- Cotes (`sources/odds_api.py`) : passage horaire ; la liste des matchs à venir de chaque ligue
  (`/events`, gratuite, vérifiée à chaque appel par l'en-tête `x-requests-last`, sinon retour au
  rythme de 12 h) dit quelles ligues ont un match dans les 6 h ; seules celles-là sont relevées,
  au plus toutes les 2 h 30 par ligue, le match le plus proche d'abord, dans la limite de 15
  crédits par jour (450 par mois sur 500 gratuits). Pinnacle (bookmaker de référence) est gardé à
  part (`reference`) et préféré par `sports_link`. cotes_bookmakers refuse des cotes de plus de 4 h.
- Cycles (mesure locale d'un cycle complet : 141 s dont 125 s d'attente réseau) :
  - relecture des carnets partagée dans le cycle (`main._reread_book`, 20 s) : 148 → 96 relectures,
    28 → 18 s ;
  - pages du scanner lues par 4 en même temps (`GammaClient.list_markets`, intervalle minimal
    protégé par un verrou dans `HttpClient`) : 16 → 8 s ;
  - GDELT limité à 6 s d'attente (15 s avant).
  Cycle sans source en attente : 109 → 65 s (comparaison approchée).

## 45. Entonnoir 80/20 (demande d'Etienne, 20/10/2026)
- `pareto.py` : opérations clôturées de chaque fantôme rangées par prix payé, délai jusqu'à
  l'échéance (noté à l'achat), issue, heure d'achat (UTC), discipline et type de pari (classement
  par source de résolution puis libellé, partagé avec les filtres), mode d'achat (immédiat ou ordre
  posé) et source de résolution. Par caractéristique : résultat, rendement par mise, confiance,
  gagnés contre attendus (z) et « cœur » = morceaux qui font 80 % des gains des morceaux gagnants.
  Filles proposées : morceau filtrable d'au moins 8 opérations, gagnant, meilleur que la stratégie
  entière, z ≥ 0 (+ le meilleur croisement de deux morceaux).
- Disséquées : croissance ≥ +5 % sur 15 opérations, ou croissance supérieure à celle de la mère.
- `scripts/research_brief.py` écrit `reports/pareto.md` et ajoute à la feuille de mission les 3
  meilleures filles pas encore dans l'arène ; le tableau de bord (bloc Entonnoir) montre, par
  stratégie, le cœur le plus simple et les filles à créer.
- Nouveaux filtres de fille (`strategy_engine.Filtered`) : `disciplines`, `types_pari`,
  `echeance_min` / `echeance_max` (heures jusqu'à l'échéance), `ecart_max`.
- Premier résultat (journaux du 20/10) : nf_sport_patiente gagne par le TENNIS (38 opérations,
  +411, 37 gagnés pour 32,6 attendus, z +2,1 ; le reste −188, z +0,1) et par ses achats IMMÉDIATS
  (+10,4 % par mise contre −2,7 % pour ses ordres posés). Filles créées : nf_sport_patiente_tennis,
  nf_tennis (achat immédiat), nf_tennis_prix_bas (0,80-0,875 ; plus cher, le tennis ne gagnait rien
  chez nf_sport_prix_haut).


## 46. Vingt nouvelles pistes (demande d'Etienne, 20/10/2026)
Recherche et tableau des 20 pistes : `experiments/vingt_pistes.md`. Toutes entrent dans l'arène
comme fantômes ; l'entonnoir 80/20 leur proposera des filles.
- Lot A (`strategies_v3.py`, données Polymarket seules) : decroissance_temps, echelle_dates,
  coherence_match, implication_politique, paire_oui_non, outsiders_surcotes, marche_neuf,
  apres_echeance (marchés échus non réglés : `ended_pages` du scanner, réservés aux stratégies
  `wants_ended`), marches_jumeaux, choc_sans_nouvelle.
- Lot B (`references.py`) : instantanés gratuits dans la petite mémoire de la base (`ref:kalshi`,
  `ref:predictit`, `ref:tweets`, `ref:outrights`, cache `manifold:<id>`), rattachés aux marchés
  (`market.references`, `market.tweets`) par des règles strictes (mêmes nombres, mots distinctifs,
  échéance proche). Stratégies `*_reference` (Kalshi, PredictIt, Manifold, champions contre
  Pinnacle via `OutrightsSource`, football à trois issues), compteur_tweets (XTracker : messages
  comptés + rythme de 14 jours heure par heure, loi binomiale négative réglée sur le passé),
  cotes_tennis (fille de cotes_bookmakers ; tournois de tennis ajoutés à odds_api). Les cotes
  de champion partagent le budget quotidien de crédits de The Odds API.
- Lot C : fatigue_nhl (`ref:nhl_repos` : calendrier NHL depuis la veille, une requête par heure ;
  `references["repos_nhl"]`), mots_prononces et mots_nouveaux (`ref:mentions` : marchés
  « mentions » réglés, comptés par orateur et par mot deux fois par jour ;
  `references["mentions"]`, `references["mot_nouveau"]`). haut_ou_bas_crypto, totaux et séries
  NHL testés sur le passé puis écartés (experiments/vingt_pistes.md).
