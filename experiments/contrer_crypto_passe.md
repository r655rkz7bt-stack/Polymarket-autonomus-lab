# Contre-mouvement crypto à 0,10-0,45 : test sur le passé (27/10/2026, piste 0c)

**Verdict : ÉCARTÉE.** Le « +8 % » du premier tirage (2 880 marchés) disparaît sur l'échantillon complet : 1 492 paris, −4,2 %, gagnés 402 pour 405,1 attendus (z −0,18).
Les 58 gagnés pour 39,3 attendus des fantômes `contrer_crypto*` ne se confirment pas sur le passé (174 paris en direct, tranche choisie après coup : probablement un tirage). Les fantômes « audace » restent en jeu (ils ne coûtent rien au principal).

## Données et méthode (`experiments/contrer_crypto_passe/scripts/`)
- `releve_marches.py` : Gamma `/events/keyset` (étiquette `crypto`, jamais `offset`), événements réglés dont la fin est depuis le 01/06/2026 : 145 605 marchés Oui/Non ;
  gardés : volume ≥ 5 000 $, pas « up or down », réglés net 0/1 → 8 996 marchés (échelles « au-dessus de X à telle heure », « reach / dip to »), plus quelques marchés plus anciens à fin lointaine.
- `releve_echanges.py` : vrais échanges des preneurs (data-api `trades?market=`), 8 974 marchés.
- `analyse.py` : la règle en direct rejouée toutes les 30 minutes, avec seulement les échanges d'avant l'instant T : mouvement = dernier échange du OUI avant T moins dernier échange avant T − 6 h ;
  on achète l'autre côté si son prix est dans la plage et s'il reste ≥ 2 h ; prix payé = premier échange réel qui achète ce côté dans l'heure suivante ; frais crypto 0,07·p(1−p) ; un pari par marché ;
  jugement `idea_test.verdict` (paris liés par événement). Contrôle du règlement : prix de règlement Gamma 0/1 net seulement (non relu sur Binance : la source de règlement n'est pas rejouée).

## Résultats (`resultats_analyse.txt`, 8 réglages de plage × mouvement essayés)
| réglage | paris | rendement | gagnés / attendus |
|---|---|---|---|
| contrer 0,10-0,45, mouvement 0,05 (règle des « audace ») | 1 492 | −4,2 % | 402 / 405,1 |
| mouvement 0,03 / 0,10 | 1 491 / 1 537 | −2,2 % / −4,6 % | 394 / 395,8 ; 424 / 431,0 |
| contrer 0,05-0,60 (règle des mères) | 1 828 | −7,7 % | 466 / 495,1 |
| sous 0,10 | 1 898 | −11,4 % | 159 / 165,9 |
| contrer 0,45-0,90 | 1 803 | −5,2 % | 1 300 / 1 353,5 (z −3,1) |
Par mois : 2026-06 +4,5 %, 07 −20,1 %, 08 −10,5 %, 09 −5,5 %, 10 +3,2 % (aucun mois solide). Par genre : « au-dessus de » −2,2 %, « touche » −6,5 %.

## Ce que les références sans signal ont montré (`resultats_baseline_non.txt`)
- **Suivre** le mouvement (l'inverse) à 0,10-0,45 : +14,4 % (z +2,98) : le même effet que le NON bon marché ci-dessous, pas un signal de mouvement.
- **NON à 0,10-0,45 sans aucun signal : +14,4 %** (1 111 paris, 398 gagnés pour 357,8, z +2,66, t par événement +1,70) mais **fragile** : sans ses 5 meilleurs jours −0,7 % ; juin +44 %, août −31 % ;
  tranche 0,20-0,30 −18,5 %. Le NON 0,05-0,10 fait +35 % (z +3,1) : billets, jamais joués.
- Dans les marchés « touche » (reach / dip to / hit), NON à 0,10-0,45 en juin-octobre : 386 paris, +22,6 % (z +3,44, 6 mois sur 6) ; dans les échelles « au-dessus de » : +10,0 %.
  **Refait sur janvier-mai 2026** (12 150 marchés, `resultats_baseline_non_janv_mai.txt`, relevé `releve_marches.py 2026-01-01 … 2026-06-02`) : « touche » **−1,1 %** (306 paris, z −0,35) et « au-dessus de » **+29,4 %** (967 paris, z +4,99) : la sous-tranche s'inverse, pas de loi par genre.
- **Le NON crypto à 0,10-0,45, tous genres, tient sur les deux périodes séparées** : juin-octobre 1 111 paris +14,4 % (z +2,66) ; janvier-mai 1 273 paris +22,1 % (496 gagnés pour 428,2, z +4,15, t par événement +3,17).
  Total 2 384 paris, 894 gagnés pour 786 attendus. Fragile : 6 mois sur 10 positifs (jan +57 %, fév +18 %, mar −4 %, avr −23 %, mai +20 %, juin +44 %, juil −6 %, août −31 %, sept −8 %, oct +24 %),
  sans ses 5 meilleurs jours +7,6 % (janvier-mai) et −0,7 % (juin-octobre). Ethereum +35 % (janvier-mai) et +19 % (juin-octobre), Bitcoin +6 % et +8 %. Tranche de prix payé 0,10-0,20 : +66 % puis +70 %.
  ~30 découpages regardés. **Verdict : indice** → fantôme `crypto_non_bon_marche` (Kelly entier, biais supposé 0,05), pas de capital principal avant 30 nouveaux paris ; les billets du NON sous 0,10 (+35 % puis +19 %) ne sont jamais joués.

## Suite
- Vers le 03/11 : juger `crypto_non_bon_marche` et les deux « audace » sur leurs nouveaux paris (gagnés contre attendus ; par événement).
- Avant toute promotion : remonter à 2025 (`releve_marches.py 2025-01-01 … 2026-01-01`), et chercher pourquoi (volatilité sous-estimée par le OUI proche du prix ?) avec les prix Binance.
- Cette piste tient une leçon : un « avantage » trouvé dans 174 paris d'un fantôme et confirmé par un premier sous-échantillon (2 880 marchés, +8 %) a disparu à 8 974 marchés. Toujours refaire sur plus de données avant d'écrire « confirmé ».

## Suite du 27/10 (matin) : le NON crypto remonté à 2024-2025 — **indice solide**, tranche « payé 0,10-0,20 » qui se répète trois fois
Relevés `releve_marches.py` (2024-01 → 2025-12, puis 2026-01 → 2026-10, `/events/keyset`) + `releve_echanges.py` : **35 884 marchés réglés nets, 35 631 avec vrais échanges** (volume ≥ 5 000 $).
Mêmes règles que ci-dessus : NON, aucun signal, prix payé = premier échange réel qui achète le NON dans l'heure, frais crypto, un pari par marché, paris liés par événement (`resultats_baseline_non_2024_2026.txt`).
- **2025 seul (hors des deux périodes déjà vues)** : 1 661 paris, **+13,1 %**, 636 gagnés pour 584,3 (z +2,73, t par événement +2,50) : le signe se répète (`resultats_baseline_non_2025.txt`).
- **Tout (2024-2026)** : 4 167 paris, **+15,8 %**, 1 573 gagnés pour 1 414,8 (z +5,33, t par événement +4,39), 20 mois sur 33 positifs ; sans ses 5 meilleurs jours **+10,0 %** (z +4,17) ; NON 0,45-0,90 : +1,3 % (rien) ; billets 0,05-0,10 : +21,0 % (z +4,1, jamais joués).
  Par actif : Bitcoin +8,0 %, Ethereum +18,4 %, Solana +24,0 %, autres +43,3 % ; par genre : « au-dessus de » +16,8 %, « touche » +13,1 % (cette fois les deux tiennent).
- **Tranches, période par période** (`resultats_non_tranches_periodes.txt`, `scripts/non_tranches_periodes.py`) :

| tranche | 2024-01 → 2025-12 | 2026-01 → 05 | 2026-06 → 10 |
|---|---|---|---|
| tous (0,10-0,45) | 1 896 paris, +17,4 % (z +3,8) | 1 290, +19,7 % (z +3,8) | 981, +7,7 % (z +1,4) |
| **payé 0,10-0,20** | 270, **+54,4 %** (z +3,9) | 265, **+62,4 %** (z +4,3) | 195, **+57,6 %** (z +2,8) |
| payé 0,20-0,30 | 264, +40,4 % (z +3,8) | 155, +23,8 % (z +1,8) | 172, **−29,1 %** (z −1,8) |
| payé 0,30-0,45 | 1 362, +5,7 % | 870, +6,0 % | 614, +2,1 % |
| fin dans ≥ 96 h | 814, +32,0 % (z +4,2) | 595, +30,2 % (z +3,4) | 365, **−2,2 %** |
| fin dans < 96 h | 1 082, +6,5 % | 695, +10,7 % | 616, +13,6 % |

- **Lecture** : l'effet est réel dans l'ensemble (z +5,3 sur 4 167 paris, trois périodes de même signe, ~30 découpages regardés : le z survit à une correction de ce nombre), mais il s'**affaiblit dans les 5 derniers mois** (+7,7 %) et les tranches « 0,20-0,30 » et « ≥ 96 h »
  l'ont perdu : ne pas les jouer. Seule la tranche **payée 0,10-0,20 (le OUI à 0,80-0,90)** est positive dans les trois périodes (730 paris, **+58,1 %**, 167 gagnés pour 106,0 attendus, z +6,4). C'est l'expérience audacieuse du jour : fantôme **`crypto_non_10_20`** (Kelly entier).
- **Pourquoi (non prouvé)** : le OUI à 0,80-0,90 d'une échelle « au-dessus de X » ou « touche X » est surcoté par rapport à la fréquence réelle (+6 à +9 points de gain pour le NON) ; piste d'explication : primes de volatilité payées pour l'« un jusqu'ici tout va bien » du OUI, ou prix de départ trop bas. Pas vérifié avec les prix Binance.
- **Profondeur (`scripts/profondeur_non_10_20.py`, `resultats_profondeur_non_10_20.txt`) — le gain est concentré dans les échanges minces** : pour les 730 paris payés 0,10-0,20, taille médiane du premier échange payé 23 parts ; parts de NON
  achetées par des preneurs à ≤ prix payé + 0,02 dans l'heure suivante : médiane 89. Rendement selon la quantité disponible : **tous +58,1 %** (z +6,4) → **≥ 20 parts +41,2 %** (536 paris, z +4,0) → **≥ 100 parts +21,0 %** (354, z +1,9) → **≥ 400 parts +1,0 %** (214, z +0,2).
  Même piège que la météo du 16/10 et `compteur_truth` : là où il y a de la quantité à acheter, l'écart disparaît. (Réserve : « parts disponibles dans l'heure suivante » regarde un peu l'avenir, c'est une mesure de l'exécutable, pas une règle de décision.)
  Conséquence : une mise de fantôme à Kelly entier (≈ 60 €, soit ≈ 400 parts à 0,15) ne sera servie qu'en partie par le carnet réel (25 % au meilleur prix, 50 % aux niveaux suivants) et verra surtout le prix du bas de la file ; les petits tickets du principal (5 à 20 parts) sont du bon côté.
  L'arène le mesurera avec les vrais carnets : lire `crypto_non_10_20` en parts remplies, pas seulement en euros.
- **Ce qui n'est pas vérifié** : le règlement des marchés « touche » (relu seulement par le prix final Gamma), l'absence de regard vers le futur est tenue (décision à T, prix des échanges après T).
- **Verdict : indice, solide en nombre mais concentré dans les échanges minces** (`idea_test.verdict` « indice » : mois irréguliers, dernière période faible, gain qui s'efface à ≥ 400 parts disponibles). `crypto_non_bon_marche` reste fantôme ; pas de capital principal avant **30 nouveaux paris en direct** et un rendement par mise > 0 sur ces paris (règle du 27/10).
- **Suite** : juger les deux fantômes vers le 03/11 ; chercher le pourquoi avec les prix Binance (volatilité réalisée contre prix du OUI) ; lire les parts réellement remplies des fantômes (la profondeur ci-dessus est un test sur les échanges, pas sur des carnets).
