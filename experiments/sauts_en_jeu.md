# Sauts de prix en match, tennis et e-sport : contrarien ou suiveur ? (28/10/2026, passage du soir)

**Question.** Pendant un match de tennis ou d'e-sport, après un gros saut du prix « vainqueur » (un break, une carte, un set), le prix va-t-il trop loin (acheter le côté
qui vient de baisser) ou pas assez loin (acheter le côté qui vient de monter) ? Le football (22/10, `contrer_football.md`, 1 110 matchs) avait répondu « le marché suit le but et ne revient pas » ;
le tennis et l'e-sport (matchs courts, jeux à points) n'avaient pas été regardés.

**Données.** Gamma `/events/keyset` (séries ATP 10365, WTA 10366, CS2 10310, LoL 10311, Dota 2 10309, Valorant 10369), matchs réglés dont le coup d'envoi tombe entre le 01/08 et le 28/10/2026,
marché « vainqueur » seul à plus de 2 000 $ : 11 158 événements, leurs **échanges réels** (data-api, preneurs ; 11 158 fichiers). Scripts : `experiments/sauts_en_jeu/scripts/releve.py`
(relevé et échanges, ≈ 20 minutes), `analyse.py`. Résultats bruts : `resultats_tennis.txt`, `resultats_esport.txt` (les données sont dans `donnees/`, ignoré par Git).

**Contrôle du règlement.** Le dernier prix échangé du joueur 1 va dans le sens du règlement officiel : 5 627 sur 5 630 (tennis) et 5 126 sur 5 128 (e-sport) ; 153 et 223 matchs réglés 50-50
(2,6 % et 4,2 %) sont écartés des paris (ils auraient payé 0,5 : à compter à part si une piste en sortait, ce n'est pas le cas).

**Méthode.** Après le coup d'envoi (`gameStartTime`), à chaque minute (jusqu'à 200 min en tennis, 170 en e-sport) : saut = variation ≥ J du prix du joueur 1 en `regard` secondes
(prix de moins de 4 minutes). **Un seul saut par match (le premier)**. Entrée = prix du premier échange de preneur dans les 5 minutes qui suivent (saut + délai), plus les frais du marché
(`feeSchedule`) ; aucun regard vers le futur. Contrarien : on achète le côté qui vient de baisser ; suiveur : le côté qui vient de monter. 24 réglages par groupe : J ∈ {0,10 ; 0,15 ; 0,20 ; 0,30},
regard 5 min (délais 1 et 3 min) et 15 min (délai 1 min), deux sens : **48 réglages en tout**. `idea_test.verdict` pour la confiance par événement.

## Résultats (tennis : 5 785 matchs, 3 000 à 4 800 sauts par réglage ; e-sport : 5 352 matchs, 1 100 à 3 900 sauts)
| groupe | sens | rendement (24 réglages → 12 par sens) | meilleure confiance par événement | pire |
|---|---|---|---|---|
| tennis | contrarien | −2,7 % à −9,7 % (12 réglages sur 12 négatifs) | −1,05 | −2,86 |
| tennis | suiveur | −2,5 % à +0,8 % (z des prix +0,5 à +1,6 : le marché ne se trompe pas) | +0,62 | −2,03 |
| e-sport | contrarien | −13,6 % à +0,2 % (J = 0,30 : −13 %, t −2,9 à −3,0) | +0,08 | −2,99 |
| e-sport | suiveur | −4,5 % à −0,4 % (11 réglages sur 12 négatifs) | +0,39 (z prix) | −2,72 |

- Aucun des 48 réglages n'atteint « indice » (`idea_test.verdict` : tous « écartée » sauf un « indice » à t 1,1 sur le premier relevé partiel d'ATP, disparu avec WTA).
- Le contrarien perd : le saut de prix est de l'information (break, carte gagnée), pas un excès ; le suiveur n'a rien à gagner après frais et écart (le prix a déjà bougé).
- Cohérent avec le football (22/10) : le marché de sport suit l'action sans la dépasser.

**Verdict : écartée** (48 réglages regardés, aucun signe stable). À ne pas refaire sans idée nouvelle (par exemple un score en direct plus fin que le prix : pas de source gratuite connue ;
séparer breaks et sets exige l'historique des points).

## Ce que ce test donne en plus
Les **échanges de 11 158 matchs** (août-octobre) peuvent resservir (`experiments/sauts_en_jeu/donnees/`, non versionné : à retélécharger, ≈ 20 minutes avec 8 fils).
