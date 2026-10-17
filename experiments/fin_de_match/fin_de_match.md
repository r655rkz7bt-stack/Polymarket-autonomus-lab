# Fin de match : peut-on encore acheter le vainqueur sous 0,99 ? (test du 17/10/2026)

**Idée testée.** Le match est officiellement fini, mais le marché Polymarket n'est pas encore réglé.
Si l'on peut encore acheter les parts du vainqueur à 0,98 ou 0,985, on gagne 1,5 à 2 % presque sans
risque. Notre robot relève les données toutes les 5 minutes : il pourrait agir 5 à 10 minutes après la fin.

**Verdict : non. Pour un robot qui relève toutes les 5 minutes, il n'y a rien à prendre.**
L'occasion existe, mais elle dure **2 à 3 secondes** (au maximum 86 secondes) après le dernier lancer.
Ensuite, plus personne ne vend le vainqueur sous 0,999 : sur 175 matchs, **aucun** achat du vainqueur
n'a eu lieu plus de 5 minutes après la fin, à aucun prix.

## Ce qui a été fait

- **Matchs** : les 176 matchs MLB terminés du 17/09 au 16/10/2026 (143 de saison régulière, 9 de wild
  card, 16 de série de division, 7 de finale de ligue). 175 retrouvés sur Polymarket (marché « vainqueur
  du match ») ; 1 non trouvé (Orioles–Yankees du 25/09).
- **Heure de fin officielle (T_fin)** : API officielle MLB (`statsapi.mlb.com`), heure de fin du dernier
  jeu du match. Contrôle : elle tombe à +0,6 min (médiane) de « premier lancer + durée officielle ».
- **Prix** : uniquement les **échanges réellement exécutés** (`data-api.polymarket.com/trades`), jamais
  l'historique de prix toutes les 10 minutes.
- **« Achetable à p »** = quelqu'un a réellement **acheté** le vainqueur à p (il y avait donc un vendeur
  à ce prix). Les ventes (quelqu'un vend à un acheteur qui attendait) sont comptées à part : elles
  montrent ce qu'un ordre d'achat posé d'avance aurait pu récupérer.
- **Pas de regard vers le futur** : la fenêtre commence à T_fin + délai (0, 1, 5 ou 10 min). L'heure de
  clôture du marché ne sert que de limite de fin (après, on ne peut plus échanger).
- **Frais** (lus dans Gamma) : `feeType = sports_fees_v3`, `feeSchedule = {rate 0,05, exponent 1,
  takerOnly, rebateRate 0,15}` pour 174 marchés ; `sports_fees_v2` (taux 0,03) pour 1. Frais par part
  = taux × p × (1 − p). Le champ `takerBaseFee = 1000` est un ancien champ, non utilisé.

## Résultats (175 matchs)

Temps entre la fin du match et la clôture du marché : **20 min en médiane** (de 16 à 103 min).
Dernier prix payé pour le vainqueur juste avant la fin : 0,99 (médiane).

Achats réels du vainqueur **après** T_fin + délai :

| Délai après la fin | Seuil | % des matchs où c'était possible | $ disponibles (médiane, si possible) | $ au total | Prix médian | Gain net moyen par $ (frais 0,05) |
|---|---|---|---|---|---|---|
| 0 s (impossible pour nous) | ≤ 0,99 | 28,0 % (49) | 450 $ | 41 852 $ | 0,99 | +1,83 % |
| 0 s (impossible pour nous) | ≤ 0,985 | 13,7 % (24) | 342 $ | 19 100 $ | 0,98 | +3,17 % |
| 0 s (impossible pour nous) | ≤ 0,98 | 13,7 % (24) | 296 $ | 18 289 $ | 0,98 | +3,17 % |
| 1 min | ≤ 0,99 | 0,6 % (1) | 1 207 $ | 1 207 $ | 0,984 | +1,57 % |
| 1 min | ≤ 0,985 | 0,6 % (1) | 811 $ | 811 $ | 0,984 | +1,57 % |
| 1 min | ≤ 0,98 | 0 % | – | 0 $ | – | – |
| **5 min** | ≤ 0,99 / 0,985 / 0,98 | **0 %** | – | **0 $** | – | – |
| **10 min** | ≤ 0,99 / 0,985 / 0,98 | **0 %** | – | **0 $** | – | – |

- **Durée de l'occasion** : le dernier achat ≤ 0,985 a lieu **2 s** (médiane) après le dernier lancer,
  71 s au plus tard. Pour ≤ 0,99 : 3 s en médiane, 86 s au plus tard.
- **Prix le plus bas échangé** (achats et ventes confondus) après T_fin + 1, + 5 et + 15 min : **0,999**
  en médiane. Après + 5 min, tous les échanges sont des **ventes à 0,999** : des détenteurs vendent le
  vainqueur à des robots qui attendent à 0,999 pour gagner 0,1 %.
- Même en gagnant ce 0,1 % : à 0,999, gain = 0,001 − frais (0,00005) ≈ **+0,095 % par $**, et
  personne n'a vendu à ce prix à un acheteur pressé.
- **Variante « ordre posé d'avance à 0,99 »** (rôle maker, sans frais) : après 1 min (presque tout avant 4 min), des vendeurs
  ont frappé des ordres à ≤ 0,99 dans 16 % des matchs (141 648 $ au total, gain maximal 1 434 $ si l'on
  avait tout pris en étant premier dans la file). Après + 5 min : 3 matchs, 150 $, gain maximal 4,66 $.
  Il faudrait donc être en place dans la première minute : pas compatible avec un relevé toutes les 5 min.
- **Litiges** : **0 sur 175**. Tous les marchés sont `resolved` et le vainqueur Polymarket est le
  vainqueur officiel MLB.

## Limites honnêtes

- **Concurrence non simulée** : quand un achat à 0,98 a eu lieu 2 s après la fin, quelqu'un d'autre l'a
  pris. Les chiffres « 0 s » sont un plafond, pas ce que nous aurions obtenu.
- **Pas de carnet d'ordres passé** : on voit les échanges, pas les offres non exécutées. Mais une offre de
  vente sous 0,999 ne peut pas rester affichée tant que des acheteurs attendent à 0,999 : elle serait
  exécutée aussitôt et apparaîtrait comme échange. L'absence d'échanges après 5 min est donc parlante.
- **Délai de l'API MLB non mesuré** : on ne sait pas combien de secondes l'API met à afficher « Final ».
  Cela ne peut qu'aggraver notre retard.
- Horodatage des échanges à la seconde ; T_fin précis à environ une minute près.
- **Seulement la MLB, 4 semaines** (175 matchs). Hockey (NHL) non testé. D'autres sports ou de petits
  marchés peu suivis pourraient se comporter autrement, mais rien ici ne le suggère.

## Conclusion pour le labo

Ne pas construire de stratégie « acheter le vainqueur après le coup de sifflet » avec un cycle de
5 minutes : sur 175 matchs, **0 occasion** à T_fin + 5 ou + 10 min, gain net possible ≈ 0. L'avantage
existe pendant **quelques secondes** et il est déjà pris par des robots plus rapides que nous.

## Refaire le test

```
.venv/bin/python -I experiments/fin_de_match/fin_de_match.py 2026-09-17 2026-10-16
```

Écrit `resultats.json` (une ligne par match) et `resume.json` (les chiffres ci-dessus). Les
téléchargements bruts sont gardés dans `cache/` (ignoré par git).
