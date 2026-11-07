# Entonnoir 80/20 : le petit morceau qui fait les gains

Pour chaque stratégie qui grandit vite (ou plus vite que sa mère) : par caractéristique, le
« cœur » = les morceaux qui font 80 % des gains (des morceaux gagnants), et la part des paris
qu'ils représentent.
Peu de paris = des pistes, pas des preuves : l'arène tranche avec les filles proposées.

## compteur_truth_v1.0.0 — croissance +21.9% (mère compteur_tweets : +16.6%)

11 opérations, résultat +219.49, rendement moyen +30.13% par mise, confiance +1.59, gagnés 10 pour 7.7 attendus (z +1.83).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,300-0,450, 0,450-0,600 | 27% | 0,300-0,450 (1, +103, +138.6%, +1.2) ; 0,450-0,600 (2, +89, +94.4%, +1.4) ; 0,800-0,850 (3, +22, +20.1%, +0.8) ; 0,900-0,925 (1, +3, +8.8%, +0.3) ; 0,875-0,900 (1, +2, +13.6%, +0.4) ; 0,850-0,875 (1, +2, +14.9%, +0.4) |
| delai | 168 h et plus, 72-168 h | 100% | 168 h et plus (5, +159, +54.0%, +1.6) ; 72-168 h (6, +61, +10.2%, +1.0) |
| issue | oui | 36% | oui (4, +190, +56.9%, +1.6) ; non (7, +29, +14.9%, +1.0) |
| heure_utc | 6-12 h UTC, 18-24 h UTC, 0-6 h UTC | 73% | 6-12 h UTC (1, +103, +138.6%, +1.2) ; 18-24 h UTC (4, +58, +31.1%, +1.1) ; 0-6 h UTC (3, +56, +45.2%, +1.1) ; 12-18 h UTC (3, +3, -22.4%, +0.3) |
| discipline | autre | 100% | autre (11, +219, +30.1%, +1.8) |
| type_pari | autre | 100% | autre (11, +219, +30.1%, +1.8) |
| mode | immédiat | 100% | immédiat (11, +219, +30.1%, +1.8) |
| source | truthsocial.com | 100% | truthsocial.com (11, +219, +30.1%, +1.8) |

## naive_favorite_v1.0.0 — croissance +21.7%

121 opérations, résultat +216.85, rendement moyen +0.35% par mise, confiance +0.13, gagnés 111 pour 110.6 attendus (z +0.13).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,900-0,925, 0,800-0,850, 0,925-0,950 | 84% | 0,900-0,925 (44, +94, -0.3%, -0.0) ; 0,800-0,850 (5, +45, +20.2%, +1.0) ; 0,925-0,950 (53, +36, -5.5%, -1.5) ; 0,875-0,900 (14, +28, +11.9%, +1.3) ; 0,850-0,875 (5, +13, +15.3%, +0.9) |
| delai | 168 h et plus, 24-72 h | 46% | 168 h et plus (21, +109, +10.3%, +1.5) ; 24-72 h (35, +91, -0.0%, -0.0) ; 72-168 h (23, +36, +9.4%, +1.5) ; 0-3 h (2, +5, +6.6%, +0.4) ; 12-24 h (13, -0, -16.0%, -1.9) ; 6-12 h (13, -2, -0.1%, +0.0) |
| issue | non, oui | 79% | non (70, +133, +0.3%, +0.1) ; oui (26, +48, -0.3%, -0.1) ; autre (25, +35, +1.2%, +0.2) |
| heure_utc | 12-18 h UTC | 34% | 12-18 h UTC (41, +212, +7.3%, +1.5) ; 18-24 h UTC (36, +20, +1.1%, +0.2) ; 0-6 h UTC (15, +8, +0.8%, +0.1) ; 6-12 h UTC (29, -22, -10.6%, -2.0) |
| discipline | autre, mlb | 81% | autre (95, +154, -0.1%, -0.0) ; mlb (3, +36, +16.7%, +0.7) ; tennis (3, +9, +9.8%, +0.6) ; counter-strike (5, +7, -11.9%, -0.8) ; football (4, +4, +6.6%, +0.5) ; lol (3, +4, +8.9%, +0.5) |
| type_pari | autre, vainqueur | 90% | autre (72, +117, -1.3%, -0.4) ; vainqueur (37, +92, +3.8%, +0.8) ; score_exact (1, +4, +7.1%, +0.3) ; handicap (4, +3, +8.0%, +0.6) ; partie (1, +1, +9.4%, +0.3) ; total (1, +1, +8.3%, +0.3) |
| mode | immédiat | 100% | immédiat (121, +217, +0.4%, +0.1) |
| source | inconnu, x.com, mlb.com, atptour.com, hltv.org | 56% | inconnu (32, +91, +5.3%, +1.0) ; x.com (25, +37, +1.5%, +0.2) ; mlb.com (3, +36, +16.7%, +0.7) ; atptour.com (3, +9, +9.8%, +0.6) ; hltv.org (5, +7, -11.9%, -0.8) ; ice.com (2, +7, +9.8%, +0.5) |

## nf_sport_v1.0.0 — croissance +21.7% (mère naive_favorite : +21.7%)

1156 opérations, résultat +216.56, rendement moyen +0.61% par mise, confiance +0.55, gagnés 1015 pour 1004.6 attendus (z +0.92).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,800-0,850, 0,925-0,950, 0,900-0,925, 0,875-0,900 | 76% | 0,800-0,850 (371, +155, +1.1%, +0.8) ; 0,925-0,950 (186, +125, +0.5%, +0.3) ; 0,900-0,925 (173, +122, +3.9%, +1.7) ; 0,875-0,900 (144, +99, +2.7%, +1.1) ; 0,950-1,000 (31, +16, -0.1%, -0.4) ; 0,600-0,800 (70, -79, -1.1%, -0.1) |
| delai | 72-168 h, 6-12 h, 0-3 h | 60% | 72-168 h (535, +364, +1.2%, +1.1) ; 6-12 h (68, +198, +8.7%, +1.9) ; 0-3 h (89, +58, +2.8%, +0.8) ; 168 h et plus (55, +52, -1.0%, -0.6) ; 24-72 h (21, +39, +0.2%, +0.2) ; 12-24 h (59, -77, -7.8%, -1.5) |
| issue | non | 10% | non (119, +226, +1.6%, +0.7) ; oui (16, +7, +7.7%, +0.8) ; autre (1021, -16, +0.4%, +0.7) |
| heure_utc | 0-6 h UTC | 15% | 0-6 h UTC (176, +336, +3.9%, +1.4) ; 12-18 h UTC (375, -21, +3.4%, +1.9) ; 6-12 h UTC (271, -31, -3.6%, -1.3) ; 18-24 h UTC (334, -67, -0.9%, -0.2) |
| discipline | inconnu, tennis, football, autre | 69% | inconnu (186, +291, +4.9%, +2.1) ; tennis (418, +187, -0.4%, -0.1) ; football (97, +159, +2.7%, +0.9) ; autre (92, +140, +1.0%, +0.4) ; dota (42, +96, +5.2%, +0.8) ; nba (9, +12, +3.2%, +0.3) |
| type_pari | inconnu, score_exact | 18% | inconnu (186, +291, +4.9%, +2.1) ; score_exact (24, +54, +3.9%, +0.7) ; partie (76, +51, +0.9%, +0.2) ; vainqueur (781, +3, -0.0%, +0.2) ; nul (13, +0, -4.8%, -0.3) ; autre (1, -34, -100.0%, -2.5) |
| mode | immédiat | 100% | immédiat (1156, +217, +0.6%, +0.9) |
| source | inconnu, wtatennis.com, ncaa.com, dotabuff.com, atptour.com, espncricinfo.com, premierleague.com, laliga.com, francefootball.fr | 57% | inconnu (212, +355, +4.8%, +2.2) ; wtatennis.com (134, +167, +1.4%, +0.7) ; ncaa.com (18, +103, +2.9%, -0.0) ; dotabuff.com (45, +90, +3.7%, +0.6) ; atptour.com (210, +76, -0.3%, -0.0) ; espncricinfo.com (16, +55, +13.5%, +1.5) |

## compteur_tweets_non_v1.0.0 — croissance +21.1% (mère compteur_tweets : +16.6%)

