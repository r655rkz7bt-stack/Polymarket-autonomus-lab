# Enquête du 21/10/2026 (passage chercheur, ~0 h UTC) : type de pari, règlement, cotes_bookmakers

Famille n° 3 (« la donnée n'est pas celle qu'on croit ») ; journaux publiés jusqu'au 20/10 23:54 UTC.

## 1. Règlement relu sur Gamma : conforme
30 paris réglés tirés au hasard (graine 21) dans les 110 fantômes + le principal (1 944 paris réglés
au total) : le règlement du journal (payout 0 ou 1) redonne le résultat officiel de Gamma dans
**30 cas sur 30** ; jeton présent dans le marché dans 30 cas sur 30 ; questions relues (tennis, e-sport,
météo, football « win on », « Exact Score », « Spread », O/U) : bon marché, bon camp.

## 2. Estimation périmée : le correctif tient
Écart « estimation − prix payé » sur tous les achats du journal : avant le correctif de 14 h 27 UTC
(PR #95) 3 312 achats, médiane 0,045, p90 0,134, p99 0,366, max 0,645 ; **après : 416 achats, médiane
0,045, p90 0,055, p99 0,075**, max 0,213. Les écarts qui restent sont des modèles (compteur de tweets,
décroissance du temps) qui annoncent volontairement un avantage, pas des carnets périmés. Les 3 achats
du principal signalés par l'enquête automatique (Uchijima 0,979 pour 0,817, etc.) datent d'avant 14 h 27.

## 3. Type de pari des variantes « favori » (nf_*, naive_favorite*), 1 944 paris réglés
Classement avec `pareto.bet_type` sur les questions de la sauvegarde (325 paris sans question connue,
« inconnu ») ; chaque ligne = somme des fantômes (paris NON indépendants : une même partie est achetée par
plusieurs variantes, donc les t sont à ne pas lire, seuls les rendements comptent).

| type | paris | misé | rendement | gagnés / attendus |
|---|---|---|---|---|
| vainqueur | 470 | 28 837 | **+0,0 %** | 414,5 / 411,7 |
| autre (météo, crypto…) | 137 | 6 836 | −6,0 % | 115 / 122,9 |
| handicap | 97 | 5 233 | **−10,5 %** (−549) | 84 / 85,6 |
| total (O/U) | 69 | 3 696 | +6,4 % | 66 / 62,9 |
| score exact | 51 | 3 051 | +8,0 % | 49 / 46,8 |
| nul | 20 | 694 | +10,5 % | 20 / 17,9 |
| partie (set, manche) | 19 | 1 258 | +12,5 % | 19 / 16,6 |

- Sur le seul type « vainqueur », les favoris gagnent exactement ce que leurs prix annoncent : aucun
  avantage ; le gain de l'arène vient des types annexes, de la sélection (meilleur de 42) et de la chance.
- Handicaps : le favori d'un handicap à 0,93 perd plus que son prix (−10,5 %) ; principal : 13 paris
  de handicap, −14,9 % (−42 €), « autre » −20,6 % (−152 €, 47 paris, surtout météo).
- Champion nf_sport_patiente : vainqueur +4,7 % (71 paris, 66 gagnés pour 60,9 attendus) ; ses 4 handicaps −15,7 %.
- Petits échantillons pour total / score exact / nul / partie (≤ 69 paris, 100 % de victoires = favoris
  très chers) : à surveiller, pas à croire.

Correctif / test : fille `nf_sport_patiente_vainqueur` (filtre `types_pari: [vainqueur]`, déjà couvert par
les tests des filtres) ; pas de modification du code des stratégies.

## 4. cotes_bookmakers muette depuis le 19/10 04 h (reste ouvert, non tranché)
La sauvegarde (jour.txt = 20/10) n'a pas les observations ni le budget de crédits (`odds_api:credits:<jour>`
n'est pas dans la sauvegarde) : impossible de savoir depuis les journaux si la stratégie s'abstient pour
« cotes trop vieilles » (`max_odds_age_hours` 4, budget 12 crédits par jour, tennis ajouté le 20/10 à ce même budget)
ou « écart trop grand ». Dernier relevé `odds_api` de la sauvegarde : 19/10 16:44 UTC. **Hypothèse la plus
probable** : budget de crédits épuisé/partagé, donc cotes périmées. À trancher en consignant les raisons
d'abstention des stratégies (voir « Reste ouvert »).
