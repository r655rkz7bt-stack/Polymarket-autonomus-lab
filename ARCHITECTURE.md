# Architecture du laboratoire « favori de sport »

Copie élaguée (28/10/2026) du système de trading de « Polymarket Autonomous Lab ». Retiré : toute la partie recherche
(expériences, tests sur le passé, enquêtes, feuille de mission, routine du chercheur), les autres stratégies et les
sources externes (actualités, météo, crypto, bookmakers…). Gardé à l'identique : le noyau protégé (journal signé,
contrôleur, simulateur d'exécution, frais, audit, réinitialisation) et le gardien des pull requests.

## Le cycle (`scripts/run_simulation.py` → `main.run_cycle`)
1. Journal signé relu et vérifié (`ledger.py`) ; faillite = arrêt.
2. Règlements des marchés terminés (`settlement.py`), ordres posés servis ou annulés (`execution_simulator.py`).
3. Arène (`arena.py`) : classement des fantômes, confiance, champion(s) et parts du capital principal ; santé et renfort
   des stratégies (`strategy_health.py`).
4. Scanner (`market_scanner.py`, Gamma) : 1 500 marchés, 150 surveillés ; carnets (CLOB).
5. Stratégie (`strategy_engine.py` : `NaiveFavorite`, enveloppée par `Filtered` et `PatientOrders`) : propositions et
   ordres posés pour chaque fantôme ; le principal copie à l'échelle de sa part (`main.Weighted`, plancher et plafonds de
   `config/settings.yaml` → `principal`).
6. Contrôleur de sécurité (`safety_controller.py`), simulation sur les vrais carnets, écriture au journal.
7. Tableau de bord (`dashboard.py`, `dashboard_template.html`) toutes les 10 minutes.

## Données
Journal signé : branche `data` ; base d'analyse : cache GitHub Actions + sauvegarde quotidienne dans `data` ;
tableau de bord : branche `gh-pages`. Détails d'exploitation : `docs/EXPLOITATION.md`.

## Confiance (arène)
`arena.standing` : capital réalisé, croissance log, score t par opération (`confiance`, en % : `confidence_percent`) ;
`learning_engine` : verdict (« prometteuse », « indéterminée »…) avec intervalle par événement ; règles d'entrée au capital
principal (12 opérations, +2 %, t ≥ 1…) et de retrait : `config/promotion.yaml`.
