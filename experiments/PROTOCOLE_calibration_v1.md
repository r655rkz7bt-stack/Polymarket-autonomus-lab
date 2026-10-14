# Protocole — stratégie « calibration » v1

Écrit le 14/10/2026 **avant** d'avoir vu le moindre résultat (téléchargement en cours).
Ces critères ne seront pas modifiés après coup. Si la stratégie échoue, elle n'est pas adoptée.

## Hypothèse

Les prix Polymarket ne sont pas parfaitement calibrés : dans certaines cases
(catégorie × horizon × prix du favori), le favori gagne plus (ou moins) souvent que son
prix ne l'indique, d'un écart assez grand pour couvrir l'écart achat/vente, les frais et
une marge de 0,02.

## Données

- Marchés binaires résolus nettement (1/0), volume final ≥ 50 000, échéance entre le
  14/10/2025 et le 13/10/2026 (`data/history/`).
- Prix horaire (CLOB `prices-history`) aux horizons 72, 48, 36, 24, 18, 12, 8, 6, 4, 3, 2, 1 h
  avant l'échéance **prévue** ; un prix vieux de plus de 2 h est ignoré.

## Découpage

Chronologique, par événement : 60 % entraînement, 20 % validation, 20 % test.
La table de calibration est ajustée sur l'entraînement seulement. Le test ne sert qu'une fois.

## Règle

- δ par case, intervalle à 90 % par bootstrap sur les événements, rétréci vers 0 (k = 200).
- Case utilisable si ≥ 150 événements d'entraînement.
- Achat du favori si `prix + δ_bas − (prix + 0,01) − frais ≥ 0,02` ; sinon de l'outsider
  avec la règle symétrique. Une seule entrée par marché (le premier horizon qui se déclenche).
- Taille et garde-fous : `risk_limits.yaml` via le vrai journal et le vrai contrôleur.

## Comparaisons

« Ne rien faire » et la référence naïve v1 (définie à l'étape 3, avant ces données).

## Critères d'adoption (tous obligatoires)

1. Validation, demi-écart 0,01 : croissance logarithmique > 0 **et** borne basse de l'IC 90 %
   du rendement moyen par euro misé > 0.
2. Validation, demi-écart 0,015 (×1,5) : croissance logarithmique > 0.
3. Au moins 100 opérations sur au moins 50 événements distincts en validation.
4. Test (une seule évaluation, demi-écart 0,01) : croissance logarithmique > 0.
5. Pas de faillite, drawdown maximal < 25 %.

Si 1 à 3 échouent : on ne regarde pas le test, la stratégie n'est pas adoptée, le bot
s'abstient (« ne rien faire » reste la meilleure option connue).
Si le test (4) échoue : stratégie rejetée, résultat archivé tel quel.
Même adoptée, elle passe ensuite par la promotion « fantôme » de `config/promotion.yaml`
(≥ 30 positions clôturées et 7 jours en paper trading réel) avant d'être jugée.

## Limites connues avant de commencer

- Le prix historique est un prix de référence (pas l'ask réel) : coût modélisé par un
  demi-écart fixe, testé ×1,5 et ×2.
- Le filtre « volume final ≥ 50 000 » utilise une information connue seulement à la fin ;
  en réel, le filtre portera sur le volume déjà échangé (plus restrictif).
- Les marchés d'un même événement sont liés : les intervalles sont calculés par événement.
- Environ 90 cases × 2 côtés testées : risque de faux positifs, d'où la validation et le test.
