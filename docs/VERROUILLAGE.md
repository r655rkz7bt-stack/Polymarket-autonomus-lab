# Verrouillage du dépôt (étape 8) — guide pour Etienne

**État au 15/10/2026 : étapes 1 à 6 faites et vérifiées.**

But : qu'aucune IA (ni personne d'autre que toi) ne puisse modifier les règles de sécurité,
le journal comptable ou les workflows. La protection repose sur GitHub, pas sur la confiance.

Fais **une étape à la fois** et vérifie avant de passer à la suivante. Ne colle jamais un
secret dans une conversation avec Claude.

## Ce qui est déjà prêt dans le code

| Fichier | Rôle |
|---|---|
| `.github/workflows/tests.yml` | lance tous les tests sur chaque pull request (contrôle `tests`) |
| `.github/workflows/guard.yml` | bloque toute pull request qui touche un fichier de `PROTECTED_PATHS.txt` (contrôle `guard`) |
| `.github/workflows/automerge.yml` | fusionne seules les pull requests `claude/` une fois `guard` et `tests` verts |
| `.github/workflows/reset-capital.yml` | réinitialisation manuelle du capital, avec ton code `RESET_CODE` |
| `scripts/guard_check.py`, `scripts/reset_capital.py` | logique testée de ces workflows (fichiers protégés) |

## Étapes

1. **Fusionner le travail dans `main`** (pull request préparée par Claude, bouton « Merge pull request »).
   Vérification : onglet **Code**, branche `main` : le dossier `.github/workflows` est visible.
2. **Créer deux secrets aléatoires, sans les montrer à personne.** Sur un ordinateur, dans un
   onglet quelconque : touche F12 → onglet **Console** → coller la ligne ci-dessous → Entrée.
   ```js
   Array.from(crypto.getRandomValues(new Uint8Array(32)), b => b.toString(16).padStart(2, "0")).join("")
   ```
   Une suite de 64 caractères s'affiche : c'est un secret. Recommence pour en avoir un second.
   Sur iPad ou téléphone (pas de console) : la page privée « Coffre du labo » préparée par Claude
   fait la même chose sur l'appareil, sans rien envoyer sur Internet.
   Garde `RESET_CODE` dans ton gestionnaire de mots de passe (c'est le seul que tu retaperas).
3. **Environnement `production`** : **Settings** → **Environments** → **New environment** →
   nom `production` → **Configure environment**.
   - **Deployment branches and tags** → **Selected branches and tags** → **Add deployment branch
     or tag rule** → `main`.
   - **Environment secrets** → **Add environment secret** : `LEDGER_KEY` (secret n°1), puis
     `RESET_CODE` (secret n°2). Plus tard, en option : `GEMINI_API_KEY`, `BLUESKY_HANDLE`,
     `BLUESKY_APP_PASSWORD`.
   Vérification : la page de l'environnement liste les secrets par leur nom (valeurs invisibles).
4. **Ruleset sur `main`** : **Settings** → **Rules** → **Rulesets** → **New ruleset** →
   **New branch ruleset**.
   - Nom : `protection-main` ; **Enforcement status** : **Active** ;
   - **Bypass list** : laisser **vide** (sinon Claude, qui agit avec ton identité, pourrait contourner) ;
   - **Target branches** → **Add target** → **Include default branch** ;
   - cocher **Restrict deletions**, **Require a pull request before merging** (0 approbation),
     **Require status checks to pass** → **Add checks** → `guard` puis `tests`,
     **Block force pushes** → **Create**.
   Les contrôles `guard` et `tests` n'apparaissent dans la recherche qu'après avoir tourné une
   fois (Claude ouvre une pull request de test juste avant cette étape).
5. **Fusion automatique** : **Settings** → **General** → section **Pull Requests** → cocher
   **Allow auto-merge**.
6. **Test réel** (critère de fin de l'étape 8) : Claude ouvre une pull request qui modifie un
   fichier protégé. Attendu : `guard` en rouge, bouton de fusion bloqué. Claude la ferme ensuite.

## Modifier toi-même un fichier protégé (plus tard)

Le ruleset n'a aucune exception, toi compris. Pour un changement voulu :
**Settings** → **Rules** → **Rulesets** → `protection-main` → **Enforcement status** :
**Disabled** → fusionner → remettre **Active** tout de suite. Claude ne peut pas le faire :
modifier un ruleset demande les droits d'administration, que l'application Claude n'a pas.

## Réinitialiser le capital après une faillite

**Actions** → **reset-capital** → **Run workflow** → code `RESET_CODE` et une raison → **Run workflow**.
Le code n'est jamais affiché dans les journaux. Par prudence, **change `RESET_CODE` après
chaque utilisation** (étape 2 puis étape 3, bouton de modification du secret).
