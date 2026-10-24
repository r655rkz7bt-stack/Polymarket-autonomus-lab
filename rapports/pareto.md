# Entonnoir 80/20 : le petit morceau qui fait les gains

Pour chaque stratégie qui grandit vite (ou plus vite que sa mère) : par caractéristique, le
« cœur » = les morceaux qui font 80 % des gains (des morceaux gagnants), et la part des paris
qu'ils représentent.
Peu de paris = des pistes, pas des preuves : l'arène tranche avec les filles proposées.

## nf_sport_v1.0.0 — croissance +27.1% (mère naive_favorite : +11.8%)

67 opérations, résultat +271.48, rendement moyen +1.80% par mise, confiance +0.50, gagnés 62 pour 60.7 attendus (z +0.56).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,925-0,950, 0,900-0,925, 0,875-0,900 | 81% | 0,925-0,950 (27, +124, +2.6%, +0.6) ; 0,900-0,925 (16, +77, +2.5%, +0.4) ; 0,875-0,900 (11, +46, +1.6%, +0.2) ; 0,800-0,850 (3, +39, +22.5%, +0.8) ; 0,850-0,875 (10, -14, -7.6%, -0.6) |
| delai | 0-3 h, 6-12 h, 3-6 h, 24-72 h, 72-168 h | 61% | 0-3 h (8, +56, +9.3%, +0.9) ; 6-12 h (9, +50, +12.6%, +1.1) ; 3-6 h (5, +49, +11.0%, +0.8) ; 24-72 h (10, +47, +8.6%, +0.9) ; 72-168 h (9, +43, +9.4%, +0.9) ; 168 h et plus (4, +21, +12.6%, +0.7) |
| issue | non, autre | 97% | non (29, +133, +1.8%, +0.4) ; autre (36, +127, +1.4%, +0.3) ; oui (2, +12, +9.2%, +0.4) |
| heure_utc | 18-24 h UTC, 6-12 h UTC | 57% | 18-24 h UTC (33, +201, +2.9%, +0.6) ; 6-12 h UTC (5, +33, +11.9%, +0.8) ; 12-18 h UTC (5, +25, +9.7%, +0.7) ; 0-6 h UTC (24, +13, -3.5%, -0.4) |
| discipline | football, autre, dota, tennis | 76% | football (29, +170, +5.1%, +1.0) ; autre (16, +84, +3.7%, +0.5) ; dota (1, +31, +11.7%, +0.3) ; tennis (5, +25, +8.8%, +0.7) ; lol (3, +25, +11.0%, +0.6) ; mlb (2, +22, +15.2%, +0.6) |
| type_pari | vainqueur, score_exact, partie | 75% | vainqueur (37, +183, +1.8%, +0.4) ; score_exact (10, +56, +7.8%, +0.9) ; partie (3, +30, +9.0%, +0.5) ; total (5, +16, +8.5%, +0.7) ; inconnu (4, +15, +8.2%, +0.6) ; nul (2, +9, +8.9%, +0.4) |
| mode | immédiat | 100% | immédiat (67, +271, +1.8%, +0.6) |
| source | inconnu, ncaa.com, uefa.com, dotabuff.com, premierleague.com, gol.gg, mlb.com, laliga.com | 70% | inconnu (15, +77, +8.0%, +1.1) ; ncaa.com (10, +70, +0.9%, +0.1) ; uefa.com (9, +35, -4.0%, -0.4) ; dotabuff.com (1, +31, +11.7%, +0.3) ; premierleague.com (5, +26, +11.7%, +0.8) ; gol.gg (3, +25, +11.0%, +0.6) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- heure d'achat 18-24 h UTC : 33 opérations, +201.27, +2.9% par mise, gagnés 31/30.0 → `filtres: {'familles': ['sports'], 'heure_utc': [18, 24]}` (déjà dans l'arène)
- type de pari vainqueur : 37 opérations, +183.03, +1.8% par mise, gagnés 34/33.3 → `filtres: {'familles': ['sports'], 'types_pari': ['vainqueur']}` (déjà dans l'arène)
- discipline football : 29 opérations, +170.22, +5.1% par mise, gagnés 28/26.6 → `filtres: {'familles': ['sports'], 'disciplines': ['football']}` (déjà dans l'arène)
- prix payé 0,925-0,950 : 27 opérations, +124.10, +2.6% par mise, gagnés 26/25.3 → `filtres: {'familles': ['sports'], 'prix_min': 0.925, 'prix_max': 0.95}` (déjà dans l'arène)
- prix payé 0,900-0,925 : 16 opérations, +76.87, +2.5% par mise, gagnés 15/14.6 → `filtres: {'familles': ['sports'], 'prix_min': 0.9, 'prix_max': 0.925}`
- type de pari score_exact : 10 opérations, +55.78, +7.8% par mise, gagnés 10/9.2 → `filtres: {'familles': ['sports'], 'types_pari': ['score_exact']}`
- délai jusqu'à la fin 0-3 h : 8 opérations, +55.64, +9.3% par mise, gagnés 8/7.3 → `filtres: {'familles': ['sports'], 'echeance_min': 0, 'echeance_max': 3}`
- délai jusqu'à la fin 6-12 h : 9 opérations, +50.39, +12.6% par mise, gagnés 9/8.0 → `filtres: {'familles': ['sports'], 'echeance_min': 6, 'echeance_max': 12}`
- délai jusqu'à la fin 24-72 h : 10 opérations, +47.24, +8.6% par mise, gagnés 10/9.2 → `filtres: {'familles': ['sports'], 'echeance_min': 24, 'echeance_max': 72}`
- délai jusqu'à la fin 72-168 h : 9 opérations, +43.10, +9.4% par mise, gagnés 9/8.2 → `filtres: {'familles': ['sports'], 'echeance_min': 72, 'echeance_max': 168}`
- heure d'achat 18-24 h UTC + type de pari vainqueur : 19 opérations, +154.03, +4.7% par mise, gagnés 18/17.2 → `filtres: {'familles': ['sports'], 'heure_utc': [18, 24], 'types_pari': ['vainqueur']}` (déjà dans l'arène)

## nf_tennis_12_18h_vainqueur_v1.0.0 — croissance +25.3% (mère nf_tennis : +17.6%)

58 opérations, résultat +253.18, rendement moyen +4.55% par mise, confiance +1.05, gagnés 53 pour 50.4 attendus (z +1.01).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,900-0,925, 0,800-0,850, 0,000-0,800 | 59% | 0,900-0,925 (10, +130, +9.2%, +1.0) ; 0,800-0,850 (20, +98, +2.6%, +0.3) ; 0,000-0,800 (4, +71, +25.4%, +1.0) ; 0,925-0,950 (7, +27, +6.6%, +0.7) ; 0,950-1,000 (4, +17, +4.7%, +0.5) ; 0,850-0,875 (8, +17, +0.4%, +0.1) |
| delai | 72-168 h | 98% | 72-168 h (57, +244, +4.3%, +0.9) ; 168 h et plus (1, +9, +20.9%, +0.5) |
| issue | autre | 100% | autre (58, +253, +4.5%, +1.0) |
| heure_utc | 12-18 h UTC | 100% | 12-18 h UTC (58, +253, +4.5%, +1.0) |
| discipline | tennis, inconnu | 100% | tennis (49, +186, +3.7%, +0.8) ; inconnu (9, +68, +9.1%, +0.9) |
| type_pari | vainqueur, inconnu | 100% | vainqueur (49, +186, +3.7%, +0.8) ; inconnu (9, +68, +9.1%, +0.9) |
| mode | immédiat | 100% | immédiat (58, +253, +4.5%, +1.0) |
| source | itftennis.com, atptour.com, inconnu | 88% | itftennis.com (17, +138, +8.2%, +0.9) ; atptour.com (25, +86, +1.2%, +0.2) ; inconnu (9, +68, +9.1%, +0.9) ; wtatennis.com (7, -38, +1.7%, +0.1) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- prix payé 0,900-0,925 : 10 opérations, +130.43, +9.2% par mise, gagnés 10/9.1 → `filtres: {'familles': ['sports'], 'disciplines': ['tennis'], 'heure_utc': [12, 18], 'types_pari': ['vainqueur'], 'prix_min': 0.9, 'prix_max': 0.925}`

## nf_tennis_v1.0.0 — croissance +17.6% (mère nf_sport_patiente : +6.4%)

86 opérations, résultat +176.21, rendement moyen +4.02% par mise, confiance +1.02, gagnés 77 pour 73.7 attendus (z +1.03).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,800-0,850, 0,900-0,925 | 45% | 0,800-0,850 (27, +139, +11.6%, +1.4) ; 0,900-0,925 (12, +101, +9.9%, +1.1) ; 0,950-1,000 (6, +16, +4.8%, +0.6) ; 0,875-0,900 (8, +1, -2.1%, -0.1) ; 0,000-0,800 (13, +1, -0.6%, -0.0) ; 0,850-0,875 (14, -11, -1.4%, -0.1) |
| delai | 72-168 h | 98% | 72-168 h (84, +158, +3.6%, +0.9) ; 168 h et plus (2, +18, +23.0%, +0.7) |
| issue | autre | 100% | autre (86, +176, +4.0%, +1.0) |
| heure_utc | 12-18 h UTC, 6-12 h UTC | 63% | 12-18 h UTC (20, +177, +18.7%, +2.0) ; 6-12 h UTC (34, +42, +3.5%, +0.5) ; 18-24 h UTC (19, +14, +2.0%, +0.3) ; 0-6 h UTC (13, -56, -14.2%, -1.2) |
| discipline | tennis | 79% | tennis (68, +147, +4.8%, +1.1) ; inconnu (18, +30, +1.2%, +0.2) |
| type_pari | vainqueur | 79% | vainqueur (68, +147, +4.8%, +1.1) ; inconnu (18, +30, +1.2%, +0.2) |
| mode | immédiat | 100% | immédiat (86, +176, +4.0%, +1.0) |
| source | atptour.com, inconnu, itftennis.com | 92% | atptour.com (46, +110, +7.5%, +1.2) ; inconnu (18, +30, +1.2%, +0.2) ; itftennis.com (15, +21, -3.3%, -0.2) ; wtatennis.com (7, +16, +4.3%, +0.3) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- heure d'achat 12-18 h UTC : 20 opérations, +176.61, +18.7% par mise, gagnés 20/16.8 → `filtres: {'familles': ['sports'], 'disciplines': ['tennis'], 'heure_utc': [12, 18]}` (déjà dans l'arène)
- discipline tennis : 68 opérations, +146.63, +4.8% par mise, gagnés 61/58.0 → `filtres: {'familles': ['sports'], 'disciplines': ['tennis']}` (déjà dans l'arène)
- type de pari vainqueur : 68 opérations, +146.63, +4.8% par mise, gagnés 61/58.0 → `filtres: {'familles': ['sports'], 'disciplines': ['tennis'], 'types_pari': ['vainqueur']}` (déjà dans l'arène)
- prix payé 0,800-0,850 : 27 opérations, +139.34, +11.6% par mise, gagnés 25/22.2 → `filtres: {'familles': ['sports'], 'disciplines': ['tennis'], 'prix_min': 0.8, 'prix_max': 0.85}`
- prix payé 0,900-0,925 : 12 opérations, +101.21, +9.9% par mise, gagnés 12/10.9 → `filtres: {'familles': ['sports'], 'disciplines': ['tennis'], 'prix_min': 0.9, 'prix_max': 0.925}`
- heure d'achat 12-18 h UTC + type de pari vainqueur : 15 opérations, +144.34, +19.4% par mise, gagnés 15/12.5 → `filtres: {'familles': ['sports'], 'disciplines': ['tennis'], 'heure_utc': [12, 18], 'types_pari': ['vainqueur']}` (déjà dans l'arène)

## nf_sport_patiente_prix_850_875_v1.0.0 — croissance +16.7% (mère nf_sport_patiente : +6.4%)

41 opérations, résultat +167.27, rendement moyen +5.80% par mise, confiance +1.14, gagnés 36 pour 34.9 attendus (z +0.50).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,850-0,875 | 61% | 0,850-0,875 (25, +215, +11.8%, +0.9) ; 0,800-0,850 (16, -48, -3.6%, -0.3) |
| delai | 3-6 h, 72-168 h, 6-12 h | 80% | 3-6 h (12, +138, +16.9%, +1.4) ; 72-168 h (17, +67, +3.3%, +0.4) ; 6-12 h (4, +66, +18.0%, +0.8) ; 0-3 h (4, +53, +3.7%, -0.5) ; 168 h et plus (4, -158, -27.0%, -2.0) |
| issue | autre, non | 100% | autre (38, +112, +4.9%, +0.3) ; non (3, +55, +17.2%, +0.7) |
| heure_utc | 0-6 h UTC, 12-18 h UTC | 44% | 0-6 h UTC (8, +117, +16.9%, +1.2) ; 12-18 h UTC (10, +30, +0.1%, -0.4) ; 18-24 h UTC (11, +21, +6.5%, +0.6) ; 6-12 h UTC (12, -0, +2.6%, -0.2) |
| discipline | tennis, counter-strike, football, inconnu | 78% | tennis (14, +99, +8.6%, +0.8) ; counter-strike (9, +95, +10.6%, +0.3) ; football (5, +67, +18.5%, +1.0) ; inconnu (4, +52, +16.6%, +0.8) ; valorant (1, +27, +17.6%, +0.4) ; dota (2, +4, +17.4%, +0.6) |
| type_pari | inconnu, total, score_exact, handicap | 22% | inconnu (4, +52, +16.6%, +0.8) ; total (3, +39, +19.1%, +0.8) ; score_exact (1, +27, +16.3%, +0.4) ; handicap (1, +26, +19.1%, +0.4) ; partie (3, +17, +17.1%, +0.7) ; nul (1, +14, +19.1%, +0.4) |
| mode | ordre posé, immédiat | 100% | ordre posé (29, +103, +5.1%, +0.1) ; immédiat (12, +64, +7.5%, +0.7) |
| source | itftennis.com, hltv.org, inconnu, uefa.com | 61% | itftennis.com (8, +131, +17.3%, +1.2) ; hltv.org (9, +95, +10.6%, +0.3) ; inconnu (5, +79, +16.6%, +0.9) ; uefa.com (3, +39, +19.1%, +0.8) ; vlr.gg (1, +27, +17.6%, +0.4) ; nbl.com.au (1, +12, +16.1%, +0.4) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- prix payé 0,850-0,875 : 25 opérations, +215.47, +11.8% par mise, gagnés 23/21.4 → `filtres: {'familles': ['sports'], 'prix_min': 0.85, 'prix_max': 0.875}` (déjà dans l'arène)
- délai jusqu'à la fin 3-6 h : 12 opérations, +138.43, +16.9% par mise, gagnés 12/10.2 → `filtres: {'familles': ['sports'], 'prix_min': 0.85, 'prix_max': 0.875, 'echeance_min': 3, 'echeance_max': 6}`
- heure d'achat 0-6 h UTC : 8 opérations, +116.76, +16.9% par mise, gagnés 8/6.8 → `filtres: {'familles': ['sports'], 'prix_min': 0.85, 'prix_max': 0.875, 'heure_utc': [0, 6]}`
- discipline tennis : 14 opérations, +98.86, +8.6% par mise, gagnés 13/11.9 → `filtres: {'familles': ['sports'], 'prix_min': 0.85, 'prix_max': 0.875, 'disciplines': ['tennis']}`
- discipline counter-strike : 9 opérations, +95.11, +10.6% par mise, gagnés 8/7.7 → `filtres: {'familles': ['sports'], 'prix_min': 0.85, 'prix_max': 0.875, 'disciplines': ['counter-strike']}`
- heure d'achat 18-24 h UTC : 11 opérations, +20.80, +6.5% par mise, gagnés 10/9.4 → `filtres: {'familles': ['sports'], 'prix_min': 0.85, 'prix_max': 0.875, 'heure_utc': [18, 24]}`
- discipline tennis + prix payé 0,850-0,875 : 9 opérations, +92.90, +16.4% par mise, gagnés 9/7.7 → `filtres: {'familles': ['sports'], 'prix_min': 0.85, 'prix_max': 0.875, 'disciplines': ['tennis']}`

## nf_sport_patiente_72_168h_12_18h_v1.0.0 — croissance +16.2% (mère nf_sport_patiente : +6.4%)

29 opérations, résultat +162.38, rendement moyen +5.36% par mise, confiance +0.97, gagnés 27 pour 25.6 attendus (z +0.81).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,875-0,900, 0,800-0,850, 0,900-0,925 | 69% | 0,875-0,900 (10, +98, +12.4%, +1.1) ; 0,800-0,850 (6, +76, +21.2%, +1.1) ; 0,900-0,925 (4, +47, +9.3%, +0.6) ; 0,925-0,950 (6, -22, -10.9%, -1.0) ; 0,850-0,875 (3, -37, -22.6%, -0.9) |
| delai | 72-168 h | 100% | 72-168 h (29, +162, +5.4%, +0.8) |
| issue | autre | 97% | autre (28, +158, +4.8%, +0.7) ; oui (1, +5, +22.3%, +0.5) |
| heure_utc | 12-18 h UTC | 100% | 12-18 h UTC (29, +162, +5.4%, +0.8) |
| discipline | tennis | 72% | tennis (21, +177, +8.2%, +1.1) ; inconnu (3, +30, +11.0%, +0.6) ; autre (5, -44, -9.8%, -0.7) |
| type_pari | vainqueur | 90% | vainqueur (26, +133, +4.7%, +0.7) ; inconnu (3, +30, +11.0%, +0.6) |
| mode | immédiat | 62% | immédiat (18, +148, +6.6%, +0.8) ; ordre posé (11, +15, +3.3%, +0.2) |
| source | atptour.com, itftennis.com, inconnu | 79% | atptour.com (14, +107, +5.3%, +0.6) ; itftennis.com (6, +56, +13.8%, +0.9) ; inconnu (3, +30, +11.0%, +0.6) ; flashscore.com (2, +15, +8.3%, +0.4) ; wtatennis.com (1, +14, +13.3%, +0.4) ; espncricinfo.com (3, -60, -21.8%, -1.1) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- discipline tennis : 21 opérations, +176.80, +8.2% par mise, gagnés 20/18.4 → `filtres: {'familles': ['sports'], 'echeance_min': 72, 'echeance_max': 168, 'heure_utc': [12, 18], 'prix_min': 0.8, 'prix_final': True, 'disciplines': ['tennis']}`
- prix payé 0,875-0,900 : 10 opérations, +98.46, +12.4% par mise, gagnés 10/8.9 → `filtres: {'familles': ['sports'], 'echeance_min': 72, 'echeance_max': 168, 'heure_utc': [12, 18], 'prix_min': 0.875, 'prix_final': True, 'prix_max': 0.9}`

## nf_tennis_12_18h_v1.0.0 — croissance +14.6% (mère nf_tennis : +17.6%)

67 opérations, résultat +146.23, rendement moyen +3.75% par mise, confiance +0.92, gagnés 61 pour 58.5 attendus (z +0.93).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,900-0,925, 0,800-0,850, 0,000-0,800 | 55% | 0,900-0,925 (13, +124, +9.0%, +1.1) ; 0,800-0,850 (21, +83, +3.5%, +0.4) ; 0,000-0,800 (3, +44, +26.1%, +0.9) ; 0,925-0,950 (8, +37, +6.2%, +0.7) ; 0,950-1,000 (3, +10, +4.8%, +0.4) ; 0,850-0,875 (10, -54, -8.0%, -0.6) |
| delai | 72-168 h | 100% | 72-168 h (67, +146, +3.8%, +0.9) |
| issue | autre | 100% | autre (67, +146, +3.8%, +0.9) |
| heure_utc | 12-18 h UTC | 100% | 12-18 h UTC (67, +146, +3.8%, +0.9) |
| discipline | inconnu | 22% | inconnu (15, +120, +9.6%, +1.2) ; tennis (52, +26, +2.1%, +0.5) |
| type_pari | inconnu | 22% | inconnu (15, +120, +9.6%, +1.2) ; vainqueur (52, +26, +2.1%, +0.5) |
| mode | immédiat | 100% | immédiat (67, +146, +3.8%, +0.9) |
| source | inconnu, itftennis.com | 46% | inconnu (15, +120, +9.6%, +1.2) ; itftennis.com (16, +81, +8.2%, +0.9) ; atptour.com (30, -10, -0.6%, +0.0) ; wtatennis.com (6, -45, -0.9%, -0.0) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- prix payé 0,900-0,925 : 13 opérations, +124.14, +9.0% par mise, gagnés 13/11.9 → `filtres: {'familles': ['sports'], 'disciplines': ['tennis'], 'heure_utc': [12, 18], 'prix_min': 0.9, 'prix_max': 0.925}`
- prix payé 0,925-0,950 : 8 opérations, +36.99, +6.2% par mise, gagnés 8/7.5 → `filtres: {'familles': ['sports'], 'disciplines': ['tennis'], 'heure_utc': [12, 18], 'prix_min': 0.925, 'prix_max': 0.95}`

## naive_favorite_v1.0.0 — croissance +11.8%

20 opérations, résultat +118.34, rendement moyen -2.07% par mise, confiance -0.28, gagnés 18 pour 18.3 attendus (z -0.27).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,925-0,950, 0,800-0,850 | 55% | 0,925-0,950 (10, +83, +6.3%, +0.8) ; 0,800-0,850 (1, +18, +23.0%, +0.5) ; 0,900-0,925 (7, +11, -22.1%, -1.9) ; 0,875-0,900 (1, +6, +13.0%, +0.4) ; 0,850-0,875 (1, +0, +14.3%, +0.4) |
| delai | 24-72 h, 168 h et plus | 45% | 24-72 h (7, +78, +6.6%, +0.7) ; 168 h et plus (2, +19, +18.7%, +0.6) ; 72-168 h (1, +6, +13.0%, +0.4) ; 0-3 h (1, +4, +7.1%, +0.3) ; 3-6 h (3, +4, -28.5%, -1.7) ; 12-24 h (4, +4, -18.7%, -1.2) |
| issue | non, oui | 70% | non (7, +55, -5.3%, -0.4) ; oui (7, +43, +7.3%, +0.7) ; autre (6, +20, -9.3%, -0.7) |
| heure_utc | 12-18 h UTC | 65% | 12-18 h UTC (13, +107, +1.5%, +0.2) ; 18-24 h UTC (4, +16, +6.4%, +0.5) ; 0-6 h UTC (3, -5, -28.6%, -1.7) |
| discipline | autre, mlb | 80% | autre (15, +90, +0.5%, +0.1) ; mlb (1, +18, +23.0%, +0.5) ; counter-strike (1, +7, +6.1%, +0.2) ; tennis (1, +6, +13.0%, +0.4) ; inconnu (2, -3, -45.8%, -2.2) |
| type_pari | autre, vainqueur | 85% | autre (11, +88, +7.6%, +0.9) ; vainqueur (6, +29, -6.9%, -0.5) ; score_exact (1, +4, +7.1%, +0.3) ; inconnu (2, -3, -45.8%, -2.2) |
| mode | immédiat | 100% | immédiat (20, +118, -2.1%, -0.3) |
| source | binance.com, mlb.com, x.com | 45% | binance.com (6, +66, +6.2%, +0.6) ; mlb.com (1, +18, +23.0%, +0.5) ; x.com (2, +16, +10.0%, +0.5) ; hltv.org (1, +7, +6.1%, +0.2) ; inconnu (5, +6, -14.4%, -1.1) ; atptour.com (1, +6, +13.0%, +0.4) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- heure d'achat 12-18 h UTC : 13 opérations, +106.70, +1.5% par mise, gagnés 12/11.8 → `filtres: {'heure_utc': [12, 18]}`
- prix payé 0,925-0,950 : 10 opérations, +82.91, +6.3% par mise, gagnés 10/9.4 → `filtres: {'prix_min': 0.925, 'prix_max': 0.95}`

## nf_court_v1.0.0 — croissance +10.9% (mère naive_favorite : +11.8%)

138 opérations, résultat +108.87, rendement moyen -1.77% par mise, confiance -0.58, gagnés 122 pour 123.4 attendus (z -0.38).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,900-0,925, 0,850-0,875 | 42% | 0,900-0,925 (36, +106, -2.8%, -0.5) ; 0,850-0,875 (22, +61, +5.0%, +0.7) ; 0,925-0,950 (44, +35, +4.1%, +1.1) ; 0,950-1,000 (1, +1, +5.1%, +0.2) ; 0,800-0,850 (24, -31, -14.5%, -1.5) ; 0,875-0,900 (11, -64, -8.2%, -0.7) |
| delai | 0-3 h, 6-12 h | 37% | 0-3 h (28, +132, +3.1%, +0.6) ; 6-12 h (23, +54, +2.1%, +0.3) ; 3-6 h (14, +22, +2.2%, +0.3) ; 24-72 h (15, +17, -5.0%, -0.4) ; 72-168 h (3, +3, +6.4%, +0.5) ; 12-24 h (49, -58, -6.3%, -1.2) |
| issue | non, oui | 59% | non (74, +83, -2.2%, -0.3) ; oui (8, +18, +8.7%, +0.9) ; autre (56, +8, -2.7%, -0.5) |
| heure_utc | 18-24 h UTC, 12-18 h UTC | 54% | 18-24 h UTC (54, +98, +3.5%, +0.9) ; 12-18 h UTC (20, +55, -1.4%, -0.1) ; 6-12 h UTC (18, +24, -2.7%, -0.2) ; 0-6 h UTC (46, -68, -7.7%, -1.2) |
| discipline | autre, football | 85% | autre (60, +145, -1.3%, -0.2) ; football (57, +106, +2.8%, +0.8) ; inconnu (3, +9, +6.6%, +0.5) ; lol (1, +8, +13.0%, +0.4) ; valorant (1, +0, +16.8%, +0.4) ; mlb (1, +0, +14.2%, +0.4) |
| type_pari | score_exact, total, handicap | 30% | score_exact (14, +73, +0.6%, +0.1) ; total (14, +25, +1.2%, +0.2) ; handicap (14, +15, +4.8%, +0.5) ; inconnu (3, +9, +6.6%, +0.5) ; nul (4, +8, +15.7%, +0.8) ; partie (1, +1, +9.4%, +0.3) |
| mode | immédiat | 100% | immédiat (138, +109, -1.8%, -0.4) |
| source | ncaa.com, inconnu, premierleague.com, laliga.com, cbf.com.br, bundesliga.com, afa.com.ar, ligue1.com | 41% | ncaa.com (15, +91, +5.4%, +0.6) ; inconnu (19, +85, +2.4%, +0.4) ; premierleague.com (10, +47, +12.1%, +1.1) ; laliga.com (5, +25, +13.6%, +0.8) ; cbf.com.br (3, +22, +9.0%, +0.5) ; bundesliga.com (1, +14, +8.3%, +0.3) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 0-3 h : 28 opérations, +131.64, +3.1% par mise, gagnés 26/25.1 → `filtres: {'heures_min': 0, 'heures_max': 24, 'echeance_min': 0, 'echeance_max': 3}`
- discipline football : 57 opérations, +105.80, +2.8% par mise, gagnés 53/51.2 → `filtres: {'heures_min': 0, 'heures_max': 24, 'disciplines': ['football']}` (déjà dans l'arène)
- heure d'achat 18-24 h UTC : 54 opérations, +97.94, +3.5% par mise, gagnés 51/49.1 → `filtres: {'heures_min': 0, 'heures_max': 24, 'heure_utc': [18, 24]}` (déjà dans l'arène)
- type de pari score_exact : 14 opérations, +72.82, +0.6% par mise, gagnés 13/12.9 → `filtres: {'heures_min': 0, 'heures_max': 24, 'types_pari': ['score_exact']}`
- prix payé 0,850-0,875 : 22 opérations, +61.19, +5.0% par mise, gagnés 20/18.9 → `filtres: {'heures_min': 0, 'heures_max': 24, 'prix_min': 0.85, 'prix_max': 0.875}`
- délai jusqu'à la fin 6-12 h : 23 opérations, +54.47, +2.1% par mise, gagnés 21/20.5 → `filtres: {'heures_min': 0, 'heures_max': 24, 'echeance_min': 6, 'echeance_max': 12}`
- prix payé 0,925-0,950 : 44 opérations, +34.57, +4.1% par mise, gagnés 43/41.2 → `filtres: {'heures_min': 0, 'heures_max': 24, 'prix_min': 0.925, 'prix_max': 0.95}`
- type de pari total : 14 opérations, +24.80, +1.2% par mise, gagnés 13/12.7 → `filtres: {'heures_min': 0, 'heures_max': 24, 'types_pari': ['total']}`
- délai jusqu'à la fin 3-6 h : 14 opérations, +22.20, +2.2% par mise, gagnés 13/12.7 → `filtres: {'heures_min': 0, 'heures_max': 24, 'echeance_min': 3, 'echeance_max': 6}`
- issue oui : 8 opérations, +18.19, +8.7% par mise, gagnés 8/7.3 → `filtres: {'heures_min': 0, 'heures_max': 24, 'issue': ['oui']}`
- type de pari handicap : 14 opérations, +15.31, +4.8% par mise, gagnés 13/12.4 → `filtres: {'heures_min': 0, 'heures_max': 24, 'types_pari': ['handicap']}`
- délai jusqu'à la fin 0-3 h + heure d'achat 18-24 h UTC : 12 opérations, +81.57, +10.8% par mise, gagnés 12/10.8 → `filtres: {'heures_min': 0, 'heures_max': 24, 'echeance_min': 0, 'echeance_max': 3, 'heure_utc': [18, 24]}`

## crypto_threshold_v1.0.0 — croissance +10.1%

18 opérations, résultat +100.81, rendement moyen +67.83% par mise, confiance +0.89, gagnés 7 pour 6.5 attendus (z +0.33).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,000-0,800, 0,875-0,900 | 89% | 0,000-0,800 (15, +229, +93.9%, +1.5) ; 0,875-0,900 (1, +85, +12.8%, +0.4) ; 0,900-0,925 (1, -9, -100.0%, -3.4) ; 0,950-1,000 (1, -204, -100.0%, -4.4) |
| delai | 24-72 h, 72-168 h | 72% | 24-72 h (10, +194, +83.3%, +1.4) ; 72-168 h (3, +44, +200.2%, +0.7) ; 168 h et plus (1, +13, +74.9%, +0.9) ; 3-6 h (1, -22, -100.0%, -0.8) ; 0-3 h (3, -128, -62.4%, -3.7) |
| issue | non, oui | 100% | non (12, +58, +127.8%, +0.6) ; oui (6, +43, -52.0%, -0.3) |
| heure_utc | 12-18 h UTC | 50% | 12-18 h UTC (9, +113, +116.1%, +0.3) ; 6-12 h UTC (7, -4, +28.7%, +0.1) ; 18-24 h UTC (2, -9, -12.5%, +0.1) |
| discipline | autre | 83% | autre (15, +229, +93.9%, +1.5) ; inconnu (3, -128, -62.4%, -3.7) |
| type_pari | autre | 83% | autre (15, +229, +93.9%, +1.5) ; inconnu (3, -128, -62.4%, -3.7) |
| mode | immédiat | 100% | immédiat (18, +101, +67.8%, +0.3) |
| source | binance.com | 83% | binance.com (15, +229, +93.9%, +1.5) ; inconnu (3, -128, -62.4%, -3.7) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- prix payé 0,000-0,800 : 15 opérations, +228.89, +93.9% par mise, gagnés 6/3.7 → `filtres: {'prix_min': 0.0, 'prix_max': 0.8}` (déjà dans l'arène)
- délai jusqu'à la fin 24-72 h : 10 opérations, +193.66, +83.3% par mise, gagnés 4/2.2 → `filtres: {'echeance_min': 24, 'echeance_max': 72}` (déjà dans l'arène)
- heure d'achat 12-18 h UTC : 9 opérations, +112.97, +116.1% par mise, gagnés 5/4.6 → `filtres: {'heure_utc': [12, 18]}`
- issue non : 12 opérations, +58.10, +127.8% par mise, gagnés 5/4.2 → `filtres: {'issue': ['non']}`
- issue non + prix payé 0,000-0,800 : 10 opérations, +271.36, +173.3% par mise, gagnés 5/2.3 → `filtres: {'issue': ['non'], 'prix_min': 0.0, 'prix_max': 0.8}` (déjà dans l'arène)

## compteur_tweets_non_v1.0.0 — croissance +9.9% (mère compteur_tweets : +2.2%)

12 opérations, résultat +99.34, rendement moyen +7.55% par mise, confiance +0.37, gagnés 9 pour 7.8 attendus (z +0.83).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,000-0,800 | 75% | 0,000-0,800 (9, +85, +5.6%, +0.6) ; 0,800-0,850 (1, +9, +18.9%, +0.4) ; 0,900-0,925 (2, +6, +10.7%, +0.5) |
| delai | 72-168 h, 12-24 h, 24-72 h | 83% | 72-168 h (1, +53, +72.8%, +0.8) ; 12-24 h (1, +32, +113.3%, +1.1) ; 24-72 h (8, +24, +13.1%, +0.7) ; 0-3 h (2, -10, -100.0%, -0.9) |
| issue | non | 100% | non (12, +99, +7.5%, +0.8) |
| heure_utc | 6-12 h UTC, 0-6 h UTC | 75% | 6-12 h UTC (5, +70, +41.4%, +1.4) ; 0-6 h UTC (4, +45, +46.0%, +1.3) ; 18-24 h UTC (1, -6, -100.0%, -1.6) ; 12-18 h UTC (2, -10, -100.0%, -0.9) |
| discipline | autre | 100% | autre (12, +99, +7.5%, +0.8) |
| type_pari | autre | 100% | autre (12, +99, +7.5%, +0.8) |
| mode | immédiat | 100% | immédiat (12, +99, +7.5%, +0.8) |
| source | x.com | 83% | x.com (10, +86, -0.1%, +0.5) ; truthsocial.com (2, +13, +46.0%, +0.9) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 24-72 h : 8 opérations, +24.12, +13.1% par mise, gagnés 7/6.2 → `filtres: {'echeance_min': 24, 'echeance_max': 72}`

## nf_sport_prix_haut_v1.0.0 — croissance +9.2% (mère naive_favorite : +11.8%)

110 opérations, résultat +91.60, rendement moyen +0.10% par mise, confiance +0.03, gagnés 101 pour 100.5 attendus (z +0.17).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,875-0,900, 0,925-0,950 | 66% | 0,875-0,900 (25, +115, +3.0%, +0.5) ; 0,925-0,950 (47, +56, +2.1%, +0.6) ; 0,800-0,850 (1, +17, +16.8%, +0.4) ; 0,900-0,925 (33, -39, -3.8%, -0.6) ; 0,850-0,875 (4, -58, -13.7%, -0.7) |
| delai | 3-6 h, 0-3 h, 24-72 h | 39% | 3-6 h (16, +119, +2.0%, +0.3) ; 0-3 h (18, +81, +9.0%, +1.3) ; 24-72 h (9, +34, +8.8%, +0.9) ; 168 h et plus (8, +30, +10.0%, +0.9) ; 12-24 h (18, +22, -3.9%, -0.5) ; 72-168 h (34, -75, -6.5%, -1.1) |
| issue | non, autre | 98% | non (29, +64, +4.3%, +0.9) ; autre (79, +18, -1.7%, -0.3) ; oui (2, +10, +8.8%, +0.4) |
| heure_utc | 12-18 h UTC, 18-24 h UTC, 0-6 h UTC | 73% | 12-18 h UTC (11, +73, +9.4%, +1.0) ; 18-24 h UTC (36, +67, -0.6%, -0.1) ; 0-6 h UTC (33, +38, +0.3%, +0.2) ; 6-12 h UTC (30, -88, -2.7%, -0.5) |
| discipline | football, counter-strike, dota, lol | 41% | football (37, +108, +5.1%, +1.1) ; counter-strike (3, +31, +12.6%, +0.6) ; dota (2, +22, -44.1%, -1.9) ; lol (3, +15, +11.0%, +0.6) ; inconnu (11, +12, +7.0%, +0.9) ; mlb (4, +9, +10.5%, +0.7) |
| type_pari | handicap, total, score_exact, partie | 34% | handicap (11, +63, +9.3%, +1.0) ; total (14, +62, +7.7%, +1.1) ; score_exact (9, +37, +7.8%, +0.9) ; partie (3, +31, +12.2%, +0.6) ; inconnu (11, +12, +7.0%, +0.9) ; nul (2, +4, +8.9%, +0.4) |
| mode | immédiat | 100% | immédiat (110, +92, +0.1%, +0.2) |
| source | inconnu, hltv.org, premierleague.com, ligamx.net, gol.gg, dotabuff.com, cbf.com.br, bundesliga.com, mlssoccer.com, laliga.com | 44% | inconnu (21, +50, +7.5%, +1.3) ; hltv.org (3, +31, +12.6%, +0.6) ; premierleague.com (6, +30, +7.0%, +0.7) ; ligamx.net (1, +30, +9.4%, +0.3) ; gol.gg (4, +26, +11.5%, +0.7) ; dotabuff.com (2, +22, -44.1%, -1.9) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 3-6 h : 16 opérations, +118.91, +2.0% par mise, gagnés 15/14.6 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.95, 'echeance_min': 3, 'echeance_max': 6}` (déjà dans l'arène)
- prix payé 0,875-0,900 : 25 opérations, +115.14, +3.0% par mise, gagnés 23/22.2 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.9}`
- discipline football : 37 opérations, +107.81, +5.1% par mise, gagnés 36/34.2 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.95, 'disciplines': ['football']}`
- délai jusqu'à la fin 0-3 h : 18 opérations, +81.06, +9.0% par mise, gagnés 18/16.5 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.95, 'echeance_min': 0, 'echeance_max': 3}`
- heure d'achat 12-18 h UTC : 11 opérations, +73.49, +9.4% par mise, gagnés 11/10.0 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.95, 'heure_utc': [12, 18]}`
- issue non : 29 opérations, +63.64, +4.3% par mise, gagnés 28/26.8 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.95, 'issue': ['non']}`
- type de pari handicap : 11 opérations, +63.13, +9.3% par mise, gagnés 11/10.0 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.95, 'types_pari': ['handicap']}`
- type de pari total : 14 opérations, +62.28, +7.7% par mise, gagnés 14/13.0 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.95, 'types_pari': ['total']}`
- prix payé 0,925-0,950 : 47 opérations, +55.97, +2.1% par mise, gagnés 45/43.9 → `filtres: {'familles': ['sports'], 'prix_min': 0.925, 'prix_max': 0.95}`
- heure d'achat 0-6 h UTC : 33 opérations, +38.42, +0.3% par mise, gagnés 30/29.7 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.95, 'heure_utc': [0, 6]}`
- type de pari score_exact : 9 opérations, +37.41, +7.8% par mise, gagnés 9/8.3 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.95, 'types_pari': ['score_exact']}`
- délai jusqu'à la fin 24-72 h : 9 opérations, +33.64, +8.8% par mise, gagnés 9/8.2 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.95, 'echeance_min': 24, 'echeance_max': 72}`
- délai jusqu'à la fin 168 h et plus : 8 opérations, +29.92, +10.0% par mise, gagnés 8/7.2 → `filtres: {'familles': ['sports'], 'prix_min': 0.875, 'prix_max': 0.95, 'echeance_min': 168}`
- délai jusqu'à la fin 3-6 h + prix payé 0,925-0,950 : 8 opérations, +42.33, +6.7% par mise, gagnés 8/7.5 → `filtres: {'familles': ['sports'], 'prix_min': 0.925, 'prix_max': 0.95, 'echeance_min': 3, 'echeance_max': 6}`

