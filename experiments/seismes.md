# Séismes : « plus gros séisme du jour » et « combien de séismes cette semaine » (24/10/2026)

Chantier n°6 de `experiments/CHANTIERS.md` (USGS), devenu une piste à tester. **Verdict : indice → fantôme `seismes_marche`** (quart de Kelly).
Scripts : `experiments/seismes/scripts/` (`usgs.py` catalogue, `releve.py` marchés et échanges, `hebdo.py`, `jour.py`, `tables.py`) ;
relevés versionnés dans `experiments/seismes/releves/` (catalogue USGS M ≥ 5 depuis 2014 : 22 526 séismes ; 122 événements Polymarket).

## Les marchés
- **Jour** : « What will the biggest earthquake be on <date> ? », 6 tranches (sous 5,3 / 5,3-5,4 / 5,5-5,6 / 5,7-5,8 / 5,9-6,0 / 6,1 ou plus), jour UTC,
  magnitude USGS arrondie au dixième ; 27 jours réglés (25/09 → 22/10), **sans frais** (`zero_fees`), 240-900 $ de liquidité.
- **Semaine** : « How many 5.5 (ou 6.5) or above earthquakes worldwide <lundi> - <dimanche> ? », 7 à 9 tranches de compte, semaine du lundi 00 h au dimanche 24 h
  **heure de l'Est**, 57 événements réglés depuis décembre (dont 28 en ≥ 5,5), frais 5 % × p(1 − p) (`weather_fees`).
- Les deux se règlent sur le catalogue USGS, lisible en direct et sans clé.

## Contrôle du règlement (ma lecture redonne-t-elle le résultat officiel ?)
- Jour : **26 sur 27** (le 27/09 : maximum 5,3 chez moi, « sous 5,3 » chez Polymarket, magnitude révisée entre-temps).
- Semaine : **47 sur 57**. Les 10 écarts sont **tous** des marchés ≥ 5,5 où Polymarket a compté **un séisme de plus** que le catalogue d'aujourd'hui
  (1 fois 3 de plus) ; les 29 marchés ≥ 6,5 sont tous bons. Cause non trouvée (fenêtre horaire, arrondi et type de magnitude essayés, rien de régulier) : probablement
  des magnitudes révisées à la baisse depuis le règlement. Les paris simulés sont réglés sur le résultat **officiel du marché**, pas sur mon compte.

## Modèle (rien de futur)
- Jour : maximum déjà vu à l'heure de décision + part des jours des 3 dernières années sans séisme ≥ x dans les heures restantes (x = 5,25 / 5,45 / 5,65 / 5,85 / 6,05).
  **Étalonnage hors marché** sur 660 jours (2025 → 22/10/2026, décision à 12 h UTC) : observés / attendus par tranche 111/124,5, 96/100,1, 117/114,0, 96/91,6, 92/85,4, 148/144,4
  (|z| ≤ 1,6) ; le modèle est calibré.
- Semaine : compte déjà vu + binomiale négative (Gamma-Poisson) calibrée sur les 156 semaines précédentes. Variance = 3,1 × la moyenne à ≥ 5,5 (répliques), 1,2 × à ≥ 6,5 :
  un Poisson simple sous-estimerait les queues.

## Contre le marché d'abord (perte log, dernier échange des 6 heures précédentes)
| Jour : heure de décision | cas | modèle | marché |
|---|---|---|---|
| 6 h UTC | 57 | 0,350 | 0,499 |
| 12 h | 89 | 0,264 | 0,322 |
| 18 h | 91 | 0,181 | 0,288 |

Semaine ≥ 6,5 : modèle 0,13-0,36 contre marché 0,14-0,35 (égalité). Semaine ≥ 5,5 : égalité de J-6 à J-3, **le marché meilleur à J-2 et J-1** (0,31/0,33 contre 0,36/0,43) :
il connaît le compte presque exact de la fin de semaine, y compris l'écart de comptage ci-dessus. Le dernier échange d'un marché mince peut dater de 6 heures : cette comparaison avantage le modèle.

## Achats simulés aux prix réellement payés (1er achat dans les 2 h après la décision, écart ≥ 0,03, billets 0,03-0,97)
| | paris | événements | rendement | t par événement | z des prix |
|---|---|---|---|---|---|
| **Jour**, 6/12/18 h, OUI et NON, écart ≥ 0,03 | 27 | 13 | **+69 %** | 1,15 | 2,5 |
| Jour, NON seulement | 11 | 9 | +53 % | 2,72 | 2,2 |
| Jour, écart ≥ 0,10 | 12 | 9 | +139 % | 1,74 | 2,5 |
| **Semaine ≥ 5,5**, frais compris | 181 | 27 | **+24 %** | 2,05 | 1,4 |
| Semaine ≥ 5,5, OUI seulement | 79 | 25 | +51 % | 1,79 | 2,5 |
| Semaine ≥ 5,5, J-3 à J-6 | 104 | 25 | +37 % | 1,53 | 2,2 |
| Semaine ≥ 6,5 | 96 | 28 | +7 % | 0,58 | −0,2 |

Robustesse de la semaine ≥ 5,5 (écart ≥ 0,03, frais compris) : référence sur 3 ans +24,1 % ; sur 1 an +18,4 % ; sur 6 ans +24,8 % ; **sans les 3 meilleurs paris +8 %** (1 an : +2 %) ;
1re moitié des semaines +37 %, 2e moitié +13 % ; mois : 5 gagnants sur 7. Le gain vient des queues (billets OUI à 0,05-0,30 sur des comptes bien plus hauts que la normale
après un séisme majeur et ses répliques) : le marché les cote trop bas, mais ce sont peu de paris gagnants. Les OUI de tranche voisine du compte déjà vu perdent.

## Verdict : indice, pas « retenue »
- 27 jours seulement côté jour (13 avec un achat possible), ~30 découpages regardés (heures, côtés, seuils d'écart, 3 références, 2 magnitudes) : le t par événement reste sous 1,5
  (jour) ou 2,05 (semaine) avec une sélection de découpages ; sans les 3 meilleurs paris, la semaine tombe à +8 %.
- Marchés minces : échange médian 8 $, carnets larges (OUI 0,15 / 0,75 vus le 24/10) ; ce que l'on peut vraiment acheter reste à mesurer dans l'arène.
- Mais : modèle étalonné sur 660 jours, calibré, qui bat le dernier prix du marché de 0,05 à 0,11 de perte log côté jour, et une source officielle lisible en direct.
→ **fantôme `seismes_marche`** (quart de Kelly, `jamais_retirer` : des jours sans marché utile ne doivent pas le faire retirer), pas dans `validated_strategies`.
Essai en direct le 24/10 à 05 h UTC : lecteur USGS (61 séismes en 10 jours), 16 tranches de la semaine rattachées (par exemple « plus de 13 séismes ≥ 5,5 » : modèle 0,68 contre prix 0,38-0,42).

## Limites et suite
- Plage horaire testée : jour entre 6 h et 23 h UTC ; semaine entre 0,5 et 6,6 jours avant la fin (pas de test avant 6 h : la stratégie s'abstient).
- Le comptage ≥ 5,5 de Polymarket dépasse parfois le mien d'un séisme : si le fantôme perd sur les tranches ≥ 5,5, regarder ce décalage avant tout.
- À refaire : `tables.py` chaque mois (tables du modèle) ; rejouer le test avec les ~25 jours de plus qui seront réglés d'ici un mois ; marchés mensuels
  (« How strong … by <mois> », « Where will a 6.0+ … ») et « Another 7.0+ earthquake by… » non testés (peu d'événements).
