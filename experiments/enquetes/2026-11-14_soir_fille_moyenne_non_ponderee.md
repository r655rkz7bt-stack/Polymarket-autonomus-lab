# 14/11/2026 (soir) : « fille +30,4 % contre sa mère −6,5 % », une moyenne qu'un pari de 3 € fabrique

**Famille 5 (comparaisons faussées)**, à partir du constat « à regarder » `filles_periode` du rapport publié à 20 h 52 UTC.
Script : `experiments/enquetes/scripts/fille_tweets_meme_evenement_14_11.py` (journaux signés `published_data/ledger/fantome_v2/`).

## Constat
Le rapport disait : `compteur_tweets_72_168h +30.4% contre sa mère compteur_tweets -6.5% depuis le 2026-11-07 (10 et 35 opérations)`.
Lu ainsi, le filtre « 72-168 h » de la fille vaudrait 37 points. Les journaux disent autre chose :

| | paris | mise | gain | pondéré par la mise | gagnés / attendus |
|---|---|---|---|---|---|
| fille `compteur_tweets_72_168h` | 10 (4 événements) | 329,0 € | −50,9 € | **−15,5 %** | 7 / 6,21 |
| mère, sur ces MÊMES 10 jetons | 10 | 327,6 € | −51,5 € | −15,7 % | 7 / 6,21 |
| mère, jetons écartés par le filtre (depuis le 07/11) | 21 (9 événements) | 235,9 € | −45,2 € | −19,2 % | 11 / 13,33 |

- La fille n'a fait AUCUN pari propre : ses 10 jetons sont 10 jetons de sa mère (même prix, même résultat, aucun sens opposé).
- Le « +30,4 % » est la moyenne NON pondérée des 10 rendements : un OUI de 3 € à 0,18 gagné (+367 %) la porte à lui seul ;
  le OUI de 60 € à 0,32 perdu (−100 %) et le NON de 46 € à 0,89 perdu y pèsent autant qu'un pari de 2 €.
- Même chose pour `compteur_truth` (mère déclarée : `compteur_tweets`) : −27,9 % en moyenne, −20,9 % pondéré, et la mère sur
  les mêmes 10 jetons : −20,9 % (identique au centime).

## Cause
`src/polymarket_agent/enquete.py`, `filles_periode` : `statistics.mean(_returns(...))`, moyenne simple des rendements par
opération, sans le rendement pondéré ni la seule comparaison qui juge un filtre (ce que le filtre a gardé contre ce qu'il a
écarté, chez la mère, sur la même période). La moyenne simple reste utile (c'est la mesure de l'arène depuis le 18/10 : elle
ne récompense pas les grosses mises chanceuses), mais à 10 paris de tailles 2 à 92 € elle est dominée par un billet.

## Ampleur
Aucun euro : aucune décision automatique ne lit ce contrôle (« à regarder »). Mais il aurait pu faire conclure qu'un filtre
marche (et pousser à en faire une fille, ou à couper la mère) alors que, sur les vrais journaux, **le filtre 72-168 h ne change
rien** : gardés −15,7 %, écartés −13,9 % (rendements pondérés, 10 et 25 opérations, rapport local après correctif).

## Correctif
`filles_periode` écrit maintenant aussi le rendement pondéré par la mise des deux, et, quand la fille joue les paris de sa mère
(au plus la moitié de ses paris absents de la mère), le résultat de la mère sur les jetons gardés par la fille contre les jetons
écartés. Rapport local après correctif :
`compteur_tweets_72_168h +30.4% contre sa mère compteur_tweets -6.5% ... ; pondéré par la mise -15.5% contre -14.9% ; chez la mère, jetons gardés par la fille -15.7% (10) contre écartés -13.9% (25)`.

## Test
`tests/test_enquete.py::test_daughter_mean_return_inflated_by_one_tiny_lottery_bet_is_put_in_perspective` : la fille rejoue
10 paris de sa mère dont un billet de 3 € à 0,18 gagné ; moyenne +37,9 %, pondéré −5,5 %, gardés −5,5 % contre écartés −100 %.

## Leçon
Une moyenne de rendements sur 10 paris de tailles très différentes se lit toujours à côté du rendement pondéré ; une fille
filtrée se juge sur « gardés contre écartés » chez la mère, jamais sur sa moyenne contre celle de la mère.
