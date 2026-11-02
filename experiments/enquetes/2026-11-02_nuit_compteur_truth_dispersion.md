# 02/11/2026 (nuit) : « 200+ à 93 % » sur un rythme record (famille 3, avec un contrôle de la famille 2)

**Contrôle à la main (famille 3 : la donnée est-elle celle qu'on croit ?)** : 10 paris tirés au hasard de `compteur_tweets` (graine 2) relus sur Gamma `/markets/<id>` :
question, tranche et règlement. 10 sur 10 conformes (9 paris sur Musk/Trump, tranche et dates de la question = celles du compteur, résultat Gamma = `SETTLE` du journal).
Remarque sans gravité : 2 règlements arrivent avant la fin de la fenêtre (compteur qui ne décroît pas), normal.

**Constat « à regarder » mené jusqu'au bout** : `estimation_perimee` de `compteur_tweets_12_18h` (estimé 0,929, payé 0,697, mise 195 €). Ce n'est pas un carnet périmé :
le prix est celui du carnet (niveaux 0,69 et 0,70), c'est l'**estimation** qui est excessive. Cause : `references.tweet_bucket_probability`, rythme 7 j/14 j sur un
rythme récent record (≈ 100 posts/jour), loi binomiale négative de dispersion 12 trop étroite pour les semaines de Trump.
Chiffres : `experiments/truth_social_dispersion.md` (calibration sur 38 semaines, log-score meilleur à dispersion 5-8 à toutes les heures de la fenêtre,
contre le marché +22 % à dispersion 5 contre +14 % à 12).

**Défaut de code ?** Non : la formule fait ce qu'elle dit ; c'est un réglage global (12, choisi sur 7 comptes) qui ne convient pas à Trump. Rien du noyau.
Le principal ne copie ce pari qu'à sa part (11 € le 31/10 pour la même famille). Aucun correctif de la mère : on teste d'abord.

**Action** : fantôme `compteur_truth_dispersion_6_audace` (dispersion 6, Kelly entier), à comparer à `compteur_truth` à période égale. Pas de contrôle ajouté à `enquete.py` : le seul
cas extrême (1 achat) est déjà levé par `estimation_perimee`.

**Vérifié, rien trouvé** : les trois obligations « 80/20 » (filles de `contrer_crypto_audace`, `crypto_non_10_20` 24-72 h, `contrer_crypto_patiente` 24-72 h + non).
`crypto_non_10_20` 24-72 h : 19 paris / 10 événements / 5 jours de règlement, 7 gagnés pour 2,7 attendus (z +2,89), +58 %, mais les 7 gains tombent les 30-31/10 (pari à la baisse
corrélé au cours, cf. `crypto_pourquoi`), tranche choisie parmi 3 après coup, et sur le passé (8 974 marchés) cette famille ne rend rien. Refusées, comme hier.
