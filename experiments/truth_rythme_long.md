# Posts de Trump : un rythme record ne dure pas (04/11/2026)

**Verdict : indice** → fantôme `compteur_truth_rythme_long_audace` (rythme des 12 dernières semaines, poids 0,8 ; dispersion 8 ; Kelly entier). Mère et champion inchangés.

## Déclencheur
Constat « à regarder » `estimation_perimee` du 04/11 : le 04/11 à 01 h 03 UTC, `compteur_tweets` (champion), `compteur_truth` et `compteur_tweets_48h_audace` ont acheté
« 200+ posts de Trump du 6 au 13/11 » à 0,724 sur une estimation de **0,968** (124 parts, 91 € pour le champion, 4 € copiés par le principal). Le marché est ensuite tombé à 0,58-0,60 (Gamma, 11 h).
`compteur_truth_dispersion_6_audace` (dispersion 6, fantôme du 02/11) a acheté le même billet sur 0,949 : **la dispersion seule ne règle pas le cas**.

## Cause
Pas un carnet périmé (niveaux 0,72 et 0,73 réels) : l'**estimation** prolonge le rythme. XTracker : 187 posts en 24 h, 676 en 7 jours (record de l'archive trumpstruth.org : 292 sur 39 semaines),
949 en 14 jours, 1 821 en 56 jours, 2 599 en 84 jours (217 par semaine). La formule de production (poids 0,5 sur 7 j, 0,5 sur 14 j) en tire 575 posts pour la semaine à venir.
Les 7 derniers jours sont ceux de l'élection du 03/11.

## Mesures (rien à regarder dans le futur)
Archive de 39 semaines, départs toutes les 12 h, log-score moyen des 11 tranches de la fenêtre de 7 jours, **mêmes 30 semaines** pour toutes les lignes
(`truth_social/scripts/dispersion_calibration.py` + variante à départ commun) :

| moment de la décision | production (7 j/14 j, d 12) | dispersion 6 | 12 semaines, poids récent 0,2, d 12 | idem d 8 |
|---|---|---|---|---|
| 220 h avant le début | −2,222 | −2,151 | **−2,023** | −2,023 |
| 54 h avant le début | −2,103 | −2,076 | **−1,972** | −1,984 |

Sur l'échantillon complet : à 220 h, production −2,565, rythme 4 semaines −2,19, **12 semaines −2,01 à −2,02**. Ramener la prévision de 50 % vers la moyenne longue (essai de lecture, moyenne ex post 184) donne −2,04 :
le défaut est bien le **retour à la moyenne**, pas la largeur de la loi.

**Contre le marché** (`truth_social/scripts/contre_marche_avant_fenetre.py`, nouveau : `LH`, `RW`, `MINJ`, `SORTIE` ; 72 événements, vrais échanges de la Data API v2, frais 5 %, marge 0,05, billets < 0,10 écartés, mêmes événements pour toutes les lignes) :

| réglage | paris | rendement | t par événement | z des prix | mois gagnants | verdict |
|---|---|---|---|---|---|---|
| production (336 h, 0,5, d 12) | 346 | +10,1 % | 1,46 | 2,06 | 5/8 | indice |
| production, d 6 | 302 | +26,9 % | 2,52 | 4,80 | 7/8 | retenue |
| 12 semaines, 0,2, d 12 | 291 | +20,3 % | 0,82 | 3,69 | 7/8 | indice |
| **12 semaines, 0,2, d 8** | 264 | +30,5 % | 1,78 | 4,49 | 7/8 | retenue |
| 12 semaines, 0,35, d 12 | 288 | +16,1 % | 0,54 | 2,70 | 6/8 | écartée |
| 12 semaines, 0, d 12 | 306 | +18,0 % | 0,71 | 3,18 | 6/8 | écartée |

6 réglages essayés (+ production) : **indice**, pas preuve. Contre le marché, la dispersion 6 de la mère fait aussi bien que le rythme long ; la différence tient au log-score (calibration), pas au rendement. Les décisions « avant la fenêtre » (S−2 j)
ne sont que 9 événements : le cas du jour (décision 9 jours avant le début, avant que le marché ne soit liquide) n'est PAS testable contre un prix.

## Ce qui reste incertain
Avec le rythme long, le billet du 04/11 aurait encore une estimation haute (0,84-0,90 : 308 posts attendus) parce que la semaine record (676) pèse 20 % et que le rythme des 12 semaines (217) est lui-même au-dessus de la médiane de l'archive (151).
Si la semaine d'élection est un **nouveau régime** (et non un pic), le marché à 0,59 se trompe ; si c'est un pic, la formule de production paie 0,72 une chance de ~0,6. Le règlement du 13/11 tranche ce cas (une seule observation).

## Ce qui a changé dans le code
- `references.fetch_tweet_trackings` : pour `realDonaldTrump` seulement (`LONG_RATE_DAYS`), relève 84 jours (un appel, 2 599 posts, 2,7 s) et ajoute `posts_long` / `heures_long` ; les autres comptes gardent 14 jours.
- `references.tweet_bucket_probability` : quand `long_hours` dépasse l'heure par heure gardée (336), le rythme long vient de `posts_long / heures_long`. Les stratégies existantes (`long_hours` ≤ 336) ne changent pas. Test : `test_trump_long_rate_is_read_over_twelve_weeks_and_pulls_a_burst_back` (échoue sans le correctif).
- Fantôme `compteur_truth_rythme_long_audace` (`config/strategies.yaml`), à comparer à `compteur_truth` et à `compteur_truth_dispersion_6_audace` sur la même période.

## Leçon si la perte arrive
La semaine record était un régime : le retour à la moyenne n'est pas le défaut, et le marché (0,59) avait tort. Dans ce cas, relever le poids du récent (0,5) et garder la dispersion 6.

## Contrôle à la main du même passage (famille 2)
60 règlements tirés au hasard parmi les 1 371 des 72 dernières heures (tous les fantômes + principal), relus sur Gamma `/markets/<id>` (`enquetes/scripts/reglements_au_hasard_04_11.py`) :
le paiement par part du journal est celui d'`outcomePrices` pour le même jeton, marché clos : **60 conformes, 0 écart**.
