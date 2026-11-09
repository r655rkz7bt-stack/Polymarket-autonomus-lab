# 2026-11-09 (nuit) — la perte de `seismes_marche` et le silence de `suivre_inities` (famille 4 puis 6)

Contrôle à la main (jour 9, 9 mod 6 + 1 = famille 4), sans « Enquête obligatoire » dans la feuille de mission.

## 1. `seismes_marche` : seule perte du labo v2 (−27,4 €)
- Achat de « Oui » sur « plus grand séisme du 07/11 : 5,5 à 5,6 » à 0,91, estimé 0,9655, le 07/11 à 22 h 51 UTC (il restait 69 minutes dans le jour UTC).
- Catalogue USGS du 07/11 : 5,5 (11 h 07), 5,5 (16 h 04), puis **5,8 à 23 h 17** (dorsale médio-atlantique) : le marché s'est réglé sur « 5,7 à 5,8 ».
- Lecture : le règlement est conforme (USGS, jour UTC, magnitude arrondie), le filtre de temps est bon (aucun séisme ≥ 5,7 avant l'achat). Un séisme ≥ 5,7 en 69 minutes arrive environ 1 fois sur 70 à 100 : 0,9655 est une estimation un peu haute mais plausible, 0,91 payé laisse peu de marge. **Pas de défaut de code, une malchance de ~1,5 %.** Une seule opération clôturée : aucune conclusion statistique.
- Remarque : la marge nette était 0,051 pour une perte possible de 0,91 ; si la stratégie perd encore à ce prix, relever `min_net_edge` pour les achats de fin de journée (< 3 h restantes).

## 2. `suivre_inities` : 0 achat, « raison non notée »
- 169 marchés vus, 0 proposition. Source `inities` : « ok (0 prix relevés) », `soupcons` : « ok (38 prix relevés) ».
- Cause : la stratégie ne se déclenche que s'il existe une référence `inities` (compte neuf et concentré ET soupçon public) : aucun groupe de ce type n'existe aujourd'hui. C'est le comportement voulu (rare, expérience), pas une panne de source.
- Pas de correctif.

## Autres constats
- `gdelt` indisponible (ReadTimeout), `gemini` en pause (budget horaire) : sans effet sur les stratégies v2 actives.
- Bitcoin « dip to 72 500 en novembre » : cours 75 170, vol réalisée 38 %/an, probabilité de toucher (mouvement brownien sans dérive, 21 jours) ≈ 0,69 pour 0,665 au marché : aucun écart, aucune conviction.
