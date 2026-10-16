# Test sur le passé : marchés crypto à seuil (16/10/2026)

**Question** : peut-on régler le modèle de `crypto_threshold` (log-normal sans dérive, prix au
comptant + volatilité réalisée sur 7 jours) pour qu'il batte le prix Polymarket hors échantillon,
après frais ? Ou le marché est-il déjà efficace sur ces marchés ?

**Réponse courte : pas d'avantage exploitable. Le marché est efficace, aux frais près.**
Les gains spectaculaires obtenus avec l'historique de prix « toutes les 10 minutes » viennent de
prix périmés ou de carnets vides, pas d'une vraie avance du modèle. Aux prix **réellement payés**
par des acheteurs (transactions publiques), la règle de production perd **−6 % à −48 %** des mises,
sur la première comme sur la seconde moitié des jours. Recommandation en fin de page.

## Données (toutes réelles, publiques, gratuites)
- **4 872 marchés résolus** du 17/08 au 15/10/2026 (60 jours d'échéance), 4 actifs (BTC, ETH,
  SOL, XRP), API Gamma :
  - échelles quotidiennes « Bitcoin au-dessus de K le <jour> ? » (tag `multi-strikes`, bougie
    Binance d'une minute à 12 h ET) ;
  - barrières « atteindre / descendre à K » sur un jour, une semaine, un mois (tag `hit-price`,
    plus haut / plus bas d'une bougie Binance d'une minute pendant la période).
  - Pas inclus : échelles horaires (`...-above-on-<jour>-3pm-et`), marchés « entre X et Y »,
    marchés « hausse ou baisse » toutes les 15 min / heure.
- **Frais** : barème réel de chaque marché, `rate` = **0,07** (et non 0,04) pour tous, frais
  preneur seulement (`takerOnly`), frais = 0,07 × p × (1 − p) par part.
- Prix au comptant : bougies Binance (`data-api.binance.vision`, source de résolution) horaires
  et d'une minute. Volatilité implicite : indice DVOL de Deribit (BTC, ETH) ; SOL et XRP :
  volatilité réalisée × (DVOL BTC / volatilité réalisée BTC).
- Prix Polymarket, deux mesures :
  1. `prices-history` du CLOB : un point toutes les 10 minutes, dernier point avant l'instant t ;
  2. **transactions réelles** (`data-api.polymarket.com/trades`, 705 201 transactions) : prix payé
     par un preneur. Achat du Oui (ou vente du Non) = prix vendeur du Oui ; vente du Oui (ou
     achat du Non) = prix acheteur du Oui.
- Instants de décision : échelles 72, 48, 24, 12, 6, 2 h avant l'échéance ; barrières du jour
  20, 12, 6, 2 h ; de la semaine 144 à 12 h ; du mois 20 jours à 1 jour. Barrière déjà touchée
  avant t : cas écarté. 14 131 cas (prix entre 0,01 et 0,99).

## Méthode
Réglage sur les 30 premiers jours d'échéance (17/08-15/09), **jugement sur les 30 suivants**
(16/09-15/10). Un même marché vu à plusieurs instants reste d'un seul côté de la coupure.
Modèles :
- **a** : production actuelle (`crypto_model.py`) : estimation centrale, et la **règle de production**
  (achat si la borne prudente de la bande σ × 0,75..1,5 dépasse prix + frais + seuil) ;
- **b** : DVOL (volatilité implicite) au lieu de la volatilité réalisée ;
- **c** : queues épaisses : σ × k réglé (k = 1,25 sur les échelles, 1,10-1,15 sur les barrières),
  loi de Student (ν = 2,5, k = 1,55-1,80) ;
- **d** : mélange modèle + prix du marché (régression logistique réglée sur l'apprentissage) ;
- **e** : prix du marché seul ré-étalonné.
Simulation : 1 part par pari, frais réels, seuils d'avantage 0,03 / 0,05 / 0,08.

## Résultat 1 : avec l'historique « 10 minutes », tout semble gagner… à tort
| Modèle (jugement, écart simulé 0,02) | Brier (marché 0,0702) | seuil 0,05 | jours gagnants |
|---|---|---|---|
| a. règle de production (bande) | | 416 paris, **+37 %** | 26 / 30 |
| b. DVOL | 0,0651 | 1 001 paris, +28 % | 25 / 30 |
| c4. Student + DVOL | 0,0648 | 881 paris, +33 % | 25 / 30 |
| e. marché ré-étalonné | 0,0707 | 1 121 paris, +4 % | 17 / 30 |

Trop beau, et c'est faux. Deux artefacts :
- **carnets vides** : 202 cas de barrières du jour sont cotés **exactement 0,50** (milieu d'un
  carnet 0,01 / 0,99 juste après la création du marché) ; dans la tranche 0,4-0,6 des barrières,
  le Oui ne gagne que 23 % du temps. Ces prix ne sont pas achetables.
- **prix périmés** : le point « 10 minutes » reflète souvent un échange plus ancien, alors que le
  prix au comptant du modèle est frais. Le modèle « voit » le mouvement du Bitcoin que le prix
  affiché n'a pas encore suivi. Preuve (DVOL, seuil 0,05, jugement, mêmes prix d'échange) :
  modèle calculé à t (échange jusqu'à 1 h plus ancien) **+23,6 %**, 22 jours / 30 ; modèle
  calculé à l'instant exact de l'échange **+7,0 %**, 12 jours / 29.

## Résultat 2 : aux prix réellement payés, au même instant, pas d'avantage
Chaque achat est simulé au prix du dernier échange de la bonne sorte dans l'heure avant t, et
le modèle est calculé **à l'instant de cet échange** (bougie d'une minute, volatilité, horizon à
cet instant). Sans glissement supplémentaire (le prix d'échange contient déjà l'écart).

| Modèle | apprentissage, seuil 0,05 | jugement, seuil 0,05 | jugement, seuil 0,08 |
|---|---|---|---|
| **règle de production (bande)** | 89 paris **−6,4 %** (11 / 21 jours) | 57 paris **−14,8 %** (7 / 17) | 30 paris **−48 %** (3 / 11) |
| production, estimation centrale | 361 paris −19,0 % (9 / 30) | 294 paris 0,0 % (14 / 30) | 148 paris −9,1 % |
| σ réalisée × k | 493 paris −24,3 % (7 / 28) | 402 paris +8,9 % (15 / 30) | 236 paris −1,2 % |
| DVOL | 355 paris −2,1 % (11 / 30) | 337 paris +7,0 % (12 / 29) | 191 paris +10,8 % (15 / 28) |
| DVOL × k | 520 paris −3,7 % (10 / 29) | 589 paris +16,2 % (17 / 30) | 388 paris +9,6 % (15 / 30) |
| Student, DVOL × k | | 300 paris +2,5 % (12 / 30) | 153 paris +8,7 % |
| mélange marché + modèle | | 451 paris −4,3 % (13 / 30) | 205 paris +4,7 % |

Lecture : tout ce qui perd sur la première moitié et gagne un peu sur la seconde, avec la moitié
des jours gagnants environ, c'est du hasard (et la seconde moitié a eu une hausse régulière).
Avec 1 cent de glissement, DVOL × k tombe à +8 % (14 / 30 jours), DVOL à +2 % (13 / 28).

**Précision des probabilités au même instant** (Brier / log loss, plus bas = mieux) :
| | marché | production | DVOL | DVOL × k |
|---|---|---|---|---|
| échelles, apprentissage (1 204 cas) | **0,0982 / 0,325** | 0,1022 / 0,396 | 0,0983 / 0,345 | 0,0994 / 0,334 |
| échelles, jugement (1 270 cas) | **0,1017 / 0,330** | 0,1040 / 0,363 | 0,1032 / 0,349 | 0,1036 / 0,341 |
| barrières, apprentissage (957 cas) | **0,0907 / 0,304** | 0,1031 / 0,381 | 0,1029 / 0,357 | 0,1065 / 0,353 |
| barrières, jugement (907 cas) | 0,0891 / 0,296 | 0,0887 / 0,299 | **0,0868 / 0,289** | 0,0911 / 0,302 |

Le prix du marché est aussi bon ou meilleur que tous les modèles (une seule case sur quatre en
faveur de DVOL, de peu). DVOL vaut mieux que la volatilité réalisée (log loss), mais pas assez
pour battre le marché.

## Le marché surpaie-t-il les queues ?
Au dernier prix d'échange (tous les jours) :
| Prix du Oui | échelles : prix / fréquence réelle | barrières : prix / fréquence réelle |
|---|---|---|
| < 0,05 | 0,022 / 0,061 (576 cas) | 0,021 / 0,030 (959) |
| 0,05-0,10 | 0,070 / 0,097 | 0,068 / 0,080 |
| 0,10-0,20 | 0,139 / 0,188 | 0,145 / 0,158 |
| 0,60-0,80 | 0,701 / 0,670 | 0,681 / 0,691 |
| > 0,95 | 0,978 / 0,990 (607) | |

Les queues ne sont **pas surpayées** (contrairement aux « billets de loterie » météo) ; elles
semblent même un peu sous-payées, mais ce n'est pas exploitable :
- sur les échelles, les gains des queues « hausse » viennent de **4 jours sur 30** seulement :
  BTC est passé de 64 200 $ (17/08) à 75 800 $ (16/09) puis 82 400 $ (15/10), ETH de 1 913 à
  2 441 $. Acheter le Oui à moins de 0,05 : +279 % puis +60 %, mais 4 jours gagnants sur 28-30 ;
  sur les barrières, la même règle fait +37 % puis **−66 %** ;
- vendre les queues (acheter le Non quand le Oui vaut moins de 0,20) perd un peu partout
  (−1,4 % à −9,8 %, apprentissage comme jugement) : le prix est juste, les frais font la perte.
Aucune tranche de cote ne gagne de façon stable : par exemple, avec DVOL, « Oui < 0,2 » fait
+69 % sur l'apprentissage puis −35 % sur le jugement ; « Non < 0,2 » −65 % puis −19 %.

## Pourquoi la stratégie perd en direct (hypothèse appuyée par ce test)
- Le marché intègre le prix du Bitcoin presque instantanément. Notre prix au comptant a jusqu'à
  `max_quote_age_minutes` = 20 minutes de retard sur le carnet lu : quand le modèle « voit » un
  avantage, c'est souvent que le marché a déjà bougé (le test « prix périmé » ci-dessus le montre
  dans l'autre sens : un écart de temps de 1 h vaut +17 points de rendement fictif).
- Frais preneur de 0,07 × p × (1 − p) : 1,75 cent par part à 0,50, plus que l'erreur du marché.
- Détail technique repéré : `sources/crypto_prices.py` date le prix (`as_of`) à l'**ouverture**
  de la bougie horaire en cours, alors que le prix est celui du moment de la lecture. Avec
  `max_quote_age_minutes` = 20, la stratégie s'abstient (« prix crypto périmé ») environ 40 minutes
  par heure. Sans effet sur la conclusion. **Corrigé le 16/10/2026** (test de non-régression).

## Recommandation
- **Mettre `max_proposals_per_cycle` à 0 pour `crypto_threshold`** (preneur, règle de production :
  négative sur les deux moitiés aux prix réels). **Appliqué le 16/10/2026.**
- `crypto_threshold_patiente` (ordres posés, sans frais preneur) n'est pas testable avec ces
  données (on ne sait pas quels ordres posés auraient été exécutés). Mais le modèle n'a pas
  d'information que le marché n'a pas : un ordre posé ne serait exécuté que quand le marché
  bouge contre lui (sélection adverse). **Mise aussi à 0 le 16/10/2026.**
- Si une version est gardée : DVOL plutôt que la volatilité réalisée, prix au comptant de moins
  d'une minute, et seulement les barrières (seul endroit où DVOL égale le marché).
- Aucun nouveau modèle en production : pas d'avantage hors échantillon prouvé.

## Limites (honnêtes)
- 60 jours d'échéance, une seule période (hausse régulière du marché crypto) ; jours très
  corrélés entre eux (une échelle entière dépend du même mouvement du Bitcoin).
- Prix d'échange : le dernier dans l'heure avant t ; il donne un prix vraiment payé, pas la
  quantité disponible. Un cas sans échange récent du bon côté est sans pari possible
  (2 177 cas jugés avec au moins un côté sur 7 152).
- Transactions : 11 000 au plus par événement (limite de l'API) ; 4 événements sur 522 tronqués
  (seuls leurs plus anciens échanges manquent).
- SOL et XRP n'ont pas de DVOL : volatilité implicite approchée par un rapport avec le Bitcoin.

## Refaire le test
```
python3 -I experiments/crypto_backtest/collect.py <dossier_de_travail> src         # ≈ 25 min la 1re fois (marchés, bougies, DVOL, historiques)
python3 -I experiments/crypto_backtest/collect_trades.py <dossier_de_travail> src  # ≈ 2 min (transactions réelles)
python3 -I experiments/crypto_backtest/evaluate.py <dossier_de_travail> src        # étalonnage, réglages, résultats 1 et 2
python3 -I experiments/crypto_backtest/robuste.py <dossier_de_travail> src         # apprentissage contre jugement aux prix réels, queues, prix périmé
```
(Avec le Python du projet : `.venv/bin/python -I ...`. Fichiers communs : `donnees.py`
— construction des cas sans regard vers le futur — et `modeles.py` — modèles et simulations.)
