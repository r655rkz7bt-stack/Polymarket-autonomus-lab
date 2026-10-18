# Vague d'opinion : un pic d'articles annonce-t-il le prochain mouvement du prix ? (test sur le passé, 18/10/2026)

**Verdict : non.** Sur 140 marchés longs (politique, géopolitique, monde, culture), un pic d'attention
médiatique n'annonce **pas** que le prix va continuer dans le même sens. En moyenne, il **revient un peu en
arrière** (environ −0,8 point à 24 h et −1,7 point à 72 h). Acheter « au début de la vague » perd
**−3,4 centimes par part** (−9 % de la mise) après l'écart et les frais. Parier sur le retour en arrière
(« contrer la vague ») perd aussi (−2,5 centimes par part, −4,6 %). Le petit retour en arrière est réel,
mais il est **plus petit que le coût d'un aller-retour** (environ 3 centimes par part).
Sur les 384 réglages essayés, **aucun** n'est gagnant.

Simulation uniquement : données passées, aucun ordre, aucune clé, aucune API payante.

## 1. Ce qu'on a testé

L'idée : sur un marché qui finit dans plus de 7 jours, quand on voit soudain beaucoup plus d'articles que
d'habitude sur le sujet, le prix bouge peut-être pendant les 6 à 72 heures suivantes. On achèterait au
début de la vague et on revendrait avant la fin du marché.

Pour chaque marché et chaque heure *t* du 15/09 au 15/10/2026, on regarde seulement **ce qui s'est passé
avant *t*** (aucun regard vers le futur) :

- **pic d'attention** = articles des 3 dernières heures ÷ nombre moyen d'articles par tranche de 3 h sur
  les 7 jours d'avant. Signal si pic ≥ 2 **et** au moins 5 articles en 3 h ;
- **sens** = sens de la dérive du prix sur les 6 dernières heures, seulement si elle vaut entre 0,02 et
  0,08 (2 à 8 points) ;
- au plus **1 signal par marché toutes les 24 h** ; prix YES entre 0,05 et 0,95 ; au moins un échange
  dans les 3 dernières heures ; fin annoncée du marché au moins 7 jours après *t*.

Ensuite on mesure le mouvement du prix dans le sens du signal à +6 h, +24 h et +72 h. On simule aussi une
transaction : achat à *t* au dernier prix + 0,01 (demi-écart), revente au dernier prix − 0,01 dès que le
prix gagne 0,05 (objectif), perd 0,05 (stop), ou au bout de 120 h. Les frais preneur sont payés **à
l'achat et à la vente**.

Contrôles :
- **B** : mêmes dérives, mais heures **sans** vague (pic < 1,2) → est-ce que l'attention apporte quelque
  chose de plus que la simple tendance ?
- **C** : mêmes signaux que A, mais on parie dans le sens **opposé** (« contrer la vague ») ;
- **D** : B en sens opposé ; **E** : toutes les dérives, sans regarder l'attention.

## 2. Les données

| Élément | Valeur |
|---|---|
| Marchés candidats (Gamma, étiquettes Politique, Géopolitique, Monde, Culture ; volume ≥ 100 000 $) | 1 388 |
| Marchés oui/non, fin ≥ 22/09, ouverts pendant la période | 1 009 |
| **Marchés retenus** (≥ 300 échanges et ≥ 20 000 $ échangés du 15/09 au 15/10 ; max 4 par événement ; 3 marchés écartés car sans lien avec l'actualité : 2 « nombre de tweets d'Elon Musk » et « retour de Jésus ») | **140** |
| Marchés avec au moins une heure exploitable et une mesure d'attention | 120 |
| Sujets distincts (requêtes de mots-clés) | 91 |
| Heures « marché × heure » exploitables | 48 645 |
| Fichiers d'articles GDELT lus (un toutes les 15 min, 07/09 → 15/10) | 3 648 sur 3 648 (aucun trou) |
| Articles (en anglais) suivis par GDELT, médiane par heure | ≈ 3 770 |

**Prix** : uniquement des échanges **réellement exécutés** (data-api Polymarket `/trades`, du 13/09 au
21/10). Pas l'historique à 10 minutes. Un échange sur le NON au prix *p* est compté comme un prix OUI de
1 − *p*.

**Frais** (lus dans Gamma, frais par part = taux × p × (1 − p) à chaque jambe) : 62 marchés sans frais
(`feesEnabled = false`), 71 marchés à 0,04 (`politics_fees`), 5 à 0,05 (`culture_fees`), 2 à 0,04
(`finance_prices_fees`). En moyenne ≈ 0,9 centime de frais par part sur l'aller-retour, plus 2 centimes
d'écart.

