# Posts Truth Social de Trump (marchés « # of Truth Social posts ») — 25/10/2026

**Verdict : indice faible → fantôme `compteur_truth`** (fille de `compteur_tweets`, Trump seulement). Contredit en apparence « Trump ≈ 0 » du 21/10 (`tweets_filles.md`) :
le gain n'existe que sur les échanges minces (moins de 100 parts en 2 h) ; là où le carnet réel suivrait, il est de −5 %.

## Données
- 70 événements réglés (février 2025 → octobre 2026, 11 tranches de 20 posts chacun, fenêtre de 7 jours du mardi 12 h ET au mardi suivant), 60 utilisables (28 jours d'historique avant le début) ;
  ~60 000-75 000 $ de volume par semaine. Frais `culture_fees` : 5 % × p × (1 − p) à l'achat.
- Posts : archive publique **trumpstruth.org** (robots.txt ouvert, flux RSS, curseur de pagination, 100 posts par page, un appel par seconde) :
  6 046 posts du 23/01 au 24/10/2026 (`scripts/releve_posts.py`). Le compteur qui tranche est XTracker (compte `realDonaldTrump`, plateforme TRUTH_SOCIAL, 5 969 posts) :
  la production (`compteur_tweets`) le lit déjà, donc **ces marchés étaient déjà joués** par la mère.
- Échanges réels des 70 événements (`data-api …/trades?eventId=`, `scripts/releve_echanges.py`), prix payé = premier échange dans les 2 h après la décision.

## Contrôle du règlement (`scripts/reglement.py`)
Notre décompte tombe dans la tranche gagnante de Gamma **48 fois sur 62** (77 %). Les 14 écarts sont tous à 1-10 posts d'une frontière de tranche (99 contre « 100-119 », 138 contre « 140-159 »…) :
l'archive manque quelques posts (supprimés, ou comptés autrement par XTracker). Conséquence : le modèle sait la tranche à ± 5 posts près ; il ne faut pas lui demander plus.

## Contre le marché, puis achats simulés (`scripts/contre_marche.py`)
Décisions à S − 2 j, S, S + 1 … S + 5 j (S = début de la fenêtre) ; posts déjà comptés (archive) + posts restants attendus, aucune information postérieure à la décision.
1. **Profil par heure de la semaine** (28 jours avant, loi binomiale négative), 8 réglages (historique 14/28/56 j, dispersion 10/20/40, marge 3/5/10 points, échelle 1,03) :
   billets ≥ 0,10 : −6 % à +13 % par achat, t par événement −0,7 à +1,3 → **écartée** ; tout le « gain » du total (+9 à +29 %) vient des billets à moins de 0,10.
2. **Formule de production** (168 h / 336 h mélangées, dispersion 12) : premier signal par (événement, tranche, côté) et billets ≥ 0,10 : **306 achats, 59 événements, +15,5 %** (t par événement +2,26, z des prix 2,9),
   6 mois sur 8 gagnants, mars-juin +12,5 % puis juillet-octobre +18 %, sans les 3 meilleurs +9,4 % ; NON +21,5 % (t +3,3), OUI +5 % ; dispersion 6 : +20 % (t 1,9) ; dispersion 25 : +2,8 % (t 0,1).
   **Mais** : par profondeur réelle (parts échangées au prix payé dans les 2 h) : moins de 20 parts +19 %, 20-100 parts +13 %, **100 parts et plus −5 % (120 achats)**. L'effet vit dans les échanges minces. (Mise en garde : « parts échangées au prix payé dans les 2 h » est un flux, pas la profondeur du carnet ; même constat sur 4 autres comptes, `tweets_prix_payes.md`.)
3. **Billets à moins de 0,10** (OUI sur les tranches de queue) : 31 premiers signaux, 6 gagnés pour 2,2 attendus (+205 %), mais profondeur médiane 35 parts (3 €) : lot de consolation, pas une stratégie.
- Log-score de la tranche gagnante, modèle contre marché : meilleur à S − 2 j (−2,03 contre −2,25) et à S (−1,63 contre −2,17) mais sur 10-13 événements seulement.
- Réglages essayés : 8 (profil) + 4 (formule de production) + découpages par mois, côté, prix, profondeur : ~25 regards ; le résultat 2 survit à la correction pour les regards répétés de justesse, pas davantage.

## Pourquoi ce n'est pas « retenue »
t par événement 2,3 sur 59 événements après ~25 regards ; l'avantage disparaît là où l'argent peut aller (≥ 100 parts) ; le 21/10 la même mère donnait Trump ≈ 0 (prix horaires du CLOB, juillet-octobre).
Le fantôme, lui, achète sur les vrais carnets de l'arène : c'est le bon arbitre. À relire après ~8 semaines (≈ 8 événements), par `compteur_truth` contre `compteur_tweets`.

## Pistes ouvertes
- Le même test sur les autres comptes de XTracker avec la profondeur par achat (`tweets_filles.md` ne regardait pas la profondeur).
- Archive trumpstruth.org : source libre fiable (77 % de tranches exactes) pour un futur lecteur de production si XTracker tombe.
