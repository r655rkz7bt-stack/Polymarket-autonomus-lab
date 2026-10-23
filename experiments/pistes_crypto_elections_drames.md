# Trois pistes testées sur le passé aux prix réellement payés (22/10/2026)

Pistes n° 2, 3 et 11 de [`vingt_cinq_pistes.md`](vingt_cinq_pistes.md). Toutes les mesures utilisent les **prix
d'échanges réels** (data-api de Polymarket, public et gratuit) : un prix « connu » avant la décision, puis le prix du
**premier vrai échange après** la décision (ce qu'on aurait payé), frais du marché compris. Aucun prix de carnet vide
(règle du 22/10 : un prix `prices-history` sans échange réel n'est pas un prix exécutable).

| Piste | Verdict | Chiffres clés |
|---|---|---|
| **2. `toucher_avant_fin`** (crypto : « touchera-t-il K ? » contre « au-dessus de K à midi ? ») | **écartée** | (a) cohérence respectée : 13 demi-heures sur 6 488 sous 1, 3 paniers exécutés à 1,000 en moyenne ; règle « ≈ 2 fois » −11 % sur la seconde moitié ; (b) modèle de barrière : 7 réglages sur 24 gagnent sur la 1re moitié, le meilleur fait +13,5 % sur la 2e mais t par événement 0,49 |
| **3. `marge_coherente`** (élections : tranches de marge additionnées = « vainqueur ») | **écartée** (indice minuscule) | 13 élections, 18 candidats ; écart médian 1,9 point ; 49 paniers « sans risque » vus aux prix connus, **18 seulement exécutables**, gain moyen **+0,64 %** par panier |
| **11. `non_aux_drames`** (acheter le NON des « drames » à 2-15 % longtemps avant l'échéance) | **retenue** (petit échantillon) | 149 paris, 106 événements (2024-2026) : **+4,6 % par pari**, ≈ **+23 % par an** sur l'argent immobilisé ; drames arrivés : **2 pour 9,3 attendus** par les prix ; t par événement 2,81 ; 26 mois gagnants sur 28 ; pire cas : un pari perdu en entier (−100 % de sa mise) |

Une découverte technique utile pour toutes les études : **le data-api accepte `start` et `end`** (secondes Unix) sur
`/trades`. On peut donc lire les échanges autour de n'importe quel instant, même pour les très gros marchés : la limite
de 10 000 échanges (décalage maximal) ne s'applique plus qu'à la fenêtre demandée. Vérifié le 22/10 (`end` seul, puis
`start` + `end` : seuls les échanges de la fenêtre reviennent).

---

## Piste 2 : `toucher_avant_fin` (crypto)

**Question.** « Le Bitcoin touchera-t-il K pendant la période ? » doit valoir **au moins** « Le Bitcoin sera-t-il
au-dessus de K à midi le jour J ? » (si J est dans la période), et environ le double pour une marche au hasard
(principe de réflexion). Le marché respecte-t-il cela ? Un modèle de barrière fait-il mieux que le prix ?

**Règles lues dans Gamma.** Échelle « above K on J » : clôture de la bougie Binance d'une minute de 12 h 00 ET,
strictement au-dessus de K. Barrière « reach K » (jour, semaine, mois) : un plus haut d'une minute ≥ K pendant la
période ; « dip to K » : un plus bas ≤ K. Donc au-dessus à midi ⇒ touché : les paniers **« reach K » OUI + « above K »
NON** et **« dip to K » OUI + « above K » OUI** paient au moins 1 quoi qu'il arrive.

**Données.** Collecte de [`crypto_backtest`](crypto_backtest.md) (relue telle quelle) : 6 618 marchés réglés du 17/08
au 15/10/2026 (BTC, ETH, SOL, XRP ; 2 670 échelles, 2 967 barrières du jour, 678 de la semaine, 303 du mois), 522
fichiers d'échanges réels, bougies Binance (source de règlement), DVOL Deribit. **8 693 paires** barrière × échelle
(même actif, même seuil, midi J dans la période). Frais : barème de chaque marché (0,07 × p × (1 − p)).

**Méthode.**
- (a) Arbitrage strict : toutes les 30 minutes, prix connus = derniers échanges des deux jambes dans les 15 min avant ;
  si somme + frais < 1, achat des deux jambes au premier échange réel dans l'heure après ; un seul panier par paire.
- (a bis) Règle « toucher ≈ r × au-dessus » : paires dont la période finit au plus 12 h après midi J, 48/24/12/6/3 h
  avant midi ; achat du OUI (ou du NON) de la barrière si l'écart au prix payé de l'échelle × r dépasse un seuil.
  12 réglages (r 1,5-2,25 × seuil 0,03-0,08), réglés sur les jours jusqu'au 16/09, jugés après.
- (b) Modèle de barrière : P(toucher) = min(1, 2 × P(finir au-delà)), σ = DVOL × k ou σ réalisée × k, prix au comptant
  de la bougie d'une minute avant t ; cas seulement si la période a commencé et la barrière n'est pas encore touchée.
  24 réglages (2 volatilités × k 0,9-1,3 × seuil 0,03-0,08), réglés sur les 30 premiers jours, jugés sur les 30 suivants.

**Résultats.**

| Test | Résultat |
|---|---|
| (a) demi-heures où les deux jambes ont un échange à moins de 15 min | 6 488 |
| … somme des prix payés < 1 | 13 (0,20 %) ; après frais : 7 (0,11 %) |
| … paniers exécutés aux prix d'après | 3 (2 sans échange dans l'heure) : coût payé 0,992 / 1,001 / 1,008, gain total 0,00 $ |
| (a bis) prix du toucher / prix du au-dessus, échelle à 0,02-0,10 | marché **4,6 fois**, réalité **4,6 fois** (93 cas) |
| (a bis) meilleur réglage de la 1re moitié (r 2,0, seuil 0,05) jugé sur la 2e | 29 paris, **−11,2 %**, 0 mois sur 2 |
| (b) Brier sur la 2e moitié (578 cas, deux côtés échangés) | marché 0,0793, DVOL 0,0761, σ réalisée 0,0777 |
| (b) réglages gagnants sur la 1re moitié | 7 sur 24 (de −36 % à +21 %) ; sur la 2e : 17 sur 24 |
| (b) meilleur réglage de la 1re moitié (DVOL × 1,15, seuil 0,08) jugé sur la 2e | 157 paris, +13,5 %, 58 événements, **t par événement 0,49**, 17 jours gagnants sur 29 ; 155 achats du OUI sur 157 ; billets < 0,10 : −21 % |

**Verdict : écartée.**
- La cohérence est respectée aux prix payés : les « arbitrages » n'apparaissent que sur des prix vieux de quelques
  minutes et disparaissent à l'exécution. Le marché ne paie pas le toucher « 2 fois » le au-dessus mais 4,6 fois sur
  les seuils lointains… et c'est exactement ce qui est arrivé (le facteur 2 suppose une période qui commence et finit
  avec l'échelle ; ici la barrière court encore 12 h après midi, ce qui pèse lourd sur un seuil lointain).
- Le modèle de barrière est un peu plus précis que le prix (Brier) sur la seconde moitié, mais il perd sur la première
  dans 17 réglages sur 24 et ne gagne sur la seconde que parce que le Bitcoin a monté régulièrement du 16/09 au 15/10
  (75 800 → 82 400 $) : presque tous ses paris sont des OUI « touchera plus haut ». Même conclusion que le 16/10 sur les
  échelles : pas d'avantage régulier.

**Limites.** 60 jours d'échéance seulement (une période de hausse) ; paires corrélées (une trajectoire du Bitcoin
règle toute une échelle) ; prix payés sans la quantité disponible ; le test (a) exige un échange des deux jambes à moins
de 15 min (6 488 demi-heures sur des centaines de milliers possibles) : les paires peu échangées ne sont pas jugées.

Scripts : [`toucher_avant_fin/coherence.py`](toucher_avant_fin/coherence.py), [`toucher_avant_fin/barriere.py`](toucher_avant_fin/barriere.py) ;
sorties : `resultats_coherence.txt`, `resultats_barriere.txt`.

---

## Piste 3 : `marge_coherente` (élections)

**Question.** Les tranches « marge de victoire » d'un candidat, additionnées, doivent valoir le prix « ce candidat
gagne ». Quand ce n'est pas le cas, deux paniers rapportent un montant connu d'avance :
- **D1** (tranches trop bon marché) : OUI de toutes les tranches du candidat + NON de « il gagne » → paie 1 ;
- **D2** (tranches trop chères) : OUI de « il gagne » + NON de chacune de ses n tranches → paie n.

**Données.** 36 événements « margin of victory » réglés trouvés par la recherche publique Gamma (hors sport), dont
**13 élections** rattachées à la main à leur marché « vainqueur » avant de regarder les prix (même élection, même tour,
même quantité) : collège électoral 2024, vote populaire 2024, Géorgie 2024, 2e tour au Portugal, 2e tour en Colombie,
vote populaire en Hongrie, primaire démocrate du Massachusetts ; « quantité voisine » (le vainqueur se juge aux
sièges, la marge aux voix) : Suède, Mecklembourg, Berlin, Lettonie. Écartés faute de marché vainqueur clair : Holborn,
Danemark, Chili, Paris, les primaires du Texas, de Géorgie, de Caroline du Sud… **18 candidats** au total.
Échanges réels lus chaque jour à 18 h UTC pendant les 30 jours avant l'élection (2 992 lectures, fenêtres `start`/`end`).

**Méthode.** Prix connus = derniers échanges réels de chaque jambe dans les 2 h avant ; si le panier coûte moins que
ce qu'il paie (frais compris), achat de chaque jambe au premier échange réel dans l'heure après ; une jambe sans
échange = panier impossible.

**Résultats.**

| Mesure | Valeur |
|---|---|
| jours × candidat où toutes les jambes ont un échange dans les 2 h | 151 (sur ~1 000) |
| écart \|somme des tranches − vainqueur\| au dernier échange | médiane **0,019**, 9e décile 0,058, maximum 0,124 (Colombie) |
| paniers sous leur paiement aux prix connus | 49 (collège électoral 19, Hongrie 14, Portugal 7, Géorgie 4, Colombie 4…) |
| paniers réellement exécutables aux prix d'après | **18** (les autres : au moins une jambe sans échange dans l'heure) |
| gain par panier exécuté | **+0,64 %** en moyenne (4 événements ; meilleur : Hongrie, 1/04, 0,976 → 0,957 payé, +4,5 %) |

