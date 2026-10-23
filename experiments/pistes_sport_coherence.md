# Pistes n° 1, 4 et 5 : la cohérence des marchés de sport (score exact, cartes d'e-sport, sets de tennis)

Étude du 22/10/2026 (session à part du passage chercheur). Idées tirées de `experiments/vingt_cinq_pistes.md`.
Scripts : `experiments/score_exact_poisson/`, `experiments/bo3_coherence/` (code commun aux pistes 4 et 5 :
`series.py`, `echanges.py`), `experiments/tennis_sets_coherence/`. Sorties complètes : `resultats.txt` de chaque dossier.
Données (ignorées par Git) : `donnees/` de chaque dossier.

## En bref

| piste | question | verdict | chiffres clés (aux prix réellement payés, après frais) |
|---|---|---|---|
| n° 5 `tennis_sets_coherence` | « set 1 », « gagne en 2 sets », « nombre de sets » s'accordent-ils avec « vainqueur du match » ? | **écartée (trompeuse)** | prix « après » T0 : −8,9 % à +1,4 % par pari (t par match −0,9 à +0,3) ; le gain du prix « avant » (+9,8 %, jusqu'à +74 % sur 31 paris) vient d'échanges vieux de 2 à 6 h (prix périmés) |
| n° 4 `bo3_coherence` | « carte 1 », « handicap de cartes », « nombre de cartes » s'accordent-ils avec « vainqueur de la série » ? | **écartée telle quelle** ; découverte annexe « moins de cartes » : **indice fort → fantôme** | modèle, prix « après » : −13 % à +2 % (réglages fixes) ; acheter « Under » du nombre de cartes, prix « après » : **+13,5 % par pari, 457 paris, 412 matchs, t +2,75, 10 mois sur 12, z des prix +2,9** (trouvé parmi ~90 essais) |
| n° 1 `score_exact_poisson` | les scores exacts sont-ils mal cotés par rapport à une loi de Poisson tirée du vainqueur et des « plus/moins de 2,5 buts » ? | **écartée : marchés trop peu négociés** | 13 061 matchs existent, mais sur 481 tirés seuls 134-233 ont des prix réels pour le modèle ; 15 à 52 paris par réglage sur 8 mois ; le réglage choisi en apprentissage n'a que 0-2 paris en test |

## Règles communes (les mêmes pour les trois pistes)

- **Les marchés existent-ils ?** Relevé complet de Gamma par le type sportif (`sportsMarketType`), avec la pagination
  « keyset » (Gamma refuse les décalages au-delà de 2 000 sur `/markets` et 5 000 sur `/events`).
- **Échantillon** : trop de matchs pour lire tous les échanges dans le temps d'une session ; tirage au hasard fixe
  (graine 7), mois par mois, parmi les matchs dont un marché lié a un volume > 0 (sans volume, aucun échange, donc aucun
  pari possible : ce filtre ne choisit rien sur le résultat).
- **Pas de regard vers le futur** : décision à T0 = coup d'envoi − h heures (h = 1, 3 ou 6) ; le modèle n'utilise que des
  échanges antérieurs à T0.
- **Prix du modèle = prix d'échanges réels** (règle du 22/10, `experiments/enquetes/README.md`) : le marché liquide
  (vainqueur, ou vainqueur + totaux pour le football) est lu sur la médiane des 5 derniers échanges réels avant T0
  (1 h pour le tennis et l'e-sport, 2 h pour le football) ; sans échange, pas de modèle (compté « sans échange »).
- **Prix d'achat = prix réellement payé par un preneur** sur le marché lié (data-api, `cout_preneur`) :
  - « avant » : dernier échange d'achat dans la fenêtre (2 h ou 6 h) AVANT T0 (prix connu à la décision, mais peut-être
    plus disponible à T0) ;
  - « après » : premier échange d'achat APRÈS T0, jamais après le coup d'envoi (prix qu'on aurait vraiment payé) ;
  - frais du marché (`rate × p × (1 − p)`, barème de chaque marché, 0,05 partout ici) ; pas d'échange = pas de pari.
- **Réglage sur la 1re moitié des jours, jugement sur la 2e** ; 72 réglages par piste (3 délais × 2 fenêtres × avant/après
  × 3 avances minimales × 2 variantes de modèle), tous comptés. Paris d'un même match regroupés (`idea_test.verdict` :
  confiance par match, mois gagnants, z des prix = gagnés contre attendus par les prix payés).

