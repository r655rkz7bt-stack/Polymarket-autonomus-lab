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
5. Pour ajuster des paramètres : `scripts/lab.py` (walk-forward, pénalité des essais multiples).
   Ses résultats sont des hypothèses : le prix historique n'est pas un prix exécutable.
6. Lis les verdicts du moteur d'apprentissage dans la feuille de mission avant de juger une stratégie.

## Commandes

À compléter au fil du projet.

- Installer : `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- Tests : `.venv/bin/python -m pytest -q`
- Initialiser le journal (une seule fois) : `.venv/bin/python scripts/initialize.py --dev-key`
- Un cycle unique : `.venv/bin/python scripts/run_simulation.py --once --dev-key`
- Feuille de mission : `.venv/bin/python scripts/research_brief.py --dev-key`
- Rapport : `.venv/bin/python scripts/generate_report.py --dev-key`
- Laboratoire : `.venv/bin/python scripts/lab.py` (ajouter `--apply` pour écrire les recommandations)
- Tableau de bord : `.venv/bin/python scripts/build_dashboard.py --dev-key` (sortie `site/`, régénéré par le cycle toutes les 30 min)
- Rapports publiés par le cycle de production : `bash scripts/fetch_published.sh` (dossier `published/`)
- Production : workflows `cycle` (toutes les 5 min), `initialize` (une fois), exploitation dans `docs/EXPLOITATION.md`
- Réinitialisation (Etienne seul, via le workflow `reset-capital`) : `scripts/reset_capital.py`
- Contrôle des fichiers protégés : `scripts/guard_check.py PROTECTED_PATHS.txt < liste_des_fichiers`
- `--dev-key` : clé locale de test (`state/dev_ledger_key`, ignorée par Git). En production, `LEDGER_KEY` vient de l'environnement GitHub `production`.
