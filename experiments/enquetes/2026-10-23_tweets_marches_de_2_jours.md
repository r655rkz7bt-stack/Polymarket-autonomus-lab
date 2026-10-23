# 23/10/2026 : marchés de tweets de 2 jours, jamais testés, achetés par la famille `compteur_tweets`

**Constat** (relecture à la main de 36 marchés achetés par `compteur_tweets`, `_non`, `_non_patiente`, famille 3 « la donnée n'est pas celle qu'on croit ») :
Polymarket propose, en plus des marchés hebdomadaires (« du 16 au 23 octobre »), des marchés de **2 jours** (« Elon Musk post 40-64 tweets from October 19 to
October 21 », « du 22 au 24 »). Les 196 périodes du test sur le passé (`tweets_filles.md`, `tweets_prix_payes.md`) sont toutes hebdomadaires. Pourtant la famille a
acheté sur ces marchés courts : **19 achats sur 81, 246 € sur 1 190 € misés** (vérifié sur les journaux signés des trois fantômes, durée lue dans la question).
Exemple : `compteur_tweets_non_patiente`, 21/10 08:15, NON « 40-64 » (19-21/10) à 0,19, estimé 0,82 : décompte 55 à ce moment (76 à la fin), le modèle
(rythme de 7 + 14 jours) projette 18 % pour la tranche, le marché 81 % ; le NON a gagné, mais rien ne dit que le modèle est calibré sur 2 jours, où quelques
messages déplacent beaucoup la tranche. Écart de 0,62 entre estimation et prix payé = ce que le contrôle `estimation_perimee` signale (6 à 9 fois par fantôme).

**Cause** : `CompteurTweets.candidates` prend tout marché qui a un `tweets` rattaché (`references.py`, XTracker), quelle que soit la durée de la période.

**Correctif** : réglage `min_period_days` (`strategies_v3.CompteurTweets`, 0 = sans filtre, les stratégies existantes ne changent pas) et sœur
`compteur_tweets_non_hebdo` (NON sans NYC Mayor, périodes ≥ 5 jours) à comparer à sa mère `compteur_tweets_non` sur la même période.

**Test** : `tests/test_references.py::test_tweet_strategy_min_period_days_skips_two_day_markets`.

**Suite** : le test du même jour (`tweets_prix_payes.md`) écarte de toute façon l'avantage supposé de la famille aux prix payés ; la sœur ne sert qu'à lever le doute
sur les marchés de 2 jours en direct. Pas de contrôle automatique ajouté : le journal ne garde pas la durée de la période (à ajouter si la famille survit).
