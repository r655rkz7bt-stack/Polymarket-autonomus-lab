# Enquête du 21/10 (passage de ~15 h UTC) : copie des ordres posés, deux camps, verdict trompeur

Famille n° 4 du jour (21 mod 6 + 1) « le filtre ne filtre pas » + familles 1 et 2. Aucune enquête obligatoire dans la feuille de mission.

## 1. `copie_fidele` : « 4 copies à 100 % sur une exécution partielle » = faux positif (corrigé)
Constat : Mannarino (19/10), Lynn Vision (20/10 04 h ; 21/10 09 h 02 et 09 h 07) : le principal obtient exactement les parts du fantôme (33,34 ; 22,56 ; 14,28).
Cause : ce sont des **ordres posés** qui se remplissent en plusieurs exécutions (le fantôme en a 3 à 5 par ordre) ; l'ordre du principal, trois fois plus petit,
est servi en entier par la première. Cumul sur tout l'ordre : Lynn Vision 20/10 principal 33,34 contre 104,67 (32 %) ; 21/10 principal 36,84 contre 119,43 (31 %)
pour une part prévue d'un tiers : **la copie est proportionnelle**. Le contrôle comparait exécution par exécution.
Correctif : `enquete._smaller_order` compare les parts cumulées par identifiant d'ordre posé (le principal préfixe « P » au identifiant du fantôme). Test :
`test_partial_fill_of_a_smaller_resting_order_is_not_a_full_copy` (cas réel + cas où le principal prendrait autant que le fantôme : toujours signalé).

## 2. `deux_camps` : re-mesure sur tout l'historique (promesse du 20/10 : « à refaire à 30 paires »)
`scripts/deux_camps_21_10.py` : 9 paires closes (hors `market_*`) dans 9 portefeuilles, mais **3 matchs seulement** (Safiullin-Shimabukuro, Clarke-Sakellaridis,
Falcons-BetBoom). Premier camp : 0 gagné sur 9, −630 € ; deuxième camp : 9 gagnés sur 9, +66 € pour 372 € misés ; paire −564 €. Le deuxième achat se fait
justement quand le favori s'est effondré, donc le premier camp perd toujours par construction. 3 matchs ne suffisent pas pour bloquer le camp opposé : le contrôle reste « à regarder ».

## 3. `idea_test.verdict` disait « retenue » à une série de victoires que les prix expliquent (famille 2)
Piste classements : 12 gagnés sur 12 à 0,78-0,95 → t par événement +6, 9 mois sur 9 : « retenue ». Aux prix payés, P(tout gagner) = 23 %. Quand tout gagne, la variance
des gains est quasi nulle et le t ne vaut rien. Correctif : `z_prix` dans `verdict` (voir `experiments/classements_status_quo.md` § 3). Les anciens verdicts « retenue »
des pistes (tweets, mots, NON de tweets) ont des centaines de paris avec des pertes : à relire si besoin avec `z_prix` (non refait ici).

## 4. Autres constats « à regarder » revus
- `estimation_perimee` : 21 achats de fantômes à estimation > 8 % au-dessus de l'écart habituel, tous des modèles (tweets, météo, tennis du 20/10 matin avant le correctif
  de 14 h 27) ; le principal : 3 achats d'avant le correctif. Rien de nouveau.
- `mises` : 7 mises de fantômes à 25-30 % du capital (nm_court, nf_court_prix_haut…), toutes des fantômes (jamais le principal) : pas un défaut du principal.
- `chance` : naive_favorite et nf_court gagnent en euros (+118, +190) mais −2,1 % par mise ; `nf_sport_patiente_2crans` : 3 paris = 114 % du gain. Déjà connu (confiance sur le rendement par mise).
