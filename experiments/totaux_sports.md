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

## Hors échantillon : février-août 2026 (même méthode, jamais regardé avant)
11 024 événements du 01/02 au 15/08 (`scripts/releve_avant.py`, `releve_echanges_avant.py`), 18 099 marchés, 5 879 événements avec échanges, 16 528 paris. « Over » : −3,3 / −2,8 / −0,2 / **−0,9 % (906 paris, t −0,24) / −5,3 %** à 1/3/6/**12**/24 h ;
« Under » −0,2 / −2,3 / −4,9 / −1,7 / −5,2 %. **Le +10 % de l'« Over » à 12 h disparaît** (−0,9 %), comme le −5 à −24 % de l'« Under » (−0,2 à −5 %, t jamais au-dessous de −1,8) : les deux écarts de la découverte étaient du bruit.

## Au passage : l'e-sport (CS2, LoL, Dota 2, Valorant, « Games Total ») sur ces mêmes relevés
Février-août (période jamais vue par `moins_de_cartes`) : « Under » **+4,2 / +11,7 / +12,9 %** à 1/3/6 h (329 / 153 / 99 paris, t par match 0,8 / 1,5 / 1,4), « Over » −10,6 / −22,8 / −23,9 % (t jusqu'à −2,6). Août-octobre (même filtre : ligne principale, plus de 1 000 $ de volume) : « Under » −0,5 / +0,8 / −7,5 % (220 / 104 / 66 paris).
Le signe de l'« Under » d'e-sport se retrouve sur une période indépendante, moins fort que le +7,7 % du 25/10 et fragile sur août-octobre avec ce filtre : **l'indice de `moins_de_cartes` reste un indice** (plutôt un peu mieux étayé), jamais une preuve.

## Verdict : écartée (les deux côtés)
Sur la découverte (15/08-26/10) le meilleur découpage faisait +10,1 % (« Over », 12 h, t 1,64) ; sur février-août le même découpage fait −0,9 % (906 paris). Rien dans l'arène : le fantôme `totaux_over`, écrit puis testé en cycle local
(3 propositions), a été **retiré avant la fusion** (classe, entrée de config et test supprimés). Le mécanisme de `moins_de_cartes` (Under des cartes d'e-sport) reste propre à l'e-sport.
Méthode retenue pour la suite : tout « indice » trouvé sur un relevé récent se refait sur la période précédente AVANT d'écrire une stratégie (ici : une demi-heure de téléchargement évite un fantôme inutile).
