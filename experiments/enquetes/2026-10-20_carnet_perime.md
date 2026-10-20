# Enquête du 20/10/2026 : mises gonflées par un carnet périmé, et autres défauts de mesure

Demande d'Etienne : chercher « les problèmes comme celui du principal qui augmentait les mises ».
Données : journaux publiés (branche data, 20/10 vers 14 h UTC), 101 fantômes + principal.

## 1. Estimation calculée sur un carnet périmé → mise trop grosse (corrigé)
**Constat.** Le 20/10 à 07 h 09, nf_sport_patiente achète « Moyuka Uchijima » à 0,817 en
l'estimant à 0,9785 (écart de 16 points ; habituel : 5). Mise : 278 parts, 229 €, 19 % de son
fantôme. Le principal la copie : **72 €, 8,9 % de son capital**, son plus gros pari du jour.
**Cause** (`main._execute`). La stratégie calcule son estimation (milieu du carnet + 5 points) sur
le carnet lu AU DÉBUT du cycle (milieu 0,93) ; l'achat s'exécute sur le carnet RELU juste avant
(vente à 0,817 : la joueuse venait de perdre du terrain). Le contrôleur revérifie les règles, mais
rien ne vérifiait que le prix avait bougé : une chute passait pour une aubaine, avec une mise
calculée sur l'ancien prix.
**Ampleur.** 38 opérations clôturées des stratégies « favori » dans ce cas, mises 46 % plus
grosses en moyenne (81 € contre 55 €). Résultat pour l'instant pas pire que les autres
(−1,2 % par mise contre −2,3 %) : c'est un défaut de RISQUE (taille de mise), pas encore une perte
mesurée.
**Correctif.** `main._price_drop` + `settings.yaml → relecture` : si le prix de vente a chuté de
plus de 3 centimes pendant le cycle, pas d'achat ; la stratégie redécide au cycle suivant avec un
carnet frais (jambes d'arbitrage exemptées). Tests : `test_price_crash_during_the_cycle_postpones_the_buy`,
`test_a_one_cent_dip_during_the_cycle_still_trades`.
**Contrôle automatique** : `enquete.estimation_perimee`.

## 2. La championne n'a plus d'avantage mesurable depuis le 19/10 (obligation pour le chercheur)
nf_sport_patiente : +256 € sur 81 opérations, mais **le 18/10 fait 95 % du gain** (+242 € ;
27 gagnés pour 23,8 attendus). Du 19 au 20/10 : 29 gagnés pour 28,9 attendus, rendement +0,2 % par
mise. Le principal suit donc un gain venu d'une journée. Pas encore de cause : à enquêter (sport,
heure, ordre posé ou non, taille des mises ce jour-là) — contrôle `enquete.chance`, grave tant que
le principal la copie.

## 3. Une fille n'est pas jugée sur la même période que sa mère
Toutes les filles de nf_sport_patiente nées le 19/10 perdaient (prix_haut −370 €, demi_mise −189 €,
large −119 €) alors que la mère gagnait… sur sa vie entière. Sur la même période, la mère ne gagnait
presque plus (+0,8 % à +1,5 % par mise, voire −1 %). Comparer une fille à sa mère entière mélange
deux périodes. Contrôle `enquete.filles_periode` : la comparaison sur la même période.

## 4. « Demi-mise » ne fait pas les mêmes paris que sa mère
nf_sport_patiente_demi_mise devait faire les mêmes paris en moitié moins gros : 9 paris communs sur
26, et parfois PLUS gros que la mère (G2 Ares : 155 parts contre 119 ; 105 contre 1,2). Les
fantômes n'ont pas le même argent disponible ni les mêmes positions ouvertes, et un ordre posé se
remplit selon la quantité affichée : « même stratégie, autre mise » n'isole pas l'effet de la mise.
À garder en tête avant de conclure sur une fille « mise ». Contrôle `enquete.meme_pari_prix_differents`.

## 5. Plage de prix contournée par les ordres posés
nf_sport_patiente_prix_haut (0,875-0,95) a acheté G2 Ares à 0,79 : la plage est vérifiée sur le
prix de VENTE, l'ordre est posé 1 cran au-dessus du meilleur ACHETEUR ; dans un carnet très écarté
(0,78 / 0,88), le pari est pris bien sous la plage — et justement dans les marchés où l'ordre posé
est servi quand le prix s'effondre (perte de 66 €). Contrôle `enquete.filtre_prix`.

## 6. Copie à 100 % sur les exécutions partielles
Deux fois (19/10 Mannarino, 20/10 Lynn Vision), le fantôme n'obtient qu'une partie de sa mise et le
principal, qui devait n'en copier que 35 %, obtient autant que lui : sur les marchés peu liquides,
le principal pèse plus lourd que prévu. Faible pour l'instant (2 cas). Contrôle `enquete.copie_fidele`.

## Vérifié sans défaut
Depuis la copie fidèle (18/10, 21 h 38) : 33 achats du principal, tous avec leur jumeau dans le
fantôme copié ; plafond de 10 % par mise respecté.
