# Températures maximales du jour : Kalshi (rapport climatologique) contre Polymarket (METAR) — piste n° 62 (15/11/2026 ; règle générale écartée, tranche sous la médiane CLI : indice faible → fantôme `meteo_sous_cli`)

Passage du chercheur de 6 h. Idée neuve (point 4 de la consigne, « cohérence entre marchés liés », et point 2, « lire les règles ») :
Kalshi (`KXHIGHAUS`, `KXHIGHMIA`, `KXHIGHDEN`, `KXHIGHLAX`, marchés très échangés) et Polymarket (« Highest temperature in
<ville> on <date>? », 11 tranches de 2 °F, `zero_fees` depuis le 20/10) cotent le maximum du jour **aux mêmes stations**
(KAUS, KMIA, KDEN, KLAX ; NYC et Chicago n'en partagent pas : Central Park / LaGuardia, Midway / O'Hare). Mais pas la même valeur :
- Kalshi : « maximum temperature recorded at <ville> (CLI…) », le rapport climatologique NWS (maximum du jour entier, pointes
  entre deux relevés comprises) ;
- Polymarket : depuis le ≈ 20/10, le plus haut **groupe T des METAR de routine** (horaire, dixièmes de °C, SPECI exclus) ; d'août
  au 20/10 la série horaire de weather.gov ; avant, Wunderground.
Les tranches sont décalées d'un degré (Kalshi « 75-76 », Polymarket « 60-61 »).

## Données (`experiments/meteo_kalshi/`, données dans `donnees/`, ignoré par Git)
- `releve_poly.py` : 1 031 événements Polymarket réglés des 4 villes (décembre 2025 → 16/11/2026, `public-search`).
- `releve_kalshi.py` : 276 événements Kalshi réglés depuis la bascule « historical » (15/09/2026), bougies horaires de
  l'événement entier en UN appel (`/series/<s>/events/<e>/candlesticks`, débit limité : ≈ 3 s par appel avec les 429).
- `releve_prix_poly.py` : prix horaires du CLOB (3 014 jetons) ; `releve_echanges.py` : 381 387 vrais échanges (2 803 marchés).
- 291 événements appariés (06/09 → 13/11/2026).

## Écart de mesure (CLI Kalshi − tranche gagnante Polymarket)
METAR (104 jours) : dedans 67, +1 °F 32, +2 °F 4, −1 °F 1 ; weather.gov (187) : dedans 104, +1 61, +2 8, +3 2, −1 à −5 : 12.
Le maximum horaire est ≤ au maximum du jour dans 98 % des cas, d'un degré une fois sur trois : la loi Kalshi doit être
décalée (EM sur les seuls événements réglés AVANT celui qu'on juge).

## Résultats (`analyse.py <heure> <seuil> <écart>`)
Loi Kalshi à l'instant T (milieu de la dernière bougie finie, normalisé), décalée, contre le prix Polymarket :
- **au prix horaire du CLOB** : log-perte Kalshi 0,176 contre Polymarket 0,208 (J 14 h UTC) ; régime METAR 0,152 contre 0,253 ;
  achats simulés (seuil 0,08) +44 % sur 446 paris, t par événement 1,7 ;
- **aux vrais échanges** (premier achat preneur de la même issue dans les 2 h, prix ≤ chance − seuil, frais 1 point avant le
  20/10) : tout s'efface. J 14 h, seuil 0,08 : ≥ 20 parts 318 paris **+0,6 %** (t par événement −1,6), ≥ 100 parts −5,3 % ;
  J−1 20 h : +5,3 % / −4,1 % ; seuil 0,05 : −0,8 à −6,5 % ; seuil 0,15 : −28,9 % à +7,5 % (t ≤ +0,2). 18 réglages
  (2 heures × 3 seuils × 3 profondeurs), aucun au-dessus de t 0,6 aux vrais échanges.
- Lecture : le « prix » horaire des tranches de température est un milieu de carnet (le défaut du 22/10 et du 04/11) ; quand un
  vrai vendeur est là, il vend au prix que Kalshi donne déjà (les échanges réels gagnent comme leur prix).

## Verdict de la règle générale : **écartée** (aux vrais échanges, « Kalshi décalé contre prix » n'apprend rien au preneur Polymarket ; voir la suite)
Ce qui reste utile : l'écart de mesure (≈ 1/3 des jours, le maximum METAR horaire est 1 °F sous le maximum CLI), à tout modèle
météo qui prévoit la valeur NWS d'un jour pour un marché Polymarket. Ne pas relancer sans un test de profondeur d'emblée.

## Suite du même passage : la foule retire-t-elle l'écart ? (`position_tranche.py <parts> <queue max>`)
Hypothèse posée AVANT le calcul : si la foule de Polymarket lit les prévisions NWS (maximum CLI) sans retirer l'écart METAR, la
tranche qui contient la médiane CLI de Kalshi (k = 0) est trop chère et celle du dessous (k = −1) trop bon marché. Vrais achats
preneurs du OUI de J−1 12 h à J 20 h UTC (premier échange qualifiant par jeton), loi Kalshi NON décalée à l'heure de l'échange,
frais `weather_fees` (5 % × p × (1 − p), les marchés de température sont de nouveau payants le 15/11) comptés partout.
- Premier passage : une queue Kalshi (« < 61 ») qui porte presque toute la loi était posée sur deux degrés : « médiane » fausse.
  Corrigé (loi refusée si une queue dépasse 0,30 ou 0,15).
- Règle **METAR** (la règle actuelle), queues ≤ 0,15 : **k = −1 : 28 gagnés pour 24,0 payés (≥ 20 parts, 75 paris, +16,5 %),
  23 pour 19,5 (≥ 100, 61 paris, +17,9 %)** ; k = 0 : +0,3 % / −4,9 % ; k = +1 : **−36 % / −33 %** ; k = −2 : −60 % / −49 %.
  Avec queues ≤ 0,30 : k = −1 +23 % / +18 %.
- Règle weather.gov (août → 20/10) : k = −1 −4,6 % / +4,3 % ; rien.
- Lecture : sous la règle METAR, la foule paie la tranche du dessus et néglige celle du dessous, comme si elle lisait le maximum
  du jour entier. z ≈ 1,4 (81 paris au plus, 104 jours, ≈ 8 réglages regardés) : **indice faible, sur la seule règle en cours**.
- Écart CLI − METAR appris (EM, 104 jours METAR) : 0 °F 0,36 ; 1 °F 0,565 ; 2 °F 0,075 (weather.gov : 0,364 / 0,53 / 0,086 / 0,02).

## Fantôme `meteo_sous_cli` (expérience audacieuse, même passage)
Source `meteo_kalshi` (4 appels publics à Kalshi toutes les 30 min, `meteo_kalshi.py`), étiquettes de ville du scanner (austin
104277, miami 100937, denver 102930, los-angeles 100743, horizon 60 h). Seule la tranche k = −1 reçoit une chance (Kalshi décalé),
OUI seulement, avantage net ≥ 0,03 sur la borne basse (chance − 0,03), prix 0,10-0,60, une tranche par ville et par jour,
Kelly entier. Cycle local du 15/11 06 h 26 : 3 tranches rattachées, 1 achat (Los Angeles 15/11, « 70-71 °F » à 0,127 pour
0,247 ; Kalshi : médiane CLI 73 °F ; Polymarket met 0,72 sur « 72-73 »). À juger sur ≥ 40 jours réglés (fin décembre) avant
toute place au capital principal.
