# Test sur le passé : marchés de température (16/10/2026)

**Question** : les prévisions météo gratuites (GFS et ECMWF, Open-Meteo) prévoient-elles mieux
que les prix de Polymarket sur les marchés « température maximale / minimale à <ville> le <jour> » ?

> **Correction du 16/10/2026 (voir « Vérification aux prix réellement payés » plus bas)** : les
> gains ci-dessous (+18 à +31 %) viennent de l'historique « 10 minutes » du CLOB. Aux prix des vrais
> échanges, le même modèle perd **−6 %** des mises (0 jour gagnant sur 8). Tout le gain venait de
> marchés **sans aucun échange** dans les 2 h avant la décision : leur prix d'historique n'était
> pas achetable. Le modèle prévoit bien la température ; il ne bat pas le prix qu'on paierait vraiment.

## Données (toutes réelles, publiques)
- 1 383 événements de température résolus du 1er au 15/10/2026 (API Gamma, tag Weather), soit
  14 553 marchés réglés à 1/0, 47 stations (`resolutionSource` weather.gov, coordonnées METAR).
- Prix du « Oui » : historique public du CLOB (`prices-history`), dernier point avant l'instant choisi.
- Prévisions telles qu'elles existaient AVANT l'instant choisi : Open-Meteo « previous runs »
  (`temperature_2m_previous_day1` / `_day2`, modèles `gfs_seamless` et `ecmwf_ifs025`).
- Deux régimes, sans regard vers le futur :
  - **day1** : prix au début du jour local, prévisions émises la veille (24 h avant chaque heure) ;
  - **day2** : prix 24 h avant le début du jour local, prévisions émises 48 h avant.

## Méthode
Probabilité d'une tranche = moyenne des deux modèles, floutés par une erreur normale σ et
décalés d'un biais b (`src/polymarket_agent/weather_model.py`). σ et b réglés sur la première moitié
des dates (1er-7/10) par vraisemblance, **jugés sur la seconde moitié (8-15/10)** :
maximum σ = 1,5 °C, b = +0,5 °C ; minimum σ = 1,8 °C, b = 0 (day2 : −0,5).
Simulation : 1 part par pari, prix = dernier prix + écart achat-vente, frais réels
(0,05 × p × (1 − p)), pari si l'avantage dépasse un seuil.

## Résultats (hors échantillon, 8-15/10)
| | day1 (5 556 marchés) | day2 (6 529 marchés) |
|---|---|---|
| Brier modèle / marché (plus bas = mieux) | **0,097** / 0,113 | **0,085** / 0,108 |
| Seuil 0,05, écart 0,01 | 4 012 paris, **+22,7 %** des mises | 4 444 paris, **+26,1 %** |
| Seuil 0,05, écart 0,04 | **+18,0 %** | **+21,3 %** |
| Jours gagnants | 8 / 8 | 8 / 8 |

D'où vient le gain (écart 0,02) :
| Type de pari | day1 | day2 |
|---|---|---|
| NON sur une tranche cotée 0,2-0,8 (la favorite surestimée) | 2 989 paris, **+23,5 %** | 3 504 paris, **+26,6 %** |
| NON coté > 0,8 | +6,8 % | +9,7 % |
| OUI bon marché (< 0,2) | **−54,7 %** | **−60,9 %** |

