# 24/10/2026 (soir) : les marchés réglés à 50-50, un coût que les tests sur le passé ne voient pas

Famille du jour (24 % 6 + 1 = 1) déjà traitée à 14 h 54 ; ce passage : **famille 3** (dix paris du principal relus à la main, graine 2419) puis **famille 2/5** pour le chiffrage.
Scripts : `experiments/void_5050/scripts/releve_void.py` (taux Gamma par sport), `arene_par_sport.py` (sport de chaque achat `nf_*`). Données : `experiments/void_5050/releve.json.gz`, `arene_marches.json`.

## Constat
- Dans les dix paris relus, « 9INE Academy » (CS2, achat du principal à 0,877 le 21/10, **2,7 h après le coup d'envoi**) est un marché **réglé à 50-50** (prix finaux 0,5 / 0,5). Les règles du marché prévoient le 50-50 si le match est annulé ou abandonné.
- Dans les journaux de toute l'arène : **9 marchés distincts réglés à 50-50 (23 règlements de portefeuilles)**, **521 € perdus sur 1 252 € misés** (une part payée 0,50 au lieu de 1 : −43 % sur un favori à 0,88), dont la championne `nf_sport_patiente` (−39 €) et le principal (2 marchés : CS2 « 9INE Academy » −12 € et cricket « Australia Women » −4,5 €, soit −17 €).
  Les neuf : 2 CS2 « vainqueur » (9INE Academy, Alter Ego), 4 CS2 « Games Total O/U 2.5 » (`moins_de_cartes`), cricket féminin T20 (abandonné, règle explicite), Dota 2 « Game 1 Winner » (`market_structure`), tennis WTA (Świątek, walkover : règle explicite du marché).
- Sur 3 241 règlements `nf_*`, 16 sont des 50-50 (0,5 %), −508 € sur 187 594 € misés (**−0,27 % de la mise**) : c'est petit **parce que 84 à 90 % des achats d'`nf_*` se font après le coup d'envoi** (tennis ATP 591 après / 57 avant, CS2 159 / 54), moment où un walkover ou une annulation de match ne peut plus arriver.

## Cause
`history.parse_resolved` et `idea_test.parse_event_market` écartent en silence tout marché dont les prix finaux ne sont pas exactement {0 ; 1} (« annulé, 50-50 ou non réglé : exclu (limite documentée) »). Un test sur le passé qui achète des favoris AVANT le match ne voit donc jamais le risque d'annulation.
Taux de 50-50 des marchés « vainqueur » (moneyline) réglés récemment (Gamma, 600 derniers événements par série, 24/10 ; sur les 7 815 « vainqueur » avec échanges de `avant_match_50_50.md` : tous 3,0 %, CS2 8,2 %, Dota 2 5,9 %, WTA 4,9 %, ATP 2,4 %, ITF 2,3 %, LoL 0,8 %, football/NHL 0 % : les deux relevés concordent sauf UFC, non rejoué) : UFC 11,3 %, CS2 10,7 %, MLB 8,3 %, cricket international 7,3 %, WTA 4,8 %, Dota 2 4,2 %, NBA 3,3 %, ATP 2,5 %, LoL 1,7 %, ITF 0,7 %, Valorant 0,2 %, NHL/CBB/football 0 %. À 0,88 une part 50-50 coûte 0,43 € par euro : **ATP −1,1 point, WTA −2,1 points, CS2 −4,6 points, UFC −4,9 points par pari acheté avant le match**.
Ce n'est pas une anomalie de code : c'est un angle mort de la mesure.

## Ce qu'il faut en retenir
- Les stratégies qui achètent **avant** le match (`nf_tennis_12_18h*`, `nf_sport_patiente_72_168h*`, les filles à échéance longue) doivent retrancher ce coût à leur gain de backtest.
  Dans l'arène : 57 achats ATP avant le match, 0 marché ATP à 50-50 (attendu 1,4) ; 25 achats WTA avant le match, 1 walkover sur la série WTA (attendu 1,2) : pas de contradiction, trop peu pour mesurer.
- Les achats après le coup d'envoi ne sont presque pas exposés (une rencontre en cours ne s'annule plus ; l'abandon à mi-match d'un joueur de tennis donne la victoire à l'autre, pas un 50-50).
- Le cricket (pluie) et les marchés « Game N » ou « Games Total » de Dota/CS2 restent exposés même en cours de route : 6 des 9 marchés à 50-50 de l'arène sont de ce genre.

## Correctif
- Contrôle `enquete.reglements_50_50` (≥ 3 marchés distincts dans l'arène) : chiffre pertes et mise par marché, signale ceux achetés avant le coup d'envoi. Test : `tests/test_enquete.py::test_fifty_fifty_settlements_are_counted_per_market_with_their_cost`.
- Pas de décote ajoutée aux estimations `nf_*` : les achats d'avant-match représentent 10 à 16 % des mises et le coût mesuré dans l'arène est de 0,27 % de la mise ; la décote est à appliquer **dans les tests sur le passé** (`experiments/PISTES.md`, rappel ajouté) quand l'entrée est avant le match.

## Reste ouvert
- Fait dans la foulée : `experiments/avant_match_50_50.md` (favori acheté 1 à 24 h avant le match, 50-50 compris : −0,9 à −3,2 % avec, −0,3 à −2,6 % sans ; les 50-50 coûtent 0,5-0,6 point, 1-2 en e-sport ; écartée).
- Reste : `idea_test.fetch_resolved` pourrait compter les 50-50 écartés (aujourd'hui invisibles).
