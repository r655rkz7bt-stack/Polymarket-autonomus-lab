# Aux prix payés : mots_prononces et compteur_tweets_non (21/10/2026)

**Question** : deux stratégies ont été « retenues » avec les prix HORAIRES du CLOB (`prices-history`) plus un
demi-écart supposé : `mots_prononces` (+19 % par achat, `experiments/vingt_pistes.md`) et
`compteur_tweets_non` (+16,3 % par achat, `experiments/tweets_filles.md`). Ces gains tiennent-ils quand on
paie les prix que de vrais preneurs ont **réellement payés** ? Deux fois déjà, la réponse a été non :
météo (+28 % → −6 %, `meteo_backtest.md`) et mentions « annonceurs » (+31 % → −7 %, `mentions_annonceurs.md`).
`config/promotion.yaml` exige ce test avant toute inscription dans `validated_strategies`.

Scripts : `experiments/prix_payes/` ; données brutes dans `donnees/` (ignoré par Git). Tout re-téléchargé
le 21/10/2026 entre 7 h 49 et 8 h 03 UTC.

## Méthode
1. **Mêmes décisions qu'avant, reproduites** avec les scripts d'origine
   (`experiments/vingt_pistes/scripts/`), sans regard vers le futur : le taux d'un mot n'utilise que les
   marchés réglés AVANT la décision ; le compteur de tweets ne lit que les messages d'avant l'instant.
2. **Vrais échanges** : `data-api.polymarket.com/trades?market=<conditionId>&takerOnly=true` avec
   `start` / `end` (ces deux paramètres filtrent bien la fenêtre, ce qui évite la limite de 10 000 de
   décalage). `conditionId` lu sur Gamma.
