# Over/Under de sport (props de joueurs, totaux, mi-temps, quarts) : l'Over est-il trop cher avant le match ?

Passage chercheur du 28/10/2026 (matin). Suite de `experiments/PISTES.md` (« props de joueurs : non testable, 80 paris », 26/10) : on change d'échelle en prenant TOUS les marchés Over/Under de 10 séries.

## Données (scripts : `experiments/props_over_under/scripts/`, résultats bruts : `resultats.txt`)

- Gamma `/events/keyset` (série par série, coup d'envoi depuis le 01/09/2026) : **94 912 marchés Over/Under réglés nettement** (CFB 56 329, NFL 31 673, NBA 5 428, NHL 1 208, WNBA 238, Euroleague 36).
- Vrais échanges des preneurs (data-api) : **seulement 18 590 marchés ont au moins un échange** (les props de joueurs sont presque tous vides : 30 à 400 $ de volume) ; 24 034 achats simulés.
- Prix payé = premier échange réel d'un preneur qui ACHÈTE le côté dans l'heure qui suit « coup d'envoi − h » (h = 0,5 / 1 / 3 / 6 h), ≥ 5 parts, frais du barème du marché ; regroupé par événement (les paris d'un même match sont liés).

## Résultats (rendement par mise, t par événement)

| h avant | Over (tous) | Under (tous) | NBA Over | NBA Under |
|---|---|---|---|---|
| 0,5 h | −3,8 % (5 955 paris, t −1,3) | −0,9 % (4 917, t −0,3) | −11,0 % (t −1,5) | +4,2 % (t +0,5) |
| 1 h | −3,1 % (4 593, t −1,1) | −2,3 % (3 202, t −0,7) | −10,6 % (t −1,4) | +6,9 % (t +0,8) |
| 3 h | −4,5 % (1 896, t −1,3) | +0,4 % (1 428, t +0,1) | −1,0 % | +0,9 % |
| 6 h | −1,6 % (1 132, t −0,4) | 0,0 % (911, t 0,0) | −8,2 % (t −0,8) | +12,1 % (250 paris, t +1,1) |

Par type : Over de yards reçus −11 à −14 % (t −1,6 à −1,7), Over de touchdowns passés −5 à −23 %, Under des mi-temps et quarts +2 à +14 % (t ≤ 0,9). **Aucun t ne dépasse 1,9 en valeur absolue** (le pire : Over des mi-temps, −14,6 %, t −1,9) sur environ 80 lignes regardées ;
le CFB et la NFL (les deux tiers des marchés) sont à −0,1 à −6 % des deux côtés (les frais).

## Verdict : **écartée** (rien dans l'arène)

Un Over un peu plus cher que l'Under (1 à 5 points d'écart de rendement, de même signe aux 4 horaires) est visible, comme pour les kills d'e-sport, mais rien n'y est significatif et le meilleur côté (NBA Under 6 h, +12 %) a t +1,1 sur 250 paris parmi 80 lignes.
Limite : les props de joueurs n'ont presque pas d'échanges avant le match ; refaire le test en janvier avec 3 mois de NBA (la saison commence).

## Par tranche de prix payé (`tranches_de_prix.py`, les 4 horaires confondus : un même marché peut compter à plusieurs horaires, les t sont donc un peu gonflés)

| prix payé | paris | gagnés / attendus | rendement | t par événement |
|---|---|---|---|---|
| 0,02-0,10 | 222 | 9 / 14,4 | −39,5 % | −1,6 |
| 0,10-0,25 | 1 123 | 197 / 207,7 | −7,0 % | −0,8 |
| 0,25-0,45 | 4 299 | 1 548 / 1 626,7 | −6,2 % | −2,1 |
| 0,45-0,55 | 10 495 | 5 307 / 5 255,5 | −0,3 % | −0,4 |
| 0,55-0,75 | 5 893 | 3 542 / 3 606,5 | −2,7 % | −1,6 |
| 0,75-0,90 | 1 330 | 1 040 / 1 076,7 | −3,9 % | −1,9 |
| 0,90-0,99 | 587 | 528 / 550,5 | −4,2 % | −2,3 |

Aucune tranche ne bat ses prix : seuls les frais et l'écart achat-vente parlent, et les billets sous 0,10 perdent encore (3e famille de marchés après l'e-sport et Up/Down). Même leçon : jamais de billets sous 0,10 sans source qui tranche.