**Verdict : écartée** (le protocole `verdict` dit « indice », mais ce sont des arbitrages : un gain d'un demi-centime
quand on réussit à tout acheter, ce qui n'arrive qu'une fois sur trois, avec 5 à 9 achats simultanés pour le collège
électoral). Les incohérences existent (un à deux points en général) mais l'écart achat-vente des tranches peu échangées
les absorbe. Sur 1 000 €, 18 paniers en deux ans rapporteraient quelques euros, pour un risque d'exécution réel (une
jambe ratée laisse un pari nu).
Règle exacte si Etienne veut quand même un fantôme : chaque heure, pour chaque élection rattachée (liste `PAIRES`),
acheter le panier D1 si somme des prix vendeurs des tranches + prix vendeur du NON « vainqueur » + frais < 0,99, ou D2 si
prix vendeur du OUI « vainqueur » + somme des prix vendeurs des NON des tranches + frais < n − 0,01 ; toutes les jambes
ou aucune. Il faudrait une classe qui achète plusieurs jambes d'un coup : coût de code élevé pour un gain minuscule.

**Limites.** 13 élections seulement ; quantité disponible à chaque prix non mesurée ; un instant par jour ; « quantité
voisine » pour 4 législatives ; pas d'élection de 2022 (les marchés anciens n'ont pas de marché vainqueur rattaché).

