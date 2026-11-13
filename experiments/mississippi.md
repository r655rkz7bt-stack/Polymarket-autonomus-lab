# Plus bas niveau du Mississippi : prévision officielle contre prix (piste n° 52, 13/11/2026, passage de 11 h)

**Marchés** : « Lowest Mississippi level at St. Louis by November 30? » (118 k$ de volume) et « … at Baton Rouge … » (81 k$),
5 tranches chacun, frais `weather_fees` (5 % × p(1−p), preneur seulement), étiquettes drought 105721 / weather 84 / climate 87
(déjà lues par le scanner). Seuls événements de ce type sur Polymarket (aucun réglé) : **pas de test sur le passé possible**.

## Règles lues mot à mot

- Saint-Louis : plus bas relevé quotidien de l'USGS, site 07010000, paramètre 00065, **statistique 30800 (relevé de 8 h)**, entre
  la création du marché (22/09) et le 30/11 ; valeurs publiées telles quelles (provisoires comprises), bornes au centième
  comprises (« -1.00 » va à la tranche « -1.00 to 0.99 »).
- Baton Rouge : même règle avec la **moyenne du jour** (statistique 00003), site 07374000, fenêtre depuis le 21/09 (`startDT` du
  lien de la règle).

## Sources (sans clé)

- Relevés : `waterservices.usgs.gov/nwis/dv/?format=json&sites=<site>&parameterCd=00065&statCd=<stat>&startDT=…` (Saint-Louis :
  relevés de 8 h depuis 1990, 13 276 jours).
- Prévisions officielles du NWS : `api.water.noaa.gov/nwps/v1/gauges/<EADM7|BTRL1>/stageflow/forecast` (Saint-Louis : 14 jours,
  pas de 6 h ; Baton Rouge : 28 jours, prévision du LMRFC qui route l'eau déjà dans le fleuve) ; les prévisions passées ne sont pas
  archivées. Amont utile : Cairo (`CIRI2`, Ohio + Mississippi).

## Lecture du 13/11 (≈ 11 h UTC)

**Saint-Louis** : plus bas 2,77 ft (01/11), puis une onde (12,7 ft le 10/11), 11,38 le 12/11. Prévision NWS (émise 03 h 29) : 10,8 →
3,0 ft le 26/11, 2,6 le 27/11 (fin de l'horizon), −0,55 ft par jour. Prolongée sans pluie : ≈ 0,6-1,0 ft le 30/11, pile sur la borne
« 1.00 ». Mais :
- ensembles Open-Meteo (GFS 31 membres, ECMWF 51) sur 8 villes du bassin (Kansas City, Omaha, Des Moines, Dubuque, Burlington,
  Columbia, Minneapolis, Sioux City) : pluie moyenne du 13 au 24/11 médiane 17 mm (GFS) / 27 mm (ECMWF), moins de 10 mm dans 23 % /
  4 % des membres ; la pluie des 20-23/11 arriverait à Saint-Louis vers le 25-28/11 ;
- **analogues 1990-2025** (`mississippi/analogues.py`, jours d'octobre à début décembre à 10,7 ± 2,5 ft en baisse) : 33 cas, baisse
  médiane −4,5 ft en 17 jours, 1 cas sur 33 passerait sous 0,99 ; surtout, quand le plus bas des 30 jours d'avant est bas (onde sur
  des basses eaux), **le plus bas des 17 jours suivants n'est jamais repassé sous ce plus bas d'avant l'onde : 19 cas sur 19** (il
  faudrait ici 1,8 ft en dessous).
Cinq estimations de P(plus bas ≤ 0,99) : prévision prolongée × chance d'un temps sec 0,13 ; analogues « onde » 0,05 ; analogues du
niveau 0,03 ; marché 0,18 ; décrue + pluie médiane 0,10 → médiane 0,10, soit « 1.00 to 2.99 » ≈ 0,90 contre 0,812 (vendeur 0,863).
Rapprochée de moitié : 0,855 < vendeur. **Pas de conviction.**

**Baton Rouge** : plus bas 6,38 (09/11), 6,67 le 12/11 en hausse (l'onde de Saint-Louis arrive) ; prévision LMRFC du 12/11 16 h :
montée à 8,4 ft les 22-23/11, **jamais sous 7,1 ft avant le 30/11** (6,0 vers le 06/12). Cairo : 16,1 ft le 12/11, 13,3 prévu le
22/11 (12,6 le 05/11 correspondait à Baton Rouge ≈ 6,4 une semaine plus tard) → le 30/11 devrait rester au-dessus de 6,4.
Analogues de Baton Rouge (56 jours d'octobre-décembre en hausse lente à 4,5-9 ft) : le plus bas des 18 jours suivants est 0,67 ft
sous le niveau du jour dans 30 % des cas (ils ignorent l'onde déjà en route). Cinq estimations de P(« 6.00 ft or more ») : prévision
0,94, Cairo 0,95, pluie (biais vers le haut) 0,97, analogues 0,70, vitesse de décrue maximale observée (0,3 ft/j depuis 8,4) 0,90 →
médiane 0,94 ; marché 0,834 (vendeur 0,837, 240 parts, puis 506 à 0,838) ; rapprochée de moitié 0,887, borne ≈ 0,86 : à 1,6 point du
vendeur + frais, **sous le seuil de 5 points : pas de conviction**. Le prix monte depuis le 04/11 (0,30 → 0,83) à mesure que l'onde
se voit dans les relevés : le marché suit le niveau du jour plus que la prévision.

## Verdict : expérience (fantôme `mississippi_plus_bas`)

Source `mississippi` (relevés USGS + prévisions NWPS, relue chaque heure) et journal `mississippi:histo` (chaque prévision émise, une
fois) : dans un mois, l'erreur réelle des prévisions à 1-3 semaines sera mesurable. Modèle (`mississippi.py`) : plus bas publié +
relevés à venir simulés = prévision (à plat au-delà de l'horizon : la pluie arrête les décrues, cf. les 19 cas sur 19) + marche
aléatoire (Saint-Louis 0,30 ft/√j, Baton Rouge 0,20) + bruit du relevé (0,45 / 0,05 ft). Le 13/11 il redonne Saint-Louis
(« 1-2,99 » 0,811 contre 0,812 ; « -1 à 0,99 » 0,18 contre 0,11) et met Baton Rouge « 6 ft ou plus » à 0,899 contre 0,834.
Fantôme à Kelly entier sur la borne basse (incertitude 0,06, avantage net 0,04, 5 % au plus par pari, une tranche par jauge) :
**aucun achat le 13/11** (borne 0,84 pour un vendeur à 0,837 + frais). Une perte apprendrait que les prévisions à 2-3 semaines se
trompent plus que la marche aléatoire supposée, ou que le marché les lit déjà.

À relire : le plus bas publié chaque jour contre la prévision du 13/11 ; les marchés de décembre s'ils sont créés.
