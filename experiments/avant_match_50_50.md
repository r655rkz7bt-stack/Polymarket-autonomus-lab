# Favori acheté AVANT le match, avec les règlements 50-50 comptés (24/10/2026)

Scripts : `experiments/avant_match_50_50/scripts/` (`releve.py` puis `analyse.py`, rien d'autre ; `LO=… HI=…` change la fourchette) ; chiffres bruts : `resultats_*.txt` ; données dans `donnees/` (ignoré par Git).
Suite de l'enquête `enquetes/2026-10-24_soir_reglements_50_50.md` : les tests sur le passé du labo écartent les marchés réglés à 50-50. **Un favori acheté avant le match gagne-t-il plus que son prix, 50-50 compris ?**

## Données
Même relevé que `apres_fin_match.md` : 10 872 événements de 37 ligues dont le coup d'envoi est depuis le 30/09/2026, 10 438 avec leurs échanges réels (data-api).
Marchés « vainqueur » (`moneyline`) réglés à 1/0 **ou à 0,5/0,5** (paiement 0,5). Règlement relu : prix finaux Gamma (pas de seconde source).
Taux de 50-50 des « vainqueur » avec échanges (7 815 marchés) : **3,0 %** ; CS2 8,2 %, Dota 2 5,9 %, WTA 4,9 %, ATP 2,4 %, ITF 2,3 %, LoL 0,8 %, football, NHL, MLS 0 %.

## Règle rejouée (sans regard vers le futur)
Pour chaque délai d (1, 3, 6, 12, 24 h **avant** le coup d'envoi) : prix payé = premier échange preneur dans les 30 minutes qui suivent coup d'envoi − d ; pari gardé si ce prix est dans la fourchette ; un pari par événement ; frais du marché ; rendement par euro misé.

## Résultats (fourchette 0,80-0,95, tous sports)
| délai avant le match | paris (dont 50-50) | rendement avec 50-50 | sans 50-50 | gagnés / attendus (hors 50-50) |
|---|---|---|---|---|
| 1 h | 691 (9) | −0,9 % (t −0,6) | −0,3 % | 590 / 588,1 |
| 3 h | 380 (5) | −1,6 % (t −0,8) | −1,1 % | 322 / 323,1 |
| 6 h | 301 (4) | −1,5 % (t −0,7) | −1,0 % | 256 / 256,7 |
| 12 h | 273 (4) | −3,2 % (t −1,3) | −2,6 % | 227 / 231,3 |
| 24 h | 84 (0) | +0,7 % (t 0,2) | +0,7 % | 74 / 73,1 |

- Les 50-50 coûtent **0,5 à 0,6 point** en moyenne (1,3 % des paris, 0,43 € perdu par euro), 1 à 2 points en e-sport (2,5 à 3,9 % des paris) : le coût prévu par l'enquête, mesuré.
- Mais **sans les 50-50 non plus il n'y a rien** : −0,3 % à −2,6 % à 1-12 h ; z des prix entre −1,4 et +0,3. Le favori à 0,80-0,95 gagne autant que son prix avant le match.
- Par groupe (tennis / e-sport / autre) × 5 délais : de −6,8 % (tennis −12 h, t −1,5) à +14,1 % (e-sport −24 h, 18 paris), aucun t au-dessus de 1,5 hors les cases de moins de 20 paris. Par ligue à −6 h : ATP −4,4 %, WTA −6,7 %, CS2 −3,4 %, ITF −1,8 %, rien de significatif.
- Autres fourchettes : 0,80-0,88 : −0,4 / −1,1 / −2,3 / −4,3 / +0,5 % ; 0,88-0,95 : −1,2 / −1,3 / 0,0 / −2,1 / −0,5 % ; 0,95-0,985 : +1,0 / +3,8 / −0,6 / +1,0 / +4,0 % (74, 36, 34, 20, 9 paris : trop peu).
- Réglages regardés : 5 délais × 4 fourchettes × (tous, trois groupes) + 14 ligues ≈ 100 cases.

## Verdict : **écartée**
Aucun avantage à acheter le favori avant le match, avec ou sans 50-50. Conséquences :
- `nf_*` ne tire pas son (faible) résultat de l'avant-match (déjà 10 à 16 % des mises) ; les 50-50 mesurés en arène (−0,27 % de la mise) sont du bon ordre de grandeur.
- Volume mince : 301 paris à −6 h sur 10 438 événements (peu d'échanges de favoris à ce prix avant le match).
- Pas de décote ajoutée aux stratégies. Les tests futurs d'une entrée avant-match doivent inclure les 50-50 (paiement 0,5) : `experiments/avant_match_50_50/scripts/analyse.py` montre comment.
