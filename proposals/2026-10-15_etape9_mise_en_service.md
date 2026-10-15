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
