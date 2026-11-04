# 04/11/2026 (matin) : d'où vient la perte du principal, et le « prix » Gamma d'un carnet vide (familles 5 et 2)

**Questions.** (1) Le principal est à 688,82 € (−311 € depuis le départ) : d'où vient la perte, est-ce un défaut de code ou le tirage ?
(2) Les cinq premières de l'arène (nf_sport_prix_haut, nf_court, nf_sport, nf_sport_non, naive_favorite) ont-elles un avantage sur leurs prix ?

**(1) Principal par stratégie copiée** (journal signé, 501 paris réglés, −311,8 €, `charge_fantome.charger`) : `nf_court` −145 € (18 paris, 14 gagnés pour 15,9 attendus, 4 paris perdus : −55, −57, −48, −28 €),
`meteo_prevision` −58 € (39 paris, ancienne promotion à t 0,61, déjà documentée), `nf_sport_patiente_prix_850_875` −28 €, `moins_de_cartes` −26 € (79 paris, 40 gagnés pour 44,9), `nf_sport_18_24h` −22 €.
Gagnantes : `nf_tennis_prix_bas` +11, `nf_sport` +12, `compteur_tweets` +10 (38 paris, 26 gagnés pour 24,4). Aucun pari sans fantôme, aucune mise démesurée : la perte est le tirage de favoris (frais + 2 à 4 paris
perdus au mauvais moment) et l'ancienne météo, pas un défaut de code. `nf_court` relu pari par pari (`scripts/principal_nf_court_04_11.py`) : les 18 paris du principal datent TOUS du 18/10 (06 h 28 → 18 h 05 UTC), c'est-à-dire d'avant la copie fidèle (défaut du 18/10,
PR #76 : le principal relançait la stratégie avec son argent). Rapport de mise principal / fantôme de 0,16 à 3,02 selon le pari (médiane ≈ 1,5, alors que son capital était déjà plus petit) ; les quatre paris perdus
(−55, −57, −48, −28 €) étaient misés 1,6 à 3 fois plus gros que chez le fantôme. C'est donc le défaut déjà trouvé et corrigé, pas le renfort ni la copie actuelle (copie fidèle vérifiée le 04/11 à 1 h : 233 sur 233).
Le −145 € est une perte historique, pas un problème en cours.

**(2) Les cinq premières contre leurs prix** (`concentration_top_31_10.py`) : payé / attendu 512,0/507,7 (z +0,64), 539,0/537,4 (+0,21), 808,5/799,2 (+0,93), 90,0/87,4 (+0,92), 48,0/47,4 (+0,30).
Aucune ne bat ses prix. `nf_sport` devient négative sans son meilleur jour (02/11 : +248 € → −77 €), `nf_sport_non` sans le 24/10 (+143 → +3). Le classement mesure des mises, pas un avantage (constat déjà fait le 31/10 et le 01/11).

**(3) Défaut de lecture trouvé** (sans conséquence sur le code, à retenir pour les tests) : `outcomePrices` de Gamma pour un marché mince est le MILIEU du carnet, même si un côté est vide.
« Republican governors < 22 » : prix affiché 0,73, acheteur le plus haut 0,48, vendeur le moins cher 0,98. Une « incohérence » à 25 points avec les 26 courses de gouverneur (qui donnent ≈ 20 sièges républicains)
n'était donc pas exploitable : l'achat coûtait 0,98. `sieges_coherence` n'est pas touchée (elle achète aux vrais vendeurs : 0,39 pour 0,376 affiché). Les relevés de `coherence_sieges.md` sont des prix Gamma de tranches minces :
tout écart doit être refait aux prix du carnet avant d'être appelé « avantage » (ajouté à `docs/ROUTINE_CHERCHEUR.md`, astuces).

**Résultat.** Aucun défaut de code, rien à corriger. Contrôles déjà en place : `copie_absente`, `copie_prix_paye`, `estimation_gonflee`.
