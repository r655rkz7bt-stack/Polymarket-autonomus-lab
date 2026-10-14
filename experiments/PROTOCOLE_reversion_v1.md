# Protocole — stratégie « reversion » v1 (mean reversion conditionnelle)

Écrit le 14/10/2026, avant le téléchargement complet des données.

**Transparence :** l'idée vient d'un essai de mise au point du script de recherche sur les
deux premiers mois téléchargés (octobre–novembre 2025, qui font partie de la période
d'entraînement) : un favori qui vient de monter de ≥ 0,10 en 6 h y gagnait 4,5 points de
moins que son prix. Aucune donnée de validation ni de test n'a été vue. L'hypothèse est
donc formulée sur l'entraînement et sera jugée sur la validation puis le test.

## Hypothèse

Après un mouvement brusque (≥ 0,10 en 6 h), le marché surréagit : le prix atteint dépasse
la probabilité réelle (et symétriquement après une baisse brusque).

## Règle

- Condition : `|prix du favori − prix du favori 6 h plus tôt| ≥ 0,10`.
- Deux cases (hausse, baisse), toutes catégories confondues ; δ, IC 90 % par bootstrap sur
  les événements et rétrécissement (k = 200) estimés sur l'entraînement seulement.
- Case utilisable si ≥ 150 événements.
- Achat du côté sous-évalué si sa borne basse dépasse prix + 0,01 + frais + 0,02, comme
  pour « calibration ».

## Données, découpage, critères d'adoption

Identiques à `PROTOCOLE_calibration_v1.md` (mêmes périodes, mêmes 5 critères, mêmes
limites). Les deux stratégies étant testées sur les mêmes données, les résultats seront
présentés ensemble, sans retenir uniquement la meilleure.
