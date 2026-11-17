# CA-06 : le second candidat est « sans parti », la marge était lue contre 0 voix (17/11/2026, passage de 6 h)

Constat de l'enquête automatique (`estimation_perimee`) sur `marges_californie`, puis famille 3 à la main (« la donnée n'est pas celle
qu'on croit » ; la famille 6 du jour a été faite au passage de 1 h).

## Constat de départ : CA-13 acheté 0,70 estimé 0,99 (pas un défaut)
- 05 h 27 : OUI « CA-13 Democrat 25%+ » (marché 4166599), 12,5 parts à 0,70, estimé 0,99.
- Le décompte officiel (`api.sos.ca.gov`, « ReportingTime » **16/11 19 h 12**, heure du Pacifique = 03 h 12 UTC) passe CA-13 de
  24,93 à **25,09 points** (603 bulletins ajoutés, D +70) : la tranche « 25%+ » devient la tranche courante. Un vendeur restait à 0,70 ;
  le carnet est à 0,90 depuis. C'est exactement l'avantage cherché (source officielle lue avant la foule). Risque réel noté : 0,09 point
  au-dessus de la borne (sortie avec 0,3 % de bulletins à 25 points de marge défavorable) ; les tardifs penchent D partout dans ce district.

## Contrôle à la main : les 13 achats de `marges_californie` relus marché par marché
Script en ligne (journal signé du fantôme, Gamma `/markets/<id>`, API officielle du district) : question, tranche, marge officielle.
12 achats conformes (tranche courante de la marge officielle, bon parti, bon district). **Un achat faux** :

| heure | marché | tranche achetée | marge officielle | estimé | payé |
|---|---|---|---|---|---|
| 01 h 37 | 4166518 | CA-06 « Democrat 25%+ » (OUI) | **D +17,76** (Pan 158 804, Kiley NPP 110 899) | 0,99 | 0,9115 × 20,84 parts = 19,0 € |

## Cause
`marges_californie.lire` prenait les voix du **premier démocrate** et du **premier républicain**. En CA-06, le second des deux
premiers est Kevin Kiley, inscrit « NPP » (sans parti) : aucun républicain, `r = 0`, marge = 158 804 / 269 703 = **58,9 points** au
lieu de 17,76. La règle du marché compte la différence des pourcentages des **deux premiers**, quel que soit leur parti.
Les scripts de recherche (`comptage_tardif/californie_marges.py`, `sortie_tranche.py`) prenaient bien les deux premiers : seul le
module de production était faux (écrit dans le même passage, testé seulement sur des duels D contre R).

## Ampleur
- 52 districts relus : 9 duels entre candidats du même parti (déjà écartés, `meme_parti`) et **un seul** duel avec un sans-parti (CA-06).
- **1 achat, 19,0 € misés** sur une tranche presque impossible (perte attendue ≈ 19 € ; acheteur à 0,01 : revente sans valeur).
  Le principal n'a rien copié (aucun champion). Aucune autre stratégie ne lit `ref:marges_ca`.
- Depuis le premier cycle de production (17/11, 01 h 20) : 4 h 40 de lecture fausse de CA-06 ; la stratégie n'a pris qu'une tranche
  par district (`max_per_event: 1`), d'où un seul achat.

## Correctif
- `lire` : `d − r` = marge signée des **deux premiers** (positive si un démocrate mène) ; `autre_en_tete` quand un sans-parti mène
  (aucune chance donnée : ni les tranches démocrates ni les républicaines ne peuvent gagner).
- Contrôle croisé dans la source : l'API publie aussi les pourcentages des candidats ; si |marge calculée| s'écarte de plus de 0,5 point
  de l'écart des deux premiers pourcentages publiés, le district ne reçoit aucune chance (aurait bloqué CA-06 : 58,9 contre 17,8).
- `marge_tardive` refuse deux relevés incomparables (voix qui baissent, ou plus de voix ajoutées aux deux premiers qu'au total) : le
  journal `marges_ca:histo` de production garde des lignes CA-06 écrites avec l'ancien calcul (`r = 0`).
- Tests du cas réel (`tests/test_marges_californie.py`) : vraie réponse CA-06 du 17/11 ; « Democrat 25%+ » < 0,001, « 15-20% » > 0,97 ;
  ligne de l'ancien calcul sans chance ; journal mixte sans « marge tardive ». Le premier test échoue avec l'ancien code (58,88 ≠ 17,76).

## Contrôle automatique ?
`enquete.py` ne voit que les journaux (estimation, prix payé) : un achat faux à 0,91 estimé 0,99 ressemble à un achat juste. Le
contrôle utile est celui qui compare à la source elle-même : il est dans la source (écart aux pourcentages publiés). Leçon de méthode :
toute nouvelle stratégie à source externe relit ses premiers achats **un par un contre la source** au passage suivant (fait ici).

## Ce qui a aussi été vérifié
- Troisième relevé daté (`comptage_tardif/releves/californie_20261117T0555.jsonl.gz`) : voir `experiments/comptage_tardif.md`, étape 3.
- `estimation_perimee` reste juste comme alerte : sur un marché de façade, un écart de 0,29 est soit une erreur, soit l'avantage ; ici
  c'était l'avantage (CA-13), alors que l'erreur (CA-06) passait sous l'alerte.

## Deuxième contrôle à la main (famille 2) : `convictions_claude`, deuxième de l'arène (+45,1 €)
Journal signé du fantôme (11 achats, 20 ventes, 1 règlement) : le gain réalisé vient d'**un seul pari** (Danube, 20,3 € → 64,5 € revendus,
+44 €) ; Rhin +6, Spotify +5, dette +6 environ ; Gemini Carbon −14,6 € (réglé OUI, conviction NON à 0,88 fausse). Sans le meilleur
pari : ≈ +1 € sur 6 opérations. Aucun défaut de mesure, mais aucune preuve d'avantage non plus : 4 convictions encore ouvertes (3
marges californiennes, Michigan), à juger à leur règlement.
