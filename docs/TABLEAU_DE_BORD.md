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
   - `replier` : les blocs repliés au départ (titre + une ligne de résumé ; Etienne les rouvre d'un
     toucher, son navigateur retient son choix) ;
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
  haut (blocs `organisme`, `resume` et `capital` : le code refuse de les cacher).
- **Couleurs** (17/10/2026) : gris partout ; bleu pastel `--blue` = hausse, rouge pastel `--red` = baisse, toujours
  avec ▲ ▼ (jamais la couleur seule). Contraste vérifié sur le fond des cartes (9,8:1 et 9,4:1).
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
| `entonnoir` (17/10) | — | forte | chaque mère et ses filles, comparaison équitable ; à garder près de l'arène |
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

## Refonte du 17/10/2026 (demande d'Etienne : « remets le cœur en haut, plus propre »)
- Le cœur (`organisme`) est en tête : capital total, variation depuis le départ, solde disponible
  et la phrase de situation au-dessus ; autour, des RÉSULTATS (capital, 24 h, gains réalisés et
  latents, arène, palier, positions, réussite, récompenses estimées, frais, rythme). Le système
  (sources, IA, pouls, terminal) est descendu dans `systeme`.
- Légendes en planche anatomique propre : ordinateur, deux colonnes rangées dans l'ordre vertical
  de leurs points ; téléphone, trois au-dessus et trois en dessous. Chaque trait part du centre
  d'un point du cœur (cercle bleu / rouge / blanc selon le sens), jamais d'entre deux points.
- Arène : chaque courbe (bleue au-dessus du départ, rouge en dessous) se dessine à son apparition,
  au survol et au toucher ; sur téléphone elle remplace la piste. Le classement dans le temps
  redessine la ligne survolée.

## Version compacte (17/10/2026, deuxième passage : « que ça prenne moins de place, plus résumé »)
- Ligne du haut : `dashboard.situation` écrit QUI pilote le capital principal, et sinon POURQUOI
  personne (champion destitué : par qui, quand, pourquoi ; et la stratégie la plus proche du seuil).
- Résumé = journal de phrases courtes (changements de champion, actions du chercheur), détail au
  toucher ; frais, perte maximale et audit en pastilles.
- Blocs repliables (`replier`), arène compacte (phrase sur deux lignes, détail au toucher, 6
  stratégies), « Aujourd'hui » à 2 phrases par sujet, entonnoir limité aux filles qui ont joué,
  positions du capital principal d'abord (celles de l'arène dans un dépliant).
- Téléphone : les tableaux deviennent des fiches empilées (aucune colonne coupée à droite).
- Hauteur de page (téléphone) : environ 19 300 px avant, 8 600 px après.
- Bloc `principal` (demande d'Etienne) : les ordres du capital PRINCIPAL, le vrai portefeuille, à
  part de ceux de l'arène, juste sous le résumé (liseré bleu) : exécutions du journal signé (la plus
  récente d'abord), ordres posés en attente, opérations clôturées (`dashboard.principal_orders`).
- Petits organes (18/10/2026, demande d'Etienne) : devant chaque titre, un organe en points dans
  le style du cœur (cerveau, noyau, poumons, ADN, cellule qui se divise, artère, cellules,
  neurone, colonne, œil, pouls, nerfs), choisi pour ce que fait le bloc (`organs()` dans le
  gabarit, table PICK). Points au repos qui scintillent ; une seule boucle d'animation, organes
  visibles seulement, image fixe si « moins d'animations ».
- Tissu de la page (18/10/2026, demande d'Etienne) : derrière les cartes, des points couvrent
  toute la place libre (marges, espaces entre les blocs) et scintillent au repos. Deux vaisseaux
  longent les marges, chaque bloc y a un point de contrôle (à hauteur de son titre) ; des influx
  voyagent d'un bloc à l'autre (par le vaisseau ou en traversant l'espace entre deux blocs) ; à
  l'arrivée, le point de contrôle s'illumine et le petit organe du bloc s'active (`field()`).
  Rien n'est dessiné sous les cartes ; 25 images/s au plus, arrêt onglet caché, image fixe si
  « moins d'animations ».
