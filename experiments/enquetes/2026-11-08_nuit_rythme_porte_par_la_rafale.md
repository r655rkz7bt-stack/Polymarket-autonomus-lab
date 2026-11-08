# 08/11/2026 (nuit) : « 200+ posts de Trump » estimé à 0,95, rythme porté par une rafale

**Constat automatique** : `compteur_tweets` v2 achète « Yes » estimé 0,950, payé 0,322, mise 60 € (180,9 parts), marché 6625358
(« 200+ Truth Social posts, 6-13/11 »), 07/11 22:17 UTC.

**Cause** (`references.tweet_bucket_probability`, famille 3, estimation périmée) : rythme = 0,5 × moyenne des 168 h + 0,5 × moyenne des 336 h =
**2,24 posts/h**, le plus haut de 3,5 ans de données (archive CNN, 37 987 posts depuis 02/2022), car les deux fenêtres contiennent la rafale du
28/10-03/11 (115 à 158 posts par jour). Depuis le 04/11 : 4 à 25 posts par jour ; 28 posts en 29 h dans la période. Rythmes : 24 h 1,04 ; 72 h 0,51 ; 84 j 1,24.
Le marché (0,295) était plus proche du vrai : cas analogues (rythme 0,95-1,4/h, compte bas à 24 h) : 3 finals sur 8 à ≥ 200.

**Chiffres du passé** (`experiments/regime_rafale/`, 130 périodes de 7 jours × 6 instants × 17 seuils) : le modèle de production est calibré en moyenne
(0,95 dit → 0,91 réel), mais quand son rythme dépasse 1,6 × la médiane de cinq rythmes (57 seuils) il dit 0,275 pour 0,175 réalisé
(log-perte 0,179, contre 0,056 pour la médiane). Ajouter le rythme observé DANS la période (poids h/(h+k), 9 réglages) est PIRE (0,150-0,231 contre 0,148) :
pas de piste de ce côté. « 7 j + 84 j » est un peu meilleur (0,142 ; −0,005 avant juillet 2025, −0,009 après) : non retenu seul (gain mince, autre portefeuille).
Au total 17 variantes de rythme essayées, une seule retenue (le contrôle de désaccord, hors échantillon non rejoué : seulement 57 seuils ≈ 6-8 périodes).

**Correctif** : `references.tweet_rates_disagree` + paramètre `desaccord_max` (1,6) dans les trois stratégies de compteur : abstention (raison
« rythmes en désaccord ») ; le contrôle se déclenche sur le cas réel (vérifié sur l'archive du 07/11). Test `test_rate_disagreement_after_a_burst_abstains`.
Il ne fait qu'enlever des achats : pas de nouvelle version de portefeuille.

**Limite honnête** : l'archive CNN rate ~25 % des posts en rafale ; le contrôle automatique `estimation_perimee` n'aurait pas expliqué la cause, mais l'a signalé (écart +0,06).
Un achat à 0,32 pour une vraie chance d'environ 0,25-0,30 coûte les frais, pas l'avantage : le risque était la mise (60 €, 6 % du fantôme) sur un faux 0,95.
