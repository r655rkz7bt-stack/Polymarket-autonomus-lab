# Skills du labo

Un skill est une fiche de méthode que Claude Code charge quand la tâche s'y prête (sessions avec Etienne
et routine du chercheur). **CLAUDE.md prime toujours**, puis docs/METHODE.md et docs/ROUTINE_CHERCHEUR.md :
un skill n'autorise jamais ce que CLAUDE.md interdit et ne touche pas au noyau (`PROTECTED_PATHS.txt`).
Installés le 22/10/2026 à la demande d'Etienne.

## Nos méthodes (écrites pour le labo, libres : améliore-les)

| Skill | Quand |
|---|---|
| `enqueter` | début de chaque passage du chercheur ; un chiffre trop beau ou incohérent |
| `tester-une-piste` | toute idée de pari dont l'historique existe, avant l'arène |
| `nouvelle-strategie` | ajouter une stratégie, une variante ou une fille dans l'arène |
| `verifier-tableau-de-bord` | avant de pousser un changement du tableau de bord ; revue quotidienne |
| `evaluer-source-externe` | une idée, un bot, un dépôt ou un skill venu d'un tiers |

Ces fiches résument et renvoient aux documents de référence ; quand un document change, mets la fiche à jour.

## Repris d'ailleurs (lus en entier avant copie ; provenance dans le `SOURCE.md` de chacun)

| Skill | Source | Licence | Pourquoi |
|---|---|---|---|
| `systematic-debugging` | [obra/superpowers](https://github.com/obra/superpowers) v7.0.1 | MIT | chercher la cause avant de corriger (enquêtes) |
| `verification-before-completion` | obra/superpowers v7.0.1 | MIT | ne rien annoncer sans la sortie de la commande (interdit n° 6) |
| `test-driven-development` | obra/superpowers v7.0.1 | MIT | le test qui reproduit le cas réel d'abord |
| `statsmodels` | [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) | MIT | régression logistique, calibration, séries temporelles |
| `pymc` | K-Dense-AI/claude-scientific-skills | MIT | modèles hiérarchiques (petits échantillons par stratégie, par sport) |

Les bibliothèques de `statsmodels` et `pymc` (environ 650 Mo) vivent dans un environnement à part :
`requirements-recherche.txt` (vérifié sous Python 3.13 le 22/10/2026), jamais dans le cycle ni la CI.
Modifications : en-tête `allowed-tools` retiré (un skill n'accorde pas d'outils sans demande) ; la section
« Citing Scientific Agent Skills » ne s'applique pas (pas de publication).

## Écartés, et pourquoi
- **Skills Polymarket** ([mjunaidca/polymarket-skills](https://github.com/mjunaidca/polymarket-skills),
  [joinQuantish/skills](https://github.com/joinQuantish/skills)) : de vrais ordres avec une clé privée ou
  un portefeuille (interdit absolu n° 1), et pas de licence pour le premier. Leurs idées ont été jugées
  une à une : `experiments/skills_polymarket.md` (une seule nouvelle, la vague de volume, réécrite dans
  `strategies_v3.py`).
- **`writing-plans`** (Superpowers) : exige une relecture humaine et un choix de méthode d'exécution à
  chaque plan, ce qui bloquerait le chercheur autonome.

## Ajouter un skill
1. Licence libre (MIT, BSD, Apache) ; sans licence, on reprend l'idée, pas le texte.
2. Tout lire avant de copier, scripts compris ; rien qui place un ordre, touche un portefeuille, demande
   une clé ou un service payant.
3. `LICENSE` et `SOURCE.md` (dépôt, commit, ce qui est repris, ce qui ne l'est pas) dans le dossier du skill.
4. Bibliothèques lourdes : `requirements-recherche.txt`, jamais `requirements.txt`.
5. Une ligne dans ce fichier.