Scripts : [`marge_coherente/releve_evenements.py`](marge_coherente/releve_evenements.py), [`marge_coherente/prix_payes.py`](marge_coherente/prix_payes.py) ;
sortie : `resultats.txt`.

---

## Piste 11 : `non_aux_drames`

**Question.** Sur les marchés longs « Est-ce que X arrivera avant <date> ? » au sujet d'un drame (invasion, guerre,
chef d'État qui tombe, faillite, extraterrestres…), le OUI à 2-15 % est-il trop cher (biais favori-outsider,
arXiv 2609.12878) ? On achète le NON.

**Données.** Tous les marchés Gamma clos d'**échéance entre le 1/01/2024 et le 21/10/2026**, au moins 5 000 $ échangés,
au moins 30 jours de vie : **7 531 marchés**. Parmi eux, **193 « drames »** réglés oui/non, choisis par une liste de
mots fixée avant de regarder les résultats : guerre (70), dirigeant (104), économie (11), insolite (8) ; le OUI doit être
le drame (« remain », « still », « survive »… exclus).

**Méthode.** Décision à T0 = échéance − 30, 90 ou 180 jours (au moins 2 jours après la création, marché pas encore
réglé). Prix connu = dernier échange réel dans les 7 jours avant T0 (toutes issues ramenées au prix du OUI), entre 0,02
et 0,15. Achat du NON au **premier échange réel « achat du NON » (ou vente du OUI) dans les 48 h après T0**, frais du
marché (barème lu dans Gamma : 6 marchés sur 111 ont des frais preneur de 0,03-0,04 × p × (1 − p), appliqués ; les autres aucun). 297 instants, dont 110 hors plage, 15 sans échange avant, 23 sans échange après : **149 paris**.
Rendement par jour = somme des gains / somme (mise × jours jusqu'au règlement).

**Résultats.**

| Ensemble | Paris (événements) | Par pari | Par an (argent immobilisé) | Durée moyenne | Drames arrivés / attendus | t par événement | Mois gagnants | Verdict |
|---|---|---|---|---|---|---|---|---|
| T0 = −30 j | 78 (75) | +2,4 % | ≈ +26 % | 35 j | 2 / 4,3 | 1,1 | 16/18 | indice |
| T0 = −90 j | 45 (44) | +6,1 % | ≈ +25 % | 88 j | 0 / 2,8 | 11,1 | 15/15 | retenue |
| T0 = −180 j | 26 (24) | +8,9 % | ≈ +19 % | 172 j | 0 / 2,2 | 10,4 | 8/8 | écartée (< 30 paris) |
| **tous** | **149 (106)** | **+4,6 %** | **≈ +23 %** | 75 j | **2 / 9,3** | **2,81** | **26/28** | **retenue** |
| tous, sans 9 faux drames (« Coupar », « Death Stranding »…) | 140 (100) | +4,4 % | ≈ +22 % | | 2 / 8,7 | 2,46 | 25/27 | retenue |

Par prix (T0 = −90 j) : OUI à 0,02-0,05 +3,7 %, 0,05-0,10 +6,4 %, 0,10-0,15 +12,9 %. Par famille (−30 j) : guerre
+5,3 % (0 drame pour 1,8 attendu), dirigeant +0,3 % (2 pour 2,4). Moitiés (−30 j) : +5,4 % puis −0,5 % ; (−90 j) : +6,3 % puis +6,0 %.

**Pires cas.** Les deux drames arrivés : « Bolsonaro arrêté avant le 31/08 » (OUI payé 0,044, août 2025) et « Starmer
parti avant le 30/06/2026 » (OUI 0,14, mai 2026) : chaque fois **−100 % de la mise** (0,92 $ et 0,86 $ pour une part).
Pire mois : mai 2026 (le seul pari du mois perdu). Un drame groupé (une guerre qui fait perdre d'un coup tous les
« frappe avant <date> ») n'est pas arrivé dans l'échantillon, mais c'est le vrai risque : il faut plafonner la mise
par événement.

**Verdict : retenue**, avec prudence. Le NON gagne nettement plus souvent que ses prix ne le disent (2 drames pour 9,3
attendus, z des prix +2,3), régulièrement (26 mois sur 28), sur 106 événements différents. Mais : le gain par pari est
petit (+2 à +9 %), l'argent reste bloqué 1 à 6 mois, et une seule perte efface 15 à 25 gains. **Groupe témoin** (mêmes
règles, marchés longs qui ne sont pas des drames, T0 = −90 j) : voir l'addendum en bas de page.

