# Billboard 200 : la prévision « Chart Preview » de HITS Daily Double contre le marché (12/11/2026, piste n° 31, écartée)

Passage du chercheur de 1 h (12/11/2026). Idée : le n° 1 du Billboard 200 (« Billboard 200 #1 Album Week of <samedi X> »,
classement de la semaine de suivi du vendredi X-15 au jeudi X-9, annoncé le dimanche X-6, marché réglé le mardi X-4) est
prévu dès le mardi X-11 par HITS Daily Double (`hitsdailydouble.com/news/charts/chart-preview-…`, sans clé ; le 10/11/2026 :
« FRESH is projected to edge out O-Rod for #1 »). Le marché est-il lent à lire cette prévision ?

## Test (`experiments/billboard_hdd/scripts/`)

- `releve_evenements.py` : 39 événements Gamma (janvier → novembre 2026 ; 3 sans gagnant lisible, 1 encore ouvert).
- `prix_meneur.py` : prix du meneur du marché (milieu horaire du CLOB) à trois instants et issue.

| instant | meneurs | gagnés | attendus (prix) | prix moyen | rendement par mise si on achète le meneur au milieu |
|---|---|---|---|---|---|
| mardi X-11, 22 h UTC (après la prévision HITS) | 28 | 24 | 23,9 | 0,854 | −6,3 % |
| jeudi X-9, 22 h UTC (fin de la semaine de suivi) | 36 | 32 | 32,1 | 0,891 | −5,9 % |
| samedi X-7, 12 h UTC (veille de l'annonce) | 37 | 34 | 33,9 | 0,916 | −5,3 % |

Sans l'événement encore ouvert (semaine du 21/11) : mardi 23 gagnés sur 27 pour 22,9 attendus. Les 4 meneurs perdants du mardi
étaient cotés 0,02-0,63 (P1Harmony, Maid of Honor, Queens of the Stone Age, Olivia Rodrigo) : le prix disait déjà le doute.

## Verdict : écartée

Le meneur du mardi soir est payé exactement sa chance (24 pour 23,9) : le marché lit la prévision de HITS le jour même (le
10/11 : FRESH à 0,96 dès le mardi soir). Pas d'avantage d'information à prendre ; le rendement négatif est l'écart achat-vente.
Même conclusion que `familles_tranches.md` (favori −9 % à 0 %) avec, cette fois, l'instant où l'information est publique.
Un réglage (3 instants) ; aucun fantôme.