## Piste n° 5 : tennis, les sets contre le vainqueur du match

**Question.** Si chaque set est gagné par le joueur A avec la même chance q (loi binomiale), alors en 2 sets gagnants :
vainqueur = q² (3 − 2q), set 1 = q, « A −1,5 set » (gagne 2-0) = q², « plus de 2,5 sets » = 2q (1 − q) (formules du BO5
pour les hommes en Grand Chelem). Le prix du vainqueur (marché liquide : 750 000 $ pour un ATP courant) donne q ; on achète
le côté d'un marché lié (set 1, handicap de sets, total de sets : 50 à 1 500 $) vendu nettement sous ce calcul.

**Les marchés existent.** ATP (série 10365) : 10 752 matchs réglés, dont ~9 400 avec « Set 1 Winner »
(`tennis_first_set_winner`), « Set Handicap » (`tennis_set_handicap`), « Total Sets O/U 2.5 » (`tennis_set_totals`) ;
WTA (10366) : 5 541 matchs, ~5 150 avec ces marchés. Depuis janvier 2026 (quelques-uns en novembre-décembre 2025).
Volumes médians : set 1 166 $ (ATP) / 301 $ (WTA), handicap 59 / 128 $, total 46 / 73 $ ; un quart sans aucun volume.

**Données du test.** 1 030 matchs tirés (50 par mois et par circuit, novembre 2025 → 22 octobre 2026), 3 560 marchés liés
réglés (1 028 set 1, 1 062 handicaps, 1 023 totaux, 439 set 2), 978 BO3 et 52 BO5 ; échanges réels de chaque match
(1 seul événement tronqué par la limite de 10 000 de la data-api). À h = 3 h : 2 131 des 2 930 marchés liés examinés
n'ont **aucun échange** dans les 6 h avant T0, et 184 matchs n'ont pas d'échange du vainqueur dans l'heure avant T0.

**Résultats.**
1. *Le modèle binomial n'est pas meilleur que le prix du marché lié* (h = 3 h, prix « avant ») : le joueur à −1,5 set
   gagne 2-0 133 fois pour 105 attendues par le modèle et 124 par le prix (Brier modèle 0,2455, prix 0,2384) ; les matchs
   en 3 sets arrivent 58 fois pour 76 attendues par le modèle et 64 par le prix (Brier 0,2522 contre 0,2442). Les sets ne
   sont pas indépendants (celui qui domine le jour gagne souvent les deux) : le marché le sait mieux que la binomiale.
2. *Période entière, réglages fixes* :

   | réglage | paris | matchs | rendement par pari | t par match | mois gagnants | gagnés / attendus par les prix (z) | verdict |
   |---|---|---|---|---|---|---|---|
   | h = 3 h, prix « avant » (6 h), avance > 0,03 | 357 | 277 | +9,8 % | +1,08 | 9/12 | 182 / 176,0 (+0,7) | indice |
   | h = 3 h, prix « avant » (6 h), avance > 0,10 | 31 | 25 | +74,3 % | +1,87 | 9/12 | 18 / 12,0 (+2,3) | « retenue » |
   | h = 3 h, prix « après » (6 h), avance > 0,03 | 489 | 366 | −3,9 % | −0,58 | 5/12 | 225 / 238,0 (−1,2) | écartée |
   | h = 3 h, prix « après » (6 h), avance > 0,10 | 39 | 34 | +1,4 % | +0,31 | 4/11 | 15 / 15,5 (−0,2) | écartée |
   | h = 1 h, prix « après » (2 h), avance > 0,03 | 351 | 275 | −8,9 % | −0,88 | 3/12 | 154 / 170,4 (−1,8) | écartée |
   | h = 6 h, prix « après » (6 h), avance > 0,03 | 568 | 386 | −0,3 % | −0,17 | 6/12 | 273 / 277,7 (−0,4) | écartée |