## nf_moyen_v1.0.0 — croissance +8.9% (mère naive_favorite : +11.8%)

18 opérations, résultat +89.31, rendement moyen +3.17% par mise, confiance +0.52, gagnés 17 pour 16.5 attendus (z +0.45).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,925-0,950, 0,900-0,925 | 83% | 0,925-0,950 (10, +54, -4.2%, -0.5) ; 0,900-0,925 (5, +30, +8.6%, +0.7) ; 0,800-0,850 (2, +4, +20.7%, +0.7) ; 0,875-0,900 (1, +1, +14.1%, +0.4) |
| delai | 24-72 h | 89% | 24-72 h (16, +88, +9.3%, +1.2) ; 72-168 h (2, +1, -46.2%, -2.5) |
| issue | oui, non | 100% | oui (7, +47, +8.3%, +0.8) ; non (11, +42, -0.1%, -0.0) |
| heure_utc | 18-24 h UTC | 72% | 18-24 h UTC (13, +83, +9.5%, +1.1) ; 12-18 h UTC (2, +10, +6.9%, +0.4) ; 6-12 h UTC (1, +0, +5.9%, +0.2) ; 0-6 h UTC (2, -5, -42.9%, -2.0) |
| discipline | autre, football | 100% | autre (14, +63, +1.9%, +0.2) ; football (4, +26, +7.7%, +0.6) |
| type_pari | autre, vainqueur | 94% | autre (14, +63, +1.9%, +0.2) ; vainqueur (3, +26, +7.5%, +0.5) ; nul (1, +0, +8.3%, +0.3) |
| mode | immédiat | 100% | immédiat (18, +89, +3.2%, +0.5) |
| source | binance.com, inconnu, laliga.com | 78% | binance.com (7, +37, +8.6%, +0.8) ; inconnu (6, +25, -9.4%, -0.8) ; laliga.com (1, +14, +7.1%, +0.3) ; uefa.com (3, +12, +7.9%, +0.5) ; weather.gov (1, +1, +22.3%, +0.5) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 24-72 h : 16 opérations, +88.47, +9.3% par mise, gagnés 16/14.6 → `filtres: {'heures_min': 24, 'heures_max': 168, 'echeance_min': 24, 'echeance_max': 72}`
- heure d'achat 18-24 h UTC : 13 opérations, +83.20, +9.5% par mise, gagnés 13/11.8 → `filtres: {'heures_min': 24, 'heures_max': 168, 'heure_utc': [18, 24]}`
- délai jusqu'à la fin 24-72 h + heure d'achat 18-24 h UTC : 12 opérations, +77.14, +9.6% par mise, gagnés 12/10.9 → `filtres: {'heures_min': 24, 'heures_max': 168, 'echeance_min': 24, 'echeance_max': 72, 'heure_utc': [18, 24]}`

