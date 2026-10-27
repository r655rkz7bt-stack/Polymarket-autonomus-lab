# Pourquoi le NON crypto à 0,10-0,45 « gagne » : un pari à la baisse, pas une erreur de prix (28/10/2026, passage du 27/10 au soir)

Suite de `contrer_crypto_passe.md` (« indice solide », z +5,3 sur 4 167 paris, `crypto_non_bon_marche` / `crypto_non_10_20` en fantômes). La note disait : « pourquoi (non prouvé) : prime de
volatilité ? à vérifier avec les prix Binance ». C'est fait. **Verdict : le gain est surtout de la direction du cours (bêta baissier), le prix du marché est aussi bon qu'un modèle de
volatilité ; l'« indice » reste un indice, mais à t ≈ 2 par mois (pas z 5,3).**

## 1. Le rendement mensuel suit le cours du mois (`scripts/mois_contre_spot.py`, barres Binance `data-api.binance.vision`)
Un NON qui coûte 0,10-0,45 sur un marché « au-dessus de X » est un OUI à 0,55-0,90 vendu : il gagne si le cours finit SOUS X. C'est un pari à la baisse.
Les 33 rendements mensuels du NON 0,10-0,45 (`resultats_baseline_non_2024_2026.txt`) contre le rendement du mois du Bitcoin / de l'Ethereum :
| mois comptés | Bitcoin : corrélation (rang) | gains de signe opposé au cours | Ethereum : corrélation | régression : rendement « cours stable » |
|---|---|---|---|---|
| 17 mois à ≥ 100 paris | **−0,82** (−0,83) | **15 / 17** | −0,79 | BTC +11,2 % (± 3,6), pente −1,84 ; ETH +14,7 % (± 3,9), pente −1,09 ; R² 0,67 / 0,62 |
| 24 mois à ≥ 30 paris | −0,71 | 21 / 24 | −0,75 | BTC +12,3 % (± 3,8) ; ETH +14,8 % (± 3,5) |
| 33 mois | −0,38 (−0,57) | 26 / 33 | −0,44 | |
Détail BTC (cours du mois / rendement du NON) : 2025-09 +5/+37, 2025-11 −18/+48, 2026-01 −10/+57, 2026-04 +12/−24, 2026-06 −20/+44, 2026-08 +25/−31, 2026-10 −3/+25. **Les mois perdants du fantôme
(avril −24 %, août −31 %) sont les mois où le cours monte.** Les paris d'un même mois ne sont pas des tirages indépendants : sur la unité qui compte (le mois), le rendement moyen est +9,9 % (33 mois, t +1,76),
+12,1 % (24 mois, t +2,41), +12,9 % (17 mois, t +2,12), 11 mois positifs sur 17. Le « z +5,33 » comptait chaque pari comme un tirage.
Ce qui reste quand le cours est stable (+11 à +15 %, t ≈ 3 par mois) est le seul candidat à un avantage ; il est d'un ordre de grandeur plus petit que les oscillations (écart-type mensuel 25 points).

## 2. Le prix du marché est aussi bon qu'un modèle de volatilité (`scripts/modele.py`, `analyse.py`)
Modèle sans dérive (log-normal, volatilité = écart-type des rendements horaires des 168 dernières heures FINIES, barres Binance ; touche : principe de réflexion), jugé à D−3/6/12/24 h
du règlement sur 4 011 marchés réglés d'août à octobre 2026 (« above / less than / reach / dip to » sur BTC, ETH, SOL, XRP, DOGE, BNB ; 2 200 avec échanges, 5 645 instants, 384 événements) :
- « above » : prix moyen du OUI 0,489-0,510, modèle moyen 0,493-0,511, OUI réel 0,462-0,511 ; log-score modèle − prix −0,127 (3 h, t −2,4), −0,031 (6 h), −0,014 (12 h), −0,005 (24 h) :
  **le modèle ne bat jamais le prix**. Pas de prime de volatilité visible : l'hypothèse « le OUI paie la volatilité » n'est pas la cause.
- NON payé 0,10-0,45 sur la même période (un pari par marché) : 191 paris, **+0,3 %** (56 gagnés pour 52,3 attendus ; août −62,8 % / septembre −5,2 % / octobre +46,0 %, soit exactement l'ordre inverse
  des mois du Bitcoin : +25 / +6 / −3 %, Ethereum +32 / +9 / −13 %). Découper par « écart modèle − prix » du NON ne donne rien de stable (−25 % / +34 % / −34 % / +67 % selon la case).
- Les mêmes marchés en panier : OUI payé 0,10-0,45 (pari à la hausse) −0,6 % (165 paris, z −0,1), pente +6,9 par point de cours et par semaine (NON : −4,6) ; un panier 50/50 des deux côtés réduit l'écart-type
  hebdomadaire de 64,7 à 37,8 points mais ne garde que +2,8 % (11 semaines : trop peu pour parler d'une couverture rentable).

## 3. Conséquences
1. **Lire les fantômes `crypto_non_bon_marche` et `crypto_non_10_20` comme « avantage + exposition à la baisse du cours »** : une perte de fantôme un mois où le Bitcoin monte de 10 % ne dit rien sur l'avantage
   (pente −1,8 point par point de cours). Juger sur plusieurs mois ou en retirant l'effet du cours (`mois_contre_spot.py`), pas sur 30 paris. Textes `hypothesis` mis à jour.
2. **Contrôle ajouté à l'enquête automatique** (`enquete._z_by_day`, utilisé par `selection_multiple`) : un jour de règlement compte comme un seul tirage (au moins 8 jours distincts), comme un événement.
   Test `test_selection_z_counts_a_day_of_common_shock_once` (100 paris, 10 jours, z +4,0 par pari → +1,3 par jour).
3. Pas de stratégie de couverture : le OUI bon marché n'a pas d'avantage propre (−0,6 %) ; une couverture coûterait l'avantage.
4. Limite : les 33 rendements mensuels viennent du relevé du 27/10 matin (données non versionnées) ; ce passage n'a pu relever que août-octobre 2026 en échanges (2 614 marchés lus ; Gamma ~60 000 événements par
   mois pour l'étiquette `crypto`, ≈ 30 min par mois lu : prévoir un relevé par fenêtre `end_date_min/max` avec `slug` « bitcoin-above-on-… » si on veut refaire 2024-2025 en échanges).
Scripts : `experiments/crypto_pourquoi/scripts/` (`releve_spot.py` : Binance par le miroir public, Yahoo répond 429 depuis la routine et `api.binance.com` refuse la zone ; `filtre_marches.py`, `modele.py`,
`analyse.py`, `analyse_couverture.py`, `mois_contre_spot.py`) ; sorties : `resultats_*.txt`.
