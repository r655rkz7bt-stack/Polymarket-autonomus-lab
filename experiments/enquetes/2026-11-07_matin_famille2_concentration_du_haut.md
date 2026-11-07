# 07/11 (matin) : famille 2, le gain du haut du classement résiste-t-il ?

Script : `experiments/enquetes/scripts/concentration_top_31_10.py` (journaux signés publiés le 07/11 à 05 h 55 UTC).
Un événement = un tirage ; « attendus » = somme des prix payés.

| Stratégie | Paris / événements | Gain (par mise) | Sans les 3 plus gros | Sans le meilleur jour | Gagnés / attendus | z événements |
|---|---|---|---|---|---|---|
| compteur_truth | 11 / 3 | +219 € (+61,8 %) | +28 | +104 | 10,0 / 7,7 | +1,83 |
| naive_favorite | 119 / 84 | +216 € (+5,7 %) | +139 | +129 | 109,0 / 108,7 | +0,08 |
| nf_sport | 1 132 / 965 | +169 € (+0,5 %) | +85 | **−79** (2 nov. : +248) | 995,5 / 983,7 | +1,05 |
| compteur_tweets_48h_audace | 28 / 13 | +112 € (+11,4 %) | **+1** | +25 | 23,0 / 20,1 | +1,40 |
| nf_court_football_soir | 96 / 70 | +134 € (+1,4 %) | +39 | +41 | 88,0 / 85,4 | +0,85 |

**Lecture.** Aucun défaut de code. Tous les z sont sous 2 : variance, pas avantage prouvé.
`compteur_truth` = 3 événements, `compteur_tweets_48h_audace` = 3 paris font tout le gain, `nf_sport` perd sans son 2 novembre.
Les deux stratégies de comptage de posts lisent XTracker, en 403 depuis le 06/11 à 19 h UTC (toujours 403 ce matin) : leurs
nouveaux achats sont suspendus par le garde-fou « compteur pas à jour », donc ces gains n'augmentent plus.
Un essai avec un User-Agent de navigateur a été refusé (contournement d'une protection) et n'a pas été refait.
