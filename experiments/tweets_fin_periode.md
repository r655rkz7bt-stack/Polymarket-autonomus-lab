# Compteur de tweets : les dernières heures, puis l'écart exigé (24/10/2026, passage chercheur de minuit)

Déclencheur : un constat de l'enquête automatique (`estimation_perimee`, 8 stratégies à tweets, mots, détroits) dont le plus gros est un achat de `compteur_tweets`
du 23/10 à 15 h 27 UTC : **« No » sur CZ 40-59 messages, estimé 0,81, payé 0,10, 33 minutes avant la fin** (perdu : la tranche a gagné ; le marché valait 0,90 pour le OUI).
Les 4 achats de moins de 6 heures de la mère en direct ont tous perdu (−39 €). Deux questions : (1) le modèle perd-il dans les dernières heures ? (2) un grand écart entre le
calcul et le prix est-il un signal ou une erreur ?

## Données (scripts : `experiments/tweets_fin_periode/`, données dans `donnees/xt/`, ignoré par Git)
- 189 périodes hebdomadaires de 7 comptes (3 juillet → 20 octobre 2026) : tranches Gamma, prix horaires du CLOB (`releve_marches.py`, en parallèle : 4 minutes au lieu d'une heure),
  messages XTracker de chaque compte, échanges réels des preneurs de chaque événement (`releve_echanges.py`, `idea_test.fetch_event_trades`).
- **Contrôle du règlement** : notre décompte redonne la tranche réglée par Polymarket pour 185 périodes sur 189 (4 écartées, comme le 21/10).
- Aucun regard vers le futur : à chaque heure de décision, seuls les messages d'avant servent (total, rythme 7 + 14 jours).
- Modèle de `compteur_tweets` inchangé (dispersion 12, rythme moitié 7 jours moitié 14 jours). Achat au prix horaire + demi-écart (0,01 Elon, 0,02 les autres), frais 0,05·p·(1−p)
  (ancien barème, plus sévère que le barème zéro d'aujourd'hui), billet ≥ 0,10. Le test du 20/10 n'achetait qu'entre « début + 6 h » et « fin − 3 h » ; ici toutes les heures jusqu'à 10 minutes de la fin.

## Question 1 : les dernières heures perdent-elles ? **Non démontré, rien n'indique que oui**
| heures avant la fin | achats | par achat | périodes | par période (t) |
|---|---|---|---|---|
| 0-1 | 8 | +16,7 % | 4 | +16,7 % (3,79) |
| 1-3 | 15 | +37,6 % | 4 | +35,6 % (1,46) |
| 3-6 | 30 | +26,6 % | 6 | +12,0 % (0,49) |
| 6-12 | 76 | +26,0 % | 9 | +28,7 % (1,66) |
| 12-24 | 176 | −2,3 % | 11 | +0,2 % |
| 24-72 | 1 542 | +22,9 % | 40 | +28,4 % (1,30) |
| 72-200 | 15 189 | +5,0 % | 165 | +3,1 % (0,59) |

Moins de 6 heures : 53 achats, tous sur `cz_binance` (les autres comptes n'ont pas de prix horaire pour toutes les tranches à ce moment-là), 6 périodes. Les 4 pertes en direct sont donc
compatibles avec la malchance ; l'échantillon est trop petit pour conclure dans un sens ou dans l'autre. **Pas de filtre ajouté.** Le CZ du 23/10 reste une valeur extrême à surveiller (le compteur
XTracker a un relevé qui peut avoir jusqu'à 1 h de retard, `max_stale_hours: 1`, et la tranche se joue sur 1 ou 2 messages).

## Question 2 : l'écart entre le calcul et le prix est-il un signal ? **Oui, et plus il est grand, plus le rendement monte**
Rendement par achat selon l'écart `q − prix payé` (tous achats, sans frais) : **< 0,10 : −4,2 %** (8 023 achats), 0,10-0,20 : +15,4 %, 0,20-0,35 : +29,1 % (t par période 3,06), ≥ 0,35 : +25,0 % (t 3,12).
Donc les achats à très grand écart que `estimation_perimee` signalait sont en moyenne **les meilleurs**, pas des erreurs de carnet : le contrôle était mal réglé pour les modèles à écart variable (voir correctif).

Écart exigé (NON sans NYC Mayor, avec frais 0,05·p·(1−p), prix du relevé horaire) :
| écart minimum | achats | par achat | périodes | par période (t) |
|---|---|---|---|---|
| 0,03 (la mère) | 8 462 | +10,9 % | 134 | +9,2 % (2,45) |
| 0,08 | 5 315 | +15,8 % | 124 | +18,2 % (3,76) |
| 0,12 | 3 632 | +19,9 % | 112 | +22,7 % (3,75) |
| 0,18 | 2 071 | +22,9 % | 94 | +38,2 % (4,57) |
| 0,25 | 761 | +40,3 % | 69 | +47,4 % (4,23) |

Réglage 0,12 (sans frais), robustesse : **sans les 3 meilleures périodes +20,2 % (t 3,55)** ; 1re moitié +24,0 % (t 2,64), 2e moitié +24,8 % (t 3,07) ; demi-écart doublé : +24,1 % (t 3,78) ;
premier signal seulement par période et par prix : +25,4 % (t 4,19) ; par compte : Zelensky +47 %, cz_binance +28 %, WhiteHouse +21 %, tedcruz +18 %, **Trump −9 % (13 périodes)** ;
par mois : juillet +34 %, août +12 %, septembre +47 %, **octobre −12,8 % (17 périodes, t −1,0)** ; par prix payé : 0,10-0,30 +104 %, 0,30-0,60 +32 %, 0,60-0,85 +15 %, ≥ 0,85 +13 %.

## Aux prix réellement payés (échanges réels)
Prix payé = premier échange de preneur qui achète NON (ou vend OUI) dans l'heure qui suit la décision. **Seuls 13 % des signaux (358 sur 2 746 à l'écart 0,15) ont un tel échange** : les tranches sont peu
échangées, on ne peut juger que ceux-là. Prix moyen payé 0,570 contre 0,571 au relevé : le relevé horaire + demi-écart décrit bien le prix.
`idea_test.verdict`, écart gardé au prix payé (écart > marge), avec frais 0,05·p·(1−p) :

| écart minimum | paris | rendement | événements (t) | z des prix | mois | verdict |
|---|---|---|---|---|---|---|
| 0,08 | 521 | +30,3 % | 87 (2,62) | 5,5 | juil +25 %, août +36 %, sept +35 %, oct −0,5 % | retenue |
| 0,12 | 389 | +36,6 % | 71 (2,48) | 5,8 | +28 %, +38 %, +52 %, +3 % | retenue |
| **0,15** | **288** | **+40,7 %** | **57 (2,55)** | **5,6** | **+27 %, +34 %, +72 %, +16 %** | **retenue** |
| 0,18 | 194 | +49,3 % | 46 (2,97) | 5,2 | +38 %, +33 %, +105 %, +24 % | retenue |

Par prix payé (écart 0,15, sans frais) : 0,10-0,30 +197 % (18 achats), **0,30-0,60 +64 % (144 achats, t par période 2,9)**, **0,60-1 −3 % (126 achats)**. Le gain est tout entier dans les NON à 0,10-0,60.

## Contre-épreuve : toutes les tranches, pas seulement celles dont TOUS les prix sont récents (`ANYBK=1`)
Le rejeu ci-dessus n'achète qu'à une heure où chacune des 26-30 tranches a un prix de moins de 2 h : cela exclut presque tout Elon (0 achat) et réduit les autres comptes. En n'exigeant que 3 prix récents, le rejeu au prix du
relevé horaire monte à **+26 % par achat, t par période 5,4 (153 périodes)** : mais c'est en partie un faux gain, le prix horaire d'une tranche peu échangée est vieux (le calcul, lui, utilise le compte à jour : l'écart est gonflé).
Aux **prix réellement payés** (premier échange de preneur dans l'heure, écart gardé au prix payé) : 1 631 achats, 133 périodes, **+16,5 % sans frais, +14,2 % avec frais 0,05·p·(1−p), t par période 2,06** (« retenue » : z des prix 6,7) ;
l'écart prix du relevé → prix payé (21 % → 12 % avant le filtre d'écart) est exactement la part « carnet périmé ». Par compte (avec frais, par période) : **WhiteHouse −14,5 % (27)**, **Elon −8,7 % (16)**, Zelensky +18 % (26),
cz_binance +39 % (23), tedcruz +28 % (28), Trump +27 % (13). Par mois : juillet −4 %, août +13 %, septembre +23 %, octobre +18 %. 1re moitié +9,7 % (t 0,96), 2e moitié +24,3 % (t 2,36). Écart exigé 0,20 : +19,4 % (114 périodes, t 2,11).

Dispersion (toutes tranches, écart 0,15, prix payés, frais) : 6 → +12,5 % (130 périodes, t 2,12) ; 8 → +13,8 % (t 2,57) ; 12 → +14,2 % (t 2,06) ; 16 → +13,3 % (t 1,98) ; 30 → +10,1 % (t 1,63) : le résultat ne dépend pas du réglage. Au total ~25 réglages et coupes regardés.

**Fourchette honnête du gain aux prix payés : +14 % (toutes tranches, 133 périodes) à +41 % (tranches toutes fraîches, 57 périodes).** Le chiffre bas est le plus représentatif des signaux qu'on verra en direct. Elon est négatif (−9 %, 16 périodes) :
la fille le garde exclu ; WhiteHouse négatif (−14,5 %) est une coupe qu'on n'ajoute pas avant d'avoir des paris en direct (découpage a posteriori de plus).

## Verdict : **indice fort, fantôme `compteur_tweets_non_ecart_large`** (pas dans `validated_strategies`)
Le protocole dit « retenue » aux quatre réglages, mais je ne la promeus pas :
- le morceau « NON sans NYC Mayor » vient d'une sélection (≈ 60 découpages regardés le 21/10, `tweets_filles.md`) sur les mêmes périodes ; j'y ajoute 5 écarts, 2 demi-écarts et ~8 coupes de robustesse : le t de 2,5 à 3 aux prix payés
  n'est pas indépendant de cette sélection (voir `selection_multiple` : z ≈ 2 attendu sans aucun avantage parmi ~40 essais) ;
- 87 % des signaux n'ont pas d'échange dans l'heure : en direct beaucoup d'ordres resteront sans exécution ou seront servis plus tard, à un prix qui a pu bouger ;
- octobre est le seul mois sans gain net par période au prix du relevé (−13 %, 5-17 périodes), la tranche 0,60-1 ne gagne rien, Trump est négatif, Elon n'est couvert que par la contre-épreuve (−9 % par période, 16 périodes) ;
- la dispersion 12 a été réglée sur ces mêmes périodes (calibrage du 20/10).
Fantôme : mère `compteur_tweets_non`, mêmes réglages sauf `min_net_edge 0,11` (écart calcul − prix ≥ 0,15) et `skip_elon_trump`. Cycle local du 24/10 : 467 marchés vus, 2 propositions (NON de la tranche 65-89 d'Elon
avant le filtre Elon/Trump : écart 0,154 ; 40-64 à 0,64 : écart 0,158). À confirmer par de nouveaux paris : **30 paris réglés au moins avant toute promotion**, et vérifier que les prix payés en direct tiennent (13 % de signaux avec échange au rejeu).

## Reste ouvert
- Rejeu avec Elon et Trump (tranches sans prix horaire : relever les échanges plutôt que le CLOB horaire).
- Plafond de prix (NON ≤ 0,60) : la coupe a l'air nette (−3 % au-dessus de 0,60) mais elle est post-hoc ; à poser comme fille seulement après ~30 paris en direct.
- Les 13 % des signaux qui ont un échange : tester ce que valent les ordres posés (limite) sur ces tranches.
