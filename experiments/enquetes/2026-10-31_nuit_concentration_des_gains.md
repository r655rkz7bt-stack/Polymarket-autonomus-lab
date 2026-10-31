# 31/10/2026 (nuit) : le gain des mieux classés résiste-t-il à ses plus gros paris ? (famille 2)

Question : parmi les 10 premiers du classement (feuille de mission du 31/10 0 h 48 UTC), que reste-t-il du gain sans les 3 plus gros paris,
sans le meilleur jour, sans le meilleur événement ? Gagnés (paiement) contre attendus (prix payés) : un événement = un tirage.
Script : `experiments/enquetes/scripts/concentration_top_31_10.py` (journaux signés publiés).

## Constat
| Stratégie | paris / événements | gain | sans les 3 plus gros | sans le meilleur jour | payé / attendu (z événements) |
|---|---|---|---|---|---|
| nf_sport_patiente_6_24h_6_12h (n° 1) | 17 / 13 | +231 € (+11,1 %) | +145 | +125 | 16,0 / 15,1 (+0,71) |
| compteur_tweets (champion) | 55 / 14 | +158 € (+26,4 %) | +47 | +80 | 42,0 / 32,8 (+3,17) |
| naive_favorite | 33 / 26 | +156 € (+7,5 %) | +80 | +69 | 30,0 / 30,0 (+0,01) |
| nf_moyen | 53 / 41 | +143 € | +99 | +97 | 49,0 / 48,0 (+0,47) |
| nf_sport_patiente_avant_match | 46 / 41 | +138 € | +67 | +47 | 37,5 / 39,3 (−0,77) |
| nf_sport_non | 82 / 63 | +111 € | +21 | **−29** | 78,0 / 75,0 (+1,18) |
| seismes_marche | 16 / 6 | +92 € | **−12** | **−26** | 12,0 / 9,6 (+1,55) |
| crypto_threshold_prix_bas | 24 / 19 | +85 € | **−215** | **−126** | 9,0 / 9,4 (−0,22) |
| moins_de_cartes | 143 / 142 | +80 € (+6,9 %) | +36 | +5 | 87,5 / 80,3 (+1,22) |

- Seule `compteur_tweets` bat ses prix de façon nette (z +3,17 sur 14 événements) ; mais elle est la première parmi ~40 : z attendu ≈ 2 sans aucun avantage
  (contrôle `selection_multiple`), et son gain sans les 3 plus gros paris tombe de +158 à +47 €. Indice, pas preuve.
- `nf_sport_non` (+111 €) : un seul jour (24/10, +141 €) fait tout le gain ; sans lui −29 €. `seismes_marche` : 6 événements, un seul fait +89 €.
  `crypto_threshold_prix_bas` : +85 € grâce à 3 paris qui font 352 % du gain, 9 gagnés pour 9,4 attendus. Rien de nouveau : déjà connus (obligations « chance »).
- Les favoris (n° 1, `naive_favorite`, `nf_moyen`) gagnent exactement leurs prix : leur classement est du rendement de mises Kelly, pas un avantage.

## Cause / correctif
Aucun défaut de code : la mesure (rendement par mise, z par événement) fait déjà la différence entre chance et avantage ; le classement en euros reste
sensible aux grosses mises (le tableau de bord montre les deux). Rien à corriger.

## Aussi vérifié
- « Remplacer les stratégies éliminées encore configurées » (40 noms) : essai de les passer à `enabled: false` → 5 tests du dépôt échouent
  (`test_favori`, `test_strategies`, `test_strategies_v3` chargent ces stratégies depuis la config) ; **annulé**. Elles n'achètent plus (éliminées) :
  obligation toujours non traitée, à régler en adaptant ces tests (chantier : un test qui ne dépend pas de stratégies mortes).
- Rougeole (piste 8) : 2 mercredis relevés (4 588 le 22/10, 4 852 le 29/10, +264 par semaine). Marchés alignés : « au moins 4 900 d'ici le 31/10 » NON à 0,976 pour 4 852 vus
  (le CDC ne publie plus avant le 05/11), « au moins 5 000 d'ici le 30/11 » OUI 0,01. Rien à acheter ; test impossible avant ~8 mercredis.
- Piste 15 (comptage de nuit d'élection) : `results.sos.ga.gov` (Géorgie) répond 200 et publie un fichier JSON complet
  (`/cdn/results/Georgia/export-2024NovGen.json`, 33 Mo) ; le fichier de 2026 n'existe pas encore (404). `electionresults.ncsbe.gov` 000, Pennsylvanie, Wisconsin, Colorado, CNN : 403/404.
