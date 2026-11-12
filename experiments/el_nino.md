# Piste n° 39 : El Niño 2026-27, les chances du CPC contre les marchés « peak RONI » (12/11/2026, passage de 11 h)

**Marchés** (étiquette `weather-science` 104180, `weather_fees`) : « What will the peak RONI be for the 2026–27 El Niño? »
(événement 867162, 179 k$ de volume ; tranches < 1,5 / 1,5-2,0 / 2,0-2,25 / 2,25-2,5 / ≥ 2,5), « Will the 2026–27 El Niño be the
strongest on record? » (1023298, > 2,40 = record de DJF 1982-83), « Super El Niño » (≥ 2,0, déjà réglé OUI). Règle : pic des
**premières** valeurs publiées par le CPC pour ASO, SON, OND, NDJ, DJF ; valeurs au dixième sur la page du règlement (2 décimales dans
`RONI.ascii.txt`) : « ≥ 2,5 » et « > 2,40 » sont donc le même événement, aux cas limites 2,41-2,49 près (ASCII contre tableau).

**Sources** (sans clé, `robots.txt` du CPC sans interdiction) : `cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt` (RONI, ERSSTv6),
`wksst9120.for` (Niño 3.4 hebdomadaire OISST, anomalie absolue), discussion mensuelle `enso_advisory/ensodisc.shtml` (2e jeudi),
mise à jour du lundi `lanina/enso_evolution-status-fcsts-web.pdf`. Copies : `el_nino/releves/`.

## Où en est-on (12/11/2026, 11 h UTC)

- RONI 2026 : MJJ 0,97, JJA 1,36, JAS 1,69, **ASO 1,97** (« 2,0 » au tableau) ; SON sort vers le 05/12.
- Niño 3.4 hebdomadaire (absolu) : 2,98 en septembre, 3,30 en octobre, 3,3 le 04/11 (plat) ; **relatif** (PDF du 09/11) : 2,3.
  L'écart RONI − OISST s'est creusé de −0,5 (avril-juin) à −0,98 (ASO) : les tropiques se réchauffent avec El Niño, la RONI monte moins
  vite que l'anomalie absolue. Chaleur de subsurface **en légère baisse depuis mi-octobre** (CPC).
- Discussion du CPC du **08/10** : « +2,5 ou plus pour une RONI de 3 mois : 54 % pour SON, 83 % pour OND, 70 % pour NDJ ». La suivante
  sort **aujourd'hui** (12/11, vers 14 h UTC).
- Marché : « ≥ 2,5 » 0,61 (0,58/0,64), « record » 0,63 (0,61/0,65), « 2,25-2,5 » 0,32, « 2,0-2,25 » 0,05.

## Analogues (`el_nino/scripts/analogues.py`)

Années où ASO ≥ 1,0 : hausse du pic (SON à DJF) au-dessus d'ASO : 1957 +0,75, 1965 +0,23, 1972 +0,33, 1982 +0,76, 1991 +1,11,
1997 +0,21, 2015 +0,45, 2023 +0,38. Depuis un ASO ≥ 1,5 : +0,23, +0,33, +0,76, +0,21, +0,45 (une fois sur cinq ≥ +0,5). Il faut ici
+0,48 au moins (2,45 arrondi à 2,5). Avec l'indice relatif à 2,3 : SON ≈ 2,2 ; OND ≥ 2,45 demande novembre + décembre ≈ 2,55 en moyenne
(+0,25 sur le niveau d'aujourd'hui), NDJ ≈ 2,45 si la hausse continue à +0,1 par mois : **à la limite**.

Mes cinq estimations de P(pic ≥ 2,5) : analogues 0,30 ; relation RONI-OISST 0,35 ; CPC du 08/10 décalé de la trajectoire manquée
(SON ≈ 2,2 au lieu de ≈ 2,5) 0,50 ; subsurface en baisse 0,25 ; hausse continue de +0,1 par mois 0,55 → **médiane 0,35**, rapprochée
de moitié du prix (0,61) : 0,48. Côté NON « ≥ 2,5 » : 0,52, borne basse ≈ 0,45, vendeur 0,42 : **sous le seuil d'une conviction**
(et la discussion du jour peut tout changer).

## Les discussions passées du CPC contre le prix (`el_nino/scripts/discussions.py`, archives `enso_disc_<mois><année>`)

| Discussion | Chance CPC « ≥ 2,5 » (RONI) | Prix de « 2.5 or above » ensuite |
|---|---|---|
| 13/08/2026 | 69 % pour OND | 0,42 le 20/08, 0,62 le 01/09 (**0,27 sous la borne une semaine après**) |
| 10/09/2026 | 75 % pour OND | 0,67 le 11/09, 0,70 le 18/09, 0,76 le 01/10 |
| 08/10/2026 | 54 % SON, 83 % OND, 70 % NDJ | 0,82 le 09/10, 0,79 le 15/10, 0,68 le 22/10, 0,73 le 05/11, **0,61 le 12/11** (après la RONI d'ASO à 2,0) |

Le marché a mis 3 semaines à rejoindre la discussion d'août, quelques jours celle de septembre, un jour celle d'octobre. Depuis la
RONI d'ASO, il s'en écarte de lui-même (0,61 contre 0,83). Calibration : en 2023 (Niño-3.4 classique, pas la RONI), le CPC donnait
75-85 % à « ≥ 1,5 » et 35 puis 54 % à « ≥ 2,0 » pour NDJ ; pic ONI 2,0 : juste, sur un seul épisode. Le lecteur `enso.parse_discussion`
lit les deux tournures de 2026 (« the chance is N% for … » et « During the … season, there is a N% chance … »), prend la borne basse
d'une fourchette (« 75-85% ») et ignore toute chance qui ne parle pas de la RONI.

## Ce qui est lancé

**Fantôme `el_nino_cpc`** (expérience audacieuse, Kelly entier, `enso.py`) : la seule chose PROUVÉE par les chances du CPC est une
borne basse : P(pic ≥ T) ≥ max des saisons de P(saison ≥ T). Il achète le OUI des tranches ≥ T (et du record) quand le vendeur
demande moins que cette borne − 0,05 − frais, ou le NON des tranches sous T de la même façon ; jamais l'autre côté. Une discussion
de plus de 7 jours est ignorée (le 12/11 au matin, celle du 08/10 l'est : la RONI d'ASO est sortie sous la trajectoire qu'elle
supposait). Le journal `enso:histo` garde chaque discussion telle que lue. Aucun test sur le passé possible (une seule saison de
marchés RONI) ; c'est une expérience : une perte apprendrait que le CPC surestime la force d'El Niño et que le marché a raison de
l'escompter.

## Reste ouvert

- Lire la discussion du 12/11 (vers 14 h UTC) au passage de 16 h 54 : chances pour SON, OND, NDJ ; comparer au prix.
- RONI de SON vers le 05/12.
