# Inventaire des sources officielles citées par les marchés ouverts (12/11/2026, piste n° 32)

Script : `experiments/sources_officielles/inventaire.py` (Gamma `/events/keyset`, 19 256 événements ouverts lus en ≈ 3 min ;
10 553 citent un domaine dans leur règle). Relevé : `sources_officielles/releves/inventaire_2026-11-12.json.gz`. But : trouver
d'autres « compteurs officiels à lecture directe » (comme la rougeole, les séismes, la sécheresse, les tornades), que le
marché ne lit peut-être pas.

## Déjà étudiés au labo

aviationweather.gov / weather.gov.hk (températures), earthquake.usgs.gov (séismes), ncei.noaa.gov (tornades), portwatch.imf.org
(détroits), data.giss.nasa.gov (température mondiale), waterservices.usgs.gov et data.usbr.gov (Mississippi, lacs Mead et
Powell), mesonet (première neige, Mont Washington), cdc.gov (rougeole), bls.gov (CPI, emploi), federalreserve.gov, status.openai.com,
apps.apple.com (App Store), open.spotify.com et newsroom.spotify.com (Spotify), billboard.com (piste n° 31), the-numbers.com et
boxofficemojo.com (box-office).

## Jamais essayés (à trier, liquidité du 12/11)

| source | marchés | liquidité | remarque |
|---|---|---|---|
| weather.gov, metoffice.gov.uk, bom.gov.au, HKO | « Precipitation in NYC / Seattle / London / Hong Kong / Seoul in November? », « NYC November 12 to 15 » | 1-4 k$ chacun | cumul du mois déjà à moitié observé : même mécanisme que les tornades ; fréquence de base par station (NOAA GHCN, gratuit) |
| status.claude.com | « Will Claude go down on __ days in November 2026? » | 12,8 k$ | page de statut (piste n° 13 : OpenAI déjà aligné) |
| nyc.gov | « How many West Nile neuroinvasive disease cases » (NYC) | 13 k$ | compteur de santé publique, saison finie en novembre |
| cdc.gov | « How many US births in 2026? » | — | statistiques provisoires trimestrielles (NCHS) |
| data.sca.isr.umich.edu | « University of Michigan Consumer Sentiment - November » | 20 k$ | chiffre préliminaire publié avant le final |
| indec.gob.ar | « Argentina Monthly Inflation - October » (12/11) | 4 k$ | regardé ce passage : CABA 1,9 % le 06/11, consultants « près de 2 % », marché 1,9-2,1 à 0,52 : rien à prendre |
| cneos.jpl.nasa.gov | « Major meteor strike (10kt+) in 2026? » | 37 k$ | fréquence de base des bolides (catalogue CNEOS public) |
| cpc.ncep.noaa.gov | « peak RONI 2026-27 El Niño » | 9 k$ | prévisions officielles mensuelles |
| tidesandcurrents.noaa.gov | « Highest sea level in San Diego this winter » | 5 k$ | déjà vu le 11/11 (anomalie dans les prix) |
| ecb.europa.eu, ons.gov.uk, statcan, ibge, stat.go.jp | inflation et PIB d'autres pays | 10-120 k$ | même famille que le CPI américain (écarté) |
| treasurydirect.gov | « Peak US National Debt before 2027? » | 4 k$ | « Debt to the Penny » publié chaque jour ouvré |

Ordre conseillé pour les prochains passages : précipitations du mois (5 villes, mécanisme connu, données gratuites, marchés
récurrents chaque mois → test sur le passé possible avec les mois réglés), puis West Nile et dette publique (compteurs
quotidiens ou hebdomadaires).

## « Will Claude go down on __ days in November 2026? » (même passage, `statut_claude/uptime.py`)

