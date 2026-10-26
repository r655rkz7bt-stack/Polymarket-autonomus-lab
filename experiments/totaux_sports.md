# Totaux de points et de buts des matchs de sport : « Over » ou « Under » ? (26/10/2026)

Question : sur les marchés « Lakers vs. Jazz: O/U 237.5 », un des deux côtés gagne-t-il plus souvent que son prix, avant le match ? (L'« Under » des cartes d'e-sport,
`moins_de_cartes`, est un indice confirmé en direct ; ici on regarde si le même mécanisme existe dans les sports classiques.)

## Données (scripts : `experiments/totaux_sports/scripts/`, données dans `donnees/`, ignorées par Git)
- Gamma, 37 ligues (`series_id`), événements réglés depuis le 15/08/2026, marchés de types `totals`, `first_half_totals`, `total_corners`, `soccer_team_totals`, `team_totals`,
  `tennis_*_totals` : 10 833 événements, 111 675 marchés ; ceux qui ont plus de 1 000 $ de volume et un règlement `resolved` : 24 246 marchés, leurs échanges relevés
  un à un (data-api `trades?market=`). 4 614 événements ont un échange dans au moins une fenêtre de décision.
- **Règlement** : `outcomePrices` de Gamma (1/0, ou 0,5/0,5 compté 0,5 : lignes entières, matchs annulés). Contrôle de lecture : `outcomes` toujours `["Over","Under"]`.
- **Pas de regard vers le futur** : prix = premier échange preneur (ou l'inverse de l'autre jeton) dans les 30 minutes qui suivent `coup d'envoi − d heures`, d = 1, 3, 6, 12, 24.
  Une ligne par événement, type de marché et délai : celle dont le « Over » est le plus proche de 0,5 (ligne principale). Frais du marché (`feeSchedule`) comptés. Prix de 0,05 à 0,95.

## Résultats (rendement par euro misé, `idea_test.verdict`)
| délai | Over : paris, rendement, t par match, z des prix | Under : paris, rendement, t par match, z des prix |
|---|---|---|
| 1 h | 2 648, +1,2 %, +0,84, +1,3 | 2 649, **−6,9 %, −3,54**, −2,4 |
| 3 h | 1 052, +1,3 %, +0,36, +1,0 | 1 052, −4,7 %, −1,22, −1,5 |
| 6 h | 624, +3,0 %, +0,39, +1,0 | 625, −9,9 %, −2,17, −1,4 |
| 12 h | 312, **+10,1 %**, +1,64, +1,7 (mois : +10,7 / +11,8 / +8,0 %) | 312, −12,2 %, −2,16, −2,0 |
| 24 h | 114, +16,9 %, +1,63, +1,9 | 113, −24,1 %, −2,33, −2,1 |

- **L'« Under » perd partout** avant le match (−5 à −24 %) : le contraire du mécanisme de l'e-sport, qui n'est donc **pas général** (même conclusion que pour les sept autres jeux d'e-sport).
- Par sport à −3 h (type `totals`) : tout est entre −20 et +20 % avec 6 à 90 paris par case, aucune case ne tient seule (Bundesliga Over +61 %, 19 paris ; Brésil Under −50 %, 18 paris : bruit).
- Le « Over » est à peine au-dessus de son prix de 1 h à 6 h avant (+1 à +3 %, t < 0,4) : **écarté** à ces délais. À 12 h et 24 h il fait +10 / +17 % (t par match 1,6, trois mois sur trois à 12 h), sur 312 et 114 paris seulement.
- Nombre de découpages regardés : environ 20 (5 délais × 2 côtés × types de marché), puis une trentaine de sports. Le meilleur de 20 découpages sans avantage atteint un t de 1,6 une fois sur deux : **le « Over » à 12-24 h n'est pas démontré**.
- **Taille de l'échange qui donne le prix** (mesurée ensuite) : médiane 25 parts à 12 h (quartiles 7 et 128), 12 parts à 24 h. « Over » à 12-24 h par taille : moins de 10 parts +11,4 % (153 paris), 10-50 parts +19,4 % (128), 50 parts et plus +5,7 % (145) : l'effet ne vit pas que dans les échanges minuscules, et nos mises (7-20 €) tiennent dans l'échange médian ; il s'affaiblit quand le carnet est épais, comme pour les tweets.

## Verdict : indice faible → fantôme `totaux_over`
Le test d'`idea_test.verdict` dit « retenue » pour le « Over » à 12 h (t 1,64, 3 mois sur 3) mais la règle de sélection (meilleur de ~20) et les carnets minces l'écartent : **indice faible, pas de part du capital principal.**
Fantôme `totaux_over` (quart de Kelly) : « Over » de la ligne principale, 8 à 26 h avant le coup d'envoi, prix 0,35-0,65. L'arène confirmera ou non avec de vrais carnets ; à relire après ~60 paris réglés, avec les paris joués à 12 h seulement.
