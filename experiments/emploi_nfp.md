# Piste n° 3 (suite) : emploi américain (NFP) et taux de chômage, contre le marché et contre Kalshi (21/10/2026, soir)

**Question** : dans les marchés Polymarket « How many jobs added in <mois> ? » (tranches de 25-50 k) et « <mois> Unemployment Rate » (tranches de 0,1 point),
les prix des tranches à l'approche de la publication (BLS, vendredi 12 h 30 UTC) sont-ils bien calibrés ? Y a-t-il un achat qui gagne après frais aux prix payés ?

**Données** (scripts dans `experiments/emploi_nfp/`, téléchargés dans `donnees/`, ignoré par Git) : 54 événements réglés, 317 marchés (28 « jobs added »
2024-02 → 2026-09, 26 « chômage » 2024-08 → 2026-09), prix OUI du CLOB (12 h pour 301 marchés, 1 h pour 16), 81 794 échanges réels (`data-api`), et pour Kalshi
(`KXPAYROLLS`) 364 marchés réglés avec leur chiffre officiel et 132 historiques horaires de seuils (API publique, y compris `historical/`).
Frais : `feesEnabled` du marché (5 % sur 93 marchés récents, 0 sur les 224 plus anciens).

## Contrôles de données (avant tout calcul)
- **Règlement** : le chiffre officiel publié par Kalshi (`expiration_value`, BLS) tombe dans la tranche Polymarket réglée « Oui » : **27 / 28** événements d'emploi
  (`reglement.py`). Le 28e est **septembre 2025** : officiel +119 k, Polymarket réglé « 0-25 k » (rapport repoussé par la paralysie de l'administration ; Polymarket a
  clos avant la publication). Écarté avec son jumeau « chômage » (dates fausses aussi).
- **Heure de publication** : les dates de fin Gamma sont des placeholders (parfois la veille, parfois +5 ou +12 jours). L'heure vraie = saut du prix du gagnant dans les
  échanges (vérifié sur 45 événements : à ± 1 h de 12 h 30 / 13 h 30 UTC) ; corrigé pour novembre 2025 (16/12), janvier 2026 (11/02), juillet 2024 (02/08).
- 2024-02 → 2024-07 : seulement 100-250 échanges par événement (les plus anciens manquent) : peu d'achats simulables.

## 1. Taux de chômage : bien calibré (écartée)
Gagnés / attendus par tranche de prix, T-6 h à T-168 h : écarts de −1,2 à +1,9 écarts-types, sans sens régulier ; tranche favorite 9 gagnées / 8,1 attendues (T-24 h) ;
« même taux que le mois d'avant » 5/4,5 à 13 cas ; NON 0,05-0,30 à T-24 h +10 % (t événement +1,5, 18 événements) mais −20 % à T-168 h. Rien à garder.

## 2. Emploi (jobs added) : la tranche favorite gagne moins que son prix
| horizon | événements | favori gagne / attendu (prix Polymarket) | z | Kalshi : prix de la même tranche | attendu Kalshi |
|---|---|---|---|---|---|
| T-6 h | 29 (23 chez Kalshi) | 2 / 11,3 | −3,6 | 0,318 | 7,3 |
| T-24 h | 29 (23) | 5 / 11,1 | −2,4 | 0,311 | 7,1 |
| T-72 h | 29 (25) | 4 / 10,6 | −2,6 | 0,287 | 7,2 |
| T-168 h | 27 (20) | 4 / 9,3 | −2,2 | 0,267 | 5,3 |
(le favori = la tranche au prix le plus haut de l'événement à cette heure ; 2 des 3 horizons ne sont pas indépendants.)
- Les deux places de marché sont d'accord entre elles (écart moyen Polymarket − Kalshi par tranche +0,001 à +0,005 ; Brier 0,1644 contre 0,1640 à T-24 h) : le
  prix de la tranche favorite est **plus haut sur Polymarket que sur Kalshi de 5 à 7 points** (0,38 contre 0,31) et, des deux côtés, **trop haut** (4-5 réussites pour 7 attendues chez Kalshi, z ≈ −1,3).
  Une part de l'excès vient du choix (« le prix le plus haut » est biaisé vers le haut, la tranche choisie sur Polymarket y est la plus chère) : c'est pourquoi la mesure honnête est
  celle de Kalshi (non choisie sur son prix) : −1,3 écart-type, pas −2,4.
- Intuition (pas une preuve) : tranches de 50 k pour une surprise typique de ~75 k : même un excellent pronostic ne dépasse pas 25-30 % sur la tranche centrale.
- Aplatir les prix du marché (q ∝ p^g, g réglé sur la 1re moitié) : meilleur g 0,30-0,45 (hors échantillon : mieux à T-6 h et T-168 h, pire à T-24 h et T-72 h) : pas fiable.
- **NON sur la tranche favorite, aux prix des vrais échanges** (premier échange dans les 2 h après la décision, frais du marché) : T-6 h +32,8 % (15 paris, t événement +1,95,
  13 mois sur 15), T-24 h +20,1 % (15, t +0,84), T-72 h +50,1 % (9, t +2,19) ; coût moyen du NON 0,60. NON si Polymarket dépasse Kalshi de 3 à 5 points : T-72 h +56 à +60 %
  (8-10 paris, t +3,4 à +3,8), T-24 h −5 % à +24 % (8-16 paris, sens non régulier).
- Réglages regardés : 4 horizons × 4 plages de prix × OUI/NON × 3 familles (~150 cellules de `analyse.py`) + 3 horizons × 4 filtres favori + 6 filtres Kalshi.
  Un z de −3 parmi ~50 cellules de calibration est ce que le meilleur de 50 donne par hasard (≈ −2,3).

## Verdict : **indice** (fantôme `jobs_favori_non`)
Pas « retenue » : 29 événements, un seul marché (même sujet, même mécanisme), la mesure non biaisée par le choix (Kalshi) donne z ≈ −1,3, les paris aux prix payés ne sont que 9-15
par réglage (les NON des tranches centrales échangent peu), et ~200 cellules ont été regardées. Mais les trois mesures vont dans le même sens, l'explication (largeur des tranches) est
simple, et le test coûte un fantôme. Stratégie : `jobs_favori_non` (classe `JobsFavoriNon`, `config/strategies.yaml`), achète le NON de la tranche favorite à 25-70 % de 4 à 72 h avant
la publication, estimation « juste » = 0,6 × le prix (mesuré 4-5 / 7-11 attendues), Kelly ¼.
À confirmer sur les prochaines publications (NFP d'octobre : vendredi 6/11/2026 à 13 h 30 UTC ; les tranches existent déjà).

## Limites et suite
- Le fantôme dépend de la date de fin Gamma (placeholder, souvent la veille ou le lendemain du rapport) : la fenêtre 4-72 h est large exprès ; après la publication le prix du favori
  sort de la bande 0,25-0,70 et la stratégie se tait.
- Pas de prévision indépendante (consensus Bloomberg, ADP, Cleveland) : restent des idées neuves. Une référence Kalshi publique existe (l'API `historical/` est limitée : ~3 s par appel).
- Le rapport est aussi mensuel pour les « Powell says » (mentions) : hors sujet ici.