## nf_court_football_soir_v1.0.0 — croissance +8.1% (mère nf_court : +10.9%)

23 opérations, résultat +80.52, rendement moyen +4.39% par mise, confiance +0.90, gagnés 22 pour 21.0 attendus (z +0.77).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,925-0,950, 0,875-0,900, 0,900-0,925 | 87% | 0,925-0,950 (14, +76, +6.4%, +1.0) ; 0,875-0,900 (3, +37, +12.2%, +0.6) ; 0,900-0,925 (3, +29, +9.4%, +0.5) ; 0,800-0,850 (2, +23, +23.0%, +0.7) ; 0,850-0,875 (1, -84, -100.0%, -2.4) |
| delai | 0-3 h, 12-24 h | 87% | 0-3 h (12, +116, +9.0%, +1.1) ; 12-24 h (8, +34, +9.6%, +0.9) ; 3-6 h (3, -69, -27.8%, -1.3) |
| issue | non, autre | 96% | non (17, +41, +2.4%, +0.4) ; autre (5, +26, +7.4%, +0.6) ; oui (1, +14, +23.8%, +0.5) |
| heure_utc | 18-24 h UTC | 100% | 18-24 h UTC (23, +81, +4.4%, +0.8) |
| discipline | football | 100% | football (23, +81, +4.4%, +0.8) |
| type_pari | score_exact, total | 44% | score_exact (7, +66, +7.0%, +0.7) ; total (3, +17, +6.4%, +0.5) ; handicap (2, +9, +8.9%, +0.4) ; vainqueur (11, -11, +1.3%, +0.2) |
| mode | immédiat | 100% | immédiat (23, +81, +4.4%, +0.8) |
| source | inconnu, uefa.com, mlssoccer.com, premierleague.com, ligamx.net | 74% | inconnu (7, +66, +7.0%, +0.7) ; uefa.com (4, +31, +9.2%, +0.6) ; mlssoccer.com (2, +18, +16.4%, +0.6) ; premierleague.com (3, +16, +6.4%, +0.5) ; ligamx.net (1, +15, +9.4%, +0.3) ; slstat.com (1, +14, +23.8%, +0.5) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 0-3 h : 12 opérations, +116.12, +9.0% par mise, gagnés 12/11.0 → `filtres: {'heures_min': 0, 'heures_max': 24, 'disciplines': ['football'], 'heure_utc': [18, 24], 'echeance_min': 0, 'echeance_max': 3}`
- prix payé 0,925-0,950 : 14 opérations, +75.80, +6.4% par mise, gagnés 14/13.1 → `filtres: {'heures_min': 0, 'heures_max': 24, 'disciplines': ['football'], 'heure_utc': [18, 24], 'prix_min': 0.925, 'prix_max': 0.95}`
- délai jusqu'à la fin 12-24 h : 8 opérations, +33.76, +9.6% par mise, gagnés 8/7.3 → `filtres: {'heures_min': 0, 'heures_max': 24, 'disciplines': ['football'], 'heure_utc': [18, 24], 'echeance_min': 12, 'echeance_max': 24}`

