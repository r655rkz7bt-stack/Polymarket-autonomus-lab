---
name: verifier-tableau-de-bord
description: Vérifier et améliorer le tableau de bord du labo (dashboard.py, dashboard_template.html, config/dashboard.yaml) - aperçu avec les dernières données publiées, photos téléphone et ordinateur, garde-fous de la règle n°1, textContent, contraste, débordements. À utiliser avant de pousser tout changement du tableau de bord, et pour la revue quotidienne demandée par docs/METHODE.md.
---

# Vérifier le tableau de bord

Référence : docs/TABLEAU_DE_BORD.md (méthode, garde-fous, évaluation de départ), qui prime en cas de désaccord.

## L'aperçu, avant de pousser
1. `.venv/bin/python scripts/apercu_dashboard.py` reconstruit la page avec les DERNIÈRES données publiées
   et le gabarit ACTUEL du dépôt, puis la photographie (390 px et 1 280 px) si Node, Playwright et Chromium
   sont là : `apercu/index.html`, `apercu/telephone.png`, `apercu/ordinateur.png`. Sans navigateur :
   `--sans-photo`.
2. Lis la sortie : erreurs JavaScript, débordements horizontaux, hauteur de chaque bloc.
3. Regarde vraiment les deux photos (outil de lecture d'image) : un test vert ne dit pas si la page est lisible.
4. Une partie qui s'ouvre au clic (fiche d'une stratégie de l'arène) : clique-la dans le navigateur
   (Playwright) et regarde la photo ; une fiche se calcule dans le navigateur à partir du journal public
   (`config/dashboard.yaml` → `journaux_url`).

## Garde-fous (non négociables)
- Capital, solde DISPONIBLE et état de faillite toujours visibles en haut (blocs `organisme`, `resume`,
  `capital` : le code refuse de les cacher).
- Les gains latents ne sont jamais présentés comme de l'argent disponible ; une estimation est marquée
  comme telle.
- Texte venu de l'extérieur (questions de marchés, articles) : `textContent`, jamais `innerHTML`
  (test « EVIL » de `tests/test_dashboard.py`).
- Couleurs : gris partout ; bleu pastel = hausse, rouge pastel = baisse, toujours avec ▲ ▼ (jamais la couleur seule).
- Lisible sur téléphone (390 px) : pas de débordement horizontal, contraste suffisant.
- Formules de la fiche alignées sur `arena.py` : `test_strategy_sheet_matches_the_python_figures` les
  compare (Node). Un nouvel onglet de la fiche (`VIEWS` dans `drawFiche`) garde cette parité.

## Améliorer
- Ordre des blocs, blocs cachés, encadré « À la une » : `config/dashboard.yaml`. Mets « À la une » à jour
  quand quelque chose d'important change (pour Etienne, en français simple).
- Pour un graphique : skill `dataviz` de Claude Code s'il est disponible (forme, couleurs vérifiées, survol, mode sombre).
- `.venv/bin/python -m pytest -q tests/test_dashboard.py` puis toute la suite avant de pousser.
