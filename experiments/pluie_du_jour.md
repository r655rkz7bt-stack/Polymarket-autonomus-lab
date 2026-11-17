# Piste n° 69 : « Where will it rain on <date>? » — le METAR avant le marché (17/11/2026, passage de 11 h)

**Idée** (avantage d'information, famille (1) « lire la source avant le marché ») : chaque jour, Polymarket ouvre un événement de 10
à 17 marchés « Will it rain in <ville> on <date>? », réglés sur la ligne PRECIPITATION du rapport climatologique quotidien de la NWS
(CLI) de la station de la ville (`issuedby=` du lien de règlement : LAX, IAH, DFW, PHX, PHL, DCA, ATL, MIA, MSY, SFO, puis NYC, MDW,
SEA, BOS, DEN). Le jour est le « jour climatique » : minuit-minuit en heure LOCALE STANDARD. Les METAR horaires (groupe de
précipitation `p01i`) disent pendant la journée s'il a déjà plu ≥ 0,01 pouce. Le marché suit-il ces relevés ?

**Règle à retenir** : « trace » ne compte pas ; un CLI qui publie « M » (manquant) compte **0,00 → NON**, même s'il a plu.

## Données (scripts dans `experiments/pluie_du_jour/`, données dans `donnees/`, ignoré par Git)

- `releve.py` : 95 événements (`public-search`, 09/06 → 17/11/2026), 1 283 marchés, 16 900 vrais échanges (data-api v2,
  `trades?event_id=`), en 7 s.
- `releve_iem.py` : METAR (rapports de routine ET spéciaux, `p01i`, trace = « T ») et CLI de 2026 des 15 stations, sur l'Iowa
  Environmental Mesonet (`mesonet.agron.iastate.edu/cgi-bin/request/asos.py` et `/json/cli.py` : robots.txt **permis**), 1 min.
  `api.weather.gov` est **INTERDIT** par son robots.txt (vérifié avec `robots_ok.py`) ; la page `forecast.weather.gov/product.php?…&product=CLI`
  est permise.
- **Contrôle du règlement** : CLI ≥ 0,01 = prix final Gamma **1 213 / 1 213**.

## Côté OUI : METAR ≥ 0,01 pouce dans le jour, achat au premier vrai « Yes / BUY » après (+10 min) — `analyse.py`

- 291 marchés où un METAR du jour a mesuré ≥ 0,01 : **288 réglés OUI**. Les 3 autres : Phoenix les 30 et 31/10 (0,10 pouce au
  METAR, CLI « M » → NON ; au 31/10, le NON s'est vendu 0,58 à 08 h 40 UTC, une minute après la publication du CLI, puis 0,98 à
  08 h 43 : quelqu'un lit le CLI à la minute ; d'autres achetaient encore le OUI à 0,50-0,80 jusqu'à 09 h 28).
- Achats : 283 ; gagnés 281 pour 277,4 attendus, +6,9 % porté par des billets minuscules ; **≥ 20 parts : 220 paris, +0,7 %** ;
  prix < 0,97 et ≥ 20 parts : 14 paris, 14 gagnés pour 12,4 attendus (z ≈ 1,3). **Le marché lit déjà les METAR** : le prix du OUI
  passe à 0,97-0,99 avant que le METAR ne soit diffusé.

## Côté NON : aucun METAR ≥ 0,01 jusqu'à H heures de la fin du jour, achat au premier « No / BUY » dans l'heure — `analyse_non.py`

| H avant la fin | ≥ 20 parts | < 0,97 et ≥ 20 parts | 0,90-0,97 (≥ 20 parts) |
|---|---|---|---|
| 8 h | 45 paris, +25,8 % | 30, +38,2 % (23 gagnés pour 21,9) | 8, −5,6 % (z −0,6) |
| 6 h | 54, +20,5 % | 24, +44,8 % (20 pour 16,9) | 8, −6,5 % (z −0,6) |
| 4 h | 67, +22,0 % | 33, +43,5 % (31 pour 27,5) | 19, −0,2 % (z −0,0) |
| 3 h | 85, +1,7 % | 31, +6,4 % (28 pour 26,1) | 19, +5,9 % (z +1,1) |
| 1 h, 0 h, après la fin | ≈ 0 | −9 à +4 % | — |

Tout le « gain » vient de **4 à 6 NON achetés sous 0,50** (pluie annoncée qui n'est pas venue : +160 à +305 % chacun) ; la tranche
où se ferait l'essentiel des achats (0,90-0,97) rend ≈ 0 ; ≈ 45 cases essayées (5 délais × 5 filtres côté NON, 6 côté OUI,
fenêtres de 1 à 48 h), meilleur z 2,06 sur 4 paris.

## Verdict : **écartée**

Le marché suit les METAR heure par heure (côté OUI) et le pari « il ne pleuvra plus ce soir » ne bat ses prix que par quelques
billets. Rien dans l'arène. À relire seulement si une source plus rapide que le METAR horaire apparaît (radar, pluviomètres
à la minute), ou pour les CLI « M » (lecture à la minute : hors de notre cycle de 5 minutes, piste « vitesse » écartée).