3. **Prix payé** = premier échange d'un preneur qui ACHÈTE le jeton après l'instant de décision, dans une
   fenêtre de 6 h (achat du jeton au prix p, ou vente de l'autre issue au prix p = jeton à 1 − p). Jamais
   d'échange pris dans la dernière heure avant la clôture (mentions) ni après la fin de la période
   (tweets). **Aucun échange dans la fenêtre = pas de pari** (compté à part).
4. Deux façons de compter :
   - **« mêmes décisions »** : l'achat décidé au prix horaire, payé au vrai prix (la question posée) ;
   - **« décision au prix payé »** : on décide avec le vrai prix (acheter si probabilité − marge > prix
     payé et prix ≥ billet minimum), comme fait la stratégie en direct avec le prix vendeur.
5. **Frais réels** relus dans `feeSchedule` (preneur seulement) : mentions 0,04·p·(1−p), tweets
   0,05·p·(1−p). Rendement = résultat par euro misé. Aucun écart en plus du prix payé (+0,01 en test).
6. **Robustesse** : plusieurs réglages, moyenne PAR ÉVÉNEMENT / PÉRIODE (les paris d'un même événement
   sont liés : c'est le t qui compte), mois, tranches de prix, fenêtre de 0,5 h à 24 h, verdict
   `idea_test.verdict`.

## 1. mots_prononces : trompeuse aux prix payés

**Données** : 1 317 événements « mentions » réglés (23 660 marchés). Sur les 3 000 marchés relevés (au
moins 3 précédents), **635 seulement ont un historique horaire** (`interval=max` ne rend rien pour les
marchés anciens) : le test ne couvre que **septembre et octobre 2026**. Échanges de preneurs entre
l'ouverture + 2 h et + 48 h : médiane **8 par marché**, 83 marchés sans aucun échange.

**Reproduction** (marge 0,05, K 2, 3 précédents, billet ≥ 0,30, sans « Will "X" be said ») :
202 achats, +20,3 % (t +2,89) à 2 h ; +28,6 % à 12 h ; +20,4 % à 24 h (le 20/10 : 223 achats,
+19 %, +27 %, +21 % ; l'échantillon a glissé d'un jour).

**Ce qui se passe au réglage principal (2 h après l'ouverture)** :
- **92 décisions sur 202 (46 %) n'ont aucun échange de preneur dans les 6 h**. Ce sont elles qui
  faisaient le gain : +26,5 % au prix horaire (t +2,82). 32 des 202 prix horaires valent 0,50 pile
  (carnet vide, milieu sans valeur).
- Les 110 décisions appariées : +15,2 % au prix horaire, **−1,5 % au prix payé** (t −0,17) ;
  par événement −8,1 % (t −0,73, 44 événements) ; septembre +16,9 %, octobre −19,3 %.
  Prix payé − (prix horaire + 0,02) : +0,015 en médiane. Premier échange : 27 parts en médiane.
- Décision au prix payé : 111 achats, +15,7 % (t +1,41), par événement +14,3 % (t +1,05). Mais
  **sans « the announcers » ni « anyone »** (jugés à part le 21/10 : Coupe du monde perdante, « anyone »
  sans échanges) : **−10,3 %** (77 achats, t −0,79). **Trump** (premier orateur du test : 112 achats horaires sur 202) :
  −17,0 % (mêmes décisions, 69 achats, par événement t −1,79), −12,2 % (décision au prix payé).

| réglage (délai, marge, K, précédents, billet min) | horaire | sans échange | payé, mêmes décisions : achats, par achat, par événement (t) | payé, décision au prix payé |
|---|---|---|---|---|
| **2 h, 0,05, 2, 3, 0,30 (en direct)** | 202, +20,3 % | 92 | 110, −1,5 %, −8,1 % (−0,73) | 111, +15,7 %, +14,3 % (+1,05) |
| 6 h, 0,05, 2, 3, 0,30 | 196, +18,6 % | 115 | 81, −4,3 %, +3,5 % (+0,31) | 69, +6,1 %, +22,1 % (+1,39) |
| 12 h, 0,05, 2, 3, 0,30 | 199, +28,6 % | 122 | 77, +20,8 %, +14,4 % (+1,14) | 79, +27,7 %, +38,0 % (+2,83) |
| 24 h, 0,05, 2, 3, 0,30 | 186, +20,4 % | 135 | 51, +5,0 %, +12,2 % (+0,77) | 50, +1,1 %, +8,0 % (+0,42) |
| 2 h, marge 0,03 | 218, +18,0 % | 101 | 117, −1,6 %, −8,3 % (−0,74) | 130, +19,0 %, +16,8 % (+1,38) |
| 2 h, marge 0,08 | 160, +27,2 % | 74 | 86, +1,9 %, −14,5 % (−1,13) | 88, +29,7 %, +29,0 % (+1,74) |
| 2 h, K 5, 5 précédents | 147, +27,9 % | 70 | 77, +4,0 %, −1,0 % (−0,07) | 89, +23,5 %, +20,9 % (+1,23) |
| 2 h, sans billet minimum | 437, +8,5 % | 216 | 221, −2,6 %, −1,8 % (−0,16) | 211, −2,3 %, +10,5 % (+0,60) |

Sans « the announcers » ni « anyone », décision au prix payé : 2 h −10,3 % ; 6 h −0,3 % ; 12 h +20,2 %
(par événement t +1,64) ; 24 h +0,8 %. Mêmes décisions : 2 h −20,0 % (t par événement −2,62) ; 6 h
−6,6 % ; 12 h +13,2 % (t +0,17) ; 24 h −1,0 %.

**Fenêtre** (réglage principal) : 1 h → 35 appariées, −2,0 % (décision au prix payé +4,9 %) ;
2 h → 63, +8,6 % (+20,9 %) ; 24 h → 163, +7,1 % (+22,3 %, par événement t +2,32) ; 6 h avec +0,01 → −3,4 %
(+11,0 %). Par prix payé (mêmes décisions) : 0,30-0,70 +3,6 % (73), ≥ 0,70 +2,6 % (32), 0,10-0,30
−103 % (5 : billets dont le prix s'est effondré entre l'heure et l'échange).

**Verdict : trompeuse / écartée.** Aux prix payés, le gain du 20/10 disparaît pour les décisions de
la stratégie (−1,5 % au réglage en direct) ; il venait surtout de marchés sans échange (46 % des
décisions) et des orateurs « the announcers » / « anyone » déjà jugés à part. Le seul réglage qui tient
(12 h après l'ouverture, décision au prix payé) est un délai sur quatre, sur deux mois : ce n'est pas une
preuve. Ne pas inscrire dans `validated_strategies`.

## 2. compteur_tweets_non : indice seulement

**Données** : 182 périodes hebdomadaires de 7 comptes (juillet → 20/10/2026), messages XTracker ; 178
passent le contrôle du règlement ; NON sans NYC Mayor : 147 périodes. 182 événements retrouvés sur Gamma.
1 888 fenêtres d'échanges relevées (médiane 30 échanges, 141 vides). 37 tranches « lourdes » (Elon Musk,
plus de 300 000 $ de volume) : échanges relevés seulement dans les 24 h après chaque achat horaire (pour
Elon, la « décision au prix payé » ne regarde donc que ces instants).

**Reproduction exacte** : mère 4 389 achats, +12,2 % ; NON sans NYC (dispersion 12, marge 0,03,
billet ≥ 0,10) 2 612 achats, 147 périodes, +16,3 %, **par période +12,8 % (t +3,90)**, comme le 21/10.

**Au réglage en direct (fenêtre 6 h)** :
- **1 589 décisions sur 2 612 (61 %) sans aucun échange** de preneur sur le NON dans les 6 h (au prix
  horaire elles faisaient +17,9 %). Les 1 023 appariées : +13,7 % au prix horaire, par période +9,9 %
  (t +2,46).
- **Payé, mêmes décisions : +6,9 % par achat (t +2,91), par période +2,6 % (t +0,65)**, 145 périodes ;
  4 mois sur 4 positifs mais petits (juillet +7,8 %, août +8,6 %, septembre +6,6 %, octobre +2,3 %) ;
  sans les 3 meilleures périodes −0,5 % ; premier achat par tranche +2,0 % par période (t +0,46).
  Prix payé − (horaire + écart) : +0,010 en médiane, **+0,057 en moyenne** (queue de prix bien plus
  chers). Premier échange : 10 parts en médiane.
- **Décision au prix payé : 810 achats, +11,7 % (t +3,63), par période +8,0 % (t +1,49)**, 136 périodes,
  4 mois sur 4 (+13,9 / +12,1 / +11,8 / +7,3 %), moitiés +8,9 % (t +1,15) et +7,1 % (t +0,95) ;
  sans les 3 meilleures périodes +3,5 % (t +0,73).

| réglage (dispersion, marge, billet min) | horaire : achats, par période (t) | sans échange | payé, mêmes décisions : achats, par achat, par période (t) | payé, décision au prix payé |
|---|---|---|---|---|
| **12, 0,03, 0,10 (en direct)** | 2 612, +12,8 % (+3,90) | 1 589 | 1 023, +6,9 %, +2,6 % (+0,65) | 810, +11,7 %, +8,0 % (+1,49) |
| 8, 0,03, 0,10 | 2 701, +9,6 % (+2,91) | 1 596 | 1 105, +4,1 %, −0,8 % (−0,19) | 891, +9,0 %, +3,9 % (+0,71) |
| 16, 0,03, 0,10 | 2 617, +13,3 % (+4,06) | 1 601 | 1 016, +7,4 %, +3,0 % (+0,75) | 770, +13,1 %, +11,3 % (+2,15) |
| 12, 0, 0,10 | 3 805, +8,0 % (+3,28) | 2 275 | 1 530, +3,4 %, +0,8 % (+0,24) | 1 194, +6,5 %, +2,6 % (+0,64) |
| 12, 0,05, 0,10 | 2 252, +15,9 % (+4,48) | 1 404 | 848, +10,6 %, +6,2 % (+1,40) | 639, +16,7 %, +13,7 % (+2,26) |
| 12, 0,03, 0,20 | 2 603, +13,6 % (+4,35) | 1 586 | 1 017, +5,9 %, +3,4 % (+0,90) | 795, +9,5 %, +8,7 % (+1,82) |

**Fenêtre** (réglage en direct ; appariées, horaire des appariées par période, payé mêmes décisions par
achat et par période) : 0,5 h → 201, +12,3 %, +11,2 % / +7,1 % (t +1,14) ; **1 h → 322, +16,7 %,
+12,9 % / +11,3 % (t +1,97)** ; 2 h → 498, +10,1 %, +7,0 % / +4,4 % (t +0,93) ; 6 h → 1 023, +9,9 %,
+6,9 % / +2,6 % (t +0,65) ; 24 h → 1 940, +11,1 %, +5,0 % / +3,0 % (t +0,87) ; 6 h avec +0,01 → +6,6 % /
+2,2 % (t +0,49). Plus l'échange est proche de la décision, plus le prix payé ressemble au prix horaire
et plus le gain reste : les marchés actifs (échange dans l'heure, 322 décisions sur 2 612) gardent
environ +11 % par période, les autres paient plus cher plus tard.

**Par compte** (par période ; horaire → payé mêmes décisions → décision au prix payé) : tedcruz +22,1 %
(t +6,86) → **+1,5 % (t +0,39)** → +15,3 % (t +2,09) ; Zelensky +23,3 % (t +3,65) → +12,0 % (t +1,18) →
+10,7 % (t +0,85) ; WhiteHouse +13,0 % → +1,5 % → +6,7 % ; cz_binance +8,1 % → +2,0 % → +10,7 % ;
Elon −1,3 % → −2,6 % → −2,3 % ; Trump −1,7 % → −3,6 % → −0,2 %. Ted Cruz, le meilleur compte au prix
horaire, avait les marchés les plus minces (4 800 à 28 000 $ par semaine pour 11 tranches).

**Par prix** (par achat ; horaire → payé mêmes décisions → décision au prix payé) :
| prix du NON | horaire | payé, mêmes décisions | payé, décision au prix payé |
|---|---|---|---|
| 0,10-0,30 | 33, +74 % | 26, +95 % | 37, +91 % |
| **0,30-0,70** | 921, +29,8 % | 267, +27,0 % | 295, +25,1 % |
| ≥ 0,70 | 1 658, +7,6 % | 729, **−3,5 %** | 478, **−2,7 %** |

Le NON cher (≥ 0,70), 63 % des achats horaires, ne gagne plus rien aux prix payés. **Le NON payé
0,30-0,70** (déjà repéré le 21/10 au prix horaire : 0,30-0,60 +39 %) reste positif aux six réglages :
mêmes décisions +4,1 % à +17,4 % par période (t +0,48 à +1,93) ; décision au prix payé +9,0 % à +16,8 %
(t +1,09 à +1,91). Au réglage en direct (décision au prix payé) : 295 achats, +25,1 %, 88 périodes
+12,7 % (t +1,47), 4 mois sur 4, moitiés +14,0 % (t +1,34) et +10,3 % (t +0,66), sans les 3 meilleures
périodes +7,2 %, premier achat par tranche +14,2 % (t +1,67) ; 48 dernières heures −53 % (15 achats).

**Verdict : indice, pas retenue aux prix payés.** Le gain existe encore mais il est nettement plus
petit (par période +2,6 % pour les mêmes décisions, +8,0 % en décidant au prix payé, au lieu de
+12,8 %) et n'est plus régulier : t par période sous 1,5 aux six réglages pour les mêmes décisions,
au-dessus pour 3 réglages sur 6 seulement en décidant au prix payé, et presque nul sans les 3
meilleures périodes (−0,5 % et +3,5 %). Tout ce qui reste vient du NON à 0,30-0,70 ; le NON
cher, qui fait l'essentiel des achats, est à zéro. Ne pas inscrire dans `validated_strategies`.

## Recommandations
- **`validated_strategies` : n'y mettre ni l'une ni l'autre.** Elles gardent les seuils normaux de
  `promotion.yaml` (`min_closed_trades: 20`, `min_age_hours: 24`, `min_log_growth: 0.02`,
  `min_t_stat: 1.5`) : l'arène tranchera en direct.
- **mots_prononces** : la remarque de `strategies.yaml` (« passé : +17 % à +27 % ») est à corriger
  (« trompeuse aux prix payés, experiments/prix_payes.md »). Fantôme seulement ; la désactiver si elle
  perd en direct. La fille `mots_prononces_nfl` reste un indice à part (`mentions_annonceurs.md`).
- **compteur_tweets_non** : une fille « NON payé 0,30-0,70 » (`filtres: {prix_min: 0.30, prix_max: 0.70}`,
  le filtre porte sur le prix payé) est le seul morceau qui tient ; fantôme, indice. Si elle confirme en
  direct (au moins 4 périodes hebdomadaires et t ≥ 1,5 sur ses opérations), une inscription allégée
  raisonnable serait `{min_closed_trades: 15, min_age_hours: 168, min_log_growth: 0.01}` (une semaine,
  car chaque pari se règle à la fin de la période). Pas avant.
- En direct, garder le garde-fou qui ne paie jamais un carnet vide ou très écarté : c'est exactement
  là que les deux tests sur l'historique se trompaient.

## Limites
- Le premier échange après la décision n'est pas le prix vendeur À l'instant de décision : il arrive en
  médiane 1,8 h (mentions) et 2,1 h (tweets) plus tard. Les fenêtres courtes (0,5 h, 1 h) sont plus
  justes mais ne gardent que les marchés actifs.
- Le premier échange est petit (10 à 27 parts en médiane) : des mises plus grosses paieraient plus cher.
- Mentions : deux mois seulement (septembre-octobre 2026), 635 marchés ; tweets : quatre mois.
- Elon Musk (tranches lourdes) : la décision au prix payé n'y est regardée qu'aux instants d'achat
  horaire. Elon est perdant dans toutes les façons de compter.
- Environ 40 découpages regardés (8 + 6 réglages, 5 fenêtres, comptes, prix, moitiés) : un seul bon
  morceau ne prouve rien sans le direct.

## Reproduire (depuis la racine, environ 15 minutes de téléchargement)
```
.venv/bin/python experiments/vingt_pistes/scripts/mentions_releve_evenements.py
.venv/bin/python experiments/vingt_pistes/scripts/mentions_releve.py
.venv/bin/python experiments/prix_payes/mentions_releve_echanges.py
.venv/bin/python experiments/prix_payes/mentions_prix_payes.py
.venv/bin/python experiments/vingt_pistes/scripts/tweets_releve_messages.py
.venv/bin/python experiments/vingt_pistes/scripts/tweets_releve_marches.py
.venv/bin/python experiments/prix_payes/tweets_cas.py
.venv/bin/python experiments/prix_payes/tweets_releve_echanges.py
.venv/bin/python experiments/prix_payes/tweets_prix_payes.py
```
`commun.py` : relevé des échanges (fenêtre `start` / `end`, cache gzip), premier prix payé (`paid`),
frais, résumé avec `idea_test.verdict`. Le relevé de `mentions_releve.py` a été lancé avec 3 requêtes à
la fois (au lieu de 4) pour ne jamais dépasser 4 requêtes en tout pendant le relevé des tweets.
