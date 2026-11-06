# 06/11/2026 soir — « 200+ posts de Trump du 6 au 13/11 » : le modèle dit 0,966, le marché 0,26

**Question.** Le constat `estimation_perimee` du jour cite un achat neuf : à 17 h 05 UTC, `compteur_tweets_72_168h` et sa fille 12-18 h achètent
« 200+ » à 0,279 sur une estimation de **0,966** (18 € chacune). C'est le même marché que le pari du 04/11 (0,724 sur 0,968, relu le matin et le
04/11 dans `truth_rythme_long.md`). Le marché est passé de 0,72 à 0,26 en trois jours : défaut du code, ou le marché a vu quelque chose ?

**Vérifié (calculs refaits sur XTracker, `experiments/silence_trump/scripts/`).**
- Marché `6625358` relu sur Gamma : bien « Trump 200+ Truth Social posts, 6-13 novembre » (fenêtre XTracker 06/11 17:00 → 13/11 16:59 UTC) ;
  carnet du journal = prix réellement payé (0,27 × 4,14 puis 0,28 × 58,9) : ni carnet périmé ni mauvais rattachement.
- **Ce que le modèle voit** : 605 posts du 30/10 au 06/11 (semaine de l'élection), 811 sur 14 jours ; ce que fait Trump depuis : **34 posts du 03/11 17 h au 06/11 21 h**
  (9, 4 et 7 par jour les 04, 05 et 06/11 ; rafale de 167 posts en 2 heures le 03/11 vers 12-13 h UTC), et **3 posts** depuis le début de la fenêtre du marché (4 heures).
- La moyenne de 14 jours est portée par une seule rafale : estimation « formule de production » 505 posts attendus pour la semaine (P(200+) = 0,996),
  « 7 j + 84 j » 409 (0,981), 84 jours seuls 212 (0,545), 72 h seules 72 (0,000).
- **Fréquence de base** (42 semaines alignées sur le jeudi 17 h UTC, 15/01 → 05/11) : médiane 143, moyenne 161 (la semaine de 650 tire), **10 semaines sur 42 (24 %) à 200 ou plus** ; le marché à 0,26 est la fréquence de base.

**Le rythme court prévoit-il mieux ?** (`rythme.py`, départs toutes les 6 h depuis février, ≈ 38 semaines indépendantes, log-vraisemblance de la semaine suivante, binomiale négative)

| rythme utilisé | dispersion 12 | dispersion 4 |
|---|---|---|
| 7 j + 84 j (50/50) | **−6,19** | **−5,78** |
| 7 j + 14 j (production) | −6,35 | −5,93 |
| 7 jours | −6,44 | −6,09 |
| 72 h | −7,61 | −6,66 |
| 48 h | −8,09 | −6,98 |

Le silence de 72 h **ne prévoit pas** la semaine suivante (72 h et 48 h sont les pires) : après un silence de 72 h sous 30 % du rythme de 84 jours, la semaine suivante vaut une médiane de 122 posts
contre 128 attendus par le rythme long (40 décisions, 13 jours distincts, trois épisodes : mai, début août, mi-août). Ce n'est donc **pas** un nouveau régime de silence : la prévision correcte est la moyenne longue, pas le rythme court.

**Calibration du modèle de production sur « ≥ 200 »** (`robuste.py`, 732 départs depuis mai, ≈ 26 semaines) : dit < 10 % → réel 14 % ; 10-50 % → réel 20 % (dit 26 %) ; **50-90 % → réel 39 % (dit 62 %, 10 semaines)** ;
il n'a jamais dit plus de 0,90 en 2026 avant la rafale du 03/11. Brier moyen (seuils 100-300) : fréquence des 12 dernières semaines 0,133, 7 j + 84 j 0,137, **production 0,151**.
Au seuil 200 seul : production 0,202, 7 j + 84 j 0,186, médiane de 12 semaines (d 6) 0,185. Différences petites (26 semaines) : même sens que `truth_rythme_long.md` (indice), rien de neuf à promouvoir.

**Verdict : aucun défaut de code.** Une estimation haute au lendemain d'un record est le défaut de modèle déjà documenté le 04/11 (14 jours = une rafale) ; ce passage ajoute deux constats :
1. le rythme court n'est pas la réparation (le silence ne se prolonge pas en moyenne) ; la réparation reste le rythme long et la fréquence de base ;
2. la fille 72-168 h (et sa fille 12-18 h) rachètent le même billet à 0,279 : **10 achats de fantômes, 796 € misés sur ce seul marché** (dont 4 € copiés par le principal). Un seul tirage, réglé le 13/11 ; avec 3 posts en 4 heures, il ressemble à une perte de l'ordre de 800 € fictifs répartis sur 10 portefeuilles.

**Pas de correctif de code** : changer le rythme de la mère `compteur_tweets` (champion, copiée par le principal) sur 26 semaines indépendantes serait un réglage de plus choisi après coup ; l'expérience correcte tourne déjà (`compteur_truth_rythme_long_audace`, estimation 0,813 le 04/11).
À relire au règlement du 13/11 : si « 200+ » perd comme le suggèrent les 3 posts de départ, c'est la deuxième semaine de suite où la formule de production surestime après une rafale ; alors proposer de passer la mère à 7 j + 84 j (mère = `compteur_tweets`, config seulement).

Scripts : `experiments/silence_trump/scripts/{releve,rythme,robuste}.py` (relevé XTracker du 15/01 au 06/11, 6 762 posts, dans `donnees/`, ignoré par Git).

## Contrôle à la main du même passage (famille 4, comparaisons)
Recouvrement des jetons achetés entre fantômes (136 fantômes de 15 jetons et plus) : 21 paires partagent 90 % ou plus de leurs jetons, toutes des **filles contenues dans leur mère** par construction
(`compteur_tweets_72_168h` ⊂ `compteur_tweets` 46/46 ; `nf_sport_patiente_prix_850_875_avant_match` ⊂ `nf_sport` 18/18 ; `moins_de_cartes_lol` ⊂ `moins_de_cartes` 17/17…) ; pas de paire de deux stratégies indépendantes qui achètent la même chose.
Conséquence déjà connue (`docs/METHODE.md`, un compte par jeton pour toute comparaison) : les classements comptent plusieurs fois le même tirage, en particulier le groupe `compteur_*` (10 portefeuilles sur le billet de Trump ci-dessus).
