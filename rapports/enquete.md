# Enquête automatique — 2026-10-24T15:37+00:00

Défauts possibles trouvés dans les journaux publiés (enquete.py). « grave » = obligation de la feuille de mission ; « à regarder » = piste pour l'enquête manuelle (docs/ROUTINE_CHERCHEUR.md).

## [grave] nf_sport_patiente_biais_faible_v1.0.0 (copiée par le principal) : 26 gagnés pour 27.5 attendus sur ses 30 dernières opérations, rendement -5.7%

*Contrôle `champion_sans_avantage`* — Plus d'avantage mesurable récemment : chercher d'où venait le gain (jour, sport, prix, mode d'achat) et si ses règles d'entrée au capital doivent changer.


## [grave] nf_sport_patiente_v1.0.0 (copiée par le principal) : 25 gagnés pour 26.4 attendus sur ses 30 dernières opérations, rendement -5.5%

*Contrôle `champion_sans_avantage`* — Plus d'avantage mesurable récemment : chercher d'où venait le gain (jour, sport, prix, mode d'achat) et si ses règles d'entrée au capital doivent changer.


## [grave] nf_sport_patiente_6_24h_v1.0.0 : 3 paris font 90% du gain (+80 €)

*Contrôle `chance`* — Résultat fragile : retirer ces 3 paris et regarder ce qui reste.

- 2026-10-23T15:22 « UConn » +25 €
- 2026-10-20T12:30 « Under » +24 €
- 2026-10-19T17:34 « 49ers » +23 €

## [grave] nf_sport_patiente_v1.0.0 : 3 paris font 213% du gain (+64 €)

*Contrôle `chance`* — Résultat fragile : retirer ces 3 paris et regarder ce qui reste.

- 2026-10-20T07:09 « Moyuka Uchijima » +61 €
- 2026-10-22T15:56 « Taylor Fritz » +37 €
- 2026-10-22T14:05 « Alex Michelsen » +37 €

## [grave] nf_sport_patiente_v1.0.0 : le 2026-10-18 fait 381% du gain (+64 €)

*Contrôle `chance`* — Avantage concentré sur une journée : vérifier qu'il existe encore les autres jours.

- 2026-10-17 : -72 €
- 2026-10-18 : +242 €
- 2026-10-19 : +16 €
- 2026-10-20 : +145 €
- 2026-10-21 : -230 €
- 2026-10-22 : -5 €
- 2026-10-23 : +37 €
- 2026-10-24 : -71 €

## [à regarder] 1 ordre(s) posé(s) copié(s) servi(s) au principal avant le fantôme

*Contrôle `copie_fidele`* — Le principal passe après les fantômes dans le cycle et relit le carnet : son exemplaire de l'ordre posé peut être servi une minute avant celui du fantôme, qui est servi (ou remplacé) au cycle suivant. Même pari, exécution décalée (23/10/2026, contrer_crypto_patiente, 0,36 €) : à surveiller seulement si les montants grossissent.

- 2026-10-23T04:01 contrer_crypto_patiente « Yes » 5.07 parts à 0.072

## [à regarder] 27 mise(s) de fantôme au-dessus de 25% de leur capital

*Contrôle `mises`* — Kelly complet sur une estimation trop optimiste : une seule mise fait le résultat (chance, pas avantage). Regarder l'estimation de ces paris.

- 2026-10-22T05:12 nf_court_prix_haut_v1.0.0 « Yes » 489 € = 53% du capital
- 2026-10-21T16:16 nf_court_prix_haut_v1.0.0 « No » 498 € = 48% du capital
- 2026-10-22T14:05 nf_sport_patiente_v1.0.0 « Alex Michelsen » 475 € = 45% du capital
- 2026-10-21T21:26 nf_sport_non_v1.0.0 « No » 317 € = 30% du capital
- 2026-10-21T21:26 nf_court_prix_haut_v1.0.0 « No » 337 € = 30% du capital
- 2026-10-22T20:00 nf_sport_patiente_v1.0.0 « No » 359 € = 30% du capital
- 2026-10-21T21:26 nf_sport_prix_haut_v1.0.0 « No » 317 € = 28% du capital
- 2026-10-22T16:28 nf_sport_patiente_v1.0.0 « UNiTY esports » 321 € = 28% du capital

## [à regarder] compteur_tweets_non_v1.0.0 : 1 achat(s) estimés 11% au-dessus de l'écart habituel (+0.037)

*Contrôle `estimation_perimee`* — L'estimation ne correspond pas au prix payé : carnet périmé (le prix a bougé pendant le cycle), mauvais marché rattaché, ou modèle qui s'emballe. La mise, calculée sur cette estimation, est trop grosse.

- 2026-10-23T15:27 « No » estimé 0.809, payé 0.100, mise 8 €

## [à regarder] compteur_tweets_v1.0.0 : 1 achat(s) estimés 20% au-dessus de l'écart habituel (+0.038)

*Contrôle `estimation_perimee`* — L'estimation ne correspond pas au prix payé : carnet périmé (le prix a bougé pendant le cycle), mauvais marché rattaché, ou modèle qui s'emballe. La mise, calculée sur cette estimation, est trop grosse.

- 2026-10-23T15:27 « No » estimé 0.809, payé 0.100, mise 8 €

## [à regarder] mots_prononces_v1.0.0 : +38 € mais rendement par mise -9.4%

*Contrôle `chance`* — Le gain vient de la taille des mises, pas d'un avantage (12 gagnés pour 14.0 attendus par les prix).


## [à regarder] mots_prononces_v1.0.0 : 3 paris font 276% du gain (+38 €)

*Contrôle `chance`* — Résultat fragile : retirer ces 3 paris et regarder ce qui reste.

- 2026-10-21T16:51 « No » +43 €
- 2026-10-22T07:03 « Yes » +32 €
- 2026-10-22T17:27 « No » +30 €

## [à regarder] mots_prononces_v1.0.0 : le 2026-10-22 fait 104% du gain (+38 €)

*Contrôle `chance`* — Avantage concentré sur une journée : vérifier qu'il existe encore les autres jours.

- 2026-10-20 : -3 €
- 2026-10-21 : +11 €
- 2026-10-22 : +40 €
- 2026-10-23 : -9 €

## [à regarder] naive_favorite_v1.0.0 : +118 € mais rendement par mise -2.1%

*Contrôle `chance`* — Le gain vient de la taille des mises, pas d'un avantage (18 gagnés pour 18.4 attendus par les prix).


## [à regarder] nf_court_v1.0.0 : +109 € mais rendement par mise -1.8%

*Contrôle `chance`* — Le gain vient de la taille des mises, pas d'un avantage (122 gagnés pour 124.0 attendus par les prix).


## [à regarder] nf_court_v1.0.0 : le 2026-10-16 fait 85% du gain (+109 €)

*Contrôle `chance`* — Avantage concentré sur une journée : vérifier qu'il existe encore les autres jours.

- 2026-10-16 : +93 €
- 2026-10-17 : +27 €
- 2026-10-18 : +33 €
- 2026-10-19 : +39 €
- 2026-10-20 : -107 €
- 2026-10-21 : +24 €
- 2026-10-22 : +13 €
- 2026-10-23 : +31 €

## [à regarder] nf_sport_non_v1.0.0 : 3 paris font 118% du gain (+70 €)

*Contrôle `chance`* — Résultat fragile : retirer ces 3 paris et regarder ce qui reste.

- 2026-10-21T21:26 « No » +30 €
- 2026-10-21T21:32 « No » +29 €
- 2026-10-23T21:02 « No » +24 €

## [à regarder] nf_sport_non_v1.0.0 : le 2026-10-23 fait 108% du gain (+70 €)

*Contrôle `chance`* — Avantage concentré sur une journée : vérifier qu'il existe encore les autres jours.

- 2026-10-18 : -15 €
- 2026-10-19 : +37 €
- 2026-10-20 : -127 €
- 2026-10-21 : +73 €
- 2026-10-22 : +10 €
- 2026-10-23 : +75 €
- 2026-10-24 : +17 €

## [à regarder] nf_sport_patiente_2crans_v1.0.0 : 3 paris font 175% du gain (+31 €)

*Contrôle `chance`* — Résultat fragile : retirer ces 3 paris et regarder ce qui reste.

- 2026-10-19T10:39 « Yellow Submarine » +18 €
- 2026-10-21T02:39 « Miguel Tobon » +18 €
- 2026-10-19T12:39 « Carlos Taberner » +18 €

## [à regarder] nf_sport_patiente_2crans_v1.0.0 : le 2026-10-19 fait 247% du gain (+31 €)

*Contrôle `chance`* — Avantage concentré sur une journée : vérifier qu'il existe encore les autres jours.

- 2026-10-19 : +77 €
- 2026-10-20 : -75 €
- 2026-10-21 : +29 €

## [à regarder] nf_sport_prix_haut_v1.0.0 : 3 paris font 86% du gain (+92 €)

*Contrôle `chance`* — Résultat fragile : retirer ces 3 paris et regarder ce qui reste.

- 2026-10-21T21:32 « Team Yandex » +31 €
- 2026-10-21T21:26 « No » +30 €
- 2026-10-18T13:09 « Aurora Gaming » +17 €

## [à regarder] nf_sport_prix_haut_v1.0.0 : le 2026-10-18 fait 147% du gain (+92 €)

*Contrôle `chance`* — Avantage concentré sur une journée : vérifier qu'il existe encore les autres jours.

- 2026-10-17 : -21 €
- 2026-10-18 : +135 €
- 2026-10-19 : +26 €
- 2026-10-20 : -53 €
- 2026-10-21 : +75 €
- 2026-10-22 : -44 €
- 2026-10-23 : +21 €
- 2026-10-24 : -47 €

## [à regarder] nf_sport_sans_fin_v1.0.0 : +34 € mais rendement par mise -9.0%

*Contrôle `chance`* — Le gain vient de la taille des mises, pas d'un avantage (13 gagnés pour 14.2 attendus par les prix).


## [à regarder] nf_sport_sans_fin_v1.0.0 : le 2026-10-17 fait 294% du gain (+34 €)

*Contrôle `chance`* — Avantage concentré sur une journée : vérifier qu'il existe encore les autres jours.

- 2026-10-17 : +100 €
- 2026-10-20 : -67 €
- 2026-10-21 : +1 €

## [à regarder] nf_sport_925_950_v1.0.0 : z = +0.65 sur 30 paris, mais choisie parmi 80 stratégies

*Contrôle `selection_multiple`* — P(hasard) corrigée = 1.00 (> 0.05) : le meilleur z de l'arène est +1.78, ce que 80 stratégies sans avantage donnent déjà. Ne pas confondre « première du classement » et « avantage prouvé » : confirmer sur de nouveaux paris (ou un test sur le passé).


## [à regarder] nf_sport_patiente_6_24h_v1.0.0 : z = +0.72 sur 23 paris, mais choisie parmi 80 stratégies

*Contrôle `selection_multiple`* — P(hasard) corrigée = 1.00 (> 0.05) : le meilleur z de l'arène est +1.78, ce que 80 stratégies sans avantage donnent déjà. Ne pas confondre « première du classement » et « avantage prouvé » : confirmer sur de nouveaux paris (ou un test sur le passé).


## [à regarder] nf_sport_patiente_biais_faible_v1.0.0 : z = -0.56 sur 48 paris, mais choisie parmi 80 stratégies

*Contrôle `selection_multiple`* — P(hasard) corrigée = 1.00 (> 0.05) : le meilleur z de l'arène est +1.78, ce que 80 stratégies sans avantage donnent déjà. Ne pas confondre « première du classement » et « avantage prouvé » : confirmer sur de nouveaux paris (ou un test sur le passé).


## [à regarder] nf_sport_patiente_v1.0.0 : z = +0.81 sur 168 paris, mais choisie parmi 80 stratégies

*Contrôle `selection_multiple`* — P(hasard) corrigée = 1.00 (> 0.05) : le meilleur z de l'arène est +1.78, ce que 80 stratégies sans avantage donnent déjà. Ne pas confondre « première du classement » et « avantage prouvé » : confirmer sur de nouveaux paris (ou un test sur le passé).


## [à regarder] nf_tennis_12_18h_vainqueur_v1.0.0 : z = +0.90 sur 58 paris, mais choisie parmi 80 stratégies

*Contrôle `selection_multiple`* — P(hasard) corrigée = 1.00 (> 0.05) : le meilleur z de l'arène est +1.78, ce que 80 stratégies sans avantage donnent déjà. Ne pas confondre « première du classement » et « avantage prouvé » : confirmer sur de nouveaux paris (ou un test sur le passé).


## [à regarder] arène : 1878 paris distincts, 1279 gagnés pour 1432.5 annoncés par les estimations (1321.4 par les prix payés), z = -10.8

*Contrôle `estimation_gonflee`* — Les probabilités des stratégies sont trop hautes : l'avantage annoncé n'existe pas et sert de base à la mise (Kelly). Regarder le paramètre `bias`/`shrink` de la stratégie et la mise par tranche de prix.


## [à regarder] arène : 24 paris promis à plus de 0.995 pour 0.978 en moyenne, -155 € pour 1748 € misés

*Contrôle `certitude_promise`* — Une estimation collée au plafond promet un gain de quelques points sur un favori déjà quasi sûr : le Kelly y mise le maximum autorisé. Regarder comment l'estimation est construite (prix + bonus ? plafond 0,999 ?) et ce que rapportent ces paris.

- nm_demi_mise v1.0.0 : 2 paris, -194 € pour 212 € misés
- nm_prix_haut v1.0.0 : 1 paris, +0 € pour 7 € misés
- nm_hors_crypto v1.0.0 : 7 paris, +2 € pour 154 € misés
- nm_court v1.0.0 : 3 paris, +6 € pour 308 € misés
- news_momentum v1.0.0 : 8 paris, +15 € pour 585 € misés
- nm_crypto v1.0.0 : 3 paris, +16 € pour 481 € misés

## [à regarder] nf_sport_patiente_tennis_875_900_v1.0.0 : 1 marché(s) dont les deux camps sont achetés (185 € misés)

*Contrôle `deux_camps`* — Le deuxième achat suit l'effondrement du premier favori : regarder si la stratégie doit refuser le camp opposé d'une position ouverte ou fermée.

- 2026-10-22T07:21 « Belinda Bencic » 83 € ↔ 2026-10-22T08:25 « Katarzyna Kawa » 102 €

## [à regarder] nf_tennis_prix_bas_800_850_v1.0.0 : 1 marché(s) dont les deux camps sont achetés (79 € misés)

*Contrôle `deux_camps`* — Le deuxième achat suit l'effondrement du premier favori : regarder si la stratégie doit refuser le camp opposé d'une position ouverte ou fermée.

- 2026-10-22T12:51 « Tereza Krejcova » 35 € ↔ 2026-10-22T13:52 « Pavla Sviglerova » 44 €

## [à regarder] nf_tennis_prix_bas_v1.0.0 : 1 marché(s) dont les deux camps sont achetés (206 € misés)

*Contrôle `deux_camps`* — Le deuxième achat suit l'effondrement du premier favori : regarder si la stratégie doit refuser le camp opposé d'une position ouverte ou fermée.

- 2026-10-22T04:32 « Mary Stoiana » 85 € ↔ 2026-10-22T05:46 « Moyuka Uchijima » 120 €

## [à regarder] nf_tennis_prix_bas_vainqueur_v1.0.0 : 1 marché(s) dont les deux camps sont achetés (86 € misés)

*Contrôle `deux_camps`* — Le deuxième achat suit l'effondrement du premier favori : regarder si la stratégie doit refuser le camp opposé d'une position ouverte ou fermée.

- 2026-10-22T04:32 « Mary Stoiana » 35 € ↔ 2026-10-22T05:46 « Moyuka Uchijima » 51 €

## [à regarder] nf_tennis_vainqueur_v1.0.0 : 1 marché(s) dont les deux camps sont achetés (63 € misés)

*Contrôle `deux_camps`* — Le deuxième achat suit l'effondrement du premier favori : regarder si la stratégie doit refuser le camp opposé d'une position ouverte ou fermée.

- 2026-10-22T04:32 « Mary Stoiana » 23 € ↔ 2026-10-22T05:46 « Moyuka Uchijima » 39 €

## [à regarder] apres_echeance_v1.0.0 : 2 événement(s) joué(s) par 3 marchés ou plus

*Contrôle `jambes_meme_evenement`* — Les marchés d'un même match (vainqueur, écarts, totaux) tombent ensemble : une seule perte fait perdre toutes les jambes. Limiter la stratégie à un pari par événement.

- 2026-10-23T00:02 événement 1197295 : 9 marchés, 524 €
- 2026-10-23T01:56 événement 1178188 : 3 marchés, 121 €

## [à regarder] detroits_marche_log_v1.0.0 : 2 événement(s) joué(s) par 3 marchés ou plus

*Contrôle `jambes_meme_evenement`* — Les marchés d'un même match (vainqueur, écarts, totaux) tombent ensemble : une seule perte fait perdre toutes les jambes. Limiter la stratégie à un pari par événement.

- 2026-10-23T18:57 événement 1236991 : 4 marchés, 140 €
- 2026-10-23T19:03 événement 1236985 : 3 marchés, 169 €

## [à regarder] nf_court_football_soir_v1.0.0 : 1 événement(s) joué(s) par 3 marchés ou plus

*Contrôle `jambes_meme_evenement`* — Les marchés d'un même match (vainqueur, écarts, totaux) tombent ensemble : une seule perte fait perdre toutes les jambes. Limiter la stratégie à un pari par événement.

- 2026-10-21T19:41 événement 1160473 : 3 marchés, 124 €

## [à regarder] nf_court_football_v1.0.0 : 1 événement(s) joué(s) par 3 marchés ou plus

*Contrôle `jambes_meme_evenement`* — Les marchés d'un même match (vainqueur, écarts, totaux) tombent ensemble : une seule perte fait perdre toutes les jambes. Limiter la stratégie à un pari par événement.

- 2026-10-21T21:02 événement 1160473 : 3 marchés, 158 €

## [à regarder] nf_court_prix_haut_v1.0.0 : 1 événement(s) joué(s) par 3 marchés ou plus

*Contrôle `jambes_meme_evenement`* — Les marchés d'un même match (vainqueur, écarts, totaux) tombent ensemble : une seule perte fait perdre toutes les jambes. Limiter la stratégie à un pari par événement.

- 2026-10-22T23:16 événement 1159506 : 3 marchés, 188 €

## [à regarder] nf_court_soir_v1.0.0 : 1 événement(s) joué(s) par 3 marchés ou plus

*Contrôle `jambes_meme_evenement`* — Les marchés d'un même match (vainqueur, écarts, totaux) tombent ensemble : une seule perte fait perdre toutes les jambes. Limiter la stratégie à un pari par événement.

- 2026-10-22T23:16 événement 1159506 : 3 marchés, 277 €

## [à regarder] nf_sport_prix_haut_3_6h_v1.0.0 : 3 événement(s) joué(s) par 3 marchés ou plus

*Contrôle `jambes_meme_evenement`* — Les marchés d'un même match (vainqueur, écarts, totaux) tombent ensemble : une seule perte fait perdre toutes les jambes. Limiter la stratégie à un pari par événement.

- 2026-10-22T11:02 événement 1203866 : 3 marchés, 190 €
- 2026-10-22T18:32 événement 1159506 : 3 marchés, 141 €
- 2026-10-23T12:57 événement 1161730 : 3 marchés, 427 €

## [à regarder] nf_sport_patiente_biais_faible_v1.0.0 : 44 achats sur 55 faits après le coup d'envoi

*Contrôle `achats_en_jeu`* — La stratégie achète des favoris EN COURS de match, pas des « paris patients » : ses filtres d'échéance (`echeance_*`, `delai` du pareto) mesurent la date placeholder de Gamma, pas le temps réel ; utiliser `heures_min/heures_max` (coup d'envoi) pour découper par délai.


## [à regarder] nf_sport_patiente_v1.0.0 : 62 achats sur 86 faits après le coup d'envoi

*Contrôle `achats_en_jeu`* — La stratégie achète des favoris EN COURS de match, pas des « paris patients » : ses filtres d'échéance (`echeance_*`, `delai` du pareto) mesurent la date placeholder de Gamma, pas le temps réel ; utiliser `heures_min/heures_max` (coup d'envoi) pour découper par délai.


