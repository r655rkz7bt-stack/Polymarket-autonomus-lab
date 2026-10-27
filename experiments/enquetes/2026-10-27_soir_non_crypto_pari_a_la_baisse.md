# 27/10/2026 (soir) : le « z +5,3 » du NON crypto comptait 4 167 paris qui perdent ou gagnent ensemble (le cours du Bitcoin) ; un compteur de « gagnés » qui comptait mal les 50-50

Point de départ : feuille de mission de 20 h 48 sans « Enquête obligatoire ». Constats « à regarder » : `moins_de_cartes` (15 gagnés pour 17,2 sur ses 30 dernières opérations), `certitude_promise` (arène : 28 paris
promis à plus de 0,995, −254 €), `estimation_gonflee`. Famille du jour (27 mod 6 + 1 = 4, « le filtre ne filtre pas ») puis famille 2 (« la mesure récompense la chance »).

## 1. `certitude_promise` rouvert à chaque passage par des paris d'avant le correctif
- 95 paris promis ≥ 0,995 (journaux des fantômes, `news_momentum` et ses 7 filles) : **le dernier date du 23/10 à 16 h 32** (2 achats `nm_court` / `nm_crypto`, −195 €), avant le correctif de 20 h 35 (plafond d'estimation de
  `news_momentum`, fiche `2026-10-23_soir_news_momentum_certitude.md`). Depuis : aucun pari promis à ≥ 0,995 en 4 jours.
- **Correctif** : `enquete.certitude_promise(depuis=CERTITUDE_CORRIGEE_LE)` ne compte que les paris ouverts après le correctif ; test `test_near_certain_promises_before_the_fix_do_not_reopen_the_finding`.

## 2. Famille 4 (filtres) : rien de neuf
`filtres_prix_24_10.py` rejoué sur les achats depuis le 24/10 (2 304 achats, 78 stratégies à plage de prix) : les écarts à la plage sont toujours de 1 à 2 crans sous la borne basse (tennis 0,78-0,79 pour une plage 0,80-0,95 :
le carnet a baissé entre la lecture et l'exécution ; `mots_prononces_patiente` 0,28 pour 0,30 ; `outsider_sport_apres_midi` 0,07 pour 0,08) ou 1 cran au-dessus d'une borne haute (`contrer_crypto_audace` 0,46 pour 0,45) : déjà documenté le
24/10 (`2026-10-24_ecart_estimation_et_reference_arene.md`). `filtres_questions_27_10.py` (disciplines, types, question_contient / exclut, issue, sources) sur 1 689 achats : 0 achat hors filtre. Pas de défaut.

## 3. Famille 2 : le « z +5,3 » du NON crypto à 0,10-0,45 (`experiments/crypto_pourquoi.md`)
- **Constat** : `contrer_crypto_passe.md` concluait « indice solide » (4 167 paris, +15,8 %, z +5,33) et en tirait deux fantômes à Kelly entier. En regroupant par mois, le rendement mensuel du NON suit le cours du mois du
  Bitcoin : corrélation **−0,82** sur 17 mois (≥ 100 paris), gain de signe opposé au cours dans 15 mois sur 17 (Ethereum −0,79, 16 sur 17), pente −1,84 point de rendement par point de cours (R² 0,67). C'est un pari à la
  baisse : un NON à 0,10-0,45 sur « au-dessus de X » est un OUI à 0,55-0,90 vendu.
- **Ampleur** : sur l'unité qui compte (le mois), rendement moyen +9,9 % (33 mois, **t +1,76**), +12,1 % (24 mois, t +2,41), +12,9 % (17 mois, t +2,12) ; ce qui reste à cours stable : +11 % (± 3,6, Bitcoin) à +15 % (± 3,9, Ethereum).
  Août-octobre 2026 (relevé refait avec les prix Binance, 191 paris) : +0,3 % (août −63 % quand le Bitcoin monte de 25 %, octobre +46 % quand l'Ethereum baisse de 13 %).
- **Cause** : deux unités différentes : le z comptait chaque pari comme un tirage, alors que les paris d'un même mois partagent le cours (la même hausse fait perdre tous les NON de l'échelle). `enquete._z_by_event` regroupait déjà
  par événement (une échelle de seuils), pas par jour de règlement. Le modèle de volatilité (barres Binance, sans dérive) ne bat jamais le prix (log-score −0,005 à −0,13 selon l'heure) : pas de prime de volatilité à prendre.
- **Correctif** : `enquete._z_by_day` (un jour de règlement = un tirage, au moins 8 jours distincts) pris en compte par `selection_multiple` avec le z par événement ; `_won_vs_expected` voir 4 ; textes `hypothesis`
  de `crypto_non_bon_marche` et `crypto_non_10_20` complétés ; test `test_selection_z_counts_a_day_of_common_shock_once` (100 paris, 10 jours, +4,0 par pari → +1,3 par jour).
- **Pas un défaut de code** : les fantômes font ce qu'ils annoncent ; c'est la lecture de leur résultat qui change (« avantage + exposition à la baisse du cours »).

## 4. `_won_vs_expected` comptait un règlement 50-50 comme une perte (ou une victoire) entière
- `champion_sans_avantage`, `chance` et `selection_multiple` comptaient `pnl > 0` : un 50-50 payé 0,55 = perte entière, payé 0,48 = victoire entière. Même défaut que `estimation_gonflee` (corrigé le 26/10), resté dans ces trois contrôles.
  `moins_de_cartes` (6 règlements 50-50 sur 85 paris) : z +0,86 → **+1,53** (`selection_multiple`) ; en direct 56 gagnés pour 48,0 attendus (+12,4 % par mise), pas « 15 pour 17,2 » : les 30 dernières opérations ne contiennent pas de 50-50, c'est
  du bruit (z −0,8), avec une soirée à −21 % (26/10, 14 paris) et une à +38 % (25/10).
- **Correctif** : `_won_vs_expected` compte le paiement par part (1 / 0,5 / 0) ; test `test_won_versus_expected_counts_the_payout_of_a_fifty_fifty_settlement`.

## 5. Contrôle des autres stratégies au z par jour (`scripts/z_par_jour_27_10.py`)
`compteur_tweets` +2,45 par pari, +1,80 par jour ; `contrer_crypto_patiente` +1,86 / +1,74 ; `nf_sport_non` +1,18 / +1,72 : pas de facteur commun caché (z par jour proche du z par pari) ; les stratégies à moins de 8 jours de règlements
(`moins_de_cartes`, `nf_sport_patiente_prix_850_875`, tennis) ne peuvent pas encore être jugées ainsi (pas de jugement plutôt qu'un faux).
