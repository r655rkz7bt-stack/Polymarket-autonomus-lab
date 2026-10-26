# Handicaps (« spreads ») des matchs de sport (26/10/2026)

Suite de `totaux_sports.md`, même méthode et mêmes scripts (`experiments/ecarts_sports/scripts/`) : marchés `spreads`, `first_half_spreads` et `tennis_set_handicap` réglés depuis le 15/08 (8 472 événements, 13 334 marchés
à plus de 1 000 $ de volume, vrais échanges), 3 347 événements avec échange dans une fenêtre de décision. Ligne principale (jeton 0 le plus près de 0,5), achat du côté qui DONNE des points (« favori ») ou qui en REÇOIT
(« outsider ») au premier échange preneur dans les 30 minutes après `coup d'envoi − d heures`, frais du marché, 50-50 comptés 0,5.

| délai | favori : paris, rendement, t par match | outsider : paris, rendement, t par match |
|---|---|---|
| 1 h | 1 414, −2,0 %, −0,43 | 1 410, −1,8 %, −0,92 |
| 3 h | 618, −4,2 %, −0,94 | 618, −3,3 %, −0,75 |
| 6 h | 346, +0,7 %, +0,03 | 347, −2,5 %, −0,45 |
| 12 h | 184, −0,5 %, −0,05 | 184, −8,8 %, −1,26 |
| 24 h | 73, +0,8 %, +0,15 | 72, −9,4 %, −0,98 |

Par sport (3 h, 6 à 99 paris par case) : NFL favori −20,7 % / outsider +13,4 %, NBA −15,2 / +12,9 %, mais MLB (+28,4 / −28,0 %) et Ligue des champions (+31,9 / −30,0 %) vont dans l'autre sens : bruit.
**Verdict : écartée** (aucun des 10 découpages par délai et côté au-dessus d'un t de 0,2 en positif ; les marchés de handicap sont aussi bien cotés que ceux des vainqueurs).
Rien dans l'arène. Le prix payé inclut déjà l'écart achat-vente observé : les deux côtés perdent ~2-4 % d'écart et de frais, ce qu'on attend d'un marché juste.
