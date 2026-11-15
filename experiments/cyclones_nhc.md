# Cyclones : prévision officielle du NHC contre les marchés d'intensité (piste n° 63, 15/11/2026) — ÉCARTÉE

Passage du chercheur du 15/11/2026 (11 h UTC). Idée neuve (jamais essayée ici : aucun mot « ouragan », « cyclone » ou
« NHC » dans `PISTES.md`) : avantage d'INFORMATION de la source du règlement. Les marchés « Will Tropical Storm X
strengthen to a hurricane? », « How strong will X be? » (catégorie de pointe, 5 tranches) et « What category will X
reach? » se règlent sur les avis publics du National Hurricane Center ; le NHC publie à chaque avis sa propre prévision
d'intensité à 120 h (OFCL). La foule de Polymarket lit-elle cette prévision moins bien qu'un modèle étalonné sur les
erreurs passées du NHC ?

## Données (toutes sans clé, `robots.txt` lus avec `scripts/robots_ok.py` avant le premier appel : permis)
- **Prévisions officielles** : fichiers ATCF « a-deck » du NHC, lignes `OFCL` (`ftp.nhc.noaa.gov/atcf/aid_public/` pour
  2026, `ftp.nhc.noaa.gov/atcf/archive/<année>/` pour 2021-2025) : 221 cyclones (Atlantique, Pacifique Est et Central),
  70 108 lignes. Avis disponible à l'heure synoptique + 3 h ; intensité de l'avis = échéance 3 h (sinon 0 h).
- **Noms** : « b-decks » (`ftp.nhc.noaa.gov/atcf/btk/`), colonne 28.
- **Marchés** : `public-search` de Gamma (événements clos, description citant le NHC) : 28 événements, dont 15 cyclones
  d'intensité utilisables (Dolly, Karina, Lowell, Norbert, Fay, Odalys, Polo ×2, Nolo, Rachel, Isaias, Simon, Trudy, Vance
  en 2026 ; Melissa 2025 ; Lee 2023), 48 marchés. Échanges réels : data-api v2 `trades?condition=` (8 313 échanges ;
  Fay et une tranche d'Isaias en 429 répété).
- Scripts : `cyclones_nhc/scripts/releve_marches.py`, `releve_echanges.py`, `analyse.py`, `reglages.py`
  (données dans `cyclones_nhc/donnees/`, ignoré par Git ; un passage suivant les relève en ≈ 3 minutes).

## Modèle (aucun regard vers le futur)
À l'instant T : dernier avis disponible ; M0 = plus forte intensité déjà annoncée, F = maximum prévu (3 à 120 h) ;
pointe finale = max(M0, F + D), D tiré des erreurs PASSÉES du NHC (3 720 avis de 2021-2025, D = pointe réelle du reste
de la vie − F, pour les avis dont F est à ±10 kt). Seuils : 64 / 83 / 96 / 113 / 137 kt (catégories 1 à 5). Rien de
2026 dans l'étalonnage. Échéance « strengthen … by <date> 11:59 PM ET » respectée.

**Contrôle du règlement : 48/48** (pointe lue dans les avis = résultat officiel de chaque marché).

## Résultats
- **Contre le marché d'abord** : 235 couples (avis, jeton OUI) avec un vrai échange 10 à 180 min après l'avis :
  log-score **modèle −0,462 contre prix −0,405** ; mélange 50/50 −0,419 : le prix est MEILLEUR que la prévision
  officielle étalonnée. La foule voit plus que l'OFCL (modèles HAFS/HWRF, images satellite entre deux avis).
- **Achats simulés** aux prix des vrais échanges, frais `weather_fees` compris, 12 réglages (seuil 0,05 / 0,10 / 0,20 /
  0,30 × parts minimales 0 / 20 / 100) :

| seuil | parts ≥ | paris | cyclones | gagnés / payés | rendement |
|---|---|---|---|---|---|
| 0,05 | 0 | 151 | 11 | 75 / 76,9 | −20,1 % |
| 0,10 | 0 | 100 | 10 | 45 / 45,4 (modèle 65,6) | −16,8 % |
| 0,10 | 20 | 63 | 10 | 30 / 26,3 | −8,1 % |
| 0,20 | 20 | 31 | 8 | 14 / 10,2 | +6,2 % |
| 0,30 | 0 | 12 | 6 | 7 / 4,5 | +73,5 % |
| 0,30 | 100 | 1 | 1 | 0 / 0,5 | −100 % |

  Le modèle annonce 65,6 victoires là où il en vient 45 (prix : 45,4) : **trop sûr de lui**. Seule la cellule
  « écart ≥ 0,30 » gagne (12 paris, 6 cyclones), meilleure de 12, et 2 de ses 7 victoires viennent d'un seul
  phénomène : le **premier échange d'un marché tout juste créé** (Polo « strengthen » ouvert à 14 h 49, échangé
  0,53 à 15 h 45 alors que l'avis de 15 h prévoyait 140 kt ; 0,98 une heure plus tard). Aucune profondeur (≥ 100 parts :
  1 pari).

## Verdict : **écartée**
Le prix bat la prévision officielle étalonnée ; les achats simulés perdent à tous les seuils sauf une cellule de 12 paris
choisie parmi 12. Pas de fantôme (saison terminée dans l'Atlantique et le Pacifique Est jusqu'au 15/05/2027 de toute façon).

**À relire seulement si** : (1) en mai-juin 2027, l'idée étroite « premier échange d'un marché de cyclone qui vient
d'ouvrir contre l'avis du NHC » sur une nouvelle saison (2 cas sur 15 cette année : trop peu) ; (2) les typhons du
Pacifique Ouest (« How strong will Koguma / Choi-wan / Champi be? ») si leur source (JTWC ou JMA) publie aussi des
prévisions archivées.

## Lecture des marchés ouverts (même passage, sans conviction)
« When will the next Atlantic or Pacific hurricane form? » (événement 1302670) : avis du NHC du 15/11 (05 h UTC) « formation
not expected during the next 7 days » dans les trois bassins. HURDAT2 (Atlantique 1851-2025, Pacifique 1949-2025),
1971-2025 : un ouragan (première intensité HU) entre le 22 et le 30/11 dans 6 années sur 55 (1980, 1982, 1998, 2001,
2015, 2016) ; Otto 2016 (né le 20/11) et Iwa 1982 (né le 19/11) auraient déjà figuré dans un avis à 7 jours → ≈ 4-5/55.
P(« No hurricane by November 30 ») ≈ 0,91-0,93, ≈ 0,90 après rapprochement vers le prix (0,875), pour un vendeur à
0,90 : rien. Atterrissages d'ouragan aux États-Unis après le 15/11 depuis 1851 : Kate 1985 seulement ; les NON par
État (vendeurs 0,95-0,997) rapportent 0,3 à 2,8 % en 3 semaines : billets de favori, pas d'avantage à prendre.
