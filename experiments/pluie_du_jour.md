# Pluie du jour : la pluie déjà tombée (METAR) contre le prix (13/11/2026, piste n° 55, passage chercheur de 16 h)

**Verdict : indice (OUI après pluie vue) → fantôme `pluie_vue` (expérience audacieuse). Côté NON : indice noté, pas de stratégie
(il faut un modèle de la pluie restante).**

## Les marchés

Événement quotidien « Where will it rain on <date>? » (Gamma, étiquettes `weather` 84 et `rain` 105879, créé la veille à 11 h 09 ou
12 h 09 UTC, frais `weather_fees` 5 % × p(1−p) pour le preneur). Depuis le 19/08/2026 : une dizaine de villes américaines par jour
(Los Angeles, Houston, Dallas, Phoenix, Philadelphie, Washington, Atlanta, Miami, La Nouvelle-Orléans, San Francisco ; certains jours
Boston, New York, Chicago Midway, Denver, Seattle). 92 événements trouvés par `public-search` (85 jours américains réglés), 1 189
marchés réglés nets, 16 489 vrais échanges (Data API v2), 1-13 k$ de volume par jour.

Règle : OUI si le rapport climatique du NWS (CLI, `product=CLI&issuedby=XXX`) donne au moins 0,01 pouce (« T » = trace : NON)
pour la journée climatique **minuit à minuit, heure locale STANDARD** (pas d'heure d'été : Los Angeles 08 h → 08 h UTC toute
l'année). Le rapport final sort le lendemain matin ; réglé sur la version publiée avant 14 h (heure de l'Est) le lendemain.

## Idée (avantage d'INFORMATION : lire la source avant le règlement)

La station du rapport CLI publie aussi un METAR chaque heure (et des SPECI) avec la pluie de l'heure (groupe P, `P0004` = 0,04 pouce),
lisible sans clé sur `aviationweather.gov/api/data/metar` (champ `precip`, 0,005 = trace) quelques minutes après l'observation
(`receiptTime`). Dès qu'un METAR de la journée climatique montre 0,01 pouce, l'issue OUI est presque acquise, des heures avant le rapport.

## Données et contrôle du règlement (`pluie_du_jour/scripts/releve.py`, `analyse.py`)

METAR horaires de juin à novembre 2026 par l'IEM (`mesonet.agron.iastate.edu/cgi-bin/request/asos.py`, colonne `p01i`, routine et
spéciaux ; téléchargement prévu pour les scripts). Journée climatique en heure standard ; le premier relevé de la journée (moins de
55 min après minuit, qui peut compter la pluie de la veille) est écarté.
**Règlement redonné : 1 178 marchés sur 1 189** (≥ 20 METAR dans la journée). Écarts : 9 OUI sans METAR ≥ 0,01 (pluie hors
groupe P ou relevé manquant : sans effet sur la stratégie, qui n'achète que la pluie vue) et **2 faux OUI à Phoenix** (30 et 31/10 :
METAR ≥ 0,01, rapport CLI à 0) : seul risque réel du pari.

## Test : premier vrai échange du OUI après la pluie vue

Premier échange réel du jeton OUI après (première pluie vue + délai), prix ≤ 0,985, au moins N parts ; gain = paiement − prix −
frais. 3 délais × 2 tailles × 2 lectures des échanges = 12 réglages, tous regardés :

| échanges | délai | ≥ parts | paris | gagnés / attendus | z | par mise | t par jour |
|---|---|---|---|---|---|---|---|
| tous | 10 min | 10 | 67 | 66 / 58,1 | +3,5 | +13,1 % | 1,72 (39 j) |
| tous | 30 min | 10 | 58 | 57 / 49,5 | +3,5 | +14,7 % | 1,72 |
| tous | 60 min | 10 | 53 | 52 / 46,2 | +2,9 | +12,2 % | 2,12 |
| preneur acheteur | 10 min | 10 | 59 | 58 / 51,2 | +3,4 | +12,9 % | 1,63 |
| preneur acheteur | 30 min | 10 | 48 | 47 / 40,4 | +3,4 | +15,8 % | 1,64 |
| preneur acheteur | 60 min | 10 | 42 | 41 / 36,1 | +2,7 | +13,1 % | 1,96 |
| preneur acheteur | 10-60 min | 50 | 24-30 | 23-29 | +1,4 à +1,7 | +6 à +10 % | 1,1-1,4 |

Mois par mois (preneur acheteur, 30 min, ≥ 10 parts) : août +14 %, septembre +9 %, octobre +11 %, novembre (2 paris) positif.
Tranches de prix (tous échanges, 10 min) : < 0,80 : 14 paris, 13 gagnés pour 7,5 attendus (+72 %) ; 0,80-0,90 : 3 pour 3 ;
0,90-0,95 : 10 pour 10 (+9 %) ; 0,95-0,99 : 40 pour 40 (+2,6 %). 13 stations sur 13 positives. Délai médian entre la pluie vue et
l'échange : 0,8 à 3 h. Un seul perdant : Phoenix, 31/10, acheté 0,50 près de 19 h après (le marché savait).

**Réserves** : une partie du gain vient de petits échanges (15-24 parts) à 0,10-0,60 juste après la pluie ; au moins 50 parts, le
gain tombe à +6-10 % (z +1,4 à +1,7). La stratégie achète au vendeur du carnet à chaque cycle (30 min), pas au prix du premier
échange. Le 13/11 à 16 h 30 UTC, Los Angeles, San Francisco et Philadelphie avaient de la pluie vue depuis 5-10 h et le OUI était
à 0,95-0,999 (cycle local : 3 marchés rattachés, aucun achat) : le gain se joue dans la première heure ou sur les vendeurs oubliés.

## Côté NON (noté, pas de stratégie)

Aucune pluie vue H heures avant la fin de la journée → premier échange du NON (preneur acheteur, ≥ 10 parts) :
12 h : 295 paris, +9,8 % (z +4,1, t par jour 1,4) ; 8 h : 214 paris, +9,0 % (z +3,7, **t par jour 2,7**) ; 4 h : +5,3 % ; 2 h : +2,8 %.
Plafond 0,95 : +14 % à 8-12 h. 8 réglages. Le NON de ces marchés est peut-être simplement sous-payé en général (biais de prix,
pas une information) : il faut comparer à une chance calculée (fréquence de pluie dans les heures restantes sachant la journée
sèche, prévision horaire NWS) avant d'en faire une stratégie. À reprendre.

## Ce qu'une perte de `pluie_vue` apprendrait

Que le marché lit maintenant les METAR (OUI déjà à 0,98 quand le cycle arrive), que les vendeurs à prix faux ne servent pas une vraie
mise, ou que METAR et rapport CLI divergent plus qu'en août-novembre (Phoenix).
