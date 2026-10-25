# Ordres posés (mode « patient ») sur les favoris de sport : sélection adverse en cours de match (25/10/2026, soir)

Question : un ordre posé 1 cran au-dessus du meilleur acheteur (`limit_ticks`) rapporte-t-il autant que l'achat immédiat sur les mêmes favoris de sport ?
Idée de départ : enquête du 21/10 (`enquetes/2026-10-21_posees_sous_la_plage.md`, indice t −1,2 sous 0,80). Ici : tous les prix, tous les paris, données neuves.

## Données et méthode
- Journaux signés publiés (`published_data/`) : toutes les stratégies `nf_*`, `naive_*` et le principal, **un seul compte par jeton** (les paris communs à plusieurs fantômes ne sont pas comptés plusieurs fois) : 1 145 paris réglés, 16-25/10.
- Gain réel du journal (frais compris, règlement du journal). Comparaison au prix payé : gagnés contre attendus (z de Bernoulli) et rendement unitaire (`paiement/prix − 1`, t de Student). Pas de modèle, pas de regard vers le futur : on lit ce qui a été payé.
- Script : `experiments/enquetes/scripts/ordres_poses_en_jeu_25_10.py`.

## Résultat
| groupe | paris | gain | rendement | gagnés / attendus | z |
|---|---|---|---|---|---|
| tous | 1 145 | −1 001 € | −1,6 % | 970,5 / 990,5 | −1,8 |
| **ordres posés** | 239 | −917 € | **−6,8 %** (unitaire −7,4 %, t −2,4) | 190,0 / 205,0 | **−2,8** |
| achats immédiats | 906 | −84 € | −0,2 % (t −0,8) | 780,5 / 785,6 | −0,5 |

Par événement (paris liés regroupés) : posés −6,9 % (229 événements, t −2,3), immédiats −0,4 % (771, t −0,3).
Tranches de prix : posés 0,80-0,85 −12,4 % (69 paris, z −2,3), 0,90-0,95 −8,2 % (58, z −2,1) ; immédiats −2,6 % et +1,6 %.

**Où ça se passe** :
- en cours de match (`depuis_coup_d_envoi_h` ≥ 0) : posés **−9,2 %** (163 paris, t −2,5, z −2,9) contre +0,6 % pour les immédiats (330) ;
- avant le match : posés +3,9 % (**13 paris seulement**, rien à conclure), immédiats −0,7 % (139).
- **Hors échantillon** (paris du 22 au 25/10, après l'indice du 21/10) : posés **−12,7 %** (117 paris, t −2,8, z −3,5) contre +0,1 % (369) ; avant le 22/10 : posés −2,2 % (122), immédiats −1,9 % (537) : l'effet est apparu surtout les 24-25/10 (32 + 11 paris, z −3,5 et −2,5), il n'était pas net avant.
- Sans les 3 pires paris des ordres posés : −445 € sur 13 051 € misés (toujours négatif).

## Lecture
Le simulateur sert un ordre posé seulement quand le marché « passe au travers » du prix (`execution_simulator.simulate_resting_*`). Pendant un match, le prix d'un favori ne descend jusqu'à notre ordre que si quelque chose est arrivé (but encaissé, blessure) : on est servi quand on a tort, jamais quand le prix remonte (sélection adverse). Avant le match, rien de tel : le prix bouge peu. Ce n'est pas un défaut de code (le fantôme paie ce que le carnet donne), c'est un coût réel du mode patient en jeu.

Réserves honnêtes : (1) environ dix découpages regardés (mode, tranches de prix, jours, en cours/avant, hors échantillon) : le z de −3,5 hors échantillon est la coupe qui compte, les autres l'accompagnent ; (2) 9 jours de données, un seul régime de matchs (octobre) ; (3) l'effet n'était pas net avant le 22/10 ; (4) la championne `nf_sport_patiente` perd donc son gain sur ses ordres posés : sur les 32 jetons qu'elle partage avec le principal depuis le 21/10, −13,8 % pour le principal, −13,1 % pour le fantôme (même résultat, la copie est fidèle) alors que les 54 autres paris de la championne, que le principal n'a pas copiés (il suivait alors une autre championne), font +7,5 %.

## Les autres familles de stratégies (même méthode, `enquetes/scripts/ordres_poses_toutes_25_10.py`)
Un compte par jeton, ordres posés contre achats immédiats de la même famille : `contrer_crypto*` +14,2 % (88) contre +65 % (46) : rien de net ; `news_momentum*` −4,9 % (95) contre −17 % (19) ; `crypto_threshold*` 4 posés seulement ;
**`meteo_prevision*` : posés −23,1 % (69 paris, t −1,9, z −1,7) contre −5,2 % (77) : même signe que le sport, indice faible, à surveiller** (météo en `zero_fees` : l'écart n'est pas un effet de frais). Hors favoris de sport : −8,4 % contre −2,0 % (t −1,0). L'effet fort est donc propre aux favoris de sport (235 posés, z −2,7).

## Verdict : **indice** (un coût, pas un avantage)
- Pas de stratégie « contre » les ordres posés (on ne sait pas tester l'inverse).
- Fantôme-sœur `nf_sport_patiente_avant_match` : mêmes paramètres que la championne, mais `heures_min: 0` (pas d'ordre posé une fois le match commencé). À juger contre la championne sur la même période ; il y aura peu de paris (13 avant match en 9 jours de toute l'arène), donc patience : l'arène ne dira rien avant plusieurs semaines. Une comparaison plus utile : `nf_sport` (achat immédiat, +2,4 %, z 0,2) contre `nf_sport_patiente`.
- Règle pour la suite : une variante « patiente » d'un favori n'est lancée qu'avec un filtre avant-match.
