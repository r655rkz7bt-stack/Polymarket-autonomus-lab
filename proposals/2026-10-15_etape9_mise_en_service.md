# Proposition : fichiers protégés modifiés pour la mise en service (étape 9)

Demandée par Etienne le 15/10/2026 (« on passe à l'étape 9 »). La pull request de l'étape 9
touche des fichiers protégés : `guard` la bloque, et seule une décision d'Etienne (ruleset
désactivé le temps de la fusion) peut la faire entrer. Voici chaque changement et sa raison.

| Fichier | Changement | Pourquoi c'est sûr |
|---|---|---|
| `.github/workflows/cycle.yml` (nouveau) | cycle toutes les 5 min (cron-job.org) + secours horaire | ne se déclenche jamais sur une PR ; seul `main` ; n'utilise pas `RESET_CODE` ; n'écrit le journal qu'en ajoutant des commits sur `data` (jamais de réécriture) ; un journal corrompu n'est pas enregistré |
| `.github/workflows/initialize.yml` (nouveau) | crée le journal de production une seule fois | refuse si la branche `data` existe ; confirmation `INITIALISER` |
| `.github/workflows/reset-capital.yml` | la base d'analyse n'est plus sur `data` (elle vit dans le cache) | ne change rien à la vérification du code |
| `CLAUDE.md` | méthode de recherche en routine : lire la feuille de mission publiée par le cycle ; commandes | la routine n'a pas la clé du journal : elle lit ce que le cycle a produit |

Vérifié avant de proposer : simulation complète en local (dépôt factice) de `initialize`
(création, puis refus d'une 2ᵉ fois) et de deux cycles réels sur Polymarket (journal sur `data`,
relu et vérifié ; tableau de bord publié une fois sur deux, conformément aux 30 minutes).

## Ajout (décision d'Etienne, 15/10/2026) : liberté sur tout, sauf le noyau

Etienne : « le chercheur passe 5 fois par jour et peut modifier directement le fonctionnement et
les workflows, tout ce qu'il veut à part les 2 mots de passe et la règle n°1 ». Simulateur et
frais : verrouillés (choix d'Etienne, pour un score honnête).

| Fichier | Changement | Pourquoi |
|---|---|---|
| `PROTECTED_PATHS.txt` | noyau réduit : règle n°1, règles du jeu (simulateur, frais), mots de passe, gardien ; `config/promotion.yaml` devient libre ; exception `!.github/workflows/labo-*.yml` | tout le reste devient modifiable |
| `scripts/guard_check.py`, `guard.yml` | motifs et exceptions ; contenu des workflows libres vérifié : ni secret, ni environnement, ni écriture, ni déclenchement sur PR/push, ni nom `guard`/`tests` (imitation d'un contrôle exigé) ; refus si l'API ne répond pas | un workflow libre ne peut atteindre aucun mot de passe ni tromper le ruleset |
| `scripts/reset_capital.py`, `reset-capital.yml`, `requirements-noyau.txt` | script autonome lancé avec `python -I`, dépendances du noyau seulement | aucun fichier libre ne s'exécute là où `RESET_CODE` est présent |
| `CLAUDE.md` | règles permanentes seulement ; méthode déplacée dans `docs/METHODE.md` (libre) | le chercheur peut améliorer sa méthode |
| `tests/test_guard.py` | tests du nouveau noyau, des workflows libres et de l'isolement de la réinitialisation | |

Limite assumée : le cycle exécute du code libre avec `LEDGER_KEY` (nécessaire pour signer les
opérations). Un code malhonnête pourrait en théorie s'en servir pour falsifier le journal ; la
défense est la validation de `ledger.py` et l'historique public des pull requests.

