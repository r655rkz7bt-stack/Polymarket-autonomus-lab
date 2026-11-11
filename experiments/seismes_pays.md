# Séismes par pays et par mois (piste n° 20, 11/11/2026, passage de 6 h)

**Question.** Les marchés « Where will a 6.0+ magnitude earthquake occur by end of <mois> ? » (un marché OUI/NON par pays : Indonésie,
Japon, Chili, Mexique, États-Unis, Philippines, Pérou) cotent-ils la chance d'un séisme ≥ 6,0 au-dessus de sa fréquence de base ?

**Règle (marché 6422863, lue en entier).** OUI si l'USGS publie un séisme de magnitude préférée ≥ 6,0 « attribué au pays dans la
description de lieu », heure d'origine du 1er au dernier jour du mois (minuit à minuit, heure de l'Est) ; révisions comptées 3 jours.
Frais : `weather_fees` (5 % × p × (1 − p) par part, preneur seulement). Un séisme d'Alaska compte pour les États-Unis (septembre 2026 :
réglé OUI sur « M 6.3 - 92 km SSW of Nikolski, Alaska », 03/09 11 h 17 UTC).

**Données.** Catalogue USGS ≥ 5,95 de 2000 à 2025 (4 005 séismes ≥ 6,0) ; pays = texte après la dernière virgule de la description
(`seismes.country_of`, États américains → United States). Fréquence de base = jours par an avec au moins un séisme attribué au pays
(les répliques du même jour ne comptent qu'une fois) : Indonésie 13,8, Japon 9,5, États-Unis 6,8, Chili 5,5, Philippines 5,0,
Mexique 3,2, Pérou 2,2 (`src/polymarket_agent/seismes_pays.json`, 45 pays). Chance du OUI = 1 − exp(−jours/an × jours restants / 365,25).
Contrôle sur 26 ans (11 au 30 novembre) : fréquence observée Indonésie 0,62, Japon 0,50, Chili 0,31, Mexique 0,15, Philippines 0,23,
Pérou 0,08, États-Unis 0,31 ; la loi dit 0,53 / 0,41 / 0,27 / 0,16 / 0,24 / 0,11 / 0,29 : bon accord.

**Grappes (répliques) ?** Sur 2000-2025, la chance d'un jour à séisme ≥ 6 dans les 20 jours suivants change peu après un séisme ≥ 6 dans le
même pays les 30 jours d'avant : Indonésie 0,48 contre 0,50, Japon 0,38/0,36, Chili 0,24/0,20, Mexique 0,18/0,15, Philippines 0,23/0,25,
Pérou 0,13/0,10, États-Unis 0,29/0,31 : pas de correction de grappe.

**Marchés réglés.** Seulement deux mois existent (septembre 944677, octobre 1108757) ; novembre (1283623) est ouvert.
Issues : 3 OUI sur 14 (Indonésie septembre, États-Unis septembre, Japon octobre) ; la base en attendait 5,4 au 1er du mois, les prix horaires 7,2.
Règlement retrouvé 14/14 par notre lecture du catalogue (premier séisme qualifiant : Indonésie 11/09, États-Unis 03/09, Japon 25/10).

**Contre le marché (prix horaires, `releve.py`).** Prix aux jours 1-20 : 0,25-0,55 pour des pays que la base met à 0,06-0,35 (Pérou
0,38-0,55 pour 0,06-0,17). Ces prix sont surtout des milieux de carnets vides : ils ne s'achètent pas.

**Aux prix payés (`echanges.py`, `analyse.py`, data-api v2).** 364 achats du NON (preneur qui achète le NON ou vend le OUI), 340 avant
le premier séisme qualifiant du pays. Un pari = le premier échange par marché dont le prix du NON est sous la base − seuil :

| seuil | marchés | NON gagnés | attendus (base) | prix payés | rendement | tous les échanges sous le seuil |
|---|---|---|---|---|---|---|
| 0,00 | 12 | 11 | 8,78 | 6,60 | +67 % | 297 échanges, +12 % |
| 0,05 | 11 | 10 | 7,96 | 5,66 | +77 % | 166 échanges, +45 % |
| 0,10 | 10 | 9 | 7,11 | 4,85 | +86 % | 109 échanges, +58 % |

Le seul NON perdu : Japon octobre (acheté 0,39 le 14/10, base 0,64, séisme le 25/10). 3 réglages essayés. Les premiers échanges sont
petits (1 à 129 parts, souvent 20) : la mise possible est de l'ordre de 10 à 50 $ par marché. Les gains sont plus grands que ce que la
base « attendait » (10 pour 7,96) : une partie est de la chance (2 mois, séismes rares) ; l'écart de prix, lui (5,66 payés pour 7,96
attendus), est mesuré.

**Aujourd'hui (11/11, novembre).** Japon déjà OUI (6,1 du 06/11). Carnets du NON : Pérou 0,51 part à 0,77 puis 0,92 (base 0,89) ;
Mexique 40 parts à 0,79, 264 à 0,80 (base 0,84) ; États-Unis 29 parts à 0,63 puis 0,95 (base 0,70) ; Chili 101 à 0,77 (base 0,73) ;
Indonésie 166 à 0,67 (base 0,47 : NON trop cher) ; Philippines 50 à 0,93 (base 0,76).

**Verdict : indice** (2 mois, 11 marchés, échanges minces) → fantôme `seismes_pays` (`strategies_v3.SeismesPays`, référence
`seismes_pays` posée par `seismes.attach_seismes`, demi-Kelly sur la borne basse, abstention si un séisme ≥ 5,8 vu par l'EMSC
n'est pas encore décrit par l'USGS). Pas de conviction : après rapprochement vers le milieu du marché (skill `prevoir-un-marche`),
aucun écart ne dépasse 5 points au prix vendeur.

**Limite connue (cycle local du 11/11).** La première proposition (NON « États-Unis ») a été refusée « carnet périmé » : l'horodatage
d'un carnet calme est celui de sa dernière modification (`proposals/2026-11-11_carnet_calme_juge_perime.md`). Tant qu'Etienne n'a pas
tranché, le fantôme n'achète que juste après un mouvement du carnet.

**À reprendre.** Novembre (réglé vers le 01/12) et décembre ; « How strong of an earthquake will occur worldwide by <date> »
(regardé ce jour pour novembre : 6,5+ 0,84-0,90 pour 0,88 calculé, 7,0+ 0,50-0,55 pour 0,52, 7,5+ 0,20-0,25 pour 0,24, 8,0+ 0,04-0,10 pour 0,055 : bien coté, rien) ; « How many 7.0 or above earthquakes in
2026 » : regardé ce jour, rien (46 ans de catalogue : P(0/1-3/4-6/7+ de plus d'ici le 31/12) = 0,09/0,70/0,20/0,02, années déjà
chargées 0,05/0,68/0,27/0 ; marché 0,05/0,67/0,27/0,06).
