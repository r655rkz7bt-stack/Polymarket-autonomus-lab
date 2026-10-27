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

## 4. Suite du même soir : la tranche centrale des échelles « <actif> price on <date> » avant le fix de 12 h (Est) — INDICE, fantôme `tranche_centrale_non`
Né de la section 2 : le modèle log-normal sans dérive, à volatilité plate, était trop sûr des tranches étroites proches du règlement (tranches cotées ≥ 0,55 : OUI réel 0,74 pour un prix moyen de 0,82 et un modèle de 0,86 à 3 h).
**Cause trouvée** : le règlement est à 12 h heure de l'Est = 16 h UTC (17 h l'hiver) ; les 3 heures qui précèdent sont l'ouverture de Wall Street : variance horaire (barres Binance 2026) **×1,98 / 2,02 / 2,34 pour les barres de 13, 14, 15 h UTC** (BTC),
×1,87 / 1,78 / 2,38 (ETH) : 1,45× en écart-type (`scripts/saison_vol.py`). Un modèle avec ce profil (estimé sur 2024-2025) fait mieux que le plat (log-score à 3 h −0,198 contre −0,222), **mais reste moins bon que le prix** (−0,193) :
le marché anticipe l'ouverture de Wall Street. Il en garde pourtant moins que ce qu'il faudrait pour la tranche centrale.
**Règle R1, prix seuls (sans modèle)** (`scripts/regle_fix.py`, relevé `releve_prix_du_jour.py` : 1 739 événements « price on » de janvier à septembre 2026 par la recherche publique de Gamma, 4 435 tranches « between » à plus de 5 000 $, plus
septembre-octobre du relevé précédent ; 15 598 instants, 858 événements, vrais échanges, frais crypto payés) : **NON de la tranche centrale (OUI coté 0,55-0,97, NON payé 0,03-0,45) 3 à 6 h avant la fin, un pari par marché** :
| période | paris | évén. | rendement | gagnés / attendus | mois | sans ses 10 meilleurs événements |
|---|---|---|---|---|---|---|
| **janvier-octobre 2026 (découverte)** | 585 | 543 | **+44,5 %** (t par événement +3,19) | 185 / 138,9 (z +4,67) | 9 / 10 | +18,3 % (z +3,78) |
| janvier-mai / juin-octobre | 349 / 236 | | +26,3 % / +71,4 % | z +2,15 / +4,79 | 4/5 / 5/5 | |
| **hold-out août-décembre 2025 (jamais vu)** | 321 | 310 | **+18,7 %** (t +1,62) | 112 / 94,4 (z +2,22) | 5 / 5 | **−1,6 %** |
- NON payé 0,10-0,25 (OUI 0,75-0,90) : +78,6 % (199 paris, 10 mois sur 10, z +5,2) en 2026 ; +39,6 % en 2025 (82 paris, z +1,6).
- **Profondeur : le gain croît avec la quantité achetable** (parts de NON achetées par des preneurs à ≤ prix + 2 centimes dans l'heure, `profondeur_fix.py`) : ≥ 20 parts +38,5 %, ≥ 100 +46,1 %, ≥ 200 +53,0 %, ≥ 400 +66,5 % (z +3,3) ; médiane 224 parts (≈ 48 €). Contrairement au NON crypto 0,10-0,20 (section 1), ce n'est pas un artefact d'échanges minces.
- **Direction neutre** : corrélation du rendement mensuel avec le rendement du mois du Bitcoin +0,10, avec sa valeur absolue +0,52 (10 mois) : c'est un pari sur l'amplitude du mouvement avant le fix.
- Écartée : **R2** (OUI des queues payé 0,02-0,25) : +22,4 % en 2026 mais −9,5 % sans ses 10 meilleurs événements, +10,8 % en 2025 (z +0,6) ; la sous-tranche payée 0,12-0,25 seule fait +64 % (z +4,3) en 2026 et +3,3 % en 2025.
- Réglages regardés : 5 listes d'heures (3, 6, 3/6, 4, 2/3/4/6) × 2 règles, puis une trentaine de découpages (mois, actif, prix, moitié, profondeur) : ≈ 50 ; un seul réglage a priori (« 3 à 6 h avant la fin », fixé avant de voir 2025). H−4 seul fait −0,2 % en 2025 (+41 % en 2026) : la fenêtre n'est pas affinée.
- **Verdict : indice** (même signe dans deux périodes indépendantes, effet 2,4× plus petit en 2025, fragile sans ses meilleurs événements en 2025). Fantôme `tranche_centrale_non` (demi-Kelly, avantage supposé 0,06 contre 0,08-0,14 mesuré) ; pas de capital principal avant 30 paris en direct.
- Mise en œuvre : étiquette `crypto-prices` (1312) ajoutée à `scanner.tag_pages` avec un horizon de 8 h (sans elle la stratégie ne voyait aucun marché) ; **à vérifier demain vers 10 h UTC** (aujourd'hui l'échelle du 28/10 finit dans 18 h, hors horizon) : ligne `propositions … abstentions` du fantôme dans le cycle de production.
Scripts : `releve_prix_du_jour.py` (événements), `saison_vol.py` (profil + log-scores, `HOLDOUT=1` pour 2025), `regle_fix.py`, `profondeur_fix.py`, `tranches.py` ; sorties `resultats_saison.txt`, `resultats_regle_fix.txt`, `resultats_regle_fix_2025.txt`, `resultats_profondeur_fix.txt`, `resultats_tranches.txt`.