3. *Le gain « avant » vient de prix périmés.* Paris du réglage « avant », h = 3 h, avance > 0,03, rangés par l'âge du
   dernier échange : moins de 30 min **−6,4 %** (61 paris, t −1,5) ; 30 min à 2 h +4,7 % (139) ; **2 à 6 h +21,1 %** (158).
   Plus le prix est vieux, plus le « gain » est grand : le vainqueur a bougé depuis, le carnet du marché lié aussi, mais
   le dernier échange n'en sait rien. Contre-épreuve : sans modèle, acheter « avant » le côté −1,5 rapporte +7,8 % ET le
   côté +1,5 du même marché +7,9 % — impossible à de vrais prix ; « après », ces deux achats font −0,8 % et −4,3 %.
4. *Réglage choisi sur la 1re moitié* (h = 1 h, « avant » 6 h, avance > 0,06, modèle recalibré) : +69,8 % sur 58 paris en
   apprentissage, **+39,0 % sur 42 paris (37 matchs) en test, t par match +1,05, 5 mois sur 6, z des prix +1,0** (« indice »
   pour `verdict`) ; mais c'est un prix « avant » (même défaut que le point 3) ; le meilleur réglage « après » en
   apprentissage (h = 3 h, 2 h, avance > 0,03, recalibré : +51,7 %) fait **−0,6 %** en test (30 paris), le suivant −13,0 %.

**Verdict : écartée (trompeuse).** Aux prix qu'on aurait vraiment payés (« après »), aucun réglage ne gagne hors
échantillon ; le seul gain vient de prix « avant » périmés (même famille de défaut que les mentions du 21/10 et les
tranches du 22/10 : un prix d'un marché mince qui n'est plus exécutable). Le binomial est moins bon que le marché lié
lui-même. Pas de fantôme.

**Limites.** Échantillon (1 030 matchs sur ~12 500 utilisables) ; pas de variante en jeu (il faudrait l'état du match :
qui a gagné le set 1, et quand ; possible avec les échanges du marché « set 1 » qui passent à 0,99, non fait) ; modèle à
sets indépendants seulement (la recalibration logistique corrige le biais moyen, pas plus) ; pas de carnet historique
(le prix « après » est celui du premier preneur, pas forcément le meilleur vendeur à T0).

## Piste n° 4 : e-sport, les cartes contre le vainqueur de la série

**Question.** Même calcul binomial qu'au tennis, avec q = chance de gagner une carte : « Map 1 / Map 2 Winner »
(`child_moneyline`), « Map Handicap −1,5 » (`map_handicap`, 2-0 en BO3), « Games Total O/U 2.5 » (`totals`, 3 cartes en BO3 ;
O/U 3,5 et 4,5 en BO5) contre « Match Winner » (`moneyline`). Le BO est lu dans le titre (« (BO3) », « (BO5) »).

**Les marchés existent.** CS2 11 901 matchs réglés, LoL 3 576, Dota 2 3 138, Valorant 2 629 (octobre 2025 → octobre 2026) ;
~15 300 matchs BO3/BO5 utilisables avec au moins un marché lié de volume > 0. Volumes médians : carte 1 650 à 55 700 $
(LoL le plus liquide), handicap 100 à 1 700 $, total 150 à 1 850 $.

**Données du test.** 1 417 matchs tirés (30 par mois et par jeu), 6 092 marchés liés réglés (1 368 carte 1, 1 364 carte 2,
138 carte 3 en BO5, 1 688 handicaps, 1 534 totaux), 1 278 BO3 et 139 BO5 ; 29 événements tronqués par la limite de la data-api.
À h = 3 h : 2 470 des 4 312 marchés liés examinés sans échange dans les 6 h avant T0 ; 419 matchs sans échange du vainqueur
dans l'heure avant T0.