**Lecture** : le marché met trop de probabilité sur la tranche favorite (1 °C de large, alors que
l'erreur d'une prévision à 1-2 jours est de l'ordre de 1,5 °C). Les « billets de loterie » OUI
bon marché perdent, comme sur la plupart des marchés de prédiction.
Villes : 50 à 53 sur 88 gagnantes (gain réparti, pas dû à une seule ville).

## Étalonnage par station (16/10/2026)
Chaque station a son propre écart avec les modèles. Valeur réelle du jour = tranche gagnante du
marché résolu (à 1 degré près). Pour chaque station et type (max, min), à chaque date : erreurs
des 7 jours PRÉCÉDENTS (réel − moyenne GFS/ECMWF de la veille), biais et flou tirés vers le
réglage global (3 jours fictifs), flou ≥ 0,8 °C, réglage global tant qu'il y a moins de 3 jours.
Jugé sur la seconde moitié des dates, NON seulement, écart simulé 0,01 :

| Réglage | Brier (marché 0,1125) | Log loss (marché 0,3615) | seuil 0,05 | seuil 0,08 |
|---|---|---|---|---|
| global (σ 1,5 / biais +0,5 au max) | 0,0969 | 0,3205 | +24,0 % | +25,4 % |
| biais par station seulement | 0,0949 | 0,3098 | | |
| biais ET flou par station | **0,0921** | **0,2985** | +26,2 % (2 983 paris) | **+28,7 %** |

Toutes les variantes gagnent 8 jours sur 8 et 41 à 43 stations sur 46. Script :
`experiments/meteo_backtest/station_bias.py`.
Le code de production (`weather_calibration.py`, rattrapage d'archive, valeurs réelles, erreurs)
rejoué sur les mêmes données (moyenne des deux modèles) : Brier **0,0901** contre 0,0966 ;
NON **+27,8 %** (2 854 paris) et **+30,8 %** (2 548 paris) contre +24,0 % et +25,7 %.
Activé dans `meteo_prevision` et sa variante patiente (`station_calibration`). Ces rendements
sont ceux de l'historique « 10 minutes » : voir la vérification aux prix réels ci-dessous.

## Vérification aux prix réellement payés (16/10/2026)
Même modèle (prévisions de la veille, étalonnage par station), même jugement (8-15/10), mais le
prix du NON est celui d'un **vrai échange** d'un preneur (`data-api.polymarket.com/trades?eventId=…`,
980 432 échanges) : achat du NON au prix p, ou vente du OUI au prix p (= NON à 1 − p).
Script : `experiments/meteo_backtest/trades_check.py`. NON coté 0,2-0,8 :

| Prix utilisé | seuil 0,05 | seuil 0,08 |
|---|---|---|
| historique + 0,01, tous les cas | 2 820 paris, **+27,6 %**, 8 / 8 jours | |
| historique + 0,01, seulement les cas AVEC échange dans les 2 h avant | 524 paris, **−2,5 %**, 3 / 8 | |
| dernier vrai échange dans les 2 h AVANT la décision | 501 paris, **−6,4 %**, 0 / 8 | 443 paris, −7,1 %, 1 / 8 |
| premier vrai échange dans les 2 h APRÈS | 575 paris, **−5,6 %**, 0 / 8 | 507 paris, −5,8 %, 3 / 8 |

Sur les mêmes cas, le NON réellement payé coûte en moyenne 0,025 de plus que ce que dit
l'historique (médiane 0,011, 1 cas sur 10 au-delà de 0,06). Mais surtout, là où des gens échangent
vraiment, le marché est juste : **le gain mesuré venait des marchés sans échange**, dont le prix
d'historique n'était pas achetable.
Conséquences : la météo n'est plus « validée » (`config/promotion.yaml`) ; elle reste dans
l'arène, jugée sur les vrais carnets ; l'étalonnage par station reste (prévision plus juste).

## Limites (honnêtes)
- Le prix historique est le dernier échange ou le milieu, pas le prix du vendeur dans le carnet :
  l'écart achat-vente est simulé (0,01 à 0,04). Les carnets réels peuvent être plus minces.
- 15 jours seulement, une seule saison (octobre), un seul réglage.
- La stratégie en direct utilise des prévisions plus fraîches que le test (mieux pour nous… et
  pour le marché aussi).

## Ce qui en est tiré
Stratégie `meteo_prevision` (fantôme, arène) : NON seulement, NON coté 0,2-0,8, avantage ≥ 0,05
après une marge de 0,02, de 36 h avant à 6 h après le début du jour local, ¼ Kelly plafonné à 3 %
du capital par pari. **C'est l'arène, avec les vrais carnets, qui confirmera ou non** (et la
vérification aux prix réels ci-dessus ne l'annonce pas gagnante).

## Refaire le test
```
python3 -I experiments/meteo_backtest/collect.py <dossier_de_travail> src     # ≈ 30 min (télécharge)
python3 -I experiments/meteo_backtest/evaluate.py <dossier_de_travail> src day1
python3 -I experiments/meteo_backtest/robust.py <dossier_de_travail> src day2
```
(les événements Gamma doivent d'abord être téléchargés dans `<dossier>/bt/ev_*.json`, voir l'en-tête
de collect.py : `/events?tag_id=84&closed=true&end_date_min=…&end_date_max=…&limit=100&offset=…`).
