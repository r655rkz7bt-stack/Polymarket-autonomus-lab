# Champions de saison, Polymarket contre Pinnacle (piste 1, 25/10/2026 nuit)

Question : les marchés « qui sera champion » (NBA, NFL, NHL) s'écartent-ils assez des cotes de Pinnacle (The Odds API, source `odds_outrights`, déjà dans le cycle) pour acheter l'écart ?

## Défaut trouvé en chemin (famille 3 : la donnée n'est pas celle qu'on croit)
`references.attach_outrights` ne rattachait que **30 marchés sur 94** (la NBA) : Polymarket écrit « Will the Buffalo Bills win the 2027 **NFL league championship**? » (plus « Super Bowl ») et « Will the Edmonton Oilers **be named** the 2026-27 NHL Stanley Cup Champion? » (plus « win »), donc `CHAMPION` et `WILL_WIN` ne reconnaissaient ni l'un ni l'autre. `futurs_bookmakers` n'a jamais pu voir le football américain ni le hockey (0 opération en 5,4 jours, éliminée). Corrigé (`CHAMPION`, `WILL_WIN`), test sur les trois libellés réels et sur un marché de finale de conférence (refusé) : `tests/test_references.py`.

## Photo du jour (`experiments/futurs_pinnacle/photo_25_10.py`, 94 marchés rattachés, cotes de Pinnacle vues le 24/10 13 h 26)
| cote Pinnacle | marchés | prix − cote (moyenne) | plus gros écart |
|---|---|---|---|
| < 2 % | 49 | +0,08 pt | 1,3 pt |
| 2-5 % | 22 | +0,07 pt | 2,3 pt |
| 5-10 % | 20 | +0,26 pt | 3,7 pt |
| 10-25 % | 3 | +0,49 pt | 2,0 pt |

Polymarket et Pinnacle sont d'accord à 0,1-0,5 point près en moyenne ; les plus gros écarts (76ers 0,123 contre 0,087, Oilers 0,115 contre 0,082, Bills 0,125 contre 0,098) sont du côté « Polymarket plus cher » : l'achat serait le NON, à 0,88-0,92, pour 3 à 3,5 points d'écart avant marge (2 points) et frais.

## Verdict : écartée (économie), pas de nouveau fantôme
- Ces marchés se règlent en **avril à juillet 2027** : un euro y est bloqué 5 à 8 mois pour au plus 1,5 point net sur les écarts les plus gros, soit 0,2 % par mois, contre 1-2 % **par jour** pour les paris de match de l'arène. Même si Pinnacle a raison, le capital immobilisé coûte plus que l'écart ne rapporte.
- Pas d'historique de cotes gratuit : aucun test sur le passé possible, seulement un fantôme. `futurs_bookmakers` (éliminée) n'est pas relancée ; si Etienne veut quand même regarder, la correction des libellés suffit pour qu'un `futurs_bookmakers` v1.1.0 voie les 94 équipes (il faudrait aussi une étiquette `tag_pages` pour les champions, la plupart ne sont pas dans les pages normales du scanner).