**Résultats.**
1. *Le modèle n'est pas meilleur que le prix* (Brier égaux à 0,003 près). Mais il montre où il se trompe : les séries en
   3 cartes arrivent **146 fois pour 180 attendues par le modèle ET 179 par le prix** ; le côté −1,5 gagne 197 fois pour 169
   (modèle) et 184 (prix). Les cartes ne sont pas indépendantes (l'équipe en forme le jour gagne 2-0) et **le marché des
   totaux semble coté comme la binomiale**, donc trop cher pour « 3 cartes ».
2. *Le modèle, aux prix payés* : réglages fixes « après » −13 % à +2 % (sauf avance > 0,10 à h = 6 h : +28 %, 47 paris, t +0,9).
   Réglage choisi en apprentissage (h = 6 h, « avant » 6 h, avance > 0,06, recalibré) : test +18,6 % (118 paris, t +1,68,
   z +1,75, « retenue » pour `verdict`) — mais prix « avant » : rangés par âge de l'échange, < 30 min **−40 %**, 2-6 h +22 %
   (prix périmés, comme au tennis). Meilleur réglage « après » : test +21,7 % (99 paris, t +1,37) : indice faible.
3. *Sans modèle* (12 essais : 3 types × 2 côtés × avant/après ; contrôle `sous_2_5.py`, sortie `resultats_sous_2_5.txt`) :

   | acheter « Under » des totaux de cartes, prix « après » | paris | matchs | rendement | t par match | mois gagnants | gagnés / attendus (z) |
   |---|---|---|---|---|---|---|
   | h = 3 h, fenêtre 6 h, période entière | 457 | 412 | **+13,5 %** | **+2,75** | 10/12 | 298 / 268,8 (+2,9) |
   | 1re moitié (avant le 28/04/2026) | 175 | 160 | +9,8 % | +1,33 | 4/6 | 110 / 102,4 (+1,2) |
   | 2e moitié | 282 | 252 | +15,8 % | +2,48 | 6/7 | 188 / 166,4 (+2,7) |
   | autres délais (h = 1 / 3 / 6, fenêtre 2 ou 6 h) | 178-520 | | +7,6 % à +20,0 % | +1,6 à +2,8 | 9-10/12 | |
   | LoL / CS2 / Dota 2 / Valorant | 238 / 68 / 70 / 81 | | +22,2 / +7,2 / +7,5 / −1,5 % | +3,2 / +0,7 / +0,7 / 0,0 | | |
   | BO3 seulement / BO5 | 339 / 118 | 339 / 73 | +7,7 % / +30,3 % | +1,71 / +2,51 | 9/12 / 8/11 | |
   | prix payé 0,30-0,70 / ≥ 0,70 | 363 / 75 | | +15,9 % / +1,9 % | | | |
   | contre-épreuve : « Over », après | 538 | 501 | −15,5 % | −2,96 | 1/12 | 218 / 260,0 (−3,8) |
   | « Under », prix « avant » (connu à T0, sans sélection future) | 322 | 290 | +8,5 % | +1,55 | 8/12 | 201 / 191,0 (+1,2) |

**Verdict.** La cohérence binomiale elle-même : **écartée** (le marché lié n'est pas moins bien coté que le modèle ; les gains
« avant » sont des prix périmés). La découverte annexe — **les séries finissent 2-0 plus souvent que les totaux ne le disent** —
est **un indice fort** : positive à tous les délais, dans les deux moitiés, mécanisme clair (la binomiale qu'applique le
marché ignore la dépendance entre cartes), contre-épreuve nette (« Over » −15,5 %), et positive aussi au prix « avant » qui ne
dépend d'aucun échange futur. `verdict` dit « retenue », mais elle a été trouvée parmi ~90 essais (72 réglages du modèle,
12 côtés, découpages) et la 2e moitié n'est pas un vrai hors-échantillon : **fantôme, pas de part du principal**.
Elle tient surtout à LoL et au BO5 ; en BO3 seul, +7,7 % (t +1,7).

**Règle exacte du fantôme proposé (`esport_moins_de_cartes`)** :
- marchés : événements e-sport des séries CS2 (10310), LoL (10311), Dota 2 (10309), Valorant (10369) dont le titre contient
  « (BO3) » ou « (BO5) » ; type Gamma `sportsMarketType == "totals"` (« Games Total: O/U 2.5 », en BO5 O/U 3.5 et 4.5) ;
- moment : entre 6 h et 1 h avant `gameStartTime`, jamais après ;
- achat : l'issue « Under », en preneur, si le prix (frais compris) est entre 0,30 et 0,70 ; un seul achat par marché ;
- mise fixe et petite (volume médian 150-1 850 $ par marché) ; garder jusqu'au règlement ;
- fille à suivre : LoL seul. Attention « stratégie sourde » : ces marchés font souvent moins de 1 000 $ par jour ;
  vérifier que le scanner les voit (`min_volume_24h`, `tag_pages`) après un cycle local.