**Attention médiatique** : on voulait l'API GDELT DOC (comptage d'articles par mot-clé). Elle a répondu
« trop de requêtes » (HTTP 429) à presque toutes nos demandes, même espacées de 25 à 60 secondes
(adresse internet partagée) : environ 1 réponse toutes les 5 minutes, il aurait fallu ~45 heures. On a
donc utilisé la **même source GDELT sous forme de fichiers publics** (« GKG », gratuits, prévus pour
le téléchargement) : une ligne par article, avec son titre, son adresse, les personnes, organisations et
lieux cités. On compte nous-mêmes les articles qui correspondent aux mots-clés du marché, heure par heure.
Les mots-clés (2 à 3 mots, souvent des noms : « Paxton », « "Kharg Island" », « Iran blockade »…) ont été
relus à la main ; ils sont dans `marches.json`.

## 3. Résultats principaux

Mouvement = variation du prix dans le sens parié, en points de probabilité (0,01 = 1 point).
« Gain net » = par part achetée, après écart et frais. IC 95 % = intervalle de confiance, calculé en
tirant au sort des **sujets** entiers (les signaux d'un même sujet se ressemblent).

| Groupe | Signaux (marchés) | Mouv. 6 h | Mouv. 24 h | Mouv. 72 h | Gagnants | Gain net / part | Rendement / mise |
|---|---|---|---|---|---|---|---|
| **A. Vague + suivre** (l'idée testée) | 242 (83) | −0,70 | −0,83 | **−1,69** | 31 % | **−3,4 cts** [−4,1 ; −2,8] | **−9,1 %** [−12,9 ; −5,9] |
| B. Sans vague + suivre | 853 (109) | −0,59 | −0,46 | −0,13 | 31 % | −3,3 cts | −10,2 % |
| C. Vague + contrer | 242 (83) | +0,70 | +0,83 | +1,69 | 39 % | −2,5 cts [−3,3 ; −1,7] | −4,6 % [−6,8 ; −2,5] |
| D. Sans vague + contrer | 853 (109) | +0,59 | +0,46 | +0,13 | 41 % | −2,4 cts | −5,7 % |
| E. Toute dérive + suivre | 975 (112) | −0,67 | −0,57 | −0,45 | 31 % | −3,3 cts | −10,4 % |

Intervalles du mouvement pour A : à 24 h [−1,61 ; −0,08] point, à 72 h [−3,52 ; −0,23] point
(clairement négatif). Pour B à 72 h : [−0,81 ; +0,84] (rien).

Ce que ça veut dire, simplement :
1. **Suivre la tendance ne marche pas, avec ou sans vague.** Après une dérive de 2 à 8 points en 6 h, le
   prix a plutôt tendance à revenir un peu en arrière dans les heures qui suivent.
2. **L'attention ajoute quelque chose, mais dans le mauvais sens pour l'idée** : avec une vague, le retour
   en arrière dure plus longtemps (−1,7 point à 72 h contre −0,1 sans vague). Ça ressemble à une
   **sur-réaction** : la nouvelle fait bouger le prix trop loin, puis il se corrige.
3. **Les vagues annoncent surtout de l'agitation.** Aux heures avec pic (5 592 heures), le prix bouge
   ensuite en valeur absolue de 2,25 points en 24 h, contre 1,70 point aux heures calmes (36 787 heures),
   soit **+32 %** de mouvement. Mais l'agitation ne dit pas dans quel sens.
4. **Le coût tue tout.** Un aller-retour coûte environ 3 centimes par part (2 d'écart + ~0,9 de frais).
   Même sans aucun coût, suivre la vague perd (−0,5 ct par part) ; contrer la vague gagnerait à peine
   +0,5 ct par part (intervalle [−0,2 ; +1,2], donc pas sûr) avant de payer 3 centimes.

Sorties des transactions A : 71 objectifs, 85 stops, 86 fins de délai ; durée moyenne 67 h.
Au moment des signaux A, le pic vaut 3,5 en médiane, avec environ 24 articles en 3 h (médiane).

## 4. Stabilité (première moitié contre deuxième moitié)

| Groupe | 15/09 → 29/09 | 30/09 → 14/10 |
|---|---|---|
| A. Vague + suivre | 154 signaux, mouv. 72 h −2,26 pts, rendement −7,9 %, 34 % gagnants | 88 signaux, mouv. 72 h −0,70 pt, rendement −11,1 %, 25 % gagnants |
| B. Sans vague + suivre | rendement −10,7 % | rendement −9,2 % |
| C. Vague + contrer | rendement −5,0 %, 42 % gagnants | rendement −3,9 %, 34 % gagnants |

Les deux moitiés disent la même chose : suivre perd, contrer perd moins, personne ne gagne. Le retour en
arrière après une vague est plus net dans la première moitié (2,3 points) que dans la deuxième (0,7).

## 5. Vérifications de solidité

- **Prix = médiane des échanges de l'heure précédente** (au lieu du dernier échange, pour éviter le
  va-et-vient entre prix acheteur et vendeur) : mêmes conclusions. A : −0,67 pt à 24 h, −1,74 pt à
  72 h, rendement −9,7 % ; C : −4,3 % ; B : −10,8 %.
- **Écart plus large** (demi-écart 0,02 au lieu de 0,01) : A tombe à −14,4 %.
- **Grille de 384 réglages** (pic ≥ 1,5 / 2 / 3 / 5 ; dérive 0,02–0,08 / 0,02–0,05 / 0,04–0,08 /
  0,02–0,15 ; objectif/stop 0,05/0,05, 0,03/0,03, 0,08/0,05, 0,10/0,10 ; durée max 24 / 72 / 120 h ;
  suivre ou contrer) : **0 % des réglages sont gagnants** (parmi ceux avec ≥ 20 signaux). Le « moins
  mauvais » : contrer, pic ≥ 1,5, dérive 0,04–0,08, objectif 0,10 / stop 0,10, 72 h → **−0,8 % par
  transaction** (94 signaux, 49 marchés), pareil dans les deux moitiés. Ce meilleur réglage est choisi
  après coup parmi 384 : il est forcément trop optimiste.
- **Marchés sans frais seulement** (choisi après coup, à prendre avec prudence) : contrer la vague perd
  −1,2 ct par part (−1,5 %, 46 % gagnants, 96 signaux) ; sur les marchés avec frais : −3,3 cts (−6,6 %).
- **Recoupement avec l'API GDELT DOC** (seulement 3 semaines du sujet « Lula Brazil » ont pu être
  téléchargées) : corrélation heure par heure de 0,82 la 1re semaine, 0,31 la 3e, et 0,03 la 2e semaine,
  où l'API DOC avait un trou (15 articles contre 158 dans les fichiers). Les fichiers GKG semblent donc
  plus complets que l'API pour cette période.

## 6. Limites honnêtes

- **Mots-clés imparfaits** : « Trump », « Putin » ou « Iran » ramènent beaucoup d'articles hors sujet ;
  à l'inverse « Renan Santos » ou « Puma Shen » n'en ramènent presque aucun. Un pic peut donc venir d'une
  autre actualité que celle du marché.
- **Couverture** : seulement les articles en **anglais** suivis par GDELT, et on cherche dans le titre,
  l'adresse et les noms cités, pas dans tout le texte. Les élections au Brésil, en Russie, à Taïwan sont
  surtout couvertes dans d'autres langues → sous-estimées.
- **Petit échantillon et sujets liés** : 242 signaux, mais seulement 60 sujets ; plusieurs marchés
  parlent de la même chose (4 marchés « blocus iranien », 4 « Hormuz »…) et bougent ensemble.
  Une seule période (un mois), dominée par la crise Iran / Hormuz et les élections au Brésil et aux
  États-Unis.
- **Exécution approchée** : on achète au dernier prix échangé + 0,01 et on revend au dernier prix − 0,01.
  Le vrai carnet pouvait être plus mince ; un seul échange suffit à déclencher l'objectif ou le stop, ce
  qui est un peu optimiste pour l'objectif.
- **Fin de marché** : pour les marchés réglés avant 120 h, on revend au dernier échange avant la clôture.

## 7. Conclusion et réglages conseillés

**Ne pas mettre en place la stratégie « suivre la vague d'opinion ».** Elle perd dans tous les cas testés,
et l'attention médiatique ne prédit pas le sens du mouvement : elle prédit seulement **plus d'agitation**,
avec un léger **retour en arrière** après les fortes dérives.

Si on veut quand même la garder en observation dans l'arène (sans argent engagé au-delà de petites
mises de simulation), les réglages les moins mauvais trouvés sont :

