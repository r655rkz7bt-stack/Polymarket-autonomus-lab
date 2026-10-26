# Acheter le favori d'un match avant le coup d'envoi, sur 30 000 marchés tirés au hasard (27/10/2026)

**Question** : `nf_sport_patiente_prix_850_875` (rang 1 de l'arène, 28,7 % du capital principal) et toute la famille `nf_*` achètent le favori d'un match à 0,85-0,875 (ou 0,80-0,95) avant le coup d'envoi.
Le marché sous-évalue-t-il ces favoris, quelle que soit la stratégie ? Les tests précédents (`avant_match_50_50.md` : 10 438 événements ; `favori.md` ; `prix_payes`) portaient sur des relevés tronqués
(`enquetes/2026-10-27_releves_tronques_offset.md`) et sur les seuls matchs récents.

**Données** : relevé complet par curseur (83 129 événements des 37 ligues, 15/01 → 26/10/2026), 59 760 marchés « vainqueur du match » (moneyline) de plus de 2 000 $ réglés (net ou 50-50), **30 000 tirés au hasard** (graine fixe ;
`totaux_sports/scripts/releve_echanges_ml.py`) et leurs vrais échanges (data-api). Méthode : pour chaque marché et chaque délai (1, 3, 6, 12, 24 h avant le coup d'envoi), premier échange preneur dans les 30 minutes qui suivent
la décision pour chaque issue ; on achète le favori (prix le plus haut, 0,55-0,97) ; frais du marché ; règlements à 0,5-0,5 comptés 0,5 ; un pari par marché et délai (`analyse_favoris.py`, résultats : `totaux_sports/resultats_favoris.txt`).
**50 232 paris.** Règlement lu sur les prix finaux Gamma (`outcomePrices` ∈ {0, 1} ou 0,5/0,5).

## Résultats (rendement par euro misé après frais, t par événement, z = gagnés contre attendus par les prix payés)
| prix payé | 1 h | 3 h | 6 h | 12 h | 24 h |
|---|---|---|---|---|---|
| 0,55-0,70 | −3,2 % (9 080 ; t −3,9) | −2,8 % (6 863 ; t −2,9) | −3,3 % (5 497 ; t −3,1) | −1,1 % (3 758) | −0,3 % (1 601) |
| 0,70-0,80 | −2,1 % (4 513 ; t −2,4) | −0,5 % (3 154) | −3,1 % (2 520 ; t −2,6) | −0,5 % (1 713) | +1,4 % (735) |
| 0,80-0,85 | −1,0 % (1 668) | −0,8 % (1 198) | −2,8 % (927 ; t −1,8) | −3,6 % (640 ; t −1,8) | +2,0 % (301) |
| **0,85-0,875** | −2,4 % (624 ; t −1,4) | **−1,2 % (435 ; t −0,6)** | +0,2 % (360) | −0,8 % (271) | +2,9 % (121) |
| 0,875-0,90 | −3,4 % (417 ; t −1,8) | −5,5 % (302 ; t −2,3) | −2,7 % (258) | −3,7 % (170) | +3,7 % (76) |
| 0,90-0,95 | −1,7 % (811 ; t −1,6) | −1,3 % (555) | −2,1 % (451) | +0,4 % (315) | −4,5 % (152) |
| 0,95-0,97 | +0,4 % (267) | +2,5 % (159 ; t +2,4) | +2,6 % (139 ; t +2,3) | −0,4 % (88) | +2,5 % (54) |

- **Aucune tranche de prix ne gagne de façon régulière** ; sur 35 cases, 25 sont négatives ; les 10 positives sont presque toutes à 24 h (moins de 310 paris) ou à 0,95-0,97 (moins de 270 paris). Le marché des vainqueurs est calibré aux frais et à l'écart près.
- La tranche de la championne (0,85-0,875, 3 h) : **−1,2 % (435 paris)** sur tout l'échantillon ; **février-août +0,4 % puis août-octobre −5,5 % (117 paris)** à 3 h (idem 1 h : −1,5 % puis −4,4 %).
- Par sport (0,80-0,95) : tennis −1,4 à −4,9 % selon le délai (6 h : −4,9 %, t −2,85) ; football (3 issues) −1,9 à −2,8 % ; e-sport −0,2 à −1,3 % ; basket +0,7 à +1,4 % (205-333 paris, t < 0,7) ; football américain −6 à −10 % (moins de 70 paris).
- Les grands écarts de l'arène (rang 1 : +1 532 € de capital réalisé en 54 paris) ne viennent donc pas d'un avantage du marché : c'est la loterie des favoris à 0,85 (un perdant à −100 % efface 5 à 6 gagnants à +15-18 %) plus le biais de sélection du classement (`selection_multiple` : 91 stratégies, z attendu du meilleur ≈ +2).

## Balayage des cases (`cellules_favoris.py`)
576 cases (37 ligues × 4 tranches de prix × 4 délais) ; 122 ont au moins 25 paris dans chacune des deux fenêtres (février-août, août-octobre). **Aucune** n'est positive et significative (t par événement ≥ 1,5) dans les deux : le hasard seul
en produit 0,01 en moyenne (gains mélangés dans chaque case, 100 tirages) : il n'y a donc pas de poche cachée dans cet échantillon (`totaux_sports/resultats_cellules_favoris.txt`).

## Verdict
**Écartée** (pour acheter « tous les favoris ») : −0,8 à −3 % par pari aux prix payés, 50 232 paris. Cela vaut aussi pour le principal : ses 28,7 % sur `nf_sport_patiente_prix_850_875` n'ont pas de preuve passée ;
l'espérance d'un favori acheté au comptant est de −1 à −2 % de la mise (frais + écart). Le mode patient (ordre posé) coûte de plus la sélection adverse (−6,8 %, `ordres_poses_en_jeu.md`).
Ce que l'arène ne peut pas dire en 11 jours, ce test le dit : **un capital qui grossit demande un avantage que le marché des favoris n'offre pas** ; les seules pistes à avantage mesuré restent `moins_de_cartes_lol` (indice) et les NON des mentions (indice).

## Reproduire
```
python experiments/totaux_sports/scripts/releve_complet.py
for i in 0 1 2 3; do N=30000 PART=$i NB=4 python experiments/totaux_sports/scripts/releve_echanges_ml.py & done      # ≈ 15 minutes, 30 000 marchés
python experiments/totaux_sports/scripts/analyse_favoris.py                                                          # ≈ 1 minute
```
