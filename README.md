# Polymarket Autonomous Lab

Agent de recherche et de **trading simulé** sur Polymarket.
Capital : 1 000 unités virtuelles. **Aucun ordre réel, aucun portefeuille, aucune clé privée.**
Règle n°1 : à 0 € tu meurs (arrêt définitif, réinitialisation manuelle uniquement).

- Architecture et décisions : [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Cahier des charges : [`docs/CAHIER_DES_CHARGES.md`](docs/CAHIER_DES_CHARGES.md)
- Règles permanentes pour Claude : [`CLAUDE.md`](CLAUDE.md)

## État d'avancement (étape 3 — prototype)

| Fonction | État |
|---|---|
| Scanner des marchés (API Gamma, horizon 30 min – 3 jours) | ✅ testé, vérifié sur données réelles |
| Carnets d'ordres (API CLOB publique) | ✅ testé, vérifié sur données réelles |
| Journal comptable signé (HMAC, chaîne de hash, faillite, verrou) | ✅ testé |
| Contrôleur de sécurité déterministe (`risk_limits.yaml`) | ✅ testé |
| Simulateur d'exécution « taker » (parcours du carnet, partiels, frais) | ✅ testé |
| Stratégie de référence `naive_favorite` | ✅ testée — **a priori non calibré, pas supposée rentable** |
| Base SQLite (marchés, carnets, décisions, cycles) | ✅ |
| Règlements des marchés résolus, ventes, rapports | ⏳ étape 4 |
| Positions corrélées (ex. deux marchés Bitcoin) | ⏳ étape 4 |
| Actualités, prix crypto, commentaires | ⏳ étape 5 |
| Backtests, laboratoire de stratégies, 7 stratégies | ⏳ étape 6 |
| Tableau de bord GitHub Pages | ⏳ étape 7 |
| Verrouillage GitHub (rulesets, `guard`) | ⏳ étape 8 |
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
