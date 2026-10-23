# « Après la fin du match » : le favori à 0,94-0,985 est-il vraiment gagné ? (23/10/2026)

Scripts : `experiments/apres_fin_match/scripts/` (`releve.py` puis `analyse.py`) ; chiffres bruts : `resultats_094_0985.txt`, `resultats_090_094.txt`,
`resultats_0985_0999.txt` ; données dans `donnees/` (ignoré par Git).

## La question
Le fantôme `apres_echeance` achetait, après l'« échéance » Gamma, le favori à 0,94-0,985 d'un marché pas encore réglé (+2,8 % les trois premiers jours,
puis −475 € le 23/10 sur huit jambes d'un même match de NBA, voir `enquetes/2026-10-23_apres_echeance_match_en_cours.md`). Pour un match, l'échéance Gamma
est le coup d'envoi. **À partir de combien d'heures après le coup d'envoi un favori à 0,94-0,985 gagne-t-il plus souvent que son prix, aux prix réellement payés ?**

## Les données
- Gamma, 37 ligues (NBA, NHL, MLB, NFL, football universitaire et européen, tennis ATP/WTA/ITF, CS2, LoL, Dota 2, Valorant, KHL, KBO…), événements réglés dont
  le coup d'envoi (`gameStartTime`) est depuis le 30/09/2026 : **10 242 événements** (ITF 2 100, ATP 1 170, CS2 1 133, football universitaire 492, MLS 470, WTA 456, MLB 374…).
- Data-api : tous les échanges de chaque événement (10 234 relevés).
- Marchés binaires réglés net à 1/0, frais du barème de chaque marché (`feeSchedule`).

## La règle rejouée (sans regard vers le futur)
Pour chaque délai d (1, 2, 3, 4, 6, 8 h) : prix payé = **premier échange preneur** (achat du jeton, ou vente de l'autre jeton) dans les 30 minutes qui suivent
coup d'envoi + d ; on garde le pari si ce prix est dans la fourchette. Un seul pari par événement (le premier acheté : moneyline, écart ou total confondus), ou toutes les jambes
(deux lectures). Rendement = (paiement − prix − frais) / prix.

## Résultats (un pari par événement)
| délai | favori 0,94-0,985 | favori 0,90-0,94 | favori ≥ 0,985 |
|---|---|---|---|
| +1 h | 1 564 paris, 1 497 gagnés / 1 508 attendus, **−0,9 %** (t −1,7) | 1 306, 1 202 / 1 201, −0,3 % (t −0,4) | 1 328, 1 302 / 1 320, −1,4 % (t −3,6) |
| +2 h | 781, 762 / 753, **+1,0 %** (t +1,8) | 578, 538 / 532, +0,8 % (t +0,7) | 1 289, 1 279 / 1 283, −0,3 % (t −1,4) |
| +3 h | 282, 272 / 272, **0,0 %** (t 0,0) | 187, 171 / 172, −1,0 % (t −0,5) | 513, 507 / 511, −0,7 % (t −1,5) |
| +4 h | 36, 35 / 35, +0,7 % | 29, 25 / 27, −6,6 % | 106, 105 / 106, −0,6 % |
| +6 h et plus | 8 paris | 4 paris | 29 paris : 24 gagnés / 28,9, **−17 %** (à +6 h : 16 gagnés / 19,9, z des prix −17) |

Toutes jambes confondues : mêmes ordres de grandeur (+2 h : +0,9 %, t +1,8). Par sport à +3 h et plus : aucun sport significatif (CFB +1,3 %, ATP −5,9 %, ITF −0,4 %, NFL −2,0 %…).
À +6 h et plus, les favoris ≥ 0,985 perdent 5 fois sur 29 (4 sur 20 à +6 h) : un prix à 0,99 ne dit plus rien de sûr à ce stade (peu de cas, à ne pas surinterpréter). Relu à la main (Kiwoom-Hanwha, 5/10) : 4 des 5 pertes sont des matchs de baseball coréen (KBO) achetés à 0,999 à +4,5 h, réglés pour l'autre équipe deux jours plus tard (`closedTime` 7/10) : match interrompu ou reporté, le marché reste ouvert « jusqu'à ce que le match soit terminé » (règle du marché) ; le prix de 0,99 était celui d'un match en cours, pas d'un match fini (un seul des quatre relu en détail, les autres sont du même type).

## Verdict : **écartée**
À aucun retard, dans aucune des trois tranches de prix, le favori d'un match en cours ou fini ne rapporte plus que son prix après frais : de −1,4 % à +1,0 %, avec
6 délais × 3 tranches × 2 lectures = 36 réglages regardés et un seul « indice » (+2 h, t +1,8, qui disparaît dans la tranche voisine). Le +2,8 % du début du
fantôme (146 paris, +123 €) était de la chance. Conséquence : `apres_echeance` est éteinte dans l'arène (`enabled: false`) ; le correctif de la veille (attendre 3 h,
un pari par événement) reste dans le code, avec ses tests, si l'on veut un jour la rallumer.
Limites : 3 semaines de matchs seulement (ligues d'octobre), pas de saison complète pour la NBA et la NHL (84 et 163 événements) ; seul le premier échange de la fenêtre est un prix exécutable
(petites tailles).

## Bonus : le même relevé relit l'« indice » du tennis en jeu (`scripts/tennis_oos.py`)
Même règle que `tennis.md` (favori à 0,80-0,95 dans une fenêtre de 10 min à +15 / +30 min du coup d'envoi, premier échange preneur, moneyline, frais du marché) ; le favori
est le jeton au prix médian le plus haut de la fenêtre (règle un peu différente de l'original, donc chiffres non identiques).
| période | +15 min | +30 min |
|---|---|---|
| 30/09 → 20/10 16 h (ATP 325, WTA 118, ITF 77 à +30 min) | 364 paris, 322 gagnés / 312,5, **+2,4 %** (t +1,2) | 520 paris, 446 / 450,8, **−1,9 %** (t −1,1) |
| après le 20/10 16 h (hors échantillon) | 54 paris, 43 / 46,7, **−8,8 %** (t −1,4) | 63 paris, 53 / 55,2, **−4,5 %** (t −0,8) |
Sur les trois dernières semaines, le favori de tennis en jeu à 0,80-0,95 gagne autant que son prix (499 pour 506 attendus à +30 min, −2,3 %) : l'« indice » de +3,1 % de `tennis.md`
(6 131 matchs, ~40 réglages) ne se retrouve pas, ni avant ni après la date de sa découverte. `PISTES.md` : indice non confirmé. Les fantômes `nf_tennis_*` restent en arène (ils jouent aussi avant le match).