## [à regarder] nf_tennis_12_18h_vainqueur_v1.0.0 : 62 achats sur 65 faits après le coup d'envoi

*Contrôle `achats_en_jeu`* — La stratégie achète des favoris EN COURS de match, pas des « paris patients » : ses filtres d'échéance (`echeance_*`, `delai` du pareto) mesurent la date placeholder de Gamma, pas le temps réel ; utiliser `heures_min/heures_max` (coup d'envoi) pour découper par délai.


## [à regarder] 36 fille(s) comparée(s) à leur mère sur la même période

*Contrôle `filles_periode`* — Juger une fille contre sa mère ENTIÈRE mélange deux périodes : une fille née un mauvais jour paraît mauvaise même si elle fait mieux que sa mère ce jour-là. Comparer ces chiffres-ci.

- nf_sport_prix_haut_3_6h -0.2% contre sa mère nf_sport_prix_haut -10.1% depuis le 2026-10-22 (48 et 12 opérations)
- nf_sport_patiente_2crans +8.5% contre sa mère nf_sport_patiente +1.1% depuis le 2026-10-19 (41 et 110 opérations)
- nf_sport_patiente_prix_850_875 +5.8% contre sa mère nf_sport_patiente -0.6% depuis le 2026-10-20 (41 et 83 opérations)
- nf_sport_patiente_72_168h_12_18h +5.4% contre sa mère nf_sport_patiente -0.7% depuis le 2026-10-20 (29 et 82 opérations)
- nf_sport_patiente_6_24h +5.8% contre sa mère nf_sport_patiente -0.1% depuis le 2026-10-19 (23 et 101 opérations)
- nf_tennis_12_18h +3.7% contre sa mère nf_tennis -0.5% depuis le 2026-10-20 (67 et 39 opérations)
- nf_tennis +4.0% contre sa mère nf_sport_patiente +0.6% depuis le 2026-10-20 (86 et 90 opérations)
- nf_tennis_12_18h_vainqueur_800_850 +9.2% contre sa mère nf_tennis_12_18h_vainqueur +7.5% depuis le 2026-10-23 (9 et 13 opérations)

