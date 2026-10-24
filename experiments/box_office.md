# Box-office du premier week-end (piste du 24/10/2026)

**Question** : dans les marchés « <film> Opening Weekend Box Office » (4 à 6 tranches de recettes par film, règlement sur the-numbers.com), la tranche
favorite gagne-t-elle plus souvent que son prix, assez pour couvrir les frais ?

**Données** (`experiments/box_office/scripts/releve.py`, versionnées dans `releves/`) : 363 événements Gamma contenant « box office », dont 244 « Opening Weekend » réglés
(juillet 2022 → octobre 2026), 240 utilisables (une seule tranche gagnante au prix final, au moins 20 échanges, 3 tranches ou plus). Échanges réels : `data-api …/trades?eventId=` (6,7 Mo).
Frais : barème 5 % (`feeSchedule`) appliqué à tous les paris, même sur les anciens marchés sans frais (prudent). Règlement = prix final Gamma (UMA) ; pas de relecture contre the-numbers.com
(le site n'est pas lu : limite assumée).

**Heure** : la fin du marché varie (lundi 12 h UTC pour 142 événements, dimanche 12 h ou 23 h pour 49, autres 49). Horizon = heures avant la fin du marché.

## 1. Calibration des tranches (prix du dernier échange avant l'heure, tous événements)
| h avant la fin | 0,50-1 : gagnantes / attendues | 0,05-0,15 | 0,15-0,30 | < 0,05 |
|---|---|---|---|---|
| 48 h | 131 / 121,6 (n = 151) | 5 / 10,7 | 17 / 21,0 | 1 / 4,6 |
| 24 h | 138 / 128,4 (n = 151) | 2 / 5,9 | 8 / 10,9 | 1 / 3,1 |
| 12 h | 130 / 126,8 | 5 / 3,6 | 7 / 6,6 | 0 / 2,4 |
Biais classique « favorite sous-cotée, tranches basses sur-cotées » à 24-48 h (somme des prix visibles : 1,00 : pas de défaut de normalisation).

## 2. Achat de la tranche favorite (prix du dernier ACHAT réel dans les 2 h, frais 5 %), un pari par événement
| h | prix | paris | rendement | t par événement | gagnés/attendus |
|---|---|---|---|---|---|
| 24 | 0,5-1 | 116 (110 films) | **+8,1 % (+7,5 % un par film)** | 2,20 (1,96) | 100 / 93,6 |
| 36 | 0,5-1 | 122 | +5,1 % | 1,16 | 97 / 92,4 |
| 48 | 0,5-1 | 117 | +5,1 % | 1,08 | 95 / 90,2 |
| 12 | 0,5-1 | 103 | +2,4 % | 0,75 | 92 / 89,4 |
| 96 | 0,5-1 | 53 | +0,9 % | 0,11 | |
Réglages regardés : 6 horizons × 4 plages de prix = 24 (+ 6 pour la robustesse) : le meilleur (24 h, 0,5-1) est choisi parmi 30 ; le signe est positif à tous les horizons de 12 à 96 h (+1 à +8 %).

## 3. Robustesse (`scripts/robuste.py`, `scripts/par_fin.py`)
- Un pari par film (doublons « Higher Brackets » retirés) : 24 h +7,5 % (t 1,96) ; sans les 3 meilleurs paris +5,3 % ; 1re moitié du temps +3,4 %, 2e moitié +11,6 %.
- Selon la fin du marché : lundi 12 h (142 événements) 24 h **+8,6 %** (t 2,40, 71 gagnés / 65,7) ; dimanche (49) 24 h +14,9 % (t 1,21) mais 36/48 h −7 % ; autres 24 h +1 %. Instable.
- Aucun prix « milieu » sans échange : tous les prix sont des achats réels (donc pas le piège des carnets vides).
- Limite : marchés minces (médiane quelques dizaines de dollars par échange), pas de test de mise à l'échelle ; règlement non relu sur the-numbers.com.

## 4. Le côté opposé : NON des tranches peu probables (`scripts/non_bas.py`)
OUI à 0,05-0,15 (NON acheté au dernier achat réel, frais 5 %) : +2,5 % (96 h), −1,2 % (72 h), +3,6 % (48 h, t 2,5), +5,4 % (36 h, t 3,3), +4,0 % (24 h, t 1,9), −0,7 % (12 h) ; OUI à 0,15-0,30 : −8 % à +5 % sans régularité.
Gagnés contre attendus par les prix : z +0,9 à +1,8 seulement. C'est l'image dans le miroir du même biais (la masse que les tranches basses surcotent, la favorite la sous-cote) : pas une deuxième preuve,
et ce n'est pas rejoué dans l'arène (seule la favorite l'est). Écartée comme piste séparée.

## 4b. Suivre l'argent (`scripts/flux.py`, 9 réglages)
Parmi les tranches à 0,10-0,85, celle dont les achats nets des 6/12/24 dernières heures sont les plus gros (au moins 20 $) à 72/48/24 h de la fin : rendements de −27 % à +13 %, aucun régulier
(24 h : −21 %, −5 %, −27 % ; 72 h/12 h : +13 %, t 0,95). **Écartée.**

## 5. Deuxième week-end et suivants (78 événements « 2nd/3rd… Weekend » utilisables, 2026)
Favorite (`scripts/suivants.py`, mêmes règles, sans lier le film à son ouverture) : 23-35 paris par horizon, de −2 % à +5 % (z des prix −1,5 à +1,0) : **rien** (écartée, trop peu de cas).
**Loi de baisse (ouverture → 2e week-end)** : pas testée,
Lien avec l'ouverture du même film (bracket gagnant) tenté : 27 films, libellés de tranches irréguliers (« 5-Day », tranches serrées/larges, doublons) et ratios incohérents (de 0,15 à 1,43) ;
trop peu de films propres pour une loi de baisse. À reprendre quand la série « 2nd Weekend » aura 60+ films réglés avec des tranches comparables.

## 6. Contrôle : la même favorite dans d'autres familles de tranches (`experiments/familles_tranches/scripts/`)
Netflix « top show de la semaine » (174 événements), vues (bandes-annonces, MrBeast : 241) et Rotten Tomatoes (51), mêmes règles (dernier achat réel, frais 5 %, favorite sûre) : **rien**.
Netflix : −7 % à +1 % selon l'horizon (z des prix −1,2 à +0,2) ; vues : −21 % à +3 % (z −1,8 à +0,9) ; Rotten Tomatoes : −1 % à +4 % (n = 21-23).
La favorite sous-cotée n'est donc pas une propriété générale des marchés à tranches : soit un trait du box-office (débutants qui sous-estiment le vendredi et le samedi), soit le hasard d'un meilleur de ~30 réglages.
Ce contrôle PLAFONNE la confiance : indice faible, pas plus.

## 7. Ancrer l'heure sur le week-end, pas sur la fin du marché (`scripts/ancre.py`, `scripts/fenetre.py`)
La fin du marché varie (lundi 12 h ou dimanche midi UTC). Ancre = dimanche 00 h UTC (samedi soir à New York) : favorite achetée à l'ancre − 48 h : −0,7 %, − 36 h : +2,3 %, − 24 h : +0,2 %, − 12 h : +5,2 % (t 1,5), à l'ancre : **+7,6 %** (121 films, t 1,94, z des prix +2,0), + 12 h : +4,5 % (t 0,9) ;
dimanche 12 h UTC +4,5 % (t 0,9) ; avant, rien. Règle « premier achat réel entre le samedi 18 h et le dimanche 16 h UTC » : **−2,0 %** (154 films, t −0,44) ; « dimanche 0 h → 16 h » : **+6,6 %** (142 films, t 1,56, 120 gagnés pour 112,5).
Le signal n'existe qu'après les chiffres du samedi (mécanisme plausible : le marché sous-réagit au vendredi et au samedi) mais il disparaît si l'on commence trois heures trop tôt : fragile. La règle jouée par le fantôme est celle de dimanche 0 h → 16 h UTC (`weekday`, `hour_from`, `hour_to`).

## 8. Test de permutation sur la sélection (`scripts/permutation.py`)
Combien de fois le meilleur des 24 réglages (6 horizons × 4 plages de prix) atteint-il un rendement aussi fort si le marché est calibré à 24 h ? 2 000 tirages du gagnant selon les prix normalisés à 24 h (mêmes événements, mêmes prix payés, mêmes frais), 160 événements, cases d'au moins 30 paris.
Observé : meilleur rendement **+20,5 %** (24 h, favorite à 0,5-0,8, 39 paris), suivi de +13,9 % (24 h, 0,6-0,9), +12,3 % (48 h, 0,5-0,8) ; sous l'hypothèse nulle : médiane du meilleur 7 %, 95e centile 17 %, **P(meilleur ≥ observé) = 0,022**.
Donc la sélection parmi 24 cases à elle seule explique mal le résultat ; elle ne couvre pas les ~15 autres découpages (ancre, premier achat, fin du marché) ni l'absence d'effet dans les 6 autres familles, ni le fait que la bande 0,5-0,8 (+20 % ici) fait −4 % dans la règle « premier achat » du §7.
Lecture : indice réel mais fragile, plus net pour les favorites à 0,5-0,8 que pour les très hautes.

## Verdict : **indice faible → fantôme** `box_office_favori`
Positif à tous les horizons, significatif seulement à 24 h (t 1,96-2,2) après sélection parmi ~30 réglages (z attendu du meilleur de 30 ≈ 2) ; la favorite gagne 6 fois de plus que son prix
sur 110 (z des prix ≈ +2). Fantôme en quart de Kelly, fenêtre dimanche 0 h → 16 h UTC ; l'arène (carnets réels, 2-3 week-ends par mois) confirmera ou non.
Prochain test honnête : les week-ends du 24-25/10, 30/10-1/11 et 7-8/11, tels que l'arène les joue (`box_office_favori`), puis `releve.py` + `favori.py` pour ajouter les films réglés depuis.
Pistes voisines non faites : « 2nd Weekend Box Office » (nouvelle série depuis octobre), « total domestic gross by <date> » (seuils), Rotten Tomatoes (12-24 k$ de volume, aucune donnée de départ).