Règle : nombre de jours de novembre dont la case du composant claude.ai sur `status.claude.com/uptime` n'est pas verte. Le
calendrier est embarqué dans la page (`UptimeCalendar`, sans clé ; `?page=N` pour remonter, décembre 2024 → aujourd'hui,
relevé dans `statut_claude/releves/jours.json`). Novembre : **0 jour non vert sur les 11 finalisés** (le 08/11 « Degraded
performance for Claude Fable 5.1 » est resté vert). Jours non verts par mois : 2 à 14 (2026 : 2, 10, 14, 14, 11, 7, 12, 7, 6, 6).
Du 12 à la fin du mois, ≥ 5 jours non verts : 12 mois sur 22 (0,55) ; 2 sur 5 quand les 11 premiers jours en ont ≤ 1 ;
0 sur 3 quand ils en ont 0 ; 1 sur 3 sur les trois derniers mois ; rythme depuis septembre 0,167 par jour → ≈ 0,25 avec dispersion.
Marché : « < 5 » 0,74, « 5-7 » 0,215, « 8+ » ≈ 0,02 (≥ 5 ≈ 0,24-0,26). Médiane de mes estimations ≈ 0,33, rapprochée → 0,30 :
**le marché est juste, pas de conviction**.

## « How many West Nile neuroinvasive disease cases … New York City … 2026? » (même passage)

Page de la ville (`nyc.gov/site/doh/health/health-topics/west-nile-virus-reports.page`, lue le 12/11) : **35 cas neuro-invasifs**
(Bronx 3, Brooklyn 11, Manhattan 6, Queens 9, Staten Island 6), saison des moustiques finie. Règle : compte affiché au 01/01/2027
puis révisions jusqu'au 31/03/2027. Marché : « 35-49 » 0,892 (vendeur 0,902), « 50 ou plus » 0,072, « 20-34 » 0,01. Le compte est
PILE sur la borne : une seule requalification à la baisse le ferait passer à « 20-34 » ; d'habitude les comptes montent avec les
déclarations tardives. Ma chance pour « 35-49 » ≈ 0,96, rapprochée → 0,93, borne basse ≈ 0,90 pour un vendeur à 0,902 : sous le
seuil, pas de conviction. À relire en janvier (révisions) ; historique des révisions des années passées à chercher.

## Bolides (CNEOS) : « 5kt / 10kt+ / 100kt / 1 megaton meteor strike in 2026? » (même passage)

API publique `ssd-api.jpl.nasa.gov/fireball.api` (sans clé, 1 074 bolides depuis 1988). 2005-2025 : **18 bolides ≥ 5 kt (13 années
sur 21 en ont au moins un), 9 ≥ 10 kt** (aucun depuis 2020), 1 ≥ 100 kt (Tcheliabinsk 2013). 2026 : 24 bolides, le plus fort 1,1 kt
(30/05) ; **dernier ajout daté du 04/10** (le catalogue arrive avec des semaines de retard : un bolide du 05/10 au 11/11 peut encore
y entrer, la règle attend jusqu'au 28/02/2027). Fenêtre encore ouverte ≈ 50 jours à venir + 38 jours non publiés (pondérés 0,7).
- « 5 kt » : 0,87 par an → ≈ 0,15-0,17 ; marché 0,075 (vendeur 0,10, 716 $). Rapproché de moitié 0,11, borne basse ≈ 0,08 < 0,10.
- « 10 kt+ » : 0,43 par an (0,27 depuis 2011) → ≈ 0,055-0,09 ; marché 0,03 (vendeur 0,033, 13,8 k$). Rapproché ≈ 0,05 : +2 points.
Le marché cote ces seuils à environ la moitié de la fréquence de base, mais l'écart reste sous le seuil d'une conviction :
**noté, pas de conviction**. À revoir en décembre si le catalogue n'a toujours rien publié après le 04/10 (marchés de 2027 :
la même fréquence de base sur une année entière).

## « Peak US National Debt before 2027? » (même passage)

Debt to the Penny (`api.fiscaldata.treasury.gov/.../debt_to_penny`, sans clé) : 40,560 T$ le 09/11/2026 ; « 41 T$ » demande
+0,44 T$ (+1,08 %) d'ici le 31/12. Même période (09/11 → 31/12) les années sans plafond de la dette ni choc : 2016 +0,92 %, 2018
+1,11 %, 2019 +0,85 %, 2022 +0,56 %, 2023 +0,89 %, 2024 +0,76 %, 2025 +1,04 % (1 sur 7 au-dessus de 1,08 %) ; mais le rythme
d'août-novembre 2026 (8,5 Md$ par jour ouvré, ≈ +0,44 T$ en 52 jours) tombe pile sur le seuil. Plafond légal de 2025 : 41,1 T$.
Ma chance ≈ 0,35 contre 0,64 au milieu (carnet 0,45/0,83, 883 $) ; rapprochée de moitié → 0,50, NON vendu 0,55 : pas de conviction.
