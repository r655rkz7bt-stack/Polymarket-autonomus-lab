# Posts de Trump : la dispersion de la formule est trop étroite (02/11/2026)

**Verdict : indice** → fantôme `compteur_truth_dispersion_6_audace` (mise franche). Pas de changement de la mère ni du champion.

## Déclencheur
Constat « à regarder » de l'enquête : `compteur_tweets_12_18h` a acheté le 01/11 à 12 h 04 « 200+ posts de Trump du 03 au 10/11 »
à 0,697 (estimé 0,929, mise 195 €, 275 parts). Le rythme récent est extrême (95 posts le 30/10, 107 le 31/10, record de l'archive avant : 121)
et la formule (rythme 7 j / 14 j, binomiale négative de dispersion 12) en tire 93 %.

## Ce qui a été mesuré (archive de 6 046 posts, 38 semaines complètes ; `truth_social/scripts/dispersion_calibration.py`)
1. **Calibration** à 54 h avant le début de la semaine, seuil « 200+ » : prévision 0,6-0,85 → réel 0,20 (41 départs, 5 semaines) ; seuil 180+ : prévu 0,69, réel 0,44 ;
   seuil 140+ : prévu 0,72, réel 0,47. Prévision moyenne 220-300 posts → total réel moyen 184, ≥ 200 dans 22 % des cas (50 départs, ~5 semaines).
   Les faibles prévisions sont l'inverse (prévu 0,10 → réel 0,17). La loi est trop étroite : elle crie trop fort aux deux bouts.
2. **Log-score moyen sur les 11 tranches** (formule de production, une dispersion seule change), départs toutes les 12 h :

| moment | dispersion 3 | 5 | 8 | 12 (production) | 20 |
|---|---|---|---|---|---|
| 48 h avant le début | −2,245 | −2,152 | **−2,134** | −2,188 | −2,379 |
| début | −2,227 | −2,125 | **−2,094** | −2,131 | −2,292 |
| +24 h | −2,106 | −2,014 | **−1,998** | −2,053 | −2,241 |
| +72 h | −1,820 | **−1,780** | −1,830 | −1,957 | −2,248 |
| +120 h | **−1,371** | −1,424 | −1,565 | −1,754 | −2,036 |
| +144 h | **−1,021** | −1,125 | −1,247 | −1,364 | −1,519 |

   À 220 h avant la fin (cas du 01/11) : production −2,565, dispersion 5 −2,435 (grille 0,2-0,7 × 2-12 essayée : le plateau est 5-8).
3. **Contre le marché** (`truth_social/scripts/contre_marche_avant_fenetre.py`, 72 événements Gamma, vrais échanges au premier échange des 2 h suivant la décision, frais 5 %,
   marge 0,05, formule de production) : seuls S−3 j (20 événements) et S−2 j (11) ont des prix (les marchés naissent ~3,5 jours avant le début) :

| dispersion | paris (hors billets < 0,10) | rendement | t par événement | z des prix | mois gagnants | verdict |
|---|---|---|---|---|---|---|
| 12 | 78 | +14,4 % | 0,58 | 1,22 | 4/8 | écartée |
| 8 | 75 | +19,9 % | 1,19 | 2,06 | 5/8 | indice |
| 5 | 81 | +22,1 % | 1,75 | 2,33 | 6/8 | retenue |

   Log-score de la tranche gagnante à S−3 j : marché −2,021, modèle 12 : −1,973, 8 : −1,939, 5 : −1,964 (20 événements).

## Contre-épreuve sur la série qui tranche (XTracker, 7 comptes, `truth_social/scripts/dispersion_par_compte.py`)
Fenêtres de 7 jours, départ toutes les 12 h, décision 54 h avant le début ; part des totaux réels tombés dans les queues de la loi (PIT < 0,1 ou > 0,9 ; attendu 20 %) et log-score d'une bande de ±8 % autour du total :

| compte (fenêtres) | queues d5 | d8 | d12 (production) | d20 | meilleure dispersion (log-score) |
|---|---|---|---|---|---|
| realDonaldTrump (531) | 19 % | 30 % | **39 %** | 53 % | **5** (−2,645 contre −2,818) |
| cz_binance (408) | 21 % | 27 % | 34 % | 40 % | 5 |
| ZelenskyyUa (409) | 12 % | 14 % | 19 % | 24 % | 5-8 (écart minime) |
| elonmusk (690) | 8 % | 13 % | 20 % | 31 % | **12** |
| tedcruz (439) | 9 % | 12 % | 19 % | 32 % | 12 |
| WhiteHouse (464) | 3 % | 6 % | 9 % | 15 % | 20 ou plus (loi trop large) |
| NYCMayor (407) | 7 % | 7 % | 8 % | 12 % | 20 ou plus |

Lecture : la dispersion 12 convient à Elon Musk et Ted Cruz, est trop large pour la Maison-Blanche et NYC Mayor, et **trop étroite pour Trump (39 % des totaux dans les queues au lieu de 20 %)** et cz_binance. Un seul réglage global ne peut pas bien faire.
Même résultat qu'avec l'archive trumpstruth.org (indépendante de XTracker) : le défaut est donc dans le réglage, pas dans la mesure. Piste suivante : une dispersion par compte (Trump 5, Elon 12, Maison-Blanche 20+), à tester contre le marché compte par compte (ici, la calibration seule).

## Réserves
- 38 semaines : les « 5 semaines chaudes » sont ce qu'on a ; le rythme actuel (≈ 100 posts/jour) est hors de tout ce que l'archive a vu, donc extrapolation.
- 3 réglages essayés contre le marché, 20 événements : indice, pas retenue. Les marchés qui naissent à S−3 j ne permettent pas de tester les 220 h du cas réel.
- Autres comptes : voir la contre-épreuve XTracker (Elon et Ted Cruz sont bien à 12 ; la Maison-Blanche et NYC Mayor voudraient plus). Ce n'est que de la calibration, pas un test contre le marché.
- En direct, les 13 paris `compteur_*` (un par jeton, 6 événements) pris à plus de 168 h de la fin sont calibrés (12 gagnés pour 11,1 estimés) : le défaut n'a pas encore coûté, seul le cas extrême du 01/11 l'expose.
- Le carnet réel : −5 % quand il sert ≥ 100 parts (`truth_social.md`).

## Suite
- Fantôme `compteur_truth_dispersion_6_audace` (Trump seul, dispersion 6, Kelly entier) à comparer à `compteur_truth` sur la même période. Au premier cycle local : estime 0,88 là où la mère estime 0,947 pour le même « 200+ » (prix 0,76).
- À relire après la semaine du 03/11 (« 200+ » réglé le 10/11) et à ~15 semaines.
