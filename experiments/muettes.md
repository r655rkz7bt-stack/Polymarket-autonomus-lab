# Réveiller les stratégies muettes (21/10/2026, soir)

Demande d'Etienne : « Réveiller les muettes » (choisi parmi les leviers pour élargir le champ des
possibles). Outil : `experiments/muettes/diagnostic.py` (essai à blanc sur les vrais marchés ouverts,
rien n'est exécuté ; ses relevés restent dans `experiments/muettes/donnees/`, non versionné).

## Constat (journaux publiés du 21/10 au soir)
- 130 fantômes : **20 n'avaient jamais rien acheté**, et beaucoup d'autres presque rien
  (outsider_itf 2 paris, mots_prononces 1, favori_politique 1).
- À chaque cycle, chaque stratégie ne voyait que ~450 marchés (les 150 plus échangés + ceux que les
  stratégies demandent).
- Sur les **10 000 marchés ouverts** lus le 21/10 (Polymarket refuse de lire au-delà de 2 000 par
  requête : lecture par tranches d'échéance), le scanner n'en gardait que ~1 100. Raisons :
  hors horizon (> 30 jours) 3 860, volume du jour insuffisant 2 864, liquidité insuffisante 1 243,
  données incohérentes 637, issue quasi certaine 231.

| Stratégie | Marchés qu'elle demanderait (tous les marchés ouverts) | Marchés vus en production | Ce qui l'écartait |
|---|---|---|---|
| echelle_dates | 433 | 12 | horizon (328), volume, liquidité |
| implication_politique | 60 | 0 | horizon : toutes les élections de 2028 |
| cross_market | 295 | 35 | horizon (109), volume, liquidité |
| marches_jumeaux | 8 | 0 | horizon, volume, issue quasi certaine |
| favori_politique | 40 | 26 | horizon (25) |
| statu_quo_ia | 25 | 0 | ne demandait pas ses marchés (fille à mots-clés) |
| outsider_itf | 25 | 1 | ne demandait pas ses marchés (fille à source de résolution) |

Les arbitrages (échelle de dates, cohérence d'un match, implication politique, OUI + NON, jumeaux)
ne disaient jamais **pourquoi** ils n'achetaient rien : aucune raison d'abstention notée.
Les stratégies à référence externe (Kalshi, PredictIt, Manifold, tweets, mentions) sont bien
branchées : en production elles notent « avantage net insuffisant » (pas d'écart aujourd'hui).

## Ce qui change
1. **Pages longues** (`config/settings.yaml` → `long_pages: 10`, jusqu'à 900 jours, volume du jour
   ≥ 100 $) : 1 000 marchés longs de toutes sortes, triés par volume. Ils ne vont **pas** dans la
   liste de surveillance de base (`extra_only`) et ne sont **montrés qu'aux stratégies qui les
   demandent** (`main._visible`) : le favori de base, sans fenêtre de temps, n'achètera pas un favori
   de 2028 qui bloquerait son fantôme deux ans.
2. **Filles à mots-clés ou à source de résolution** (`question_contient`, `sources`) : elles
   demandent elles-mêmes leurs marchés (25 au plus, les plus échangés).
3. **Raisons d'abstention des arbitrages** : « aucune paire complète parmi les marchés vus »,
   « une jambe sans vendeur », « paire cohérente : aucun écart après frais », « position déjà
   ouverte », « frais inconnus ». Elles apparaissent dans le tableau de bord.
4. Marchés demandés par les stratégies : 320 → 600 au plus par cycle.

## Effet mesuré (essai à blanc, 21/10 vers 21 h 30 UTC)
| | Avant | Après |
|---|---|---|
| Marchés scannés / exploitables | 1 853 / 1 072 | 2 832 / 1 734 |
| Durée du scan | 9,8 s | 13,0 s (cycle ≈ 50-90 s pour 5 min) |
| echelle_dates : marchés vus | 12 | 139 |
| implication_politique | 0 | 18 |
| cross_market | 35 | 53 |
| marches_jumeaux | 0 | 2 |
| favori_politique | 26 | 40 |
| statu_quo_ia | 0 | 7 |
| outsider_itf | 1 | 4 |
| market_maker | 32 | 50 |

**Honnêtement** : voir plus de marchés ne crée pas d'avantage. Les arbitrages purs sont rares (les
robots les ferment en secondes) ; ils pourront maintenant dire combien de paires ils voient et
pourquoi elles ne paient pas. statu_quo_ia attend les marchés de novembre (sa fenêtre est de 12 à
35 jours avant la fin ; ceux d'octobre sont à 10 jours).
