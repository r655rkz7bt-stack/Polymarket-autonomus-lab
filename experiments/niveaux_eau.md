# Niveaux des fleuves : la prévision officielle contre le prix (piste n° 25, 11/11/2026)

Passage du chercheur du 11/11/2026, 15 h 54 UTC. Idée « radicalement différente » demandée par la feuille de mission : nouvelle
source (services hydrologiques officiels), nouveau type de marché (niveaux de fleuves européens), avantage d'INFORMATION.

## Les marchés

Relevé `public-search` (`scripts/releve_evenements.py`, mots « Mississippi », « Lake Mead », « Rhine », « Danube », « river level »…) :
11 événements de niveaux d'eau seulement, dont 3 réglés.

| Événement | Fin | Volume | Source de règlement |
|---|---|---|---|
| When will the Rhine River return to normal levels? (1284739) | 01/01/2027 | 21 k$ | Kaub (25700100) ≥ 77 cm, PegelOnline, heure de Berlin |
| When will the Danube River return to normal levels? (1301594) | 02/01/2027 | 8 k$ | Budapest (HU442027) ≥ 93 cm, DanubeHIS, heure de l'Est |
| Lowest Mississippi level at St. Louis / Baton Rouge by November 30? | 02/12 | 118 / 80 k$ | USGS (piste n° 23) |
| Lowest Great Salt Lake elevation in 2026? | 02/01/2027 | 61 k$ | USGS (étudié le 11/11 à 11 h) |
| How low will Lake Mead / Lake Powell drop? | 16/04/2027 | 15 / 94 k$ | USBR, minimum quotidien jusqu'au 31/03/2027 |
| Highest sea level in San Diego this winter? | 01/04/2027 | 15 k$ | NOAA CO-OPS 9410230 (La Jolla), valeurs vérifiées |
| Réglés : Rhin (2, août-octobre), Danube (1, août-octobre) | | 115-188 k$ | Rhin : retour avant le 01/09 (événement d'août), aucun retour en septembre-octobre ; Danube : aucun retour avant le 01/11 |

Règles lues mot à mot : une seule lecture au-dessus du seuil suffit (« transient spikes count ») ; la tranche est celle de la date de
la première lecture, dans le fuseau du marché (Berlin pour le Rhin, heure de l'Est pour le Danube : « before November 15 » finit le
15/11 à 06 h à Budapest).

## La source que le marché ne lit pas : la prévision officielle

- **Kaub** : PegelOnline publie, sans clé, la prévision WSV/BfG (`stations/KAUB/WV/measurements.json`, pas de 2 h, ~4 jours,
  « forecast » puis « estimate »). Les stations amont (Maxau, Mannheim, Worms, Mainz) n'ont que la série observée `W`.
- **Budapest** : l'OVF (service hydrologique hongrois) publie chaque matin vers 08 h 30 un tableau de prévision à 6 jours, avec une
  marge « ± » par jour, pour toutes les stations hongroises (`hydroinfo.hu/tables/ENG/dunelotH.html`, page publique sans protection).
  DanubeHIS (`danubehis.org/results/HU442027_HYDRO`) donne les lectures horaires (règlement) ; même zéro que l'OVF (36 cm le 11/11 au matin).

### Le 11/11/2026 vers 16 h UTC (relevé : `niveaux_eau/releve_2026-11-11.json`, tableau OVF : `donnees/`, non versionné)

| | Rhin à Kaub | Danube à Budapest |
|---|---|---|
| Niveau | 16-17 cm (seuil 77) | 35 cm (seuil 93) |
| Amont | vague en route : Maxau 295 → 376 cm, Mannheim 68 → 113, Worms −14 → 22, Mainz 112 → 128 ; Bâle plat (~500) | Linz plat (~350) ; Hofkirchen +16 cm ; l'OVF annonce une crue de l'Ipoly (Ipolytarnóc 262 cm le 13/11) |
| Prévision officielle | culmine à **69 cm** le 14/11 (émise le 11/11 à 07 h, heure de Berlin) | **64 ± 13** le 14/11 à 7 h, **124 ± 17** le 15/11 à 7 h, 167 le 16/11 (émise à 08 h 28) |
| Marché « avant le 15/11 » | OUI 0,655 (0,42 à 11 h UTC, petits échanges de 20-90 parts) | OUI 0,26 (vendeur 0,292, 260 parts) ; « 15-30/11 » à 0,65 |
| Chance calculée (`fleuves.p_first_crossing`) | **0,39** (0,36-0,40 selon 4 réglages) | **0,76** (0,65-0,96 selon le retard supposé de la vague) |

Analogue pour le Rhin : la vague du 25-28/10 (Maxau 355, Mannheim 121, Worms 36, Mainz 157) a donné 60 cm à Kaub. Relation lue sur
31 jours : Kaub ≈ Mainz − 97 cm (décalé d'une demi-journée) ; il faudrait Mainz ≈ 174 cm.

## Modèle (`src/polymarket_agent/fleuves.py`)

Niveau simulé = prévision décalée d'un retard commun (écart-type 0,15 × horizon) + erreur commune (écart-type = la marge publiée par
l'OVF, sinon 3 cm + 0,25 cm par heure d'horizon pour Kaub) + 2 cm de pointe d'une lecture de 15 minutes ; 2 000 tirages, graine fixe.
Chance de la tranche = part des tirages dont le PREMIER passage tombe dans la tranche. Seules les tranches qui finissent avant la fin
de la prévision sont chiffrées. Pas de référence si la prévision a plus de 36 h ou si le seuil est déjà atteint.
Réglages regardés : 4 (pointe 0 ou 2 cm, retard 0 / 0,15 / 0,30) ; non étalonné (aucune prévision archivée).

## Verdict

**Pas de test sur le passé possible** : les prévisions ne sont pas archivées (PegelOnline ne garde que la dernière, l'OVF aussi) et
3 événements seulement sont réglés. Ce qui est fait :
1. **Deux convictions** (`config/convictions.yaml`, méthode `prevoir-un-marche`, date limite le jour même) : Rhin NON (0,52, borne
   0,45, vendeur 0,37) et Danube OUI (0,455, borne 0,40, vendeur 0,292), après rapprochement de moitié vers le prix.
2. **Fantôme `fleuves_prevision`** (expérience audacieuse, demi-Kelly sur chance − 0,10) et **source `fleuves`** (toutes les heures) :
   le journal `ref:fleuves` de la base garde chaque prévision émise ; dans 1-2 mois, comparer prévision et niveau réel (marge
   tenue ?) et le prix de chaque tranche à la chance calculée, avant d'élargir.
Résultat des deux tranches « avant le 15/11 » : connu le 15/11 (Kaub à minuit à Berlin, Budapest à 06 h).

## À reprendre
- Lire les deux tranches le 15/11 : le Rhin a-t-il dépassé 77 cm, quand Budapest a-t-il passé 93 cm ? (DanubeHIS, PegelOnline)
- Lac Mead / Powell : le « 24-Month Study » de l'USBR (projection officielle mensuelle) contre « 1 028-1 033 ft » à 0,47 ; San Diego :
  la marée astronomique prévue de l'hiver (NOAA) contre les seuils 8,1-8,3 ft.
- Si la prévision OVF se révèle bonne : d'autres stations (Mohács, Baja) n'ont pas de marché ; rester sur les marchés existants.
