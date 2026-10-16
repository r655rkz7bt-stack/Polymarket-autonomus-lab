# Le tableau de bord : à toi de l'améliorer (chercheur, depuis le 17/10/2026)

**Décision d'Etienne** : « Je voudrais que le chercheur puisse aussi modifier le dashboard, qu'il
améliore les choses, qu'il mette plus en haut les infos qu'il considère comme les plus importantes,
qu'il trie un peu, qu'il élimine les trucs qui sont superflus. »

Etienne lit le tableau de bord sur iPad ou téléphone, en quelques minutes, sans être spécialiste.
La question à se poser pour chaque bloc : **« Est-ce que ça aide Etienne à comprendre où on en est
et ce qui va se passer ? »** Si non, plus bas, replié ou caché.

## Comment faire
1. **Sans code** (le plus courant) : `config/dashboard.yaml`
   - `ordre` : l'ordre des blocs du haut vers le bas ;
   - `masquer` : les blocs jugés superflus ;
   - `a_la_une` : au plus 5 points courts en tête du résumé, ce que TU juges le plus important en ce
     moment (date du jour). Des faits avec leur source, jamais une promesse de gain. Mets-les à jour
     à chaque passage où quelque chose d'important a changé ; sinon laisse-les.
2. **Avec du code** (autorisé, libre) : `src/polymarket_agent/dashboard.py` (données) et
   `src/polymarket_agent/dashboard_template.html` (affichage) ; tests dans `tests/test_dashboard.py`.
   Supprimer un bloc devenu inutile, simplifier un texte, ajouter un graphique : tout est permis.
3. **Vérifier avant de publier** : `bash scripts/fetch_published.sh` puis
   `.venv/bin/python scripts/apercu_dashboard.py` → `apercu/telephone.png` et `apercu/ordinateur.png`
   (vraies données publiées + ton gabarit). Regarde les photos. Le script signale les erreurs
   JavaScript et les débordements horizontaux : il n'en faut aucun.
4. Écris ce que tu as changé et pourquoi dans `experiments/journal_recherche.md`.

## Garde-fous (non négociables)
- **Règle n°1** : le capital, le solde DISPONIBLE et l'état de faillite restent toujours visibles en
  haut (blocs `resume` et `capital` : le code refuse de les cacher).
- Les gains latents ne sont jamais présentés comme de l'argent disponible ; une estimation (ex.
  récompenses de liquidité) est toujours marquée comme telle.
- Tout texte venu de l'extérieur (questions de marchés, articles) reste affiché comme du texte
  (`textContent`, jamais `innerHTML`) : le test « EVIL » de `tests/test_dashboard.py` le vérifie.
- Lisible sur téléphone (390 px) : pas de débordement horizontal, contraste suffisant.
- Les tests doivent passer (sinon la pull request ne fusionne pas).

## Point de départ : évaluation du 17/10/2026 (Claude, à revoir par toi)
Mesures sur les vraies données (390 px de large) : la page fait **14 800 px de haut sur téléphone,
soit environ 17 écrans**. Objectif raisonnable : la moitié.

| Bloc | Hauteur (téléphone) | Utilité pour Etienne | Remarques et pistes |
|---|---|---|---|
| `resume` | 1 940 px | essentielle | 7 puces : garder les 4 les plus utiles ; « Dernières actions du chercheur » très bavard (replier à 1) ; « À la une » ajouté en tête |
| `aujourdhui` | 1 070 px | forte | le récit des 24 h : bien placé |
| `arene` | 2 360 px | forte | 28 stratégies ; le vocabulaire (« mise ×0,50 · prévisions jugées · avance · dérive ») est obscur pour un débutant : traduire ou replier ; regrouper « aucune opération clôturée » |
| `capital` | 430 px | essentielle | courbe du principal ; garder |
| `positions` | 990 px | moyenne | 287 positions tous portefeuilles confondus : surtout du bruit ; piste : principal d'abord, résumé par stratégie |
| `journal` | 1 890 px | moyenne | opérations clôturées (utile) + marchés surveillés (peu utile) |
| `ordres-poses` | 1 790 px | moyenne (recherche) | utile pour juger la sélection adverse ; tableau large sur téléphone |
| `organisme` | 1 530 px | moyenne | joli et apprécié, mais le « terminal » répète l'état des sources de `systeme` ; piste : n'en garder qu'un |
| `decisions-recentes` | 780 px | faible | détail technique (rejets du contrôleur) : plus bas ou caché |
| `systeme` | 1 600 px | faible au quotidien | utile en cas de panne ; doublon partiel avec `organisme` |

Ordre appliqué le 17/10/2026 (point de départ) : résumé, aujourd'hui, arène, capital, positions,
opérations, ordres posés, organisme, décisions, système. Rien n'a été caché : à toi de juger.
