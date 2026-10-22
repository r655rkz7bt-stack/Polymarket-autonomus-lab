# Piste n° 10 (queues de tranches) et n° 9 (lissage) : événements à tranches, tests sur le passé

Scripts : `experiments/queues_tranches/` (`releve_evenements.py`, `releve_prix.py`, `analyse.py`, `prix_payes.py`, `lissage.py`) ; sortie complète
de `analyse.py` : `experiments/queues_tranches/resultats.txt`. Données (ignorées par Git) : `donnees/`.

## Données (relevé du 22/10/2026)
Événements Gamma réglés, neg-risk, hors sport, ≥ 5 marchés, au plus un OUI gagnant, échéance entre le 1/08 et le 20/10 : **990 événements, 17 796 marchés**
(politique et élections 56 %, tweets, IA, crypto, séismes, Billboard…). Prix OUI heure par heure du CLOB (10 derniers jours) ; prix pris **avant** T0 = échéance − 24 h / 72 h / 168 h,
au plus 6 h de retard. Règlement relu dans Gamma (prix final 0 ou 1 ; litiges écartés). Frais : barème du marché. Cas retenus : 10 625 (marché × horizon).

## Question 1 (piste 10) : les OUI à 3-25 % gagnent-ils moins que leur prix ? → NON
Par tranche de prix et horizon (gagnés − attendus, en points) : −0,1 à −2,7 points, z entre −3,0 et −0,1 ; seules les cases à 1-3 % à T-72 h/T-168 h sont
significativement sous leur prix (z −2,0 / −3,0), mais acheter leur NON coûte 0,97-0,99 pour gagner 0,01-0,03 : après écart et frais rien ne reste.
Achat du NON, 18 réglages (3 horizons × 3 plages × 2 écarts) : rendement −1,3 % à +0,9 % par pari, t par événement entre −1,9 et +0,7, **tous « écartée »**.
Par famille (T-72 h) : tweets −1,6 %, élections −1,2 %, autres 0 % ; crypto +6,4 % (102 paris, 44 événements) et IA +4,1 % : voir question 2.
**Verdict : écartée** (la queue n'est pas surévaluée au prix payé ; `cpi_tranches` reste un cas particulier des CPI).

## Question 2 (suite) : les OUI de 0,25 à 0,60 gagnent-ils moins que leur prix ? → oui au prix du CLOB, non aux prix payés
À T-72 h : 127 gagnés pour 152,7 attendus (0,25-0,40, z −2,5) et 108 pour 135,7 (0,40-0,60, z −3,4) ; à T-168 h z −2,3 et −2,3 ; à T-24 h z −1,4 et −0,6.
Achat du NON (27 réglages) au prix du CLOB : +8,8 % par pari à T-72 h (écart 0,01, 757 paris, 392 événements, t +1,5, z des prix +2,9 : « indice »),
mais +5,4 % à écart 0,03 et −2,1 % à +1,1 % à T-24 h. Crypto : +23,5 % (174 paris, 50 événements, z des prix +3,8).
**Contrôle aux prix réellement payés** (`prix_payes.py`, premier échange d'achat du NON ou de vente du OUI après T0, data-api) :
- Seuls 188 des 757 paris trouvent un échange dans les 2 h qui suivent (317 en 6 h, 520 en 24 h) : les tranches du milieu se négocient peu ;
- aux prix des échanges de 2 h : +5,5 % (t +1,4) ; 6 h : +3,9 % (t +1,6) ; **24 h : −0,6 % (520 paris, 332 événements, t −0,1, z des prix −0,4)** ;
  T-168 h, 24 h : +0,1 % ; T-24 h, 24 h : −1,3 % ; crypto, 24 h : −2,5 % (55 paris) ;
- les fenêtres courtes ne gardent que les paris où quelqu'un a échangé vite (sélection) : le signe disparaît dès qu'on laisse le temps d'être servi.
Au total ~55 réglages essayés. **Verdict : écartée** : le gain au prix du CLOB n'est pas exécutable (même défaut que les mentions du 21/10 : prix historique
sans carnet). Somme des OUI par événement exclusif à T-72 h : médiane 1,05 (83 événements complets) : la surcote globale est de 5 %, que l'écart achat-vente absorbe.

## Piste n° 9 (lissage des tranches) : le « pic isolé » est un prix de carnet vide → trompeuse
Données élargies à avril → octobre (43 207 marchés avec prix, 679 événements ordonnés complets à T-72 h ; tranches ordonnées par le premier nombre de leur libellé).
- **Creux** (OUI à moins de 0,6 × sa plus basse voisine) : 65 cas à T-72 h, OUI gagnés 6 pour 4,8 attendus (z +0,6) ; achat du OUI −3 % à +10 %, t par événement +0,3 à +0,5 : **écartée**.
- **Pic isolé** (OUI à plus de 1,6 × sa plus haute voisine, pas le favori, prix à 0,05-0,70) : **OUI gagnés 1 pour 10,7 attendus à T-72 h (z −3,4)**, 1 pour 8,5 à T-168 h (z −3,0),
  1 pour 6,0 à T-24 h (z −2,3) ; achat du NON +19 à +21 % (t par événement +6 à T-72 h) au prix du CLOB : en apparence le meilleur résultat de la semaine.
- **Mais ce sont des prix de carnets vides ou très écartés.** Premier relevé (avant filtre) : les pics tombaient à 0,49-0,50 (« Solana price on August 1 » : tranches 50-60 et 90-100 à 0,49 alors que le règlement est la tranche 70-80 à 0,90 ;
  le CLOB affiche le milieu d'un carnet 0,01 / 0,99). Même après avoir écarté 0,44-0,56 : sur les 58 pics, seuls **13 ont un échange réel du OUI dans les 24 h avant T0** (`lissage_echanges.py`),
  54 % de ceux-là se sont négociés à moins de 0,6 × le prix affiché (0,35 affiché → 0,05 payé), et **aux prix d'achat réels du NON (25 paris avec un échange dans les 24 h suivantes) : +2,0 % (t +0,4), 4 mois sur 5 : écartée**.
- Même défaut que les mentions du 21/10 (+31 % au prix horaire, −7 % aux prix payés) et que les tranches moyennes ci-dessus : **l'historique `prices-history` d'un marché mince n'est pas un prix exécutable.**
  Règle à retenir pour tout test sur des marchés à tranches : écarter tout prix « milieu » dont le marché n'a pas d'échange réel à T0, et refaire le test aux prix des échanges avant de parler d'avantage.
**Verdict : écartée (trompeuse)**. Ni stratégie, ni fantôme.
