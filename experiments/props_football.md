# Football : marchés de joueurs, premier à marquer, corners d'équipe (28/10/2026)

Piste neuve : les marchés de football autres que le résultat, les totaux de buts et les scores exacts (déjà jugés : `sous_marches_football.md`, `btts.md`, `pistes_sport_coherence.md`).
Scripts : `props_football/scripts/` (relevé des événements par `/events/keyset`, échanges de la data-api, analyse) ; chiffres : `props_football/resultats.txt`.

## Ce qui existe
17 ligues, 11 000 événements réglés depuis le 27/02/2026. Types relevés et nombre de marchés : scores exacts 58 494, tirs d'un joueur 27 915, passes décisives 22 689, tirs cadrés 22 332,
buteur à tout moment 19 761, buts + passes 16 749, buts d'une équipe 15 312, buts d'un joueur 15 126, corners d'une équipe 11 704, buts d'une équipe en 1re mi-temps 10 208, premier à marquer 5 517, arrêts du gardien 3 276.
**Les marchés de joueurs (tirs, passes, tirs cadrés, buts + passes, arrêts : ≈ 108 000 marchés) n'ont presque aucun volume** (`volumeNum` vide ; au plus 7 marchés à plus de 500 $ pour 3 types) : rien à acheter.
Seuls s'échangent : buteur à tout moment (774 marchés à plus de 500 $), premier à marquer (1 012), corners d'équipe (468), buts d'équipe en 1re mi-temps (774).

## Test
4 125 marchés à plus de 300 $ de volume, 1 418 événements ; vrais échanges (data-api), premier échange preneur dans les 30 minutes qui suivent T = coup d'envoi − 1, 3, 6, 12 ou 24 h, prix payé de 0,05 à 0,95, frais du marché (`feeSchedule`), 50-50 compté 0,5.
3 260 paris simulés. Règlement : prix finaux Gamma (`outcomePrices`) ; **non relu à la source** (pas de score officiel relu), comme les autres relevés de sport.

## Résultats (rendement par mise, t par événement, gagnés / attendus par les prix)
- Buteur à tout moment, OUI : −1 h +1,4 % (440 paris, t +1,10) ; −3 h −1,0 % ; −6 h +14,1 % (110 paris, t +0,41) ; −12 h +9,5 % (51). NON : −6,3 % (−1 h), −15,8 % (−3 h, t −1,68).
- Premier à marquer, NON : +3,3 % (−1 h, 421 paris), −11,4 % (−3 h, t −1,97), +0,2 % (−6 h), −4,7 %, +0,7 % (−24 h) ; OUI : −0,2 %, −7,4 %, +12,0 % (32 paris).
- Corners d'équipe, Over : +2,1 %, −1,9 %, +2,3 %, +16,5 % (−12 h, 45 paris, t +1,17), −20,0 % (−24 h) ; Under −7,7 %.
- Buts d'équipe en 1re mi-temps, Over : +1,2 %, +13,9 % (51 paris), +14,2 % (31), −11,1 % ; Under −7,6 %.
- Aucune cellule n'a un t par événement au-dessus de 1,5 (sur ≈ 45 cellules regardées, 2 sont en dessous de −1,9) ; les signes changent d'un délai à l'autre.

## Verdict : écartée
Rien de régulier : les marchés qui s'échangent battent à peine leurs prix, et les ≈ 108 000 marchés de joueurs ne s'échangent pas. Pas de stratégie, pas de fantôme.
Écart avec ce qui compte : l'« avantage » de l'arène vient de familles précises (cartes d'e-sport, tweets), pas des marchés de football annexes.
À refaire seulement si les marchés de tirs de joueurs prennent du volume (compter ceux à plus de 500 $ une fois par mois).