**Règle exacte du fantôme** (`non_aux_drames`) :
1. Marchés binaires oui/non ouverts dont l'échéance est à **30 à 120 jours**, au moins 5 000 $ échangés, question qui
   contient un mot de la liste `DRAME` de `non_aux_drames/prix_payes.py` (corrigée : `\bcoup\b`, sans « win », « award »,
   « sentenced to between ») et aucun mot de statu quo.
2. Dernier prix échangé du OUI entre **0,02 et 0,15**.
3. Acheter le **NON au prix vendeur** (preneur), une seule fois par marché ; **au plus 2 % du capital du fantôme par
   événement** (un drame fait perdre toute la mise) ; garder jusqu'au règlement.
4. Juger après 30 paris réglés ; arrêter si deux drames arrivent dans le même mois.

**Limites.** 149 paris seulement (le relevé ne garde que les marchés ≥ 5 000 $ et la liste de mots est étroite) ; 2
pertes seulement : un ou deux drames de plus changeraient beaucoup le résultat ; les paris d'un même marché à trois
horizons sont liés (regroupés par événement dans `verdict`) ; les marchés à échéance après le 21/10/2026 manquent (dans
les deux sens) ; aucune récompense de détention mesurée (`holdingRewardsEnabled` absent des 149 paris) ; quantité
disponible au prix payé non mesurée.

