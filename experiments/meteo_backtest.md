# Test sur le passé : marchés de température (16/10/2026)

**Question** : les prévisions météo gratuites (GFS et ECMWF, Open-Meteo) prévoient-elles mieux
que les prix de Polymarket sur les marchés « température maximale / minimale à <ville> le <jour> » ?

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

## Limites (honnêtes)
- Le prix historique est le dernier échange ou le milieu, pas le prix du vendeur dans le carnet :
  l'écart achat-vente est simulé (0,01 à 0,04). Les carnets réels peuvent être plus minces.
- 15 jours seulement, une seule saison (octobre), un seul réglage.
- La stratégie en direct utilise des prévisions plus fraîches que le test (mieux pour nous… et
  pour le marché aussi).

## Ce qui en est tiré
Stratégie `meteo_prevision` (fantôme, arène) : NON seulement, NON coté 0,2-0,8, avantage ≥ 0,05
après une marge de 0,02, de 36 h avant à 6 h après le début du jour local, ¼ Kelly plafonné à 3 %
du capital par pari. **C'est l'arène, avec les vrais carnets, qui confirmera ou non.**

## Refaire le test
```
python3 -I experiments/meteo_backtest/collect.py <dossier_de_travail> src     # ≈ 30 min (télécharge)
python3 -I experiments/meteo_backtest/evaluate.py <dossier_de_travail> src day1
python3 -I experiments/meteo_backtest/robust.py <dossier_de_travail> src day2
```
(les événements Gamma doivent d'abord être téléchargés dans `<dossier>/bt/ev_*.json`, voir l'en-tête
de collect.py : `/events?tag_id=84&closed=true&end_date_min=…&end_date_max=…&limit=100&offset=…`).