**Limites.** Échantillon (1 417 matchs sur ~15 300) ; prix « après » = premier preneur, pas le carnet (l'arène tranchera) ;
pas de variante en jeu ; carte 1 souvent choisie par une équipe (avantage du choix ignoré).

## Piste n° 1 : football, score exact contre loi de Poisson

**Question.** Les prix « domicile / nul / extérieur » et « plus/moins de 1,5 / 2,5 / 3,5 buts » donnent λ domicile et λ extérieur
(deux lois de Poisson ajustées aux moindres carrés ; variante Dixon-Coles ρ = −0,1) ; on achète le OUI ou le NON d'un score
exact vendu loin de ce calcul.

**Les marchés existent.** 13 061 événements « … - Exact Score » réglés (265 701 marchés, type `soccer_exact_score`, 37 marchés
par match : 0-0 à 5-5 et « Any Other Score »), de février à octobre 2026 (4 067 en août), surtout ligues secondaires
(Ligue Europa Conference, MLS, Amérique du Sud, Brésil 2, USL…) ; le match lui-même est l'événement sans suffixe, les totaux
dans « …-more-markets ». Volume médian d'un match : 1 225 $ pour les 37 scores réunis (p90 20 000 $).

**Données du test.** 505 matchs tirés (60 par mois), 481 utilisables, 9 214 scores réglés, 113 023 échanges sur les scores.
Le modèle exige un échange réel des 4 marchés indispensables dans les 2 h avant T0 : seuls **233 matchs à h = 1 h, 176 à 3 h,
134 à 6 h** l'ont. À h = 3 h, 2 151 des 3 131 scores examinés n'ont aucun échange dans les 6 h avant T0.

**Résultats.** Les OUI des scores qui ont un échange gagnent 48 fois pour 51 attendues par le modèle et 63,5 par le prix payé
(Brier modèle 0,0608, prix 0,0632) : les scores exacts sont **trop chers** (biais des billets improbables), et le modèle le voit.
Mais il y a très peu de paris : 15 à 52 par réglage sur 8 mois (11 à 23 matchs) ; OUI seulement : 0 gagné sur 4 à 6 paris dans
la plupart des réglages ; NON seulement, prix « après » : +9,4 % (33 paris, 17 matchs, 2 mois) à +12,9 % (46 paris, 19 matchs).
Réglage choisi en apprentissage (h = 1 h, « avant » 6 h, avance > 0,03, ρ = −0,1 : +22,9 % sur 30 paris) : **2 paris en test,
tous deux perdus**.

**Verdict : écartée (marchés trop peu négociés).** Les marchés existent mais presque aucun ne s'échange avant le coup d'envoi ;
trop peu de matchs pour un jugement, rien de régulier. La surcote des OUI de scores exacts rejoint la piste n° 10 (queues de
tranches, écartée : le NON à 0,90-0,97 ne laisse rien après frais) ; pas de fantôme.

**Limites.** Échantillon de 505 matchs ; les grandes ligues (Premier League 170 matchs) sont rares dans le tirage ;
Dixon-Coles seulement à ρ = −0,1 ; pas de variante en jeu.

## Ce qu'on en retient

- Le défaut du 22/10 revient sous une nouvelle forme : **le prix « avant » d'un marché mince est souvent périmé** (gain qui
  croît avec l'âge du dernier échange). Pour tout test, ranger les paris « avant » par âge du prix ; ne juger que sur « après ».
- Les marchés liés du sport sont minces : 55 à 75 % sans échange dans les 6 h avant le match.
- La seule piste vivante est structurelle, pas « de cohérence » : en e-sport, le marché suppose des cartes indépendantes ;
  en réalité les séries se finissent 2-0 plus souvent. Au tennis, l'effet de même sens existe pour les sets mais il est
  déjà dans les prix (z −1,1 « avant », rien « après »).

## Reproduire

```
python experiments/score_exact_poisson/releve_marches.py
python experiments/score_exact_poisson/releve_matchs.py 60
python experiments/score_exact_poisson/test_passe.py
python experiments/bo3_coherence/releve_evenements.py cs2 lol dota2 val atp wta
python experiments/bo3_coherence/inventaire.py cs2 lol dota2 val atp wta
FILS=8 python experiments/bo3_coherence/releve_echanges.py 30 cs2 lol dota2 val
FILS=8 python experiments/bo3_coherence/releve_echanges.py 50 atp wta
python experiments/bo3_coherence/test_passe.py esport   # et : tennis
python experiments/bo3_coherence/sous_2_5.py esport
```
