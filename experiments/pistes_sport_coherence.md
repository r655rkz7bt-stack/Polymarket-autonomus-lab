# Pistes n° 1, 4 et 5 : la cohérence des marchés de sport (score exact, cartes d'e-sport, sets de tennis)

Étude du 22/10/2026 (session à part du passage chercheur). Idées tirées de `experiments/vingt_cinq_pistes.md`.
Scripts : `experiments/score_exact_poisson/`, `experiments/bo3_coherence/` (code commun aux pistes 4 et 5 :
`series.py`, `echanges.py`), `experiments/tennis_sets_coherence/`. Sorties complètes : `resultats.txt` de chaque dossier.
Données (ignorées par Git) : `donnees/` de chaque dossier.

## En bref

| piste | question | verdict | chiffres clés (aux prix réellement payés, après frais) |
|---|---|---|---|
| n° 5 `tennis_sets_coherence` | « set 1 », « gagne en 2 sets », « nombre de sets » s'accordent-ils avec « vainqueur du match » ? | **écartée (trompeuse)** | prix « après » T0 : −8,9 % à +1,4 % par pari (t par match −0,9 à +0,3) ; le gain du prix « avant » (+9,8 %, jusqu'à +74 % sur 31 paris) vient d'échanges vieux de 2 à 6 h (prix périmés) |
| n° 4 `bo3_coherence` | « carte 1 », « handicap de cartes », « nombre de cartes » s'accordent-ils avec « vainqueur de la série » ? | _à remplir_ | _à remplir_ |
| n° 1 `score_exact_poisson` | les scores exacts sont-ils mal cotés par rapport à une loi de Poisson tirée du vainqueur et des « plus/moins de 2,5 buts » ? | _à remplir_ | _à remplir_ |

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
