# Méthode de travail et de recherche

Fichier libre : le chercheur peut l'améliorer. Les règles permanentes sont dans `CLAUDE.md`.

## Méthode de travail

- Suis le plan de `ARCHITECTURE.md §10`. Chaque étape se termine par : fichiers créés, tests exécutés, bilan honnête (fait / pas fait / limites).
- Tests avec `pytest`. Tout défaut découvert donne lieu à un test de non-régression.
- Petits commits clairs. Jamais un gros bloc de code non testé.
- Dépendances peu nombreuses, maintenues, versions épinglées dans `requirements.txt`.
- Le cycle de 5 minutes n'appelle aucun modèle d'IA par défaut : filtres statistiques et règles déterministes d'abord.
- Avant d'utiliser un endpoint Polymarket, vérifie sa documentation actuelle sur docs.polymarket.com : frais et limites changent.
- Verrouillage actif depuis le 15/10/2026 : uniquement des branches `claude/` et des pull requests vers `main`, fusionnées automatiquement si `guard` et `tests` passent.
- Tes propres workflows : `.github/workflows/labo-*.yml`, avec un bloc `permissions:` en lecture seule, déclenchés par `workflow_dispatch` ou `schedule`, sans secret, sans environnement, sans les noms `guard` ou `tests`.
- Si un domaine réseau est bloqué (erreur 403 `host_not_allowed`), dis à Etienne exactement quel domaine ajouter dans l'environnement Claude Code.

## Méthode de recherche (chaque session de recherche)

Liste de travail permanente : `experiments/CHANTIERS.md` (nouvelles sources, décidées par
Etienne). Sans obligation dans la feuille de mission, avance au moins un chantier par passage.
À chaque passage, ajoute au moins une nouvelle stratégie ou variante dans l'arène (tester en
portefeuille fantôme ne coûte rien ; la prudence statistique sert à juger, pas à s'abstenir).


1. Lis la feuille de mission en premier : classement de l'arène, champion, palier suivant
   (cliquet ×1,5), obligations. En routine (production) : `bash scripts/fetch_published.sh`
   puis `published/rapports/brief.md` (produite par le cycle avec la vraie clé). En local :
   `.venv/bin/python scripts/research_brief.py --dev-key` puis `reports/brief.md`.
2. Remplis **toutes** les obligations de la feuille de mission (idées à ajouter, stratégies
   éliminées à remplacer, idée radicale si aucun palier depuis 7 jours).
3. Mission : battre le record, atteindre le palier suivant le plus vite possible, sans jamais
   atteindre 0. Prends des risques et essaie des idées neuves ; l'arène tranche en conditions réelles.
4. Une nouvelle stratégie = une classe dans `strategy_engine.py` ou `strategies_v2.py`, une entrée
   dans `strategies.yaml`, des tests. Elle entre dans l'arène dans son propre portefeuille fantôme.
   Variante sans nouveau code : une entrée `strategies.yaml` avec `class: <stratégie existante>`
   (autres paramètres, autre nom, son propre fantôme). `limit_ticks: N` la passe en mode
   « patient » : elle POSE ses achats N crans au-dessus du meilleur acheteur au lieu de payer le
   vendeur. Une stratégie peut aussi remplir `StrategyOutput.limit_orders` elle-même.
   Exécution d'un ordre posé (noyau, `execution_simulator.py`) : seulement si un carnet relu
   APRÈS la pose montre le marché passé au travers du prix (vendeurs à prix − 1 cran ou moins),
   pour la quantité affichée, au prix posé. Un nouvel ordre remplace l'ancien sur le même jeton ;
   durée de vie et nombre d'ordres : `settings.yaml` → `limit_orders`.
   Règles de l'arène et de la promotion : `config/promotion.yaml` et `arena.py`, entièrement
   libres (seuils d'entrée et de maintien, marge, ancienneté, nombre de stratégies dans le
   principal, élimination). Change-les quand les données le justifient ; explique pourquoi dans
   `experiments/journal_recherche.md`. Seules limites : le noyau protégé (journal signé,
   contrôleur, simulateur, frais, mots de passe).
   Simulation (noyau) : 25 % de la quantité au meilleur prix, 50 % aux niveaux suivants, liquidité
   partagée entre tes ordres d'un même cycle. Chaque exécution est auditée contre l'historique
   public des prix (job `audit`) : un prix impossible déclenche une alerte à Etienne.
   Clés disponibles dans l'environnement du cycle (si Etienne les a ajoutées) : GUARDIAN_API_KEY,
   FOOTBALL_DATA_KEY, ODDS_API_KEY, BALLDONTLIE_API_KEY, PANDASCORE_API_KEY, FRED_API_KEY,
   DATA_GOV_API_KEY, YOUTUBE_API_KEY, TMDB_API_KEY, COINGECKO_API_KEY, ETHERSCAN_API_KEY
   (une source sans sa clé doit dire « désactivée (pas de clé …) », jamais planter).
   Source de résolution de chaque marché : `resolution_sources.domain_for(db, market_id)` et
   `experiments/sources_resolution.md` ; relevés NOAA (`meteo_metar`), scores des ligues
   (`mlb_stats`, `nhl_stats`, `football_data`), cotes (`odds_api`) arrivent comme observations
   (`market.intel`, table `observations`, champ `data`). Chantier n°0, étape 3 : à toi.
   Exemple de méthode : `experiments/meteo_backtest.md` (prévisions passées sans
   regard vers le futur, réglage sur la première moitié des dates, jugement sur la seconde,
   coûts réels). Fais pareil avant toute nouvelle stratégie quand l'historique existe.
   **Toujours vérifier aux prix réellement payés** (`idea_test.fetch_event_trades` et
   `taker_cost`) : le 16/10/2026, la météo gagnait +28 % avec l'historique « 10 minutes » du
   CLOB, mais −6 % aux prix des vrais échanges (tout le gain venait de marchés sans échange) ;
   même piège en crypto (`experiments/crypto_backtest.md`).
   Outil tout prêt : `src/polymarket_agent/idea_test.py` (marchés résolus d'une famille, prix à
   un instant sans regard vers le futur, jugement hors échantillon, simulation avec frais) ;
   exemple d'emploi : `experiments/meteo_backtest/station_bias.py`.
   Une stratégie qui a passé un tel test (gain hors échantillon, après frais, la plupart des
   jours) peut être inscrite dans `config/promotion.yaml` → `validated_strategies` : elle
   reçoit une part du capital principal plus tôt (seuils allégés), si elle gagne aussi en direct.
