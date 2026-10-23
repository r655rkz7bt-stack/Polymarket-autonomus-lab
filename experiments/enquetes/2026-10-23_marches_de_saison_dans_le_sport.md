# Enquête du 23/10/2026 (passage chercheur, nuit) : des marchés de saison pris pour des paris de match

Passage 23 h 55 UTC (22/10) → 23/10. Famille du jour : n° 5 (comparaisons faussées), puis famille 3 (la donnée n'est pas celle qu'on croit).
Les 4 obligations de la feuille de mission (championne `nf_sport_patiente`, `nf_tennis_prix_bas`, concentration de `nf_sport_patiente_prix_850_875`,
journée du 18/10) sont les mêmes que ce matin : causes déjà écrites dans `2026-10-22_championne_biais_et_mises.md` et `2026-10-22_midi_tennis_prix_bas_et_deux_camps.md`.

## Constat 1 : le principal copie bien la championne (contrôle refait)
Depuis le 19/10 : 53 jetons de la championne copiés par le principal, mise médiane **0,333** de celle du fantôme (1 573 € contre 5 762 €, soit 0,27 en somme). Gain du principal sur ces jetons −22,6 €,
celui du fantôme sur les mêmes jetons −121 € (0,19 : même signe, même ordre de grandeur). 14 achats du principal n'ont pas de jumeau chez la championne ni chez `nf_tennis_prix_bas`
(86,9 €, −9,7 €) : ce sont les autres fantômes copiés (`champion_sans_avantage` ne les couvre pas, 14 paris sur 73). Le déficit du principal (786 €) vient de la journée du 18/10 (64 paris, −130 € :
l'ancien défaut de relance, corrigé le 18/10) ; depuis le 19/10, −84 € sur 1 530 € misés.

## Constat 2 : un marché de saison pris par la famille « sports »
Le pari de 20 h 00 UTC de la championne (22/10) : « Will Kylian Mbappé win the 2026 Ballon d'Or ? » **NON à 0,94**, estimé 0,99, **359 € = 30 % de son capital**. Gamma ne donne à ce marché aucun
`sportsMarketType` ni coup d'envoi : ce n'est pas un pari de match. Pourtant `filtres: {familles: [sports]}` (frais « sports ») le laisse passer, et tous les tests sur le passé de la famille
(tennis.md, 14 097 marchés `moneyline`) portent sur des matchs. Le principal a copié ce pari à **18 €** (2,3 % de son capital), donc pas de dégât réel.
Ampleur : 15 achats de la championne sur des marchés sans type de match (Ballon d'Or masculin et féminin, Série mondiale, Demacia Cup), **857 €**, dont 10 non réglés ; les 5 réglés ont gagné
(+ une série Cleveland 4/4 : un seul marché). Aucune preuve de perte : c'est une absence de test. Le biais fixe de 0,05 fait l'estimation (0,99 plafonnée, `prob_low` 0,975 sur un prix de 0,94) : 5 points d'avantage
affirmés sur un vote de journalistes, sans donnée. Autres fantômes : `nf_sport` 237 € (Ballon d'Or, 20/10), `nf_sport_patiente_12_18h` 122 €, `72_168h_12_18h` 136 €, `biais_faible` 104 €.
Dans la copie par jeton des 4 762 couples (stratégie, jeton) réglés ou non : 897 couples « autre » sans type (20 880 €) sont des marchés de sport hors famille « sports » (crypto, politique…), pas ceux-ci.

## Cause
`src/polymarket_agent/strategy_engine.py`, classe `Filtered` : le filtre `familles` repose sur les frais du marché ; aucun filtre ne distinguait « un match » d'une « saison ». Le contrôle
`achats_en_jeu` ne voit que les achats avec `depuis_coup_d_envoi_h` (donc les matchs) : ces achats étaient invisibles pour lui.

## Correctif (hors noyau)
- nouveau filtre `un_match: true` (marché avec `sportsMarketType` Gamma) dans `Filtered._market_ok` ; test `test_match_only_filter_refuses_season_and_award_markets` ;
- sœur **`nf_sport_patiente_matchs`** (mêmes paramètres que la championne + `un_match`), à comparer sur la **même période**. La championne n'est pas modifiée (le principal la copie) ;
  si la sœur fait aussi bien, la décision de filtrer la championne revient à Etienne (même place que la décision sur `bias`) ;
- contrôle automatique **`sport_hors_match`** (`enquete.py`) : achats de ≥ 100 € sans `depuis_coup_d_envoi_h` par une stratégie « sports » sans `un_match` ; test `test_sport_buy_without_kickoff_is_a_lead`.
  Il signale aujourd'hui 6 stratégies (359, 237, 160, 136, 122, 104 €).

## Reste ouvert
Résultat du Ballon d'Or 2026 (clôture du marché 27/10) : donnera le premier pari réglé de ce type à ce prix. Les marchés de saison pourraient avoir un avantage à part (NON sur les outsiders) :
à tester sur l'historique (`PISTES.md`, piste « NON sur les marchés de gagnant de saison »), pas à jouer sans test.
