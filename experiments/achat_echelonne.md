# Achat échelonné et autres façons d'entrer et de sortir (20/10/2026)

**Demande d'Etienne** : « acheter un petit bout, attendre, racheter un peu… pour minimiser les
pertes ; trouver des stratégies similaires et créer des stratégies autour, ou des filles ».
Scripts : `experiments/achat_echelonne/` (données dans `donnees/`, non versionnées).

## Ce que dit la recherche (études lues le 20/10, liens dans le compte rendu de session)
- Sur un marché « juste » (le prix est la meilleure estimation à chaque instant), **aucune règle
  d'entrée ou de sortie ne change le gain espéré** : elle change la forme des résultats et ajoute
  des coûts (écart achat-vente et frais à chaque passage). Achat en une fois contre achat en 3 fois :
  l'achat en une fois gagne 68 % du temps sur les actions (Vanguard 2023).
- Un stop-loss n'aide que s'il y a du **momentum** (Kaminski & Lo) ; renforcer en baisse n'aide que
  s'il y a **sur-réaction** puis retour.
- Polymarket sport : pas de biais favori-outsider global, favoris ≥ 0,90 à −0,23 % avant frais
  (Cardozo & Rivero-Wildemauwe 2026) ; sur Kalshi, les preneurs perdent nettement plus que ceux
  qui posent leurs ordres (Bürgi, Deng & Whelan).

## Test 1 — nos 386 vrais paris « favori » (15-20/10), chemin de prix minute par minute
Frais 0,04·p·(1−p), écart 1 centime. Rendement par euro misé :

| Façon de faire | Rendement | Écart avec l'achat d'un coup |
|---|---|---|
| Achat d'un coup (ce qu'on fait) | −3,5 % | — |
| Échelonné : 3 tranches à 30 min d'écart | −2,0 % | +1,5 point |
| Échelonné : 3 tranches à 2 h / 6 h d'écart | −3,1 % / −3,7 % | ≈ 0 |
| Moitié + moitié si le prix baisse de 10 / 20 points | +0,7 % / +2,1 % | +4,2 / +5,6 points |
| Moitié + moitié si le prix monte de 3 points | −6,0 % | −2,6 points |
| Stop-loss à −10 / −20 / −30 points | −7,6 / −6,9 / −5,6 % | −4,1 / −3,4 / −2,1 points |
| Revente dès 0,97 / 0,98 / 0,99 | −4,7 / −4,5 / −4,8 % | −1,0 à −1,3 point |
| Stop suiveur 10 / 20 points | −5,8 / −6,4 % | −2,4 / −2,9 points |

Renforcer en baisse semblait gagner : après une baisse de 10 points, le favori valait 0,718 et a
gagné 76 % du temps. **Mais seulement sur 5 jours et sur nos propres paris** : vérifié ailleurs.

## Test 2 — 2 152 matchs à deux issues (22/09-19/10), favori à 0,70-0,95 avant le match
- Acheter le favori avant le match : −4,2 % (2 h 30 avant), −4,4 % (1 h avant), −5,2 %
  (5 min avant) ; t de −3,7 à −4,7. Acheter un peu plus tôt est légèrement moins mauvais.
- Acheter le favori **après une baisse** de 5 à 30 points pendant le match : −2,1 à −3,6 %. Le
  prix après une chute est **juste** en moyenne (baisse de 10 points : prix 0,666, gagnés 65,9 %).
  Tennis : −5 à −6 % (t −2,4). E-sport : +2,7 à +4 % (t 0,6, semaines mêlées) : rien de solide.
- **Verdict : renforcer en baisse, échelonner, stop-loss, prise de gain, stop suiveur → écartés.**
  Aucune stratégie construite sur eux.

## Test 3 — ce que le test 2 a fait découvrir : favoris et outsiders par circuit
Prix historiques, 1 h avant le match : favoris de tennis 0,807 pour 76,2 % gagnés (−7,4 %, perdants
chaque semaine) ; favoris d'e-sport 0,803 pour 82,6 % ; outsiders de tennis 0,05-0,30 : +21 %, dont
**ITF +62 %**, ATP −15 %, WTA −11 %.
**Vérification aux prix RÉELLEMENT payés par les preneurs** (`data-api` trades, premier achat après
la décision, avant le début du match ; frais du marché) :

| Pari, 1 h avant | Paris réels | Prix payé | Gagnés | Rendement | Semaines + | Verdict |
|---|---|---|---|---|---|---|
| Favori ITF (0,70-0,95) | 204 | 0,832 | 72,1 % | **−13,9 %** (t −3,65) | 0 / 5 | à éviter |
| Favori WTA | 221 | 0,805 | 78,7 % | −3,4 % | 2 / 5 | écarté |
| Favori ATP | 382 | 0,798 | 81,4 % | +1,1 % | 3 / 5 | écarté (neutre) |
| Outsider ITF (0,05-0,30) | 150 | 0,187 | 20,7 % | **+17 %** (confiance +0,78) | 3 / 5 | **indice** |
| Outsider ATP / WTA | 333 / 206 | 0,21 / 0,20 | 20 / 23 % | −9 % / +1,5 % | 2 / 5, 3 / 5 | écartés |
| Favori e-sport | 384 | 0,806 | 81,0 % | −0,4 % | 1 / 4 | écarté |

Leçon déjà vue avec la météo : le +62 % des prix historiques de l'ITF fondait à +17 % aux vrais
prix, et sur 150 matchs seulement (les autres n'avaient aucun échange avant le début : impossible
d'y acheter). Le favori ITF, lui, perd lourdement et régulièrement aux vrais prix.

## Ce qui entre dans l'arène
- `outsider_itf` (indice) : outsider ITF 0,05-0,30, achat immédiat 15 min à 3 h avant le match,
  écart ≤ 5 centimes, quart de Kelly. Nouveau filtre `sources` (domaine de la source de résolution).
- `nf_sport_patiente_sans_itf` (fille de la championne) : la championne sans les favoris ITF
  (nouveau filtre `sources_exclues`). La championne ne fait que 6 paris ITF sur 84 : effet attendu
  modeste, mais ce morceau perd −13,9 % aux vrais prix.

## Avec le passage du chercheur de 15 h (experiments/tennis.md)
Même conclusion avant le match (tennis +0,6 % sur 6 131 matchs chez lui ; ATP +1,1 %, WTA −3,4 %,
ITF −13,9 % ici aux vrais prix). Il a trouvé que 84 % des achats de la championne se font PENDANT
le match et un indice en jeu (favori à +30 min : +3,1 %, `nf_tennis_debut_match`). Les deux
études se complètent : ce qui fait la différence n'est pas la façon d'entrer par tranches, mais le
moment (avant / pendant le match) et le circuit (ITF).

## Pour l'enquête sur la championne (obligation du 20/10)
Ses gains de tennis viennent de l'ATP (+258 € sur 26 paris, +12,5 % par mise) et de la WTA
(+155 € sur 7 paris) ; sur 382 matchs ATP, le favori acheté une heure avant ne fait que +1,1 % aux
vrais prix. Son avance en tennis ressemble donc à de la chance (et à son ordre posé), pas à un
avantage du circuit.