5. Pour ajuster des paramètres : `scripts/lab.py` (walk-forward, pénalité des essais multiples).
   Ses résultats sont des hypothèses : le prix historique n'est pas un prix exécutable.
6. Lis les verdicts du moteur d'apprentissage dans la feuille de mission avant de juger une stratégie.
7. Santé des stratégies (`strategy_health.py`, réglages `sante_strategies` dans `settings.yaml`) :
   chaque prévision est jugée quand son marché est réglé (Brier comparé au prix payé : « avance »
   positive = mieux que le marché). Tant que moins de 20 prévisions sont jugées, la mise est
   réduite (½ Kelly) ; prouvée meilleure → mise entière ; moins bonne → ¼. Une stratégie gagnante
   avant frais mais perdante après est suspendue. Visible dans l'arène du tableau de bord : sers-
   t'en pour corriger une stratégie avant que l'élimination hebdomadaire ne tranche.

## Commandes

À compléter au fil du projet.

- Installer : `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- Tests : `.venv/bin/python -m pytest -q`
- Initialiser le journal (une seule fois) : `.venv/bin/python scripts/initialize.py --dev-key`
- Un cycle unique : `.venv/bin/python scripts/run_simulation.py --once --dev-key`
- Feuille de mission : `.venv/bin/python scripts/research_brief.py --dev-key`
- Rapport : `.venv/bin/python scripts/generate_report.py --dev-key`
- Laboratoire : `.venv/bin/python scripts/lab.py` (ajouter `--apply` pour écrire les recommandations)
- Tableau de bord : `.venv/bin/python scripts/build_dashboard.py --dev-key` (sortie `site/`, régénéré par le cycle toutes les 10 min)
- Rapports publiés par le cycle de production : `bash scripts/fetch_published.sh` (dossier `published/`)
- Production : workflows `cycle` (toutes les 5 min), `initialize` (une fois), exploitation dans `docs/EXPLOITATION.md`
- Réinitialisation (Etienne seul, via le workflow `reset-capital`) : `scripts/reset_capital.py`
- Contrôle des fichiers protégés : `scripts/guard_check.py PROTECTED_PATHS.txt < liste_des_fichiers`
- `--dev-key` : clé locale de test (`state/dev_ledger_key`, ignorée par Git). En production, `LEDGER_KEY` vient de l'environnement GitHub `production`.

### Commandes d'Etienne (dans la conversation)

- **« AMELIORATION »** (décision d'Etienne, 16/10/2026) : à chaque fois que ce mot est envoyé,
  répondre à la question : « Qu'est-ce qui peut être amélioré (workflow, limites à assouplir,
  sources à apporter, stratégies à explorer…) ? Réfléchis à ton maximum, de manière out of the
  box ; tourne et retourne les problèmes dans tous les sens possibles pour en extraire les idées
  qui peuvent maximiser les gains. » Façon de répondre :
  1. partir des faits du moment, jamais de mémoire : tableau de bord publié (`data.json` sur
     `gh-pages` : capital, arène, positions, sources, audit), journaux (`data`), journal de
     recherche, chantiers, derniers tests sur le passé ;
  2. explorer tous les axes : stratégies (nouvelles familles, marchés tranchés vite, inefficacités
     mesurables), exécution (ordres posés, frais, écart achat-vente), mise et répartition du
     capital, règles de l'arène, sources (gratuites, officielles, source de résolution), workflow
     et fiabilité, limites à assouplir, et ce qui ne marche pas (à couper) ;
  3. pour chaque idée : pourquoi elle peut rapporter, comment la vérifier (test sur le passé ou
     arène), coût et risque, en chiffrant quand c'est possible ; classer par gain attendu ;
  4. finir par une courte liste de ce qu'il vaut mieux lancer d'abord et demander à Etienne
     lesquelles lancer (ne rien construire sans son accord, sauf s'il l'a dit dans le message).