45 opérations, résultat +211.32, rendement moyen +9.39% par mise, confiance +1.19, gagnés 38 pour 33.9 attendus (z +1.56).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,450-0,600, 0,600-0,800, 0,800-0,850 | 51% | 0,450-0,600 (6, +105, +51.4%, +1.4) ; 0,600-0,800 (11, +64, +14.8%, +0.8) ; 0,800-0,850 (6, +23, +20.6%, +1.1) ; 0,900-0,925 (5, +12, +10.0%, +0.7) ; 0,850-0,875 (10, +9, +4.1%, +0.3) ; 0,875-0,900 (2, +6, +12.1%, +0.5) |
| delai | 72-168 h, 24-72 h, 12-24 h | 76% | 72-168 h (19, +139, +25.7%, +2.2) ; 24-72 h (13, +40, +5.9%, +0.4) ; 12-24 h (2, +30, +6.6%, +0.2) ; 168 h et plus (5, +17, +14.6%, +0.8) ; 3-6 h (4, -5, -7.4%, -0.5) ; 0-3 h (2, -10, -100.0%, -0.9) |
| issue | non | 100% | non (45, +211, +9.4%, +1.6) |
| heure_utc | 6-12 h UTC, 0-6 h UTC | 62% | 6-12 h UTC (12, +124, +31.4%, +1.6) ; 0-6 h UTC (16, +73, +14.3%, +1.3) ; 18-24 h UTC (9, +21, -1.5%, +0.2) ; 12-18 h UTC (8, -5, -21.3%, -0.4) |
| discipline | autre | 100% | autre (45, +211, +9.4%, +1.6) |
| type_pari | autre | 100% | autre (45, +211, +9.4%, +1.6) |
| mode | immédiat | 100% | immédiat (45, +211, +9.4%, +1.6) |
| source | x.com | 82% | x.com (37, +179, +6.2%, +1.1) ; truthsocial.com (8, +32, +23.9%, +1.4) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 72-168 h : 19 opérations, +138.80, +25.7% par mise, gagnés 19/15.4 → `filtres: {'echeance_min': 72, 'echeance_max': 168}` (déjà dans l'arène)

## nf_sport_prix_haut_v1.0.0 — croissance +18.4% (mère naive_favorite : +21.7%)

696 opérations, résultat +184.11, rendement moyen -0.22% par mise, confiance -0.19, gagnés 634 pour 632.8 attendus (z +0.15).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,925-0,950, 0,850-0,875 | 34% | 0,925-0,950 (198, +310, +2.6%, +1.4) ; 0,850-0,875 (42, +109, +1.3%, +0.3) ; 0,950-1,000 (19, +71, +5.0%, +1.0) ; 0,800-0,850 (1, +17, +16.8%, +0.4) ; 0,875-0,900 (192, -143, -3.7%, -1.2) ; 0,900-0,925 (244, -180, -0.5%, -0.1) |
| delai | 168 h et plus, 72-168 h, 24-72 h | 54% | 168 h et plus (31, +109, +6.2%, +1.2) ; 72-168 h (327, +74, -0.7%, -0.2) ; 24-72 h (20, +59, +3.9%, +0.6) ; 3-6 h (185, +12, -1.1%, -0.2) ; 12-24 h (35, +10, -0.7%, -0.1) ; 6-12 h (29, -16, +1.4%, +0.3) |
| issue | autre, non | 99% | autre (598, +85, -0.2%, +0.1) ; non (88, +84, -0.0%, +0.1) ; oui (10, +15, -1.1%, -0.1) |
| heure_utc | 0-6 h UTC, 6-12 h UTC | 38% | 0-6 h UTC (126, +221, +2.4%, +0.9) ; 6-12 h UTC (135, +96, +0.4%, +0.3) ; 12-18 h UTC (187, +14, -2.8%, -1.0) ; 18-24 h UTC (248, -147, +0.0%, +0.2) |
| discipline | inconnu, football, autre | 34% | inconnu (95, +233, +4.2%, +1.5) ; football (84, +113, +0.9%, +0.4) ; autre (54, +56, +2.8%, +0.8) ; nba (4, +26, +10.9%, +0.7) ; counter-strike (111, +26, +1.2%, +0.6) ; mlb (7, +18, +9.9%, +0.8) |
| type_pari | inconnu, score_exact, total | 21% | inconnu (95, +233, +4.2%, +1.5) ; score_exact (23, +62, -1.6%, -0.2) ; total (26, +48, +4.3%, +0.8) ; partie (34, +23, +1.0%, +0.3) ; nul (6, +16, +9.5%, +0.8) ; handicap (30, +11, +5.2%, +1.0) |
| mode | immédiat | 100% | immédiat (696, +184, -0.2%, +0.1) |
| source | inconnu, wtatennis.com, premierleague.com, espncricinfo.com, legaseriea.it, laliga.com, ligamx.net, hltv.org, nba.com, cbf.com.br | 52% | inconnu (120, +300, +3.1%, +1.3) ; wtatennis.com (89, +195, +1.5%, +0.6) ; premierleague.com (8, +41, +7.4%, +0.8) ; espncricinfo.com (10, +40, +10.4%, +1.1) ; legaseriea.it (9, +40, +9.6%, +0.9) ; laliga.com (7, +34, +9.5%, +0.8) |

## nf_tennis_v1.0.0 — croissance +17.6% (mère nf_sport_patiente : -1.8%)

86 opérations, résultat +176.21, rendement moyen +4.02% par mise, confiance +1.02, gagnés 77 pour 73.7 attendus (z +1.03).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,800-0,850, 0,900-0,925 | 45% | 0,800-0,850 (27, +139, +11.6%, +1.4) ; 0,900-0,925 (12, +101, +9.9%, +1.1) ; 0,950-1,000 (6, +16, +4.8%, +0.6) ; 0,875-0,900 (8, +1, -2.1%, -0.1) ; 0,600-0,800 (13, +1, -0.6%, -0.0) ; 0,850-0,875 (14, -11, -1.4%, -0.1) |
| delai | 72-168 h | 98% | 72-168 h (84, +158, +3.6%, +0.9) ; 168 h et plus (2, +18, +23.0%, +0.7) |
| issue | autre | 100% | autre (86, +176, +4.0%, +1.0) |
| heure_utc | 12-18 h UTC, 6-12 h UTC | 63% | 12-18 h UTC (20, +177, +18.7%, +2.0) ; 6-12 h UTC (34, +42, +3.5%, +0.5) ; 18-24 h UTC (19, +14, +2.0%, +0.3) ; 0-6 h UTC (13, -56, -14.2%, -1.2) |
| discipline | tennis | 79% | tennis (68, +147, +4.8%, +1.1) ; inconnu (18, +30, +1.2%, +0.2) |
| type_pari | vainqueur | 79% | vainqueur (68, +147, +4.8%, +1.1) ; inconnu (18, +30, +1.2%, +0.2) |
| mode | immédiat | 100% | immédiat (86, +176, +4.0%, +1.0) |
| source | atptour.com, inconnu, itftennis.com | 92% | atptour.com (46, +110, +7.5%, +1.2) ; inconnu (18, +30, +1.2%, +0.2) ; itftennis.com (15, +21, -3.3%, -0.2) ; wtatennis.com (7, +16, +4.3%, +0.3) |

## compteur_tweets_v1.0.0 — croissance +16.6%

107 opérations, résultat +165.63, rendement moyen +16.64% par mise, confiance +1.41, gagnés 78 pour 68.4 attendus (z +2.45).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,300-0,450, 0,450-0,600, 0,100-0,200, 0,800-0,850, 0,850-0,875 | 61% | 0,300-0,450 (3, +71, +149.6%, +2.1) ; 0,450-0,600 (12, +71, +54.2%, +2.1) ; 0,100-0,200 (17, +42, +13.8%, +0.4) ; 0,800-0,850 (13, +40, +11.4%, +0.9) ; 0,850-0,875 (20, +33, +10.1%, +1.2) ; 0,900-0,925 (6, +24, +8.9%, +0.7) |
| delai | 72-168 h, 168 h et plus | 56% | 72-168 h (34, +208, +64.6%, +3.7) ; 168 h et plus (26, +100, +13.2%, +1.4) ; 0-3 h (2, -7, -46.0%, -0.1) ; 3-6 h (2, -29, -100.0%, -2.0) ; 24-72 h (39, -48, -13.7%, +0.2) ; 12-24 h (4, -58, +16.4%, -0.8) |
| issue | oui, non | 100% | oui (34, +102, +35.9%, +1.7) ; non (73, +64, +7.7%, +1.8) |
| heure_utc | 12-18 h UTC, 6-12 h UTC | 71% | 12-18 h UTC (60, +114, +26.7%, +2.3) ; 6-12 h UTC (16, +75, +14.6%, +1.9) ; 0-6 h UTC (8, +45, +89.6%, +1.9) ; 18-24 h UTC (23, -69, -33.7%, -1.0) |
| discipline | autre | 97% | autre (104, +213, +17.5%, +2.6) ; inconnu (3, -48, -14.5%, -0.3) |
| type_pari | autre | 97% | autre (104, +213, +17.5%, +2.6) ; inconnu (3, -48, -14.5%, -0.3) |
| mode | immédiat | 100% | immédiat (107, +166, +16.6%, +2.5) |
| source | truthsocial.com, x.com | 97% | truthsocial.com (15, +127, +43.3%, +2.5) ; x.com (89, +86, +13.2%, +1.7) ; inconnu (3, -48, -14.5%, -0.3) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 72-168 h : 34 opérations, +208.22, +64.6% par mise, gagnés 30/21.6 → `filtres: {'echeance_min': 72, 'echeance_max': 168}` (déjà dans l'arène)
- heure d'achat 12-18 h UTC : 60 opérations, +114.20, +26.7% par mise, gagnés 47/40.4 → `filtres: {'heure_utc': [12, 18]}` (déjà dans l'arène)
- prix payé 0,450-0,600 : 12 opérations, +70.99, +54.2% par mise, gagnés 10/6.3 → `filtres: {'prix_min': 0.45, 'prix_max': 0.6}`
- délai jusqu'à la fin 72-168 h + heure d'achat 12-18 h UTC : 20 opérations, +121.18, +78.8% par mise, gagnés 18/12.6 → `filtres: {'echeance_min': 72, 'echeance_max': 168, 'heure_utc': [12, 18]}` (déjà dans l'arène)

## compteur_tweets_oui_v1.0.0 — croissance +16.0% (mère compteur_tweets : +16.6%)

25 opérations, résultat +159.83, rendement moyen +1.04% par mise, confiance +0.03, gagnés 9 pour 8.4 attendus (z +0.29).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,450-0,600, 0,600-0,800 | 24% | 0,450-0,600 (4, +172, +37.4%, +0.9) ; 0,600-0,800 (2, +126, +53.6%, +1.0) ; 0,850-0,875 (1, +2, +16.0%, +0.4) ; 0,100-0,200 (9, -10, +44.4%, +0.6) ; 0,300-0,450 (4, -31, -36.6%, -0.5) ; 0,200-0,300 (5, -99, -100.0%, -1.3) |
| delai | 72-168 h, 168 h et plus, 12-24 h | 28% | 72-168 h (2, +104, +254.8%, +1.9) ; 168 h et plus (1, +100, +77.0%, +0.9) ; 12-24 h (4, +62, -6.9%, +0.1) ; 6-12 h (1, -1, -100.0%, -0.4) ; 24-72 h (17, -105, -25.5%, -0.5) |
| issue | oui | 100% | oui (25, +160, +1.0%, +0.3) |
| heure_utc | 0-6 h UTC | 40% | 0-6 h UTC (10, +255, +21.7%, +0.8) ; 6-12 h UTC (4, -11, +83.7%, +0.7) ; 12-18 h UTC (6, -14, -23.6%, +0.0) ; 18-24 h UTC (5, -70, -76.8%, -1.0) |
| discipline | autre | 100% | autre (25, +160, +1.0%, +0.3) |
| type_pari | autre | 100% | autre (25, +160, +1.0%, +0.3) |
| mode | immédiat | 100% | immédiat (25, +160, +1.0%, +0.3) |
| source | truthsocial.com | 16% | truthsocial.com (4, +214, +21.1%, +0.9) ; x.com (21, -54, -2.8%, -0.1) |

## naive_favorite_sans_fin_v1.0.0 — croissance +15.9%

30 opérations, résultat +159.23, rendement moyen +5.28% par mise, confiance +1.43, gagnés 29 pour 27.5 attendus (z +1.00).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,925-0,950, 0,800-0,850, 0,900-0,925 | 90% | 0,925-0,950 (15, +66, +6.6%, +1.0) ; 0,800-0,850 (2, +34, +20.4%, +0.7) ; 0,900-0,925 (10, +32, -1.9%, -0.2) ; 0,875-0,900 (2, +25, +11.6%, +0.5) ; 0,850-0,875 (1, +2, +15.1%, +0.4) |
| delai | 168 h et plus, 72-168 h | 67% | 168 h et plus (11, +92, +10.9%, +1.1) ; 72-168 h (9, +36, -4.6%, -0.5) ; 24-72 h (10, +31, +8.0%, +0.9) |
| issue | non | 83% | non (25, +136, +4.9%, +0.8) ; oui (5, +23, +7.3%, +0.6) |
| heure_utc | 18-24 h UTC, 12-18 h UTC | 80% | 18-24 h UTC (21, +124, +9.5%, +1.4) ; 12-18 h UTC (3, +29, +7.8%, +0.5) ; 6-12 h UTC (5, +6, -14.2%, -1.1) ; 0-6 h UTC (1, +0, +6.5%, +0.3) |
| discipline | autre, mlb | 93% | autre (26, +122, +3.9%, +0.7) ; mlb (2, +34, +20.4%, +0.7) ; lol (1, +2, +8.7%, +0.3) ; football (1, +1, +7.1%, +0.3) |
| type_pari | vainqueur, autre | 100% | vainqueur (11, +83, +10.5%, +1.1) ; autre (19, +76, +2.3%, +0.4) |
| mode | immédiat | 100% | immédiat (30, +159, +5.3%, +1.0) |
| source | inconnu, mlb.com, x.com, dadosabertos.tse.jus.br, ice.com | 63% | inconnu (6, +47, +7.8%, +0.7) ; mlb.com (2, +34, +20.4%, +0.7) ; x.com (9, +32, +8.1%, +0.9) ; dadosabertos.tse.jus.br (1, +16, +9.6%, +0.3) ; ice.com (1, +16, +11.9%, +0.3) ; fec.gov (3, +11, +6.9%, +0.5) |

## nf_sport_non_v1.0.0 — croissance +13.6% (mère naive_favorite : +21.7%)

104 opérations, résultat +135.69, rendement moyen +2.03% par mise, confiance +0.74, gagnés 97 pour 94.7 attendus (z +0.81).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,900-0,925, 0,875-0,900 | 38% | 0,900-0,925 (27, +319, +9.2%, +1.6) ; 0,875-0,900 (13, +80, +3.4%, +0.4) ; 0,800-0,850 (5, +40, +20.3%, +1.0) ; 0,850-0,875 (11, -127, -16.3%, -1.3) ; 0,925-0,950 (48, -177, -0.0%, +0.1) |
| delai | 3-6 h, 12-24 h, 168 h et plus | 47% | 3-6 h (9, +126, +10.0%, +1.0) ; 12-24 h (24, +117, +4.3%, +0.8) ; 168 h et plus (16, +76, +4.4%, +0.6) ; 6-12 h (10, +34, -1.9%, -0.1) ; 72-168 h (6, +26, +11.9%, +0.9) ; 24-72 h (12, -24, -0.2%, +0.0) |
| issue | non | 100% | non (104, +136, +2.0%, +0.8) |
| heure_utc | 6-12 h UTC, 12-18 h UTC | 40% | 6-12 h UTC (18, +161, +7.9%, +1.2) ; 12-18 h UTC (24, +89, +4.7%, +0.8) ; 0-6 h UTC (23, +16, +0.1%, +0.1) ; 18-24 h UTC (39, -131, -1.2%, -0.2) |
| discipline | autre, lol, football | 76% | autre (11, +84, +9.3%, +1.0) ; lol (2, +56, +10.7%, +0.5) ; football (66, +52, +2.2%, +0.7) ; inconnu (9, +23, -3.4%, -0.3) ; f1 (9, +10, -0.8%, -0.0) ; mlb (2, +6, +16.6%, +0.6) |
| type_pari | score_exact | 34% | score_exact (35, +288, +7.6%, +1.7) ; inconnu (9, +23, -3.4%, -0.3) ; partie (1, +14, +9.4%, +0.3) ; nul (7, -32, -4.2%, -0.2) ; vainqueur (50, -68, +1.5%, +0.4) ; autre (2, -91, -40.3%, -1.4) |
| mode | immédiat | 100% | immédiat (104, +136, +2.0%, +0.8) |
| source | inconnu, legaseriea.it, laliga.com, lolesports.com | 55% | inconnu (45, +325, +5.5%, +1.4) ; legaseriea.it (5, +131, +10.6%, +0.8) ; laliga.com (5, +90, +9.7%, +0.7) ; lolesports.com (2, +56, +10.7%, +0.5) ; ligamx.net (2, +31, +11.2%, +0.5) ; slstat.com (2, +26, +7.1%, +0.4) |

## nf_court_football_soir_v1.0.0 — croissance +13.4% (mère nf_court : -10.8%)

96 opérations, résultat +134.43, rendement moyen +2.88% par mise, confiance +0.89, gagnés 88 pour 85.4 attendus (z +0.85).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,925-0,950, 0,800-0,850, 0,850-0,875, 0,900-0,925 | 85% | 0,925-0,950 (29, +154, -0.9%, -0.1) ; 0,800-0,850 (16, +147, +21.2%, +1.9) ; 0,850-0,875 (16, +113, +8.3%, +0.9) ; 0,900-0,925 (21, +83, -6.3%, -0.8) ; 0,600-0,800 (2, +36, +23.8%, +0.7) ; 0,875-0,900 (10, -141, +0.8%, +0.1) |
| delai | 0-3 h | 72% | 0-3 h (69, +297, +4.3%, +1.1) ; 3-6 h (3, -69, -27.8%, -1.3) ; 12-24 h (24, -93, +2.6%, +0.4) |
| issue | autre, oui | 25% | autre (16, +104, +10.3%, +1.3) ; oui (8, +46, +1.7%, +0.1) ; non (72, -16, +1.4%, +0.3) |
| heure_utc | 18-24 h UTC | 100% | 18-24 h UTC (96, +134, +2.9%, +0.8) |
| discipline | football, inconnu | 100% | football (83, +86, +2.7%, +0.8) ; inconnu (13, +49, +3.9%, +0.4) |
| type_pari | vainqueur, nul, inconnu, total | 71% | vainqueur (41, +98, +3.0%, +0.5) ; nul (7, +77, +15.6%, +1.1) ; inconnu (13, +49, +3.9%, +0.4) ; total (7, +41, +10.2%, +0.9) ; handicap (5, +26, +11.2%, +0.8) ; score_exact (23, -156, -5.8%, -0.9) |
| mode | immédiat | 100% | immédiat (96, +134, +2.9%, +0.8) |
| source | laliga.com, legaseriea.it, premierleague.com, ligue1.com, bundesliga.com, ligaportugal.pt | 30% | laliga.com (7, +92, +17.3%, +1.1) ; legaseriea.it (5, +76, +12.0%, +0.8) ; premierleague.com (6, +67, +9.6%, +0.8) ; ligue1.com (5, +31, +14.8%, +0.9) ; bundesliga.com (1, +31, +15.5%, +0.4) ; ligaportugal.pt (5, +24, -10.0%, -0.7) |

## nf_sport_sans_fin_v1.0.0 — croissance +12.6% (mère naive_favorite : +21.7%)

62 opérations, résultat +126.20, rendement moyen -2.34% par mise, confiance -0.47, gagnés 53 pour 54.3 attendus (z -0.53).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,800-0,850, 0,900-0,925, 0,850-0,875 | 58% | 0,800-0,850 (24, +85, -9.4%, -0.9) ; 0,900-0,925 (9, +42, +9.2%, +0.9) ; 0,850-0,875 (3, +22, +15.9%, +0.7) ; 0,600-0,800 (1, +7, +24.2%, +0.5) ; 0,950-1,000 (1, +4, +5.0%, +0.2) ; 0,925-0,950 (17, -3, -3.0%, -0.9) |
| delai | 72-168 h, 168 h et plus | 74% | 72-168 h (31, +76, -5.8%, -1.0) ; 168 h et plus (15, +60, +11.2%, +1.3) ; 24-72 h (16, -10, -8.4%, -0.8) |
| issue | non, autre | 89% | non (29, +82, +2.7%, +0.5) ; autre (26, +75, -8.0%, -1.1) ; oui (7, -31, -1.9%, -0.1) |
| heure_utc | 12-18 h UTC, 0-6 h UTC, 6-12 h UTC | 55% | 12-18 h UTC (14, +109, +13.5%, +1.4) ; 0-6 h UTC (15, +59, -1.8%, -0.1) ; 6-12 h UTC (5, +52, +2.5%, -0.6) ; 18-24 h UTC (28, -94, -11.4%, -1.5) |
| discipline | mlb, lol, autre, nfl | 40% | mlb (3, +39, +19.9%, +0.8) ; lol (10, +35, -7.2%, -0.5) ; autre (6, +26, +9.1%, +0.8) ; nfl (6, +25, -9.9%, -1.1) ; counter-strike (6, +11, -8.6%, -0.5) ; ufc (1, +7, +15.5%, +0.4) |
| type_pari | vainqueur, handicap, total | 90% | vainqueur (50, +65, -6.2%, -1.2) ; handicap (3, +20, +17.4%, +0.7) ; total (3, +19, +16.9%, +0.7) ; nul (3, +10, +10.4%, +0.6) ; score_exact (2, +6, +6.1%, +0.4) ; inconnu (1, +6, +18.5%, +0.4) |
| mode | immédiat | 100% | immédiat (62, +126, -2.3%, -0.5) |
| source | mlb.com, laliga.com, premierleague.com, inconnu, nfl.com, gol.gg, lolesports.com, hltv.org | 63% | mlb.com (3, +39, +19.9%, +0.8) ; laliga.com (5, +34, +13.5%, +0.8) ; premierleague.com (4, +28, +13.6%, +0.8) ; inconnu (6, +25, +8.5%, +0.7) ; nfl.com (5, +25, -2.6%, -0.1) ; gol.gg (8, +20, -11.7%, -0.7) |

## nf_oui_v1.0.0 — croissance +11.6% (mère naive_favorite : +21.7%)

37 opérations, résultat +116.11, rendement moyen -0.93% par mise, confiance -0.19, gagnés 34 pour 34.2 attendus (z -0.12).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,925-0,950 | 73% | 0,925-0,950 (27, +117, +6.6%, +1.4) ; 0,900-0,925 (6, +11, -8.4%, -0.6) ; 0,800-0,850 (1, +4, +24.1%, +0.5) ; 0,875-0,900 (3, -16, -61.9%, -3.0) |
| delai | 24-72 h, 168 h et plus | 73% | 24-72 h (18, +64, +1.2%, +0.2) ; 168 h et plus (9, +55, +7.5%, +0.8) ; 3-6 h (2, +6, +15.9%, +0.6) ; 0-3 h (1, +1, +6.0%, +0.2) ; 72-168 h (6, -3, -10.0%, -0.8) ; 6-12 h (1, -7, -100.0%, -3.0) |
| issue | oui | 100% | oui (37, +116, -0.9%, -0.1) |
| heure_utc | 12-18 h UTC, 0-6 h UTC, 6-12 h UTC | 73% | 12-18 h UTC (10, +44, +7.0%, +0.8) ; 0-6 h UTC (13, +34, +0.3%, +0.1) ; 6-12 h UTC (4, +28, +8.6%, +0.6) ; 18-24 h UTC (10, +10, -14.3%, -1.5) |
| discipline | autre | 97% | autre (36, +110, -1.2%, -0.2) ; mlb (1, +6, +9.7%, +0.3) |
| type_pari | autre, vainqueur | 100% | autre (27, +75, -3.8%, -0.6) ; vainqueur (10, +41, +6.9%, +0.8) |
| mode | immédiat | 100% | immédiat (37, +116, -0.9%, -0.1) |
| source | inconnu, binance.com, federalreserve.gov | 84% | inconnu (22, +54, -6.8%, -1.0) ; binance.com (8, +29, +6.6%, +0.8) ; federalreserve.gov (1, +10, +6.8%, +0.3) ; fec.gov (1, +7, +6.1%, +0.2) ; mlb.com (1, +6, +9.7%, +0.3) ; app.pyth.com (1, +4, +6.1%, +0.2) |

## seismes_marche_v1.0.0 — croissance +11.5%

29 opérations, résultat +115.09, rendement moyen +39.92% par mise, confiance +1.27, gagnés 22 pour 17.9 attendus (z +1.99).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,200-0,300, 0,875-0,900, 0,850-0,875 | 45% | 0,200-0,300 (5, +56, +72.4%, +0.9) ; 0,875-0,900 (3, +23, +12.9%, +0.6) ; 0,850-0,875 (5, +21, +15.9%, +0.9) ; 0,900-0,925 (2, +9, +9.6%, +0.4) ; 0,600-0,800 (8, +8, +22.5%, +1.0) ; 0,800-0,850 (2, +7, +22.7%, +0.7) |
| delai | 24-72 h, 72-168 h | 86% | 24-72 h (18, +66, +22.3%, +1.3) ; 72-168 h (7, +28, +99.6%, +1.4) ; 12-24 h (4, +21, +14.7%, +0.8) |
| issue | non | 55% | non (16, +108, +28.2%, +1.5) ; oui (13, +7, +54.4%, +1.3) |
| heure_utc | 12-18 h UTC, 18-24 h UTC | 41% | 12-18 h UTC (5, +80, +47.9%, +1.2) ; 18-24 h UTC (7, +40, +17.0%, +1.1) ; 0-6 h UTC (6, +28, +124.6%, +1.9) ; 6-12 h UTC (11, -33, +4.7%, +0.3) |
| discipline | autre | 100% | autre (29, +115, +39.9%, +2.0) |
| type_pari | autre | 100% | autre (29, +115, +39.9%, +2.0) |
| mode | immédiat | 100% | immédiat (29, +115, +39.9%, +2.0) |
| source | earthquake.usgs.gov | 100% | earthquake.usgs.gov (29, +115, +39.9%, +2.0) |

## compteur_tweets_48h_audace_v1.0.0 — croissance +11.2% (mère compteur_tweets : +16.6%)

28 opérations, résultat +112.28, rendement moyen +23.71% par mise, confiance +1.21, gagnés 23 pour 20.1 attendus (z +1.40).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,450-0,600, 0,800-0,850, 0,900-0,925 | 46% | 0,450-0,600 (3, +105, +95.6%, +1.7) ; 0,800-0,850 (8, +34, +5.1%, +0.3) ; 0,900-0,925 (2, +13, +8.5%, +0.4) ; 0,850-0,875 (8, +12, +1.6%, +0.1) ; 0,100-0,200 (3, +10, +88.3%, +0.8) ; 0,600-0,800 (4, -62, +10.4%, +0.3) |
| delai | 72-168 h, 168 h et plus | 71% | 72-168 h (12, +168, +71.8%, +2.5) ; 168 h et plus (8, +45, -1.2%, +0.2) ; 24-72 h (8, -101, -23.5%, -0.8) |
| issue | non, oui | 100% | non (21, +68, +4.4%, +0.7) ; oui (7, +45, +81.6%, +1.4) |
| heure_utc | 12-18 h UTC, 6-12 h UTC, 0-6 h UTC | 86% | 12-18 h UTC (17, +68, +10.8%, +0.9) ; 6-12 h UTC (6, +31, +11.0%, +1.0) ; 0-6 h UTC (1, +30, +464.8%, +2.2) ; 18-24 h UTC (4, -17, -12.8%, -0.6) |
| discipline | autre | 93% | autre (26, +193, +28.6%, +1.7) ; inconnu (2, -81, -40.3%, -0.8) |
| type_pari | autre | 93% | autre (26, +193, +28.6%, +1.7) ; inconnu (2, -81, -40.3%, -0.8) |
| mode | immédiat | 100% | immédiat (28, +112, +23.7%, +1.4) |
| source | truthsocial.com, x.com | 93% | truthsocial.com (4, +97, +56.9%, +1.5) ; x.com (22, +96, +23.5%, +1.2) ; inconnu (2, -81, -40.3%, -0.8) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 72-168 h : 12 opérations, +168.11, +71.8% par mise, gagnés 12/8.5 → `filtres: {'echeance_min': 72, 'echeance_max': 168}` (déjà dans l'arène)

## nf_moyen_v1.0.0 — croissance +10.9% (mère naive_favorite : +21.7%)

167 opérations, résultat +108.64, rendement moyen -0.40% par mise, confiance -0.16, gagnés 151 pour 151.4 attendus (z -0.11).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,850-0,875, 0,875-0,900, 0,925-0,950, 0,900-0,925 | 87% | 0,850-0,875 (13, +43, -11.0%, -0.9) ; 0,875-0,900 (21, +42, +12.2%, +1.6) ; 0,925-0,950 (66, +23, -4.9%, -1.5) ; 0,900-0,925 (46, +20, -0.3%, -0.0) ; 0,950-1,000 (3, +17, +5.2%, +0.4) ; 0,800-0,850 (18, -37, +7.6%, +0.8) |
| delai | 24-72 h | 57% | 24-72 h (96, +127, +3.7%, +1.2) ; 168 h et plus (3, +12, +8.3%, +0.5) ; 72-168 h (68, -30, -6.6%, -1.7) |
| issue | oui, non | 97% | oui (44, +74, -2.7%, -0.5) ; non (118, +69, +0.7%, +0.3) ; autre (5, -35, -7.0%, -0.3) |
| heure_utc | 18-24 h UTC | 38% | 18-24 h UTC (64, +189, +5.6%, +1.4) ; 6-12 h UTC (50, +47, -0.9%, -0.1) ; 0-6 h UTC (26, -53, -6.9%, -1.2) ; 12-18 h UTC (27, -75, -7.4%, -1.2) |
| discipline | autre, football | 96% | autre (153, +98, -0.7%, -0.2) ; football (7, +31, +7.5%, +0.7) ; mlb (1, +14, +9.7%, +0.3) ; lol (2, +2, +13.3%, +0.5) ; f1 (1, +0, +6.1%, +0.2) ; nfl (3, -37, -20.5%, -0.7) |
| type_pari | vainqueur, autre | 98% | vainqueur (38, +60, +8.2%, +1.6) ; autre (125, +43, -3.3%, -1.2) ; score_exact (2, +5, +6.6%, +0.4) ; handicap (1, +1, +18.5%, +0.4) ; nul (1, +0, +8.3%, +0.3) |
| mode | immédiat | 100% | immédiat (167, +109, -0.4%, -0.1) |
| source | binance.com, x.com, arena.ai, federalreserve.gov, laliga.com, mlb.com, uefa.com | 44% | binance.com (34, +64, -1.2%, -0.2) ; x.com (30, +38, -0.9%, -0.2) ; arena.ai (2, +36, +13.1%, +0.5) ; federalreserve.gov (2, +17, +5.3%, +0.3) ; laliga.com (1, +14, +7.1%, +0.3) ; mlb.com (1, +14, +9.7%, +0.3) |

## crypto_threshold_v1.0.0 — croissance +10.1%

18 opérations, résultat +100.81, rendement moyen +67.83% par mise, confiance +0.89, gagnés 7 pour 6.5 attendus (z +0.33).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,300-0,450, 0,875-0,900, 0,000-0,100 | 56% | 0,300-0,450 (5, +172, +42.9%, +0.9) ; 0,875-0,900 (1, +85, +12.8%, +0.4) ; 0,000-0,100 (4, +64, +179.5%, +1.4) ; 0,100-0,200 (3, +42, +200.2%, +1.1) ; 0,450-0,600 (1, +13, +74.9%, +0.9) ; 0,900-0,925 (1, -9, -100.0%, -3.4) |
| delai | 24-72 h, 72-168 h | 72% | 24-72 h (10, +194, +83.3%, +1.4) ; 72-168 h (3, +44, +200.2%, +0.7) ; 168 h et plus (1, +13, +74.9%, +0.9) ; 3-6 h (1, -22, -100.0%, -0.8) ; 0-3 h (3, -128, -62.4%, -3.7) |
| issue | non, oui | 100% | non (12, +58, +127.8%, +0.6) ; oui (6, +43, -52.0%, -0.3) |
| heure_utc | 12-18 h UTC | 50% | 12-18 h UTC (9, +113, +116.1%, +0.3) ; 6-12 h UTC (7, -4, +28.7%, +0.1) ; 18-24 h UTC (2, -9, -12.5%, +0.1) |
| discipline | autre | 83% | autre (15, +229, +93.9%, +1.5) ; inconnu (3, -128, -62.4%, -3.7) |
| type_pari | autre | 83% | autre (15, +229, +93.9%, +1.5) ; inconnu (3, -128, -62.4%, -3.7) |
| mode | immédiat | 100% | immédiat (18, +101, +67.8%, +0.3) |
| source | binance.com | 83% | binance.com (15, +229, +93.9%, +1.5) ; inconnu (3, -128, -62.4%, -3.7) |

## nf_sport_18_24h_v1.0.0 — croissance +8.1% (mère nf_sport : +21.7%)

401 opérations, résultat +81.41, rendement moyen -0.26% par mise, confiance -0.14, gagnés 352 pour 351.1 attendus (z +0.13).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,925-0,950, 0,850-0,875, 0,875-0,900 | 45% | 0,925-0,950 (75, +270, +3.6%, +1.3) ; 0,850-0,875 (61, +237, +2.2%, +0.6) ; 0,875-0,900 (44, +88, -0.9%, -0.1) ; 0,600-0,800 (21, +34, +6.4%, +0.7) ; 0,950-1,000 (11, +21, +5.0%, +0.8) ; 0,900-0,925 (74, -48, -2.6%, -0.6) |
| delai | 0-3 h, 72-168 h | 56% | 0-3 h (72, +330, +4.5%, +1.1) ; 72-168 h (152, +144, +2.5%, +1.0) ; 168 h et plus (22, +45, -0.4%, -0.3) ; 24-72 h (8, -2, -12.3%, -0.8) ; 6-12 h (20, -5, -6.9%, -0.6) ; 3-6 h (106, -127, -3.6%, -0.8) |
| issue | non, oui | 18% | non (66, +140, +1.4%, +0.4) ; oui (8, +38, +1.1%, +0.1) ; autre (327, -97, -0.6%, -0.0) |
| heure_utc | 18-24 h UTC | 100% | 18-24 h UTC (401, +81, -0.3%, +0.1) |
| discipline | football, inconnu, autre | 33% | football (55, +199, +3.8%, +0.9) ; inconnu (44, +130, +4.3%, +0.8) ; autre (33, +85, +3.2%, +0.6) ; nfl (15, +29, -0.1%, +0.1) ; dota (11, +21, +2.4%, +0.3) ; valorant (4, +14, +13.2%, +0.7) |
| type_pari | inconnu, partie, score_exact, handicap | 26% | inconnu (44, +130, +4.3%, +0.8) ; partie (17, +63, +0.7%, +0.1) ; score_exact (17, +58, -4.0%, -0.5) ; handicap (26, +39, -3.9%, -0.3) ; total (14, +34, +4.2%, +0.5) ; nul (5, +28, +13.9%, +0.8) |
| mode | immédiat | 100% | immédiat (401, +81, -0.3%, +0.1) |
| source | inconnu, ncaa.com, wtatennis.com, legaseriea.it, itftennis.com, premierleague.com, uefa.com, ligaportugal.pt, nfl.com, dotabuff.com, francefootball.fr | 42% | inconnu (61, +188, +2.0%, +0.5) ; ncaa.com (8, +70, +15.4%, +1.1) ; wtatennis.com (26, +63, -0.4%, +0.1) ; legaseriea.it (5, +39, +10.9%, +0.8) ; itftennis.com (18, +39, +4.9%, +0.6) ; premierleague.com (5, +34, +10.3%, +0.7) |

## compteur_tweets_72_168h_v1.0.0 — croissance +8.0% (mère compteur_tweets : +16.6%)

24 opérations, résultat +80.11, rendement moyen +35.25% par mise, confiance +1.64, gagnés 21 pour 16.0 attendus (z +2.62).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,450-0,600, 0,600-0,800, 0,800-0,850 | 50% | 0,450-0,600 (3, +41, +91.5%, +1.7) ; 0,600-0,800 (5, +27, +42.9%, +1.5) ; 0,800-0,850 (4, +10, +20.7%, +0.9) ; 0,850-0,875 (4, +8, +15.5%, +0.8) ; 0,900-0,925 (2, +6, +9.8%, +0.4) ; 0,875-0,900 (2, +4, +13.6%, +0.5) |
| delai | 72-168 h | 100% | 72-168 h (24, +80, +35.2%, +2.6) |
| issue | oui | 29% | oui (7, +73, +101.1%, +2.2) ; non (17, +7, +8.1%, +1.6) |
| heure_utc | 12-18 h UTC, 6-12 h UTC | 71% | 12-18 h UTC (10, +41, +30.5%, +1.7) ; 6-12 h UTC (7, +26, +10.1%, +1.2) ; 0-6 h UTC (2, +14, +239.9%, +1.9) ; 18-24 h UTC (5, -1, -1.8%, +0.7) |
| discipline | autre | 96% | autre (23, +75, +35.9%, +2.6) ; inconnu (1, +5, +19.5%, +0.5) |
| type_pari | autre | 96% | autre (23, +75, +35.9%, +2.6) ; inconnu (1, +5, +19.5%, +0.5) |
| mode | immédiat | 100% | immédiat (24, +80, +35.2%, +2.6) |
| source | truthsocial.com, x.com | 96% | truthsocial.com (8, +43, +22.0%, +1.4) ; x.com (15, +32, +43.4%, +2.2) ; inconnu (1, +5, +19.5%, +0.5) |

## compteur_tweets_72_168h_12_18h_v1.0.0 — croissance +6.6% (mère compteur_tweets : +16.6%)

19 opérations, résultat +65.94, rendement moyen +47.90% par mise, confiance +2.04, gagnés 18 pour 13.5 attendus (z +2.61).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,600-0,800, 0,100-0,200, 0,850-0,875, 0,800-0,850, 0,450-0,600 | 79% | 0,600-0,800 (5, +26, +42.9%, +1.5) ; 0,100-0,200 (2, +10, +166.8%, +1.2) ; 0,850-0,875 (4, +8, +15.9%, +0.8) ; 0,800-0,850 (3, +7, +20.2%, +0.8) ; 0,450-0,600 (1, +6, +75.4%, +0.9) ; 0,875-0,900 (2, +4, +13.6%, +0.5) |
| delai | 72-168 h | 100% | 72-168 h (19, +66, +47.9%, +2.6) |
| issue | oui, non | 100% | oui (6, +42, +100.8%, +2.0) ; non (13, +24, +23.5%, +1.7) |
| heure_utc | 12-18 h UTC | 100% | 12-18 h UTC (19, +66, +47.9%, +2.6) |
| discipline | autre | 95% | autre (18, +61, +49.5%, +2.6) ; inconnu (1, +5, +19.5%, +0.5) |
| type_pari | autre | 95% | autre (18, +61, +49.5%, +2.6) ; inconnu (1, +5, +19.5%, +0.5) |
| mode | immédiat | 100% | immédiat (19, +66, +47.9%, +2.6) |
| source | x.com, truthsocial.com | 95% | x.com (11, +31, +64.0%, +2.2) ; truthsocial.com (7, +30, +26.7%, +1.4) ; inconnu (1, +5, +19.5%, +0.5) |

## favori_politique_nuit_v1.0.0 — croissance +6.3% (mère favori_politique : +5.8%)

29 opérations, résultat +62.50, rendement moyen +3.45% par mise, confiance +0.64, gagnés 27 pour 26.0 attendus (z +0.62).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,900-0,925, 0,925-0,950 | 48% | 0,900-0,925 (11, +55, +9.2%, +1.0) ; 0,925-0,950 (3, +10, +6.3%, +0.4) ; 0,875-0,900 (2, +9, +12.4%, +0.5) ; 0,950-1,000 (2, +1, +5.3%, +0.3) ; 0,850-0,875 (11, -12, -5.0%, -0.4) |
| delai | 168 h et plus, 12-24 h | 72% | 168 h et plus (18, +82, +3.5%, +0.5) ; 12-24 h (3, +20, +15.4%, +0.7) ; 24-72 h (4, +18, +14.8%, +0.8) ; 6-12 h (1, +1, +16.3%, +0.4) ; 72-168 h (3, -59, -28.3%, -1.4) |
| issue | non | 62% | non (18, +74, +11.2%, +1.4) ; oui (11, -11, -9.3%, -0.8) |
| heure_utc | 6-12 h UTC | 86% | 6-12 h UTC (25, +119, +10.7%, +1.6) ; 0-6 h UTC (4, -56, -41.8%, -2.0) |
| discipline | autre | 100% | autre (29, +62, +3.5%, +0.6) |
| type_pari | vainqueur | 38% | vainqueur (11, +55, +12.5%, +1.2) ; autre (18, +7, -2.1%, -0.2) |
| mode | immédiat | 100% | immédiat (29, +62, +3.5%, +0.6) |
| source | inconnu, events.gop.com, dadosabertos.tse.jus.br, ice.com | 86% | inconnu (21, +35, +0.7%, +0.2) ; events.gop.com (2, +9, +17.0%, +0.6) ; dadosabertos.tse.jus.br (1, +7, +8.5%, +0.3) ; ice.com (1, +5, +6.9%, +0.3) ; gov.il (1, +5, +8.3%, +0.3) ; fec.gov (1, +3, +16.3%, +0.4) |

## nf_sport_patiente_6_24h_6_12h_v1.0.0 — croissance +6.2% (mère nf_sport_patiente_6_24h : -2.1%)

23 opérations, résultat +62.27, rendement moyen +4.58% par mise, confiance +0.66, gagnés 21 pour 20.2 attendus (z +0.52).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,800-0,850, 0,850-0,875, 0,925-0,950 | 70% | 0,800-0,850 (7, +122, +20.7%, +1.2) ; 0,850-0,875 (5, +83, +15.4%, +0.9) ; 0,925-0,950 (4, +45, -19.9%, -1.6) ; 0,875-0,900 (2, +23, +11.4%, +0.5) ; 0,900-0,925 (5, -211, -11.9%, -0.8) |
| delai | 6-12 h | 100% | 6-12 h (23, +62, +4.6%, +0.5) |
| issue | autre, oui | 44% | autre (8, +127, +16.7%, +1.2) ; oui (2, +48, +19.6%, +0.6) ; non (13, -113, -5.2%, -0.6) |
| heure_utc | 18-24 h UTC, 6-12 h UTC | 56% | 18-24 h UTC (6, +99, +14.6%, +0.9) ; 6-12 h UTC (7, +69, -1.0%, -0.2) ; 0-6 h UTC (1, +22, +25.0%, +0.5) ; 12-18 h UTC (9, -128, -0.1%, -0.0) |
| discipline | autre, nfl | 39% | autre (6, +114, +14.0%, +0.9) ; nfl (3, +46, +20.1%, +0.8) ; nba (1, +12, +20.5%, +0.5) ; football (13, -110, -4.6%, -0.6) |
| type_pari | handicap, total | 17% | handicap (3, +48, +14.6%, +0.7) ; total (1, +25, +17.2%, +0.4) ; score_exact (3, +7, -29.2%, -2.0) ; vainqueur (16, -17, +8.2%, +0.8) |
| mode | immédiat | 48% | immédiat (11, +163, +4.6%, +0.3) ; ordre posé (12, -101, +4.6%, +0.4) |
| source | francefootball.fr, nfl.com, ligaportugal.pt, the-afc.com, ligue1.com, epo.gr, wnba.com, legaseriea.it | 56% | francefootball.fr (2, +56, +15.9%, +0.6) ; nfl.com (2, +33, +21.7%, +0.7) ; ligaportugal.pt (2, +26, +10.5%, +0.5) ; the-afc.com (2, +25, +15.9%, +0.6) ; ligue1.com (1, +25, +17.2%, +0.4) ; epo.gr (1, +24, +16.0%, +0.4) |

## vague_volume_suivre_x5_v1.0.0 — croissance +5.9% (mère vague_volume_suivre : +4.8%)

58 opérations, résultat +58.74, rendement moyen +15.27% par mise, confiance +2.70, gagnés 52 pour 45.3 attendus (z +2.20).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,600-0,800, 0,900-0,925, 0,875-0,900, 0,800-0,850 | 88% | 0,600-0,800 (26, +25, +19.9%, +1.6) ; 0,900-0,925 (9, +11, +10.2%, +1.0) ; 0,875-0,900 (7, +8, +12.7%, +0.9) ; 0,800-0,850 (9, +8, +8.2%, +0.5) ; 0,850-0,875 (4, +7, +16.3%, +0.8) ; 0,450-0,600 (3, -1, +16.0%, +0.3) |
| delai | 72-168 h, 168 h et plus | 95% | 72-168 h (23, +36, +27.6%, +2.5) ; 168 h et plus (32, +20, +5.8%, +0.6) ; 24-72 h (3, +3, +21.5%, +0.8) |
| issue | non, oui | 100% | non (30, +33, +16.2%, +1.9) ; oui (28, +26, +14.2%, +1.3) |
| heure_utc | 6-12 h UTC, 12-18 h UTC, 18-24 h UTC | 78% | 6-12 h UTC (15, +27, +32.0%, +2.2) ; 12-18 h UTC (16, +18, +21.1%, +1.6) ; 18-24 h UTC (14, +10, +10.4%, +0.8) ; 0-6 h UTC (13, +4, -6.0%, -0.3) |
| discipline | autre | 98% | autre (57, +58, +15.3%, +2.2) ; football (1, +1, +10.6%, +0.3) |
| type_pari | autre, vainqueur | 98% | autre (29, +31, +20.4%, +1.9) ; vainqueur (28, +27, +10.1%, +1.2) ; nul (1, +1, +10.6%, +0.3) |
| mode | immédiat | 100% | immédiat (58, +59, +15.3%, +2.2) |
| source | inconnu, x.com, fec.gov, gov.il, banrep.gov.co, storymaps.arcgis.com, billboard.com | 83% | inconnu (27, +27, +12.8%, +1.3) ; x.com (5, +6, +13.8%, +0.8) ; fec.gov (11, +4, -1.4%, +0.0) ; gov.il (2, +4, +28.5%, +0.8) ; banrep.gov.co (1, +3, +66.7%, +0.8) ; storymaps.arcgis.com (1, +2, +72.4%, +0.8) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 72-168 h : 23 opérations, +35.82, +27.6% par mise, gagnés 23/18.3 → `filtres: {'echeance_min': 72, 'echeance_max': 168}`
- heure d'achat 6-12 h UTC : 15 opérations, +26.75, +32.0% par mise, gagnés 15/11.6 → `filtres: {'heure_utc': [6, 12]}`

## favori_politique_v1.0.0 — croissance +5.8%

25 opérations, résultat +58.36, rendement moyen +3.57% par mise, confiance +0.57, gagnés 23 pour 22.1 attendus (z +0.56).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,875-0,900, 0,900-0,925 | 40% | 0,875-0,900 (5, +42, +12.0%, +0.8) ; 0,900-0,925 (5, +29, +9.4%, +0.7) ; 0,925-0,950 (3, +13, +7.1%, +0.5) ; 0,850-0,875 (12, -25, -3.2%, -0.2) |
| delai | 168 h et plus, 24-72 h | 72% | 168 h et plus (12, +93, +10.8%, +1.1) ; 24-72 h (6, +33, +13.7%, +0.9) ; 12-24 h (2, +9, +17.0%, +0.6) ; 72-168 h (5, -76, -31.4%, -1.7) |
| issue | non | 60% | non (15, +91, +12.3%, +1.4) ; oui (10, -33, -9.6%, -0.8) |
| heure_utc | 12-18 h UTC, 6-12 h UTC, 18-24 h UTC | 92% | 12-18 h UTC (4, +22, +14.8%, +0.8) ; 6-12 h UTC (3, +19, +15.9%, +0.7) ; 18-24 h UTC (16, +9, -3.0%, -0.3) ; 0-6 h UTC (2, +9, +15.7%, +0.6) |
| discipline | autre | 100% | autre (25, +58, +3.6%, +0.6) |
| type_pari | vainqueur | 36% | vainqueur (9, +48, +13.5%, +1.1) ; autre (16, +10, -2.0%, -0.2) |
| mode | immédiat | 100% | immédiat (25, +58, +3.6%, +0.6) |
| source | inconnu, ice.com, dadosabertos.tse.jus.br, events.gop.com | 96% | inconnu (20, +19, +1.6%, +0.3) ; ice.com (2, +16, +9.7%, +0.5) ; dadosabertos.tse.jus.br (1, +8, +9.6%, +0.3) ; events.gop.com (1, +7, +16.3%, +0.4) ; apps.apple.com (1, +7, +12.4%, +0.3) |

## compteur_tweets_12_18h_v1.0.0 — croissance +5.4% (mère compteur_tweets : +16.6%)

55 opérations, résultat +54.40, rendement moyen +14.70% par mise, confiance +0.89, gagnés 40 pour 35.2 attendus (z +1.67).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,450-0,600, 0,800-0,850, 0,900-0,925 | 20% | 0,450-0,600 (4, +65, +49.0%, +1.0) ; 0,800-0,850 (4, +19, +19.9%, +0.9) ; 0,900-0,925 (3, +13, +8.4%, +0.5) ; 0,850-0,875 (10, +9, +4.2%, +0.3) ; 0,100-0,200 (8, +6, +59.6%, +0.7) ; 0,925-0,950 (2, +2, +7.2%, +0.4) |
| delai | 72-168 h, 168 h et plus, 3-6 h | 49% | 72-168 h (14, +49, +52.7%, +2.3) ; 168 h et plus (10, +47, +8.6%, +0.6) ; 3-6 h (3, +39, +49.6%, +1.2) ; 12-24 h (3, +15, +5.2%, +0.8) ; 0-3 h (1, +1, +7.9%, +0.3) ; 24-72 h (24, -96, -7.8%, -0.4) |
| issue | non | 66% | non (36, +58, +9.8%, +1.4) ; oui (19, -4, +24.1%, +0.9) |
| heure_utc | 12-18 h UTC | 100% | 12-18 h UTC (55, +54, +14.7%, +1.7) |
| discipline | autre | 94% | autre (52, +114, +16.4%, +1.8) ; inconnu (3, -60, -14.5%, -0.3) |
| type_pari | autre | 94% | autre (52, +114, +16.4%, +1.8) ; inconnu (3, -60, -14.5%, -0.3) |
| mode | immédiat | 100% | immédiat (55, +54, +14.7%, +1.7) |
| source | truthsocial.com, x.com | 94% | truthsocial.com (9, +60, +31.4%, +1.7) ; x.com (43, +54, +13.2%, +1.2) ; inconnu (3, -60, -14.5%, -0.3) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 72-168 h : 14 opérations, +49.05, +52.7% par mise, gagnés 13/9.7 → `filtres: {'heure_utc': [12, 18], 'echeance_min': 72, 'echeance_max': 168}` (déjà dans l'arène)

## nf_sport_patiente_prix_850_875_avant_match_v1.0.0 — croissance +5.4%

16 opérations, résultat +54.08, rendement moyen +3.17% par mise, confiance +0.32, gagnés 14 pour 13.5 attendus (z +0.31).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,800-0,850 | 50% | 0,800-0,850 (8, +67, +4.4%, +0.3) ; 0,850-0,875 (8, -13, +1.9%, +0.1) |
| delai | 168 h et plus, 0-3 h, 72-168 h | 44% | 168 h et plus (4, +36, +18.0%, +0.8) ; 0-3 h (2, +22, +18.0%, +0.6) ; 72-168 h (1, +13, +19.5%, +0.4) ; 12-24 h (1, +8, +15.5%, +0.4) ; 6-12 h (8, -26, -11.5%, -0.8) |
| issue | non, oui | 31% | non (4, +42, +16.8%, +0.8) ; oui (1, +10, +20.5%, +0.5) ; autre (11, +2, -3.4%, -0.3) |
| heure_utc | 6-12 h UTC, 12-18 h UTC | 50% | 6-12 h UTC (6, +34, -1.3%, -0.1) ; 12-18 h UTC (2, +20, +18.6%, +0.6) ; 0-6 h UTC (2, +11, +18.0%, +0.6) ; 18-24 h UTC (6, -11, -2.4%, -0.1) |
| discipline | autre, football, tennis, f1 | 44% | autre (1, +22, +17.8%, +0.4) ; football (2, +22, +18.0%, +0.6) ; tennis (2, +19, +19.8%, +0.6) ; f1 (2, +17, +16.2%, +0.6) ; dota (1, +10, +16.8%, +0.4) ; counter-strike (8, -36, -11.5%, -0.8) |
| type_pari | total, vainqueur, score_exact | 100% | total (1, +22, +17.8%, +0.4) ; vainqueur (14, +20, +1.2%, +0.1) ; score_exact (1, +12, +15.5%, +0.4) |
| mode | immédiat, ordre posé | 100% | immédiat (6, +32, -3.2%, -0.1) ; ordre posé (10, +22, +7.0%, +0.5) |
| source | gol.gg, itftennis.com, formula1.com, inconnu, dotabuff.com | 44% | gol.gg (1, +22, +17.8%, +0.4) ; itftennis.com (2, +19, +19.8%, +0.6) ; formula1.com (2, +17, +16.2%, +0.6) ; inconnu (1, +12, +15.5%, +0.4) ; dotabuff.com (1, +10, +16.8%, +0.4) ; slstat.com (1, +10, +20.5%, +0.5) |

## crypto_non_10_20_v1.0.0 — croissance +3.5% (mère crypto_non_bon_marche : -13.5%)

86 opérations, résultat +35.11, rendement moyen +24.73% par mise, confiance +0.88, gagnés 17 pour 12.6 attendus (z +1.37).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,100-0,200 | 94% | 0,100-0,200 (81, +84, +32.4%, +1.6) ; 0,200-0,300 (1, -8, -100.0%, -0.5) ; 0,000-0,100 (4, -40, -100.0%, -0.7) |
| delai | 24-72 h | 33% | 24-72 h (28, +173, +114.1%, +2.7) ; 0-3 h (4, +1, +24.5%, +0.5) ; 12-24 h (12, -2, -46.5%, -0.6) ; 6-12 h (3, -25, +111.1%, +0.8) ; 3-6 h (5, -35, -100.0%, -0.9) ; 168 h et plus (2, -37, -100.0%, -0.7) |
| issue | non | 100% | non (86, +35, +24.7%, +1.4) |
| heure_utc | 12-18 h UTC, 18-24 h UTC | 52% | 12-18 h UTC (23, +111, +55.9%, +1.6) ; 18-24 h UTC (22, +106, +68.2%, +1.7) ; 6-12 h UTC (13, -71, -10.9%, -0.1) ; 0-6 h UTC (28, -110, -18.5%, -0.5) |
| discipline | autre | 99% | autre (85, +48, +26.2%, +1.4) ; inconnu (1, -13, -100.0%, -0.4) |
| type_pari | autre | 99% | autre (85, +48, +26.2%, +1.4) ; inconnu (1, -13, -100.0%, -0.4) |
| mode | immédiat | 100% | immédiat (86, +35, +24.7%, +1.4) |
| source | binance.com, predict.fun | 94% | binance.com (80, +39, +28.2%, +1.4) ; predict.fun (1, +32, +373.5%, +2.0) ; inconnu (1, -13, -100.0%, -0.4) ; 1wtoken.com (4, -23, -100.0%, -0.9) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 24-72 h : 28 opérations, +173.16, +114.1% par mise, gagnés 9/4.0 → `filtres: {'familles': ['crypto'], 'issue': ['non'], 'prix_min': 0.1, 'prix_max': 0.2, 'echeance_min': 24, 'echeance_max': 72, 'question_exclut': ['up or down']}`

## nf_sport_patiente_2crans_v1.0.0 — croissance +3.1% (mère nf_sport_patiente : -1.8%)

41 opérations, résultat +31.19, rendement moyen +8.52% par mise, confiance +2.01, gagnés 38 pour 35.7 attendus (z +1.10).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,800-0,850, 0,850-0,875 | 56% | 0,800-0,850 (13, +105, +21.1%, +1.7) ; 0,850-0,875 (10, +101, +16.9%, +1.3) ; 0,600-0,800 (1, +18, +29.5%, +0.6) ; 0,875-0,900 (4, -27, -1.9%, -0.9) ; 0,925-0,950 (8, -29, -6.5%, -0.7) ; 0,900-0,925 (5, -137, -12.8%, -0.9) |
| delai | 3-6 h, 12-24 h, 6-12 h | 44% | 3-6 h (10, +40, +10.0%, +0.3) ; 12-24 h (3, +31, +17.8%, +0.7) ; 6-12 h (5, +22, +13.7%, +0.8) ; 168 h et plus (3, +18, +13.8%, +0.6) ; 72-168 h (17, -28, +9.5%, +0.9) ; 0-3 h (3, -52, -24.9%, -1.4) |
| issue | non, oui | 15% | non (4, +22, +7.0%, +0.5) ; oui (2, +12, +15.4%, +0.6) ; autre (35, -2, +8.3%, +0.9) |
| heure_utc | 0-6 h UTC, 18-24 h UTC | 32% | 0-6 h UTC (6, +55, +18.9%, +1.1) ; 18-24 h UTC (7, +48, +13.5%, +1.0) ; 12-18 h UTC (15, -4, +3.2%, -0.1) ; 6-12 h UTC (13, -69, +7.2%, +0.6) |
| discipline | football, inconnu, dota | 29% | football (7, +55, +11.5%, +0.9) ; inconnu (3, +34, +19.1%, +0.8) ; dota (2, +30, +15.9%, +0.6) ; mlb (4, +19, +14.8%, +0.8) ; nfl (1, +5, +13.2%, +0.4) ; counter-strike (11, -49, +1.9%, -0.4) |
| type_pari | inconnu, total, score_exact | 20% | inconnu (3, +34, +19.1%, +0.8) ; total (2, +26, +13.8%, +0.5) ; score_exact (3, +17, +7.3%, +0.5) ; partie (1, +13, +16.3%, +0.4) ; handicap (1, +5, +13.2%, +0.4) ; vainqueur (31, -64, +6.9%, +0.6) |
| mode | ordre posé | 68% | ordre posé (28, +236, +15.5%, +2.1) ; immédiat (13, -205, -6.5%, -1.1) |
| source | inconnu, uefa.com, dotabuff.com, itftennis.com, wtatennis.com | 39% | inconnu (6, +51, +13.2%, +0.9) ; uefa.com (3, +34, +17.0%, +0.7) ; dotabuff.com (2, +30, +15.9%, +0.6) ; itftennis.com (4, +23, +12.0%, +0.7) ; wtatennis.com (1, +17, +20.6%, +0.5) ; flashscore.com (2, +13, +17.7%, +0.6) |

## nm_long_v1.0.0 — croissance +2.3% (mère news_momentum : -0.8%)

91 opérations, résultat +23.32, rendement moyen -1.55% par mise, confiance -0.14, gagnés 55 pour 53.6 attendus (z +0.36).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,600-0,800, 0,450-0,600 | 28% | 0,600-0,800 (18, +101, +20.6%, +1.3) ; 0,450-0,600 (7, +54, +35.8%, +1.0) ; 0,900-0,925 (7, +13, -5.8%, -0.5) ; 0,875-0,900 (4, +7, +11.9%, +0.7) ; 0,925-0,950 (3, +7, +7.3%, +0.5) ; 0,950-1,000 (3, +1, +2.4%, +0.3) |
| delai | 168 h et plus | 30% | 168 h et plus (27, +32, +17.2%, +0.6) ; 24-72 h (40, -2, -27.5%, -0.6) ; 72-168 h (24, -7, +20.6%, +0.8) |
| issue | non | 44% | non (40, +49, +6.3%, +0.5) ; oui (51, -25, -7.7%, +0.1) |
| heure_utc | 12-18 h UTC, 6-12 h UTC | 50% | 12-18 h UTC (31, +65, -10.9%, +0.3) ; 6-12 h UTC (15, +22, +27.9%, +0.9) ; 18-24 h UTC (33, +4, +6.6%, +0.9) ; 0-6 h UTC (12, -68, -36.6%, -2.1) |
| discipline | autre, mlb | 99% | autre (87, +25, +0.1%, +0.5) ; mlb (3, +9, -16.4%, +0.2) ; football (1, -11, -100.0%, -1.1) |
| type_pari | vainqueur | 32% | vainqueur (29, +59, +25.6%, +1.8) ; autre (62, -36, -14.3%, -0.8) |
| mode | immédiat | 100% | immédiat (91, +23, -1.6%, +0.4) |
| source | inconnu, arena.ai, events.gop.com, fec.gov, bankofcanada.ca, dadosabertos.tse.jus.br | 45% | inconnu (28, +44, +40.7%, +1.7) ; arena.ai (2, +21, +18.6%, +0.6) ; events.gop.com (2, +19, +52.4%, +1.0) ; fec.gov (6, +19, +50.3%, +1.6) ; bankofcanada.ca (2, +13, +33.2%, +0.8) ; dadosabertos.tse.jus.br (1, +12, +53.8%, +0.7) |

## rallies_non_favori_v1.0.0 — croissance +1.7% (mère rallies_non : +0.2%)

10 opérations, résultat +16.99, rendement moyen +57.84% par mise, confiance +3.27, gagnés 9 pour 5.7 attendus (z +2.11).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,450-0,600, 0,600-0,800 | 100% | 0,450-0,600 (8, +13, +55.6%, +1.8) ; 0,600-0,800 (2, +4, +66.7%, +1.1) |
| delai | 6-12 h, 12-24 h | 90% | 6-12 h (4, +9, +73.4%, +1.7) ; 12-24 h (5, +6, +41.8%, +1.1) ; 3-6 h (1, +2, +75.4%, +0.9) |
| issue | non | 100% | non (10, +17, +57.8%, +2.1) |
| heure_utc | 6-12 h UTC, 0-6 h UTC | 90% | 6-12 h UTC (5, +11, +72.6%, +1.9) ; 0-6 h UTC (4, +4, +35.0%, +0.8) ; 18-24 h UTC (1, +2, +75.4%, +0.9) |
| discipline | autre | 90% | autre (9, +15, +54.8%, +1.9) ; football (1, +2, +85.2%, +0.9) |
| type_pari | autre | 100% | autre (10, +17, +57.8%, +2.1) |
| mode | immédiat | 100% | immédiat (10, +17, +57.8%, +2.1) |
| source | events.gop.com | 100% | events.gop.com (10, +17, +57.8%, +2.1) |

## moins_de_cartes_lol_v1.0.0 — croissance +1.3% (mère moins_de_cartes : +0.2%)

17 opérations, résultat +12.98, rendement moyen +25.98% par mise, confiance +1.17, gagnés 12 pour 9.6 attendus (z +1.21).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,600-0,800, 0,450-0,600 | 88% | 0,600-0,800 (8, +8, +16.2%, +0.7) ; 0,450-0,600 (7, +7, +28.6%, +0.9) ; 0,300-0,450 (2, -2, +55.9%, +0.5) |
| delai | 6-12 h | 100% | 6-12 h (17, +13, +26.0%, +1.2) |
| issue | autre | 100% | autre (17, +13, +26.0%, +1.2) |
| heure_utc | 12-18 h UTC, 6-12 h UTC | 100% | 12-18 h UTC (14, +7, +7.7%, +0.5) ; 6-12 h UTC (3, +6, +111.5%, +1.8) |
| discipline | autre | 100% | autre (17, +13, +26.0%, +1.2) |
| type_pari | total | 100% | total (17, +13, +26.0%, +1.2) |
| mode | immédiat | 100% | immédiat (17, +13, +26.0%, +1.2) |
| source | gol.gg | 100% | gol.gg (17, +13, +26.0%, +1.2) |

## nf_sport_patiente_prix_moyen_v1.0.0 — croissance +0.6% (mère nf_sport_patiente : -1.8%)

48 opérations, résultat +6.31, rendement moyen +0.29% par mise, confiance +0.05, gagnés 40 pour 40.1 attendus (z -0.04).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,850-0,875, 0,800-0,850 | 92% | 0,850-0,875 (20, +85, +8.0%, +0.6) ; 0,800-0,850 (24, +48, +5.2%, +0.6) ; 0,600-0,800 (4, -126, -67.6%, -2.5) |
| delai | 72-168 h, 168 h et plus | 54% | 72-168 h (24, +147, +8.8%, +1.1) ; 168 h et plus (2, +22, +17.7%, +0.6) ; 6-12 h (2, +17, +21.2%, +0.7) ; 12-24 h (1, +12, +21.9%, +0.5) ; 3-6 h (15, -88, -13.1%, -1.0) ; 0-3 h (4, -103, -25.5%, -1.9) |
| issue | autre | 100% | autre (48, +6, +0.3%, -0.0) |
| heure_utc | 6-12 h UTC, 0-6 h UTC | 54% | 6-12 h UTC (16, +80, +3.0%, +0.4) ; 0-6 h UTC (10, +38, +6.9%, +0.5) ; 18-24 h UTC (10, +28, +7.9%, +0.6) ; 12-18 h UTC (12, -140, -15.2%, -1.6) |
| discipline | tennis, inconnu, mlb, autre | 58% | tennis (18, +77, +5.9%, +0.6) ; inconnu (5, +52, +18.2%, +1.0) ; mlb (3, +34, +17.7%, +0.7) ; autre (2, +23, +19.1%, +0.6) ; dota (2, +23, +22.7%, +0.7) ; football (1, +13, +19.1%, +0.4) |
| type_pari | inconnu, total | 12% | inconnu (5, +52, +18.2%, +1.0) ; total (1, +13, +19.1%, +0.4) ; handicap (1, +12, +21.9%, +0.5) ; vainqueur (37, -25, -1.8%, -0.4) ; partie (4, -45, -12.7%, -0.5) |
| mode | immédiat | 33% | immédiat (16, +63, +4.5%, +0.5) ; ordre posé (32, -56, -1.8%, -0.4) |
| source | atptour.com, inconnu, wtatennis.com, dotabuff.com, flashscore.com | 48% | atptour.com (12, +83, +9.3%, +0.8) ; inconnu (5, +52, +18.2%, +1.0) ; wtatennis.com (2, +27, +18.2%, +0.6) ; dotabuff.com (2, +23, +22.7%, +0.7) ; flashscore.com (2, +22, +17.7%, +0.6) ; uefa.com (1, +13, +19.1%, +0.4) |

## moins_de_cartes_bo5_v1.0.0 — croissance +0.5% (mère moins_de_cartes : +0.2%)

10 opérations, résultat +5.02, rendement moyen +24.13% par mise, confiance +0.77, gagnés 7 pour 5.5 attendus (z +0.97).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,600-0,800, 0,450-0,600 | 70% | 0,600-0,800 (6, +7, +24.2%, +0.9) ; 0,450-0,600 (1, +3, +84.4%, +0.9) ; 0,300-0,450 (3, -4, +3.9%, -0.0) |
| delai | 6-12 h | 100% | 6-12 h (10, +5, +24.1%, +1.0) |
| issue | autre | 100% | autre (10, +5, +24.1%, +1.0) |
| heure_utc | 12-18 h UTC, 6-12 h UTC | 80% | 12-18 h UTC (5, +8, +26.7%, +1.0) ; 6-12 h UTC (3, +6, +102.6%, +1.7) ; 0-6 h UTC (2, -9, -100.0%, -1.6) |
| discipline | autre | 70% | autre (7, +12, +56.4%, +1.7) ; counter-strike (3, -7, -51.1%, -0.9) |
| type_pari | total | 100% | total (10, +5, +24.1%, +1.0) |
| mode | immédiat | 100% | immédiat (10, +5, +24.1%, +1.0) |
| source | gol.gg, dotabuff.com | 70% | gol.gg (6, +9, +57.2%, +1.5) ; dotabuff.com (1, +3, +51.2%, +0.7) ; hltv.org (3, -7, -51.1%, -0.9) |

## nf_sport_patiente_72_168h_v1.0.0 — croissance -0.0% (mère nf_sport_patiente : -1.8%)

23 opérations, résultat -0.03, rendement moyen +0.10% par mise, confiance +0.01, gagnés 20 pour 19.9 attendus (z +0.07).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,850-0,875, 0,875-0,900 | 35% | 0,850-0,875 (5, +57, +16.1%, +0.9) ; 0,875-0,900 (3, +37, +12.0%, +0.6) ; 0,800-0,850 (6, +8, +0.7%, +0.0) ; 0,925-0,950 (2, +5, +7.1%, +0.4) ; 0,600-0,800 (2, -40, -36.7%, -1.0) ; 0,900-0,925 (5, -66, -11.8%, -0.8) |
| delai | — | 0% | 72-168 h (23, -0, +0.1%, +0.1) |
| issue | — | 0% | autre (23, -0, +0.1%, +0.1) |
| heure_utc | 12-18 h UTC | 44% | 12-18 h UTC (10, +95, +16.9%, +1.3) ; 18-24 h UTC (3, -15, -27.8%, -1.1) ; 6-12 h UTC (10, -81, -8.3%, -0.7) |
| discipline | inconnu | 22% | inconnu (5, +48, +18.1%, +1.0) ; mlb (1, +4, +26.6%, +0.5) ; tennis (17, -52, -6.8%, -0.7) |
| type_pari | inconnu | 22% | inconnu (5, +48, +18.1%, +1.0) ; vainqueur (18, -48, -4.9%, -0.5) |
| mode | immédiat | 52% | immédiat (12, +136, +14.4%, +1.3) ; ordre posé (11, -136, -15.4%, -1.3) |
| source | atptour.com, inconnu | 83% | atptour.com (14, +51, -2.4%, -0.1) ; inconnu (5, +48, +18.1%, +1.0) ; itftennis.com (2, +15, +9.2%, +0.4) ; flashscore.com (1, +4, +26.6%, +0.5) ; wtatennis.com (1, -119, -100.0%, -3.2) |

## nf_sport_patiente_72_168h_12_18h_v1.0.0 — croissance -0.4% (mère nf_sport_patiente : -1.8%)

158 opérations, résultat -4.42, rendement moyen +1.13% par mise, confiance +0.40, gagnés 140 pour 138.4 attendus (z +0.39).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,875-0,900, 0,850-0,875 | 31% | 0,875-0,900 (28, +232, +10.4%, +1.3) ; 0,850-0,875 (21, +46, -0.9%, -0.1) ; 0,600-0,800 (7, +21, +7.0%, +0.4) ; 0,800-0,850 (43, -37, -2.1%, -0.2) ; 0,900-0,925 (32, -106, +2.5%, +0.5) ; 0,925-0,950 (27, -159, -5.0%, -0.9) |
| delai | — | 0% | 72-168 h (158, -4, +1.1%, +0.4) |
| issue | non, oui | 6% | non (7, +51, +13.7%, +1.0) ; oui (3, +22, +20.6%, +0.8) ; autre (148, -77, +0.1%, +0.1) |
| heure_utc | 18-24 h UTC | 2% | 18-24 h UTC (3, +15, +9.4%, +0.5) ; 12-18 h UTC (155, -19, +1.0%, +0.3) |
| discipline | inconnu, mlb, nfl, counter-strike | 16% | inconnu (17, +49, +5.7%, +0.8) ; mlb (3, +20, +19.7%, +0.8) ; nfl (2, +19, +22.4%, +0.7) ; counter-strike (3, +16, +12.3%, +0.6) ; football (2, +12, +16.4%, +0.6) ; autre (14, -10, -11.3%, -1.1) |
| type_pari | inconnu | 11% | inconnu (17, +49, +5.7%, +0.8) ; nul (1, +6, +12.4%, +0.3) ; vainqueur (140, -59, +0.5%, +0.1) |
| mode | immédiat | 65% | immédiat (102, +95, +2.4%, +0.8) ; ordre posé (56, -99, -1.2%, -0.5) |
| source | atptour.com, inconnu, francefootball.fr, hltv.org | 58% | atptour.com (69, +72, +2.2%, +0.6) ; inconnu (17, +49, +5.7%, +0.8) ; francefootball.fr (2, +26, +13.6%, +0.5) ; hltv.org (3, +16, +12.3%, +0.6) ; mlb.com (2, +15, +19.3%, +0.6) ; flashscore.com (6, +12, -3.0%, -0.1) |

## nf_sport_patiente_prix_850_875_v1.0.0 — croissance -0.6% (mère nf_sport_patiente : -1.8%)

161 opérations, résultat -6.03, rendement moyen -0.73% par mise, confiance -0.22, gagnés 135 pour 136.5 attendus (z -0.33).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,850-0,875 | 53% | 0,850-0,875 (85, +78, +2.9%, +0.4) ; 0,800-0,850 (76, -84, -4.8%, -0.9) |
| delai | 72-168 h, 24-72 h, 6-12 h | 55% | 72-168 h (72, +176, -3.8%, -0.7) ; 24-72 h (4, +108, +17.9%, +0.8) ; 6-12 h (12, +81, +8.1%, +0.7) ; 12-24 h (3, +61, +18.2%, +0.8) ; 168 h et plus (11, -39, +1.5%, -0.3) ; 0-3 h (6, -126, -11.5%, -1.2) |
| issue | non | 9% | non (14, +262, +17.2%, +1.6) ; autre (147, -268, -2.4%, -0.8) |
| heure_utc | 12-18 h UTC | 27% | 12-18 h UTC (43, +495, +10.7%, +1.5) ; 0-6 h UTC (33, -17, +7.0%, +1.0) ; 18-24 h UTC (42, -43, -5.2%, -0.7) ; 6-12 h UTC (43, -441, -13.7%, -2.3) |
| discipline | inconnu, f1, valorant, dota, football | 26% | inconnu (17, +158, +10.3%, +1.0) ; f1 (5, +84, +17.4%, +0.9) ; valorant (4, +77, -12.6%, -0.6) ; dota (9, +75, +17.8%, +1.3) ; football (7, +70, +18.2%, +1.1) ; lol (4, +57, -11.4%, -0.5) |
| type_pari | inconnu, handicap | 12% | inconnu (17, +158, +10.3%, +1.0) ; handicap (3, +73, +17.7%, +0.7) ; score_exact (1, +27, +16.3%, +0.4) ; nul (3, +17, +18.0%, +0.8) ; total (4, -1, -10.7%, -0.5) ; vainqueur (119, -26, -3.2%, -1.0) |
| mode | immédiat | 41% | immédiat (66, +8, -4.0%, -0.6) ; ordre posé (95, -14, +1.5%, +0.1) |
| source | inconnu, formula1.com, francefootball.fr, vlr.gg, dotabuff.com, itftennis.com | 37% | inconnu (18, +185, +10.7%, +1.1) ; formula1.com (5, +84, +17.4%, +0.9) ; francefootball.fr (2, +81, +16.7%, +0.6) ; vlr.gg (4, +77, -12.6%, -0.6) ; dotabuff.com (9, +75, +17.8%, +1.3) ; itftennis.com (22, +74, +1.7%, +0.2) |

## nf_tennis_prix_bas_v1.0.0 — croissance -1.3% (mère nf_sport_patiente : -1.8%)

98 opérations, résultat -12.61, rendement moyen +0.81% par mise, confiance +0.18, gagnés 82 pour 80.7 attendus (z +0.34).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,800-0,850 | 61% | 0,800-0,850 (60, +73, +2.5%, +0.6) ; 0,850-0,875 (21, -3, +4.4%, +0.6) ; 0,600-0,800 (17, -83, -9.8%, -0.8) |
| delai | 168 h et plus | 4% | 168 h et plus (4, +38, +22.7%, +1.0) ; 72-168 h (94, -51, -0.1%, +0.1) |
| issue | — | 0% | autre (98, -13, +0.8%, +0.3) |
| heure_utc | 12-18 h UTC, 18-24 h UTC | 56% | 12-18 h UTC (28, +71, +8.1%, +1.0) ; 18-24 h UTC (27, +65, +1.4%, +0.3) ; 0-6 h UTC (14, -50, -14.9%, -1.1) ; 6-12 h UTC (29, -99, +0.9%, +0.2) |
| discipline | inconnu | 17% | inconnu (17, +23, +4.9%, +0.5) ; tennis (81, -36, -0.0%, +0.1) |
| type_pari | inconnu | 17% | inconnu (17, +23, +4.9%, +0.5) ; vainqueur (81, -36, -0.0%, +0.1) |
| mode | — | 0% | immédiat (98, -13, +0.8%, +0.3) |
| source | itftennis.com, atptour.com | 69% | itftennis.com (16, +88, -2.5%, -0.1) ; atptour.com (52, +53, +2.6%, +0.5) ; inconnu (17, +23, +4.9%, +0.5) ; wtatennis.com (13, -176, -7.7%, -0.5) |

## nf_court_soir_v1.0.0 — croissance -1.4% (mère nf_court : -10.8%)

71 opérations, résultat -14.48, rendement moyen +1.13% par mise, confiance +0.30, gagnés 65 pour 63.8 attendus (z +0.48).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,925-0,950, 0,900-0,925 | 63% | 0,925-0,950 (32, +205, +6.5%, +1.5) ; 0,900-0,925 (13, +89, +1.2%, +0.2) ; 0,875-0,900 (6, +26, -6.6%, -0.4) ; 0,600-0,800 (1, +23, +25.0%, +0.5) ; 0,850-0,875 (8, -109, +1.7%, +0.2) ; 0,800-0,850 (11, -249, -13.0%, -0.8) |
| delai | 0-3 h, 3-6 h | 39% | 0-3 h (18, +199, +2.2%, +0.4) ; 3-6 h (10, +69, +14.0%, +1.2) ; 24-72 h (4, +23, -12.8%, -0.5) ; 168 h et plus (2, +6, +11.3%, +0.5) ; 6-12 h (12, -149, -1.5%, -0.0) ; 12-24 h (25, -162, -2.1%, -0.2) |
| issue | non | 52% | non (37, +207, +2.2%, +0.6) ; autre (30, -18, +6.1%, +1.0) ; oui (4, -204, -46.7%, -2.6) |
| heure_utc | — | 0% | 18-24 h UTC (71, -14, +1.1%, +0.5) |
| discipline | football, lol, nba | 35% | football (21, +138, +7.9%, +1.3) ; lol (3, +49, +11.0%, +0.6) ; nba (1, +23, +25.0%, +0.5) ; ufc (1, +15, +19.5%, +0.5) ; inconnu (1, +10, +9.6%, +0.3) ; dota (1, +10, +11.7%, +0.3) |
| type_pari | handicap, score_exact, autre | 56% | handicap (10, +132, +14.9%, +1.2) ; score_exact (14, +124, -0.7%, -0.0) ; autre (16, +35, -5.6%, -0.6) ; total (3, +32, +6.4%, +0.5) ; inconnu (1, +10, +9.6%, +0.3) ; nul (1, +6, +16.8%, +0.4) |
| mode | — | 0% | immédiat (71, -14, +1.1%, +0.5) |
| source | inconnu, binance.com, gol.gg, laliga.com, ncaa.com, nba.com, premierleague.com | 56% | inconnu (15, +135, -0.0%, +0.1) ; binance.com (13, +55, +7.1%, +1.0) ; gol.gg (3, +49, +11.0%, +0.6) ; laliga.com (2, +35, +13.3%, +0.5) ; ncaa.com (3, +31, +15.2%, +0.7) ; nba.com (1, +23, +25.0%, +0.5) |

## mots_prononces_patiente_v1.0.0 — croissance -1.7% (mère mots_prononces : -6.6%)

23 opérations, résultat -16.72, rendement moyen -8.82% par mise, confiance -0.29, gagnés 8 pour 8.7 attendus (z -0.30).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,100-0,200, 0,450-0,600 | 35% | 0,100-0,200 (1, +59, +426.3%, +2.1) ; 0,450-0,600 (7, +39, +7.9%, +0.2) ; 0,300-0,450 (8, -14, +1.9%, +0.1) ; 0,200-0,300 (7, -101, -100.0%, -1.6) |
| delai | 6-12 h, 24-72 h | 61% | 6-12 h (3, +75, +22.4%, +0.4) ; 24-72 h (11, +19, +13.8%, +0.3) ; 3-6 h (2, +6, -3.9%, +0.1) ; 0-3 h (2, -31, -100.0%, -0.9) ; 12-24 h (5, -85, -42.9%, -0.8) |
| issue | non | 74% | non (17, +22, +2.0%, -0.2) ; oui (6, -39, -39.4%, -0.3) |
| heure_utc | 12-18 h UTC | 30% | 12-18 h UTC (7, +129, +48.7%, +1.3) ; 18-24 h UTC (8, -38, -34.2%, -1.2) ; 6-12 h UTC (3, -39, -18.7%, -0.4) ; 0-6 h UTC (5, -69, -42.9%, -0.5) |
| discipline | — | 0% | autre (23, -17, -8.8%, -0.3) |
| type_pari | — | 0% | autre (23, -17, -8.8%, -0.3) |
| mode | — | 0% | immédiat (8, -1, +0.4%, +0.4) ; ordre posé (15, -15, -13.8%, -0.7) |
| source | — | 0% | events.gop.com (23, -17, -8.8%, -0.3) |

## nf_court_football_v1.0.0 — croissance -2.2% (mère nf_court : -10.8%)

112 opérations, résultat -22.04, rendement moyen +0.97% par mise, confiance +0.30, gagnés 101 pour 99.6 attendus (z +0.41).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,875-0,900, 0,850-0,875 | 28% | 0,875-0,900 (18, +95, +5.6%, +0.8) ; 0,850-0,875 (13, +15, +6.7%, +0.7) ; 0,600-0,800 (1, +11, +23.8%, +0.5) ; 0,900-0,925 (24, +6, -4.4%, -0.6) ; 0,800-0,850 (21, -8, +4.2%, +0.5) ; 0,950-1,000 (3, -31, -30.0%, -2.3) |
| delai | 0-3 h | 38% | 0-3 h (42, +93, +4.5%, +0.9) ; 6-12 h (15, +8, -4.3%, -0.4) ; 168 h et plus (1, +6, +10.6%, +0.3) ; 3-6 h (22, -32, -2.8%, -0.3) ; 12-24 h (32, -97, +1.1%, +0.2) |
| issue | autre | 17% | autre (19, +90, +12.8%, +1.6) ; oui (12, -16, -2.9%, -0.2) ; non (81, -97, -1.2%, -0.2) |
| heure_utc | 6-12 h UTC, 12-18 h UTC | 62% | 6-12 h UTC (25, +94, +1.6%, +0.3) ; 12-18 h UTC (44, +35, +2.6%, +0.6) ; 0-6 h UTC (8, -24, -0.9%, +0.0) ; 18-24 h UTC (35, -126, -1.1%, -0.2) |
| discipline | inconnu | 16% | inconnu (18, +54, +7.3%, +0.8) ; football (94, -76, -0.2%, +0.1) |
| type_pari | total, inconnu | 26% | total (11, +58, +11.5%, +1.1) ; inconnu (18, +54, +7.3%, +0.8) ; handicap (6, +20, +12.1%, +0.9) ; nul (9, -30, -11.3%, -0.8) ; score_exact (29, -30, -2.8%, -0.5) ; vainqueur (39, -94, -1.0%, -0.1) |
| mode | — | 0% | immédiat (112, -22, +1.0%, +0.4) |
| source | laliga.com, ligue1.com, premierleague.com, slstat.com, ligaportugal.pt, inconnu, ligamx.net, dfb.de | 71% | laliga.com (8, +41, +14.5%, +1.1) ; ligue1.com (6, +32, +13.7%, +0.9) ; premierleague.com (8, +32, +10.1%, +0.9) ; slstat.com (4, +28, +15.0%, +0.8) ; ligaportugal.pt (4, +25, +12.5%, +0.7) ; inconnu (47, +24, +1.1%, +0.3) |

## contrer_crypto_audace_v1.0.0 — croissance -3.8% (mère contrer_crypto : -25.5%)

47 opérations, résultat -38.15, rendement moyen +3.01% par mise, confiance +0.11, gagnés 13 pour 11.8 attendus (z +0.41).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,200-0,300, 0,300-0,450 | 64% | 0,200-0,300 (15, +50, +26.0%, +0.8) ; 0,300-0,450 (15, +23, +8.6%, +0.3) ; 0,450-0,600 (1, -21, -100.0%, -0.9) ; 0,100-0,200 (16, -90, -17.4%, -0.2) |
| delai | 72-168 h | 19% | 72-168 h (9, +154, +114.6%, +2.0) ; 6-12 h (11, +11, -5.6%, -0.8) ; 24-72 h (9, -22, +11.1%, +0.4) ; 0-3 h (2, -29, -100.0%, -0.8) ; 3-6 h (5, -44, -29.5%, +0.0) ; 12-24 h (11, -107, -52.9%, -0.3) |
| issue | oui | 55% | oui (26, +104, +27.2%, +1.1) ; non (21, -143, -26.9%, -0.5) |
| heure_utc | 6-12 h UTC, 18-24 h UTC | 60% | 6-12 h UTC (18, +64, +26.3%, +0.7) ; 18-24 h UTC (10, +50, +45.8%, +0.7) ; 0-6 h UTC (6, -44, -60.0%, -0.8) ; 12-18 h UTC (13, -108, -33.0%, -0.0) |
| discipline | — | 0% | autre (46, -10, +5.2%, +0.5) ; inconnu (1, -28, -100.0%, -0.7) |
| type_pari | — | 0% | autre (46, -10, +5.2%, +0.5) ; inconnu (1, -28, -100.0%, -0.7) |
| mode | — | 0% | immédiat (47, -38, +3.0%, +0.4) |
| source | 1wtoken.com | 8% | 1wtoken.com (4, +7, -1.1%, +0.0) ; binance.com (42, -17, +5.9%, +0.5) ; inconnu (1, -28, -100.0%, -0.7) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 72-168 h : 9 opérations, +153.97, +114.6% par mise, gagnés 5/2.4 → `filtres: {'echeance_min': 72, 'echeance_max': 168}`

## outsider_sport_apres_midi_v1.0.0 — croissance -4.6% (mère outsider_sport_patiente : -7.3%)

30 opérations, résultat -46.48, rendement moyen -37.64% par mise, confiance -0.86, gagnés 2 pour 3.3 attendus (z -0.78).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | — | 0% | 0,000-0,100 (13, -20, -16.4%, -0.1) ; 0,100-0,200 (17, -26, -53.8%, -0.9) |
| delai | 3-6 h | 13% | 3-6 h (4, +17, +171.6%, +1.1) ; 0-3 h (6, -5, +30.8%, +0.4) ; 6-12 h (3, -7, -100.0%, -0.6) ; 72-168 h (4, -7, -100.0%, -0.7) ; 168 h et plus (6, -15, -100.0%, -0.9) ; 12-24 h (7, -30, -100.0%, -1.0) |
| issue | non | 3% | non (1, +25, +986.4%, +3.2) ; autre (20, -35, -60.8%, -0.9) ; oui (9, -36, -100.0%, -1.1) |
| heure_utc | — | 0% | 12-18 h UTC (13, -1, +43.9%, +0.6) ; 0-6 h UTC (5, -14, -100.0%, -0.8) ; 18-24 h UTC (12, -32, -100.0%, -1.3) |
| discipline | football | 23% | football (7, +8, +55.2%, +0.4) ; counter-strike (1, -2, -100.0%, -0.3) ; dota (2, -4, -100.0%, -0.5) ; inconnu (1, -4, -100.0%, -0.3) ; lol (2, -4, -100.0%, -0.5) ; f1 (2, -7, -100.0%, -0.6) |
| type_pari | total | 10% | total (3, +7, +161.5%, +1.3) ; score_exact (1, -2, -100.0%, -0.3) ; inconnu (1, -4, -100.0%, -0.3) ; autre (1, -4, -100.0%, -0.5) ; handicap (2, -10, -100.0%, -0.6) ; vainqueur (22, -33, -50.6%, -0.9) |
| mode | immédiat | 37% | immédiat (11, +1, +70.1%, +0.7) ; ordre posé (19, -48, -100.0%, -1.5) |
| source | efl.com, dfb.de | 7% | efl.com (1, +25, +986.4%, +3.2) ; dfb.de (1, +14, +684.5%, +2.6) ; itftennis.com (1, -1, -100.0%, -0.3) ; the-afc.com (1, -2, -100.0%, -0.4) ; euroleaguebasketball.net (1, -2, -100.0%, -0.4) ; conmebollibertadores.com (1, -2, -100.0%, -0.4) |

## nf_sport_patiente_tennis_850_875_v1.0.0 — croissance -22.6% (mère nf_sport_patiente_tennis : -22.7%)

30 opérations, résultat -225.74, rendement moyen -14.91% par mise, confiance -1.56, gagnés 22 pour 25.8 attendus (z -2.00).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,800-0,850 | 3% | 0,800-0,850 (1, +6, +18.1%, +0.4) ; 0,850-0,875 (29, -232, -16.1%, -2.1) |
| delai | — | 0% | 72-168 h (30, -226, -14.9%, -2.0) |
| issue | — | 0% | autre (30, -226, -14.9%, -2.0) |
| heure_utc | 0-6 h UTC | 17% | 0-6 h UTC (5, +52, +15.9%, +0.9) ; 18-24 h UTC (7, -55, -16.8%, -1.1) ; 12-18 h UTC (10, -94, -18.8%, -1.4) ; 6-12 h UTC (8, -129, -27.6%, -1.9) |
| discipline | inconnu | 10% | inconnu (3, +29, +15.4%, +0.7) ; tennis (27, -255, -18.3%, -2.3) |
| type_pari | inconnu | 10% | inconnu (3, +29, +15.4%, +0.7) ; vainqueur (27, -255, -18.3%, -2.3) |
| mode | — | 0% | ordre posé (21, -92, -11.6%, -1.3) ; immédiat (9, -134, -22.6%, -1.6) |
| source | itftennis.com, inconnu | 43% | itftennis.com (10, +48, +4.6%, +0.4) ; inconnu (3, +29, +15.4%, +0.7) ; wtatennis.com (4, -27, -13.0%, -0.6) ; atptour.com (13, -276, -37.5%, -3.4) |

## contrer_crypto_v1.0.0 — croissance -25.5%

345 opérations, résultat -255.49, rendement moyen +4.28% par mise, confiance +0.31, gagnés 65 pour 54.9 attendus (z +1.53).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,450-0,600 | 1% | 0,450-0,600 (2, +9, +69.6%, +1.2) ; 0,100-0,200 (134, +0, +22.1%, +1.4) ; 0,300-0,450 (33, -8, +11.7%, +0.6) ; 0,200-0,300 (62, -31, +10.9%, +1.0) ; 0,000-0,100 (114, -226, -23.6%, -0.5) |
| delai | 168 h et plus, 0-3 h | 8% | 168 h et plus (19, +6, +6.1%, +0.4) ; 0-3 h (7, +3, +4.6%, +1.1) ; 6-12 h (41, -1, +38.3%, +1.8) ; 24-72 h (106, -45, +19.5%, +1.1) ; 3-6 h (33, -52, -42.0%, -0.8) ; 72-168 h (79, -78, -23.5%, +0.1) |
| issue | non | 42% | non (145, +14, +36.3%, +2.8) ; oui (200, -270, -18.9%, -0.4) |
| heure_utc | 18-24 h UTC | 17% | 18-24 h UTC (59, +9, +46.5%, +1.4) ; 12-18 h UTC (103, -30, +40.7%, +2.0) ; 6-12 h UTC (90, -108, -10.3%, +0.9) ; 0-6 h UTC (93, -127, -48.8%, -1.2) |
| discipline | — | 0% | inconnu (3, -8, -100.0%, -0.5) ; autre (342, -247, +5.2%, +1.6) |
| type_pari | — | 0% | inconnu (3, -8, -100.0%, -0.5) ; autre (342, -247, +5.2%, +1.6) |
| mode | — | 0% | immédiat (345, -255, +4.3%, +1.5) |
| source | — | 0% | 1wtoken.com (5, -1, -20.9%, +0.2) ; predict.fun (1, -2, -100.0%, -0.4) ; x.com (1, -4, -100.0%, -0.5) ; inconnu (3, -8, -100.0%, -0.5) ; binance.com (335, -240, +6.2%, +1.6) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- issue non : 145 opérations, +14.48, +36.3% par mise, gagnés 36/23.8 → `filtres: {'issue': ['non']}`