## nf_sport_patiente_6_24h_v1.0.0 — croissance +8.0% (mère nf_sport_patiente : +6.4%)

23 opérations, résultat +80.49, rendement moyen +5.83% par mise, confiance +0.82, gagnés 21 pour 19.8 attendus (z +0.74).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,900-0,925, 0,875-0,900 | 26% | 0,900-0,925 (5, +79, +9.1%, +0.7) ; 0,875-0,900 (1, +23, +13.4%, +0.4) ; 0,925-0,950 (3, +11, +6.3%, +0.4) ; 0,850-0,875 (1, +8, +16.3%, +0.4) ; 0,000-0,800 (1, +5, +26.6%, +0.5) ; 0,800-0,850 (12, -45, +1.1%, +0.1) |
| delai | 6-12 h | 52% | 6-12 h (12, +165, +13.9%, +1.3) ; 168 h et plus (3, +25, +19.0%, +0.8) ; 12-24 h (8, -110, -11.2%, -0.7) |
| issue | autre, non | 87% | autre (15, +70, +9.4%, +0.9) ; non (5, +45, +9.3%, +0.7) ; oui (3, -35, -17.6%, -0.6) |
| heure_utc | 12-18 h UTC, 18-24 h UTC | 56% | 12-18 h UTC (8, +110, +13.8%, +1.1) ; 18-24 h UTC (5, +50, +15.5%, +0.9) ; 0-6 h UTC (4, -33, -11.8%, -0.5) ; 6-12 h UTC (6, -47, -1.2%, -0.1) |
| discipline | autre, football, tennis, nfl | 78% | autre (3, +53, +12.4%, +0.6) ; football (11, +49, +4.8%, +0.4) ; tennis (3, +25, +19.0%, +0.8) ; nfl (1, +23, +13.4%, +0.4) ; dota (1, +14, +8.7%, +0.3) ; inconnu (1, +8, +16.3%, +0.4) |
| type_pari | total, score_exact, handicap | 44% | total (4, +72, +16.9%, +0.8) ; score_exact (3, +35, +8.1%, +0.5) ; handicap (3, +25, +13.2%, +0.6) ; inconnu (1, +8, +16.3%, +0.4) ; vainqueur (12, -59, -1.1%, -0.1) |
| mode | immédiat | 44% | immédiat (10, +129, +15.0%, +1.2) ; ordre posé (13, -48, -1.2%, -0.1) |
| source | uefa.com, inconnu, ncaa.com, nfl.com, wtatennis.com | 61% | uefa.com (6, +85, +18.4%, +1.1) ; inconnu (4, +43, +10.1%, +0.6) ; ncaa.com (1, +25, +18.8%, +0.4) ; nfl.com (1, +23, +13.4%, +0.4) ; wtatennis.com (2, +17, +16.8%, +0.6) ; dotabuff.com (1, +14, +8.7%, +0.3) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 6-12 h : 12 opérations, +165.18, +13.9% par mise, gagnés 12/10.6 → `filtres: {'familles': ['sports'], 'heures_min': 6, 'heures_max': 24, 'prix_min': 0.8, 'prix_final': True, 'echeance_min': 6, 'echeance_max': 12}` (déjà dans l'arène)
- heure d'achat 12-18 h UTC : 8 opérations, +110.34, +13.8% par mise, gagnés 8/7.0 → `filtres: {'familles': ['sports'], 'heures_min': 6, 'heures_max': 24, 'prix_min': 0.8, 'prix_final': True, 'heure_utc': [12, 18]}`
- issue autre : 15 opérations, +70.09, +9.4% par mise, gagnés 14/12.8 → `filtres: {'familles': ['sports'], 'heures_min': 6, 'heures_max': 24, 'prix_min': 0.8, 'prix_final': True, 'issue': ['autre']}` (déjà dans l'arène)
- délai jusqu'à la fin 6-12 h + issue autre : 8 opérations, +122.28, +15.8% par mise, gagnés 8/6.9 → `filtres: {'familles': ['sports'], 'heures_min': 6, 'heures_max': 24, 'prix_min': 0.8, 'prix_final': True, 'echeance_min': 6, 'echeance_max': 12, 'issue': ['autre']}`

## nf_sport_non_v1.0.0 — croissance +7.0% (mère naive_favorite : +11.8%)

39 opérations, résultat +69.67, rendement moyen +2.80% par mise, confiance +0.72, gagnés 37 pour 35.8 attendus (z +0.69).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,900-0,925, 0,875-0,900 | 41% | 0,900-0,925 (12, +157, +9.3%, +1.1) ; 0,875-0,900 (4, +46, +12.7%, +0.7) ; 0,925-0,950 (21, -41, +1.5%, +0.3) ; 0,850-0,875 (2, -92, -42.6%, -1.5) |
| delai | 0-3 h, 12-24 h, 3-6 h | 72% | 0-3 h (12, +120, +7.8%, +1.0) ; 12-24 h (12, +77, +8.6%, +1.0) ; 3-6 h (4, +51, +9.0%, +0.6) ; 168 h et plus (1, +4, +14.8%, +0.4) ; 72-168 h (1, +3, +9.4%, +0.3) ; 6-12 h (3, -75, -28.6%, -1.4) |
| issue | non | 100% | non (39, +70, +2.8%, +0.7) |
| heure_utc | 6-12 h UTC, 12-18 h UTC | 31% | 6-12 h UTC (6, +39, +6.5%, +0.6) ; 12-18 h UTC (6, +32, +7.0%, +0.7) ; 18-24 h UTC (17, +8, +2.6%, +0.4) ; 0-6 h UTC (10, -9, -1.6%, -0.1) |
| discipline | football, autre | 87% | football (28, +79, +4.4%, +0.9) ; autre (6, +55, +8.7%, +0.7) ; inconnu (3, +27, +6.2%, +0.4) ; mlb (1, +4, +14.8%, +0.4) ; nfl (1, -96, -100.0%, -2.5) |
| type_pari | score_exact, inconnu | 56% | score_exact (19, +149, +8.0%, +1.3) ; inconnu (3, +27, +6.2%, +0.4) ; nul (2, +16, +11.2%, +0.5) ; partie (1, +14, +9.4%, +0.3) ; vainqueur (13, -39, +0.5%, +0.1) ; autre (1, -96, -100.0%, -2.5) |
| mode | immédiat | 100% | immédiat (39, +70, +2.8%, +0.7) |
| source | inconnu, ligamx.net | 64% | inconnu (23, +189, +7.8%, +1.4) ; ligamx.net (2, +31, +11.2%, +0.5) ; cbf.com.br (1, +24, +9.4%, +0.3) ; laliga.com (1, +14, +8.3%, +0.3) ; slstat.com (1, +7, +7.1%, +0.3) ; mlb.com (1, +4, +14.8%, +0.4) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- prix payé 0,900-0,925 : 12 opérations, +157.33, +9.3% par mise, gagnés 12/10.9 → `filtres: {'familles': ['sports'], 'issue': ['non'], 'prix_min': 0.9, 'prix_max': 0.925}` (déjà dans l'arène)
- type de pari score_exact : 19 opérations, +148.57, +8.0% par mise, gagnés 19/17.5 → `filtres: {'familles': ['sports'], 'issue': ['non'], 'types_pari': ['score_exact']}`
- délai jusqu'à la fin 0-3 h : 12 opérations, +119.71, +7.8% par mise, gagnés 12/11.1 → `filtres: {'familles': ['sports'], 'issue': ['non'], 'echeance_min': 0, 'echeance_max': 3}`
- discipline football : 28 opérations, +79.41, +4.4% par mise, gagnés 27/25.8 → `filtres: {'familles': ['sports'], 'issue': ['non'], 'disciplines': ['football']}`
- délai jusqu'à la fin 12-24 h : 12 opérations, +77.24, +8.6% par mise, gagnés 12/11.0 → `filtres: {'familles': ['sports'], 'issue': ['non'], 'echeance_min': 12, 'echeance_max': 24}`
- discipline football + prix payé 0,900-0,925 : 9 opérations, +117.41, +9.4% par mise, gagnés 9/8.2 → `filtres: {'familles': ['sports'], 'issue': ['non'], 'disciplines': ['football'], 'prix_min': 0.9, 'prix_max': 0.925}`

## nf_sport_patiente_v1.0.0 — croissance +6.4% (mère naive_favorite : +11.8%)

168 opérations, résultat +63.59, rendement moyen +2.98% par mise, confiance +1.09, gagnés 150 pour 145.9 attendus (z +0.94).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,850-0,875, 0,800-0,850 | 52% | 0,850-0,875 (31, +267, +8.6%, +1.2) ; 0,800-0,850 (56, +258, +5.4%, +1.0) ; 0,875-0,900 (14, +28, +0.4%, -0.3) ; 0,000-0,800 (8, +2, +12.9%, +0.7) ; 0,925-0,950 (29, -126, -0.5%, -0.1) ; 0,900-0,925 (30, -366, -5.5%, -0.9) |
| delai | 72-168 h, 168 h et plus | 60% | 72-168 h (88, +612, +8.4%, +2.1) ; 168 h et plus (13, +137, +15.4%, +1.4) ; 6-12 h (11, +103, +5.3%, +0.5) ; 0-3 h (15, -50, -3.0%, -0.3) ; 12-24 h (4, -173, -14.3%, -0.9) ; 3-6 h (37, -565, -10.8%, -1.8) |
| issue | autre | 92% | autre (154, +98, +2.8%, +0.8) ; oui (1, +0, +8.3%, +0.3) ; non (13, -35, +4.8%, +0.4) |
| heure_utc | 12-18 h UTC, 0-6 h UTC, 6-12 h UTC | 82% | 12-18 h UTC (49, +232, +5.1%, +0.7) ; 0-6 h UTC (30, +175, +5.9%, +0.9) ; 6-12 h UTC (58, +169, +2.9%, +0.6) ; 18-24 h UTC (31, -512, -3.0%, -0.4) |
| discipline | tennis, inconnu, mlb | 56% | tennis (75, +454, +7.6%, +1.7) ; inconnu (14, +96, +5.9%, +0.6) ; mlb (6, +77, +16.7%, +1.0) ; autre (12, +39, +5.5%, +0.5) ; valorant (6, +29, +17.0%, +1.0) ; nfl (2, +20, +11.0%, +0.5) |
| type_pari | inconnu, total, score_exact | 15% | inconnu (14, +96, +5.9%, +0.6) ; total (5, +62, +18.6%, +1.0) ; score_exact (6, +62, +10.3%, +0.8) ; nul (2, +27, +18.6%, +0.6) ; partie (9, +21, +2.3%, +0.2) ; handicap (8, -31, -1.3%, -0.0) |
| mode | immédiat | 64% | immédiat (108, +70, +4.3%, +1.1) ; ordre posé (60, -7, +0.7%, +0.1) |
| source | itftennis.com, inconnu, wtatennis.com, espncricinfo.com, atptour.com, mlb.com | 62% | itftennis.com (21, +277, +14.9%, +1.8) ; inconnu (20, +158, +7.2%, +0.9) ; wtatennis.com (12, +115, +4.3%, +0.4) ; espncricinfo.com (6, +70, +15.0%, +1.0) ; atptour.com (42, +62, +4.8%, +0.8) ; mlb.com (4, +53, +16.6%, +0.8) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- délai jusqu'à la fin 72-168 h : 88 opérations, +611.78, +8.4% par mise, gagnés 83/76.4 → `filtres: {'familles': ['sports'], 'prix_min': 0.8, 'prix_final': True, 'echeance_min': 72, 'echeance_max': 168}` (déjà dans l'arène)
- discipline tennis : 75 opérations, +454.38, +7.6% par mise, gagnés 70/65.0 → `filtres: {'familles': ['sports'], 'prix_min': 0.8, 'prix_final': True, 'disciplines': ['tennis']}` (déjà dans l'arène)
- prix payé 0,850-0,875 : 31 opérations, +267.17, +8.6% par mise, gagnés 29/26.6 → `filtres: {'familles': ['sports'], 'prix_min': 0.85, 'prix_final': True, 'prix_max': 0.875}`
- prix payé 0,800-0,850 : 56 opérations, +257.67, +5.4% par mise, gagnés 49/46.2 → `filtres: {'familles': ['sports'], 'prix_min': 0.8, 'prix_final': True, 'prix_max': 0.85}`
- heure d'achat 12-18 h UTC : 49 opérations, +232.29, +5.1% par mise, gagnés 44/42.3 → `filtres: {'familles': ['sports'], 'prix_min': 0.8, 'prix_final': True, 'heure_utc': [12, 18]}` (déjà dans l'arène)
- heure d'achat 0-6 h UTC : 30 opérations, +174.88, +5.9% par mise, gagnés 28/26.3 → `filtres: {'familles': ['sports'], 'prix_min': 0.8, 'prix_final': True, 'heure_utc': [0, 6]}`
- délai jusqu'à la fin 168 h et plus : 13 opérations, +137.34, +15.4% par mise, gagnés 13/11.3 → `filtres: {'familles': ['sports'], 'prix_min': 0.8, 'prix_final': True, 'echeance_min': 168}`
- délai jusqu'à la fin 6-12 h : 11 opérations, +102.91, +5.3% par mise, gagnés 10/9.5 → `filtres: {'familles': ['sports'], 'prix_min': 0.8, 'prix_final': True, 'echeance_min': 6, 'echeance_max': 12}`
- prix payé 0,000-0,800 : 8 opérations, +2.49, +12.9% par mise, gagnés 7/6.2 → `filtres: {'familles': ['sports'], 'prix_min': 0.0, 'prix_final': True, 'prix_max': 0.8}`
- délai jusqu'à la fin 72-168 h + prix payé 0,850-0,875 : 12 opérations, +178.69, +16.2% par mise, gagnés 12/10.3 → `filtres: {'familles': ['sports'], 'prix_min': 0.85, 'prix_final': True, 'echeance_min': 72, 'echeance_max': 168, 'prix_max': 0.875}` (déjà dans l'arène)

## nm_court_v1.0.0 — croissance +2.8% (mère news_momentum : -0.8%)

54 opérations, résultat +28.00, rendement moyen +0.97% par mise, confiance +0.08, gagnés 37 pour 35.5 attendus (z +0.53).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,000-0,800, 0,950-1,000 | 85% | 0,000-0,800 (34, +71, +0.9%, +0.5) ; 0,950-1,000 (12, +22, +2.5%, +0.6) ; 0,850-0,875 (1, +3, +16.3%, +0.4) ; 0,800-0,850 (2, +1, +22.0%, +0.7) ; 0,900-0,925 (1, +1, +10.6%, +0.3) ; 0,925-0,950 (4, -70, -20.0%, -1.5) |
| delai | 24-72 h, 12-24 h, 0-3 h | 61% | 24-72 h (7, +23, +3.4%, +0.7) ; 12-24 h (21, +22, -11.3%, -0.6) ; 0-3 h (5, +17, +39.0%, +0.9) ; 3-6 h (4, +2, -47.3%, -0.7) ; 6-12 h (17, -36, +15.3%, +1.0) |
| issue | non, autre | 56% | non (25, +44, -3.0%, +0.2) ; autre (5, +31, +66.3%, +1.8) ; oui (24, -47, -8.5%, -0.3) |
| heure_utc | 12-18 h UTC, 18-24 h UTC | 72% | 12-18 h UTC (15, +56, +4.6%, +1.1) ; 18-24 h UTC (24, +39, +5.8%, +0.2) ; 0-6 h UTC (9, +6, -1.5%, +0.3) ; 6-12 h UTC (6, -72, -23.8%, -0.8) |
| discipline | nba | 9% | nba (5, +31, +66.3%, +1.8) ; football (1, +4, +381.3%, +2.0) ; autre (48, -7, -13.8%, -0.5) |
| type_pari | handicap | 7% | handicap (4, +26, +74.5%, +1.7) ; vainqueur (1, +5, +33.3%, +0.6) ; autre (49, -3, -5.7%, -0.2) |
| mode | immédiat | 100% | immédiat (54, +28, +1.0%, +0.5) |
| source | weather.gov, nba.com | 67% | weather.gov (31, +39, -5.6%, -0.1) ; nba.com (5, +31, +66.3%, +1.8) ; events.gop.com (10, +13, -4.0%, +0.3) ; binance.com (8, -55, -8.1%, -0.9) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- heure d'achat 12-18 h UTC : 15 opérations, +55.59, +4.6% par mise, gagnés 12/10.5 → `filtres: {'heures_min': 0, 'heures_max': 24, 'heure_utc': [12, 18]}`
- heure d'achat 18-24 h UTC : 24 opérations, +38.61, +5.8% par mise, gagnés 15/14.7 → `filtres: {'heures_min': 0, 'heures_max': 24, 'heure_utc': [18, 24]}`
- prix payé 0,950-1,000 : 12 opérations, +21.94, +2.5% par mise, gagnés 12/11.7 → `filtres: {'heures_min': 0, 'heures_max': 24, 'prix_min': 0.95, 'prix_max': 1.0}`

## nm_long_v1.0.0 — croissance -0.6% (mère news_momentum : -0.8%)

11 opérations, résultat -6.15, rendement moyen -38.72% par mise, confiance -2.18, gagnés 6 pour 6.8 attendus (z -0.68).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,850-0,875, 0,800-0,850 | 27% | 0,850-0,875 (2, +8, +17.4%, +0.6) ; 0,800-0,850 (1, +2, +23.5%, +0.5) ; 0,950-1,000 (2, +1, +1.7%, +0.2) ; 0,875-0,900 (1, +0, +12.4%, +0.3) ; 0,000-0,800 (5, -17, -100.0%, -1.6) |
| delai | 168 h et plus | 18% | 168 h et plus (2, +6, -41.4%, +0.1) ; 24-72 h (9, -12, -38.1%, -0.8) |
| issue | non | 64% | non (7, +9, -3.7%, -0.0) ; oui (4, -16, -100.0%, -1.0) |
| heure_utc | 0-6 h UTC | 18% | 0-6 h UTC (2, +7, +9.3%, +0.4) ; 12-18 h UTC (3, -2, -100.0%, -0.6) ; 18-24 h UTC (6, -11, -24.1%, -0.7) |
| discipline | mlb | 9% | mlb (1, +7, +17.1%, +0.4) ; autre (10, -13, -44.3%, -0.9) |
| type_pari | vainqueur | 18% | vainqueur (2, +6, -41.4%, +0.1) ; autre (9, -12, -38.1%, -0.8) |
| mode | — | 0% | immédiat (11, -6, -38.7%, -0.7) |
| source | mlb.com | 9% | mlb.com (1, +7, +17.1%, +0.4) ; youtube.com (1, -1, -100.0%, -0.3) ; inconnu (1, -1, -100.0%, -0.3) ; weather.gov (8, -11, -30.4%, -0.8) |

## nf_sport_patiente_tennis_875_900_v1.0.0 — croissance -14.8% (mère nf_sport_patiente_tennis : -23.5%)

72 opérations, résultat -147.56, rendement moyen -4.56% par mise, confiance -0.95, gagnés 61 pour 63.8 attendus (z -1.03).

| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |
|---|---|---|---|
| prix | 0,850-0,875, 0,900-0,925 | 24% | 0,850-0,875 (7, +44, +14.8%, +1.0) ; 0,900-0,925 (10, +39, -0.1%, +0.0) ; 0,875-0,900 (55, -230, -7.8%, -1.6) |
| delai | — | 0% | 72-168 h (72, -148, -4.6%, -1.0) |
| issue | — | 0% | autre (72, -148, -4.6%, -1.0) |
| heure_utc | 12-18 h UTC, 0-6 h UTC | 50% | 12-18 h UTC (26, +54, -0.6%, -0.0) ; 0-6 h UTC (10, +19, +1.6%, +0.2) ; 18-24 h UTC (14, -42, -11.5%, -1.2) ; 6-12 h UTC (22, -178, -7.6%, -1.0) |
| discipline | — | 0% | inconnu (9, -32, +0.4%, +0.0) ; tennis (63, -115, -5.3%, -1.1) |
| type_pari | — | 0% | inconnu (9, -32, +0.4%, +0.0) ; vainqueur (63, -115, -5.3%, -1.1) |
| mode | — | 0% | immédiat (29, -23, -2.7%, -0.3) ; ordre posé (43, -124, -5.8%, -1.1) |
| source | itftennis.com | 35% | itftennis.com (25, +83, +8.1%, +1.1) ; inconnu (9, -32, +0.4%, +0.0) ; wtatennis.com (12, -78, -15.8%, -1.5) ; atptour.com (26, -120, -13.2%, -1.9) |

**Filles proposées** (morceau qui bat la stratégie entière) :

- prix payé 0,900-0,925 : 10 opérations, +38.90, -0.1% par mise, gagnés 9/9.0 → `filtres: {'familles': ['sports'], 'disciplines': ['tennis'], 'prix_min': 0.9, 'prix_max': 0.925, 'prix_final': True}`
- heure d'achat 0-6 h UTC : 10 opérations, +18.79, +1.6% par mise, gagnés 9/8.8 → `filtres: {'familles': ['sports'], 'disciplines': ['tennis'], 'prix_min': 0.875, 'prix_max': 0.9, 'prix_final': True, 'heure_utc': [0, 6]}`

## nf_sport_patiente_tennis_850_875_v1.0.0 — croissance -22.6% (mère nf_sport_patiente_tennis : -23.5%)

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