Scripts : [`non_aux_drames/releve_marches.py`](non_aux_drames/releve_marches.py), [`non_aux_drames/prix_payes.py`](non_aux_drames/prix_payes.py) ;
sortie : `resultats.txt`.

---

## Addendum : groupe témoin de la piste 11 (même règle, marchés longs qui ne sont PAS des drames)

`prix_payes.py --temoin`, T0 = échéance − 90 jours, OUI à 0,02-0,15, mêmes prix payés (sortie : `non_aux_drames/resultats_temoin.txt`).

| Ensemble (T0 = −90 j) | Paris (événements) | Par pari | Par an | OUI arrivés / attendus | t par événement | Mois gagnants | Verdict |
|---|---|---|---|---|---|---|---|
| **drames** | 45 (44) | **+6,1 %** | ≈ +25 % | 0 / 2,8 | 11,1 | 15/15 | retenue |
| **témoin** (sport de saison, élections, prix, entreprises…) | 784 (370) | **+0,9 %** | ≈ +4 % | 40 / 49,9 | 2,45 | 20/31 | indice |
| témoin, OUI à 0,02-0,05 | 334 (194) | −0,7 % | ≈ −3 % | 12 / 10,6 | −0,29 | 19/28 | écartée |
| témoin, OUI à 0,05-0,10 | 307 (192) | +2,6 % | ≈ +12 % | 13 / 21,9 | 3,59 | 22/29 | retenue |

Lecture : le biais favori-outsider existe un peu partout sur les marchés longs (le NON gagne +0,9 % par pari), mais il
est **environ six fois plus fort sur les drames** (+6,1 % par pari au même horizon). Ce sont bien les drames que la foule
surpaie (peur ou frisson), pas seulement les outsiders. Le témoin à 0,05-0,10 est lui aussi « retenu » : une variante
`non_aux_outsiders_longs` (NON des OUI à 0,05-0,10 à environ 90 jours, hors drames) pourrait accompagner le fantôme,
avec la même limite de mise par événement (les pertes du témoin viennent du sport de saison : Knicks, Zverev, Verstappen).

## Réglages essayés (pour juger la chance de sélection)
- Piste 2 : 12 réglages (règle « r fois ») + 24 (modèle de barrière) ; l'arbitrage strict n'a aucun réglage.
- Piste 3 : aucun réglage (seuil de paiement fixe).
- Piste 11 : 3 horizons × 3 tranches de prix × 4 familles regardés, **un seul ensemble jugé** (2-15 %, tous horizons),
  fixé par la piste avant le test ; le groupe témoin sert de contrôle.

## Refaire les tests
```
.venv/bin/python experiments/toucher_avant_fin/coherence.py    # données : collecte de crypto_backtest copiée dans donnees/
.venv/bin/python experiments/toucher_avant_fin/barriere.py
.venv/bin/python experiments/marge_coherente/releve_evenements.py && .venv/bin/python experiments/marge_coherente/prix_payes.py
.venv/bin/python experiments/non_aux_drames/releve_marches.py 2024-01-01 2026-10-21 && .venv/bin/python experiments/non_aux_drames/prix_payes.py
.venv/bin/python experiments/non_aux_drames/prix_payes.py --temoin   # groupe témoin
```