| Paramètre | Valeur conseillée |
|---|---|
| sens | **contrer** la dérive (pas la suivre) |
| seuil de pic (`spike`) | ≥ 3 (au moins 5 articles en 3 h) — plus strict que 2, moins de faux pics |
| dérive sur 6 h (`max_move`) | entre 0,04 et 0,08 |
| objectif (`take_profit`) | +0,10 |
| stop | −0,10 |
| durée max (`max_hold`) | 72 h |
| marchés | sans frais de préférence ; fin ≥ 7 jours |

Même avec ces réglages, le résultat attendu sur le passé reste **légèrement négatif** (−0,8 % à −2 % par
transaction). Une piste plus prometteuse serait d'utiliser la vague comme **alarme d'agitation** (par
exemple pour retirer ou écarter ses ordres) plutôt que comme signal d'achat.

## 8. Refaire le test

```
.venv/bin/python -I experiments/vague_opinion/vague_opinion.py            # tout (select, gkg, analyse)
.venv/bin/python -I experiments/vague_opinion/vague_opinion.py analyse    # seulement l'analyse (cache)
```

Fichiers : `vague_opinion.py` (script), `marches.json` (marchés retenus, frais, mots-clés),
`resultats.json` (tous les chiffres), `signaux.csv` (chaque signal A et C avec sa transaction simulée).
Les téléchargements (≈ 600 Mo) sont gardés dans `cache/` (ignoré par Git) : relancer ne retélécharge rien.
