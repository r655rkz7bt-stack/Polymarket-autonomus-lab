# Polymarket Autonomous Lab

Agent de recherche et de **trading simulé** sur Polymarket.
Capital : 1 000 unités virtuelles. **Aucun ordre réel, aucun portefeuille, aucune clé privée.**
Règle n°1 : à 0 € tu meurs (arrêt définitif, réinitialisation manuelle uniquement).

- Architecture et décisions : [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Cahier des charges : [`docs/CAHIER_DES_CHARGES.md`](docs/CAHIER_DES_CHARGES.md)
- Règles permanentes pour Claude : [`CLAUDE.md`](CLAUDE.md)

## État d'avancement (étape 8 terminée — 15/10/2026)

| Fonction | État |
|---|---|
| Scanner des marchés (API Gamma, horizon 30 min – 3 jours) | ✅ testé, vérifié sur données réelles |
| Carnets d'ordres des deux issues (API CLOB publique) | ✅ testé, vérifié sur données réelles |
| Journal comptable signé (HMAC, chaîne de hash, faillite, verrou) | ✅ testé |
| Contrôleur de sécurité déterministe (`risk_limits.yaml`) | ✅ testé |
| Simulateur d'exécution « taker » (parcours du carnet, partiels, frais officiels) | ✅ testé |
| Règlement des marchés résolus (1/0 et 50-50) | ✅ testé, vérifié sur un vrai marché |
| Positions corrélées (même actif crypto) plafonnées à 15 % | ✅ testé |
| Rapports (`scripts/generate_report.py`) | ✅ testé |
| Historique non biaisé : 111 528 marchés résolus sur 40 jours tirés au hasard | ✅ `data/history/` |
| Backtest via le vrai journal et le vrai contrôleur, anti-fuite temporelle | ✅ testé |
| Portefeuilles « fantômes » (journal séparé par stratégie à l'essai) | ✅ testé |
| Liberté de trading totale (seule règle : à 0 € tu meurs) | ✅ décision du 15/10/2026 |
| Arène : 9 stratégies (les 7 familles du cahier des charges + 2), champion automatique, élimination hebdo | ✅ testé |
| Ventes (sorties objectif / stop / durée) | ✅ testé, vérifié en réel |
| Moteur d'apprentissage (verdicts par stratégie) | ✅ testé |
| Laboratoire : walk-forward, paramètres bornés, pénalité des essais multiples | ✅ testé |
| Cliquet des paliers (×1,5) inscrit dans le journal signé | ✅ testé |
| Feuille de mission du chercheur (`scripts/research_brief.py`) | ✅ testé |
| Sources : commentaires Polymarket | ✅ vérifié en réel |
| Sources : prix crypto, RSS (10 flux) | ✅ testées et vérifiées en réel |
| Sources : GDELT, Bluesky | ✅ testées — GDELT refuse souvent (429, IP partagée) ; Bluesky demande un compte (étape 8) |
| Gemini (gratuit, optionnel) | ✅ testé — inactif tant qu'il n'y a pas de clé |
| Mode dégradé (source en panne) | ✅ testé et vérifié en réel |
| **Stratégie rentable prouvée** | ❌ pas encore — l'arène tranche en réel |
| Tableau de bord (page statique, clair/sombre, téléphone) | ✅ testé, régénéré par le cycle toutes les 30 min |
| Publication du tableau de bord sur GitHub Pages | ⏳ étape 9 |
| Scénarios de panne (dont base SQLite illisible) | ✅ testés |
| Verrouillage : ruleset `main`, environnement `production`, `guard`, `tests`, fusion automatique | ✅ actif, vérifié en réel (PR de test bloquée) |
| Réinitialisation `reset-capital` | ✅ testée localement — ⏳ essai réel à l'étape 9 (branche `data`) |
| Exécution automatique toutes les 5 min | ⏳ étape 9 |

## Lancer le prototype (dans un terminal Linux / Claude Code)

Chaque commande, à quoi elle sert, et comment vérifier :

1. `python3 -m venv .venv` — crée un environnement Python isolé.
   Vérification : un dossier `.venv/` apparaît.
2. `.venv/bin/pip install -r requirements.txt` — installe les 3 dépendances épinglées.
   Vérification : la commande se termine sans `ERROR`.
3. `.venv/bin/python -m pytest -q` — lance tous les tests.
   Vérification : la dernière ligne indique `passed` et aucun `failed`.
4. `.venv/bin/python scripts/initialize.py --dev-key` — crée le journal avec 1 000 unités virtuelles.
   `--dev-key` crée une clé locale de test dans `state/dev_ledger_key` (jamais committée).
   Vérification : le message `Journal créé` s'affiche. Une 2ᵉ exécution est refusée (c'est voulu).
5. `.venv/bin/python scripts/run_simulation.py --once --dev-key` — lance un cycle.
   Vérification : le résumé JSON affiche `"statut": "OK"` et le capital.

6. `.venv/bin/python scripts/generate_report.py --dev-key` — écrit le rapport dans `reports/`.
   Vérification : le tableau « Capital » s'affiche, puis un rapport par portefeuille fantôme.
7. (Recherche, long) `.venv/bin/python scripts/research_calibration.py` — refait l'étude sur
   `data/history/` (environ 1 minute). Ne jamais ajouter `--final-test` sans protocole écrit avant.
8. (Laboratoire, ≈ 4 minutes) `.venv/bin/python scripts/lab.py` — teste des variantes de paramètres
   en walk-forward. Vérification : un rapport `experiments/lab_*.md` est écrit.
9. `.venv/bin/python scripts/build_dashboard.py --dev-key` — génère le tableau de bord.
   Vérification : le message `Tableau de bord : …/site/index.html` s'affiche ; ouvrir ce fichier
   dans un navigateur. (Le cycle le régénère tout seul toutes les 30 minutes.)

Codes de sortie de `run_simulation.py` : `0` OK / dégradé / faillite, `1` erreur, `2` journal corrompu ou absent.

## Dépannage

| Message | Cause | Solution |
|---|---|---|
| `LEDGER_KEY absente` | Pas de clé | En local : ajouter `--dev-key` |
| `"statut": "NON_INITIALISE"` | Journal absent | `scripts/initialize.py --dev-key` |
| `"statut": "CORROMPU"` | Journal modifié, tronqué, ou mauvaise clé | Ne rien effacer : prévenir Etienne |
| `"statut": "DEGRADE"` | API Polymarket injoignable | Rien à faire : le cycle suivant réessaie |
| `"statut": "FAILLITE"` | Capital virtuel épuisé | Seul le workflow `reset-capital` (étape 8) peut repartir |
| `403 host_not_allowed` | Domaine bloqué dans Claude Code | Ajouter le domaine dans les réglages réseau de l'environnement |