## [à regarder] nf_sport : 1 achat(s) de sport de 100 € ou plus sur un marché sans match

*Contrôle `sport_hors_match`* — Marché de saison ou de prix (pas de coup d'envoi) : les tests sur le passé portent sur des matchs ; ajouter `un_match: true` aux `filtres` ou prouver ce type à part.

- 2026-10-21T21:26 « No » 160 € à 0.827

## [à regarder] nf_sport_patiente : 1 achat(s) de sport de 100 € ou plus sur un marché sans match

*Contrôle `sport_hors_match`* — Marché de saison ou de prix (pas de coup d'envoi) : les tests sur le passé portent sur des matchs ; ajouter `un_match: true` aux `filtres` ou prouver ce type à part.

- 2026-10-22T20:00 « No » 359 € à 0.940

## [à regarder] nf_sport_patiente_biais_faible : 1 achat(s) de sport de 100 € ou plus sur un marché sans match

*Contrôle `sport_hors_match`* — Marché de saison ou de prix (pas de coup d'envoi) : les tests sur le passé portent sur des matchs ; ajouter `un_match: true` aux `filtres` ou prouver ce type à part.

- 2026-10-22T18:11 « No » 104 € à 0.949

## [à regarder] nf_sport_patiente_prix_850_875 : 2 achat(s) de sport de 100 € ou plus sur un marché sans match

*Contrôle `sport_hors_match`* — Marché de saison ou de prix (pas de coup d'envoi) : les tests sur le passé portent sur des matchs ; ajouter `un_match: true` aux `filtres` ou prouver ce type à part.

- 2026-10-23T01:01 « No » 160 € à 0.858
- 2026-10-24T11:25 « No » 235 € à 0.856

## [à regarder] nf_sport_patiente_72_168h_12_18h : 1 achat(s) de sport de 100 € ou plus sur un marché sans match

*Contrôle `sport_hors_match`* — Marché de saison ou de prix (pas de coup d'envoi) : les tests sur le passé portent sur des matchs ; ajouter `un_match: true` aux `filtres` ou prouver ce type à part.

- 2026-10-22T18:11 « No » 136 € à 0.949

## [à regarder] nf_sport_patiente_12_18h : 1 achat(s) de sport de 100 € ou plus sur un marché sans match

*Contrôle `sport_hors_match`* — Marché de saison ou de prix (pas de coup d'envoi) : les tests sur le passé portent sur des matchs ; ajouter `un_match: true` aux `filtres` ou prouver ce type à part.

- 2026-10-22T18:11 « No » 122 € à 0.949

## [à regarder] nf_sport_patiente_72_168h_850_875 : 1 achat(s) de sport de 100 € ou plus sur un marché sans match

*Contrôle `sport_hors_match`* — Marché de saison ou de prix (pas de coup d'envoi) : les tests sur le passé portent sur des matchs ; ajouter `un_match: true` aux `filtres` ou prouver ce type à part.

- 2026-10-23T01:01 « No » 114 € à 0.858

## [à regarder] nf_sport_non_900_925 : 1 achat(s) de sport de 100 € ou plus sur un marché sans match

*Contrôle `sport_hors_match`* — Marché de saison ou de prix (pas de coup d'envoi) : les tests sur le passé portent sur des matchs ; ajouter `un_match: true` aux `filtres` ou prouver ce type à part.

- 2026-10-24T10:07 « No » 199 € à 0.921

## [à regarder] 45 paire(s) de stratégies : mêmes paris, autres prix

*Contrôle `meme_pari_prix_differents`* — Même marché, prix d'entrée très différents : moment d'achat, ordre posé ou carnet relu. La différence de résultat entre elles vient alors du prix, pas du choix des paris.

- market_structure_v1.0.0 / news_momentum_v1.0.0 : 11 paris communs, écart moyen 0.333
- market_maker_serre_v1.0.0 / nm_long_v1.0.0 : 9 paris communs, écart moyen 0.200
- market_structure_v1.0.0 / news_momentum_patiente_v1.0.0 : 27 paris communs, écart moyen 0.138
- crypto_threshold_v1.0.0 / market_structure_v1.0.0 : 9 paris communs, écart moyen 0.122
- market_structure_v1.0.0 / reversion_v1.0.0 : 8 paris communs, écart moyen 0.114
- crypto_threshold_patiente_v1.0.0 / crypto_threshold_v1.0.0 : 8 paris communs, écart moyen 0.107
- meteo_prevision_v1.0.0 / news_momentum_patiente_v1.0.0 : 25 paris communs, écart moyen 0.099
- nf_sport_patiente_biais_faible_v1.0.0 / nf_tennis_prix_bas_vainqueur_v1.0.0 : 11 paris communs, écart moyen 0.095

## [à regarder] 2 stratégie(s) sans aucun achat depuis plus de 48 h

*Contrôle `muettes`* — Une stratégie muette ne teste rien : lire ses abstentions (journal du cycle, tableau de bord) et corriger le filtre ou la source qui la bloque.

- cpi_tranches_v1.0.0 (née le 2026-10-21) — dernier cycle : 444 marchés vus, 0 propositions ; hors de la fenêtre avant la publication ×15
- jobs_favori_non_v1.0.0 (née le 2026-10-21) — dernier cycle : 444 marchés vus, 0 propositions ; hors de la fenêtre avant la publication ×1

## [à regarder] 11 stratégie(s) retirée(s) pour inactivité sans aucun achat

*Contrôle `retraits_inactifs`* — Retrait définitif d'une stratégie qui n'avait peut-être rien à faire (calendrier, arbitrage rare, source en panne). Si elle attend une date ou une rareté : l'ajouter à `jamais_retirer` (config/promotion.yaml) et relancer une nouvelle version ; si c'est un bug, le corriger avant.

- cotes_tennis_v1.0.0 : retirée le 2026-10-22T12:01 (inactive : fille sans opération ni position en 2 jours)
- crypto_threshold_24_72h_v1.0.0 : retirée le 2026-10-22T15:55 (inactive : fille sans opération ni position en 2 jours)
- mots_prononces_nfl_v1.0.0 : retirée le 2026-10-23T05:21 (inactive : fille sans opération ni position en 2 jours)
- coherence_match_v1.0.0 : retirée le 2026-10-23T11:25 (inactive : aucune opération ni position en 3 jours)
- implication_politique_v1.0.0 : retirée le 2026-10-23T11:25 (inactive : aucune opération ni position en 3 jours)
- paire_oui_non_v1.0.0 : retirée le 2026-10-23T11:25 (inactive : aucune opération ni position en 3 jours)
- marches_jumeaux_v1.0.0 : retirée le 2026-10-23T11:25 (inactive : aucune opération ni position en 3 jours)
- kalshi_reference_v1.0.0 : retirée le 2026-10-23T12:01 (inactive : aucune opération ni position en 3 jours)

## [à regarder] 2 fantôme(s) sans argent disponible depuis plus de 48 h

*Contrôle `capital_bloque`* — Capital immobilisé dans des positions longues : le fantôme ne teste plus rien, et le comparer à une fille ou à une mère qui a de l'argent compare deux situations différentes (juger sur la même période ET avec le même argent disponible).

- favori_politique_v1.0.0 : 81.47 € disponibles sur 1043 €, 15 positions ouvertes, dernier achat le 2026-10-16T21:57
- favori_politique_nuit_v1.0.0 : 7.62 € disponibles sur 1010 €, 18 positions ouvertes, dernier achat le 2026-10-17T11:24

## [à regarder] nf_court_v1.0.0 : 1 position(s) ouverte(s) bien après l'échéance

*Contrôle `positions_oubliees`* — Marché contesté, règlement manqué ou mauvaise échéance : l'argent reste bloqué.

- 2026-10-19T04:19 « No » (marché 5475240, échéance dépassée de 108 h)

## [à regarder] nm_court_v1.0.0 : 1 position(s) ouverte(s) bien après l'échéance

*Contrôle `positions_oubliees`* — Marché contesté, règlement manqué ou mauvaise échéance : l'argent reste bloqué.

- 2026-10-19T14:15 « No » (marché 5475240, échéance dépassée de 108 h)

## [à regarder] nm_demi_mise_v1.0.0 : 2 position(s) ouverte(s) bien après l'échéance

*Contrôle `positions_oubliees`* — Marché contesté, règlement manqué ou mauvaise échéance : l'argent reste bloqué.

- 2026-10-18T09:19 « No » (marché 5767158, échéance dépassée de 148 h)
- 2026-10-18T09:24 « No » (marché 5767157, échéance dépassée de 148 h)

## [à regarder] nm_hors_crypto_v1.0.0 : 2 position(s) ouverte(s) bien après l'échéance

*Contrôle `positions_oubliees`* — Marché contesté, règlement manqué ou mauvaise échéance : l'argent reste bloqué.

- 2026-10-18T09:19 « No » (marché 5767158, échéance dépassée de 148 h)
- 2026-10-18T09:24 « No » (marché 5767157, échéance dépassée de 148 h)

## [à regarder] nm_prix_bas_v1.0.0 : 1 position(s) ouverte(s) bien après l'échéance

*Contrôle `positions_oubliees`* — Marché contesté, règlement manqué ou mauvaise échéance : l'argent reste bloqué.

- 2026-10-19T14:15 « No » (marché 5475240, échéance dépassée de 108 h)

## [à regarder] nm_prix_haut_v1.0.0 : 3 position(s) ouverte(s) bien après l'échéance

*Contrôle `positions_oubliees`* — Marché contesté, règlement manqué ou mauvaise échéance : l'argent reste bloqué.

- 2026-10-18T09:19 « No » (marché 5767158, échéance dépassée de 148 h)
- 2026-10-18T09:24 « No » (marché 5767157, échéance dépassée de 148 h)
- 2026-10-19T18:19 « No » (marché 5475240, échéance dépassée de 108 h)

## [à regarder] suivre_politique_v1.0.0 : 2 position(s) ouverte(s) bien après l'échéance

*Contrôle `positions_oubliees`* — Marché contesté, règlement manqué ou mauvaise échéance : l'argent reste bloqué.

- 2026-10-18T11:59 « No » (marché 5475242, échéance dépassée de 108 h)
- 2026-10-18T23:20 « Yes » (marché 5475240, échéance dépassée de 108 h)
