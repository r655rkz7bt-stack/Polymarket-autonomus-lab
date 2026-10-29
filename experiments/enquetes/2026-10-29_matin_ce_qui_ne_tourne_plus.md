# 29/10/2026 (matin) : ce qui ne tourne plus (famille 6) et `moins_de_cartes` relue

Questions : (1) des positions restent-elles ouvertes sur des marchés que Gamma a clos (argent bloqué, règlement manqué) ?
(2) quelles stratégies vivantes sont muettes depuis 48 h, et pourquoi ? (3) constat « à regarder » `moins_de_cartes` copiée par
le principal (15 gagnés pour 17,1 sur 30, −8,3 %) : défaut ou hasard ?

Scripts : `experiments/enquetes/scripts/positions_fermees_gamma_29_10.py`, `positions_fermees_actifs_29_10.py`,
`gamma_marches_29_10.py`, `moins_de_cartes_blocs_28_10.py` (rejoué).

## Constat
- **Positions ouvertes depuis plus de 3 jours : 537 marchés** relus un par un sur Gamma (`/markets/<id>`, 0 erreur) ; 172 sont clos.
  Les 215 positions ouvertes sur ces marchés clos (6 218 € virtuels) sont toutes dans des **portefeuilles éteints** (35 journaux dont le
  dernier événement date du 17 ou du 21/10 : `news_momentum`, `meteo_prevision`, `reversion`, `nf_politique`…). Aucun portefeuille
  qui a écrit dans les dernières 24 h, ni le principal, ne garde une position sur un marché clos : **les règlements tournent**.
  Les quatre positions « échéance dépassée de 78 h » de l'enquête automatique sont des marchés encore non clos (litiges/UMA, déjà notés).
- Conséquence à connaître : les paris d'un portefeuille éteint qui se règlent après son arrêt ne sont jamais écrits ; les comptes
  « gagnés pour attendus » de ces stratégies s'arrêtent à leur dernier règlement (pas de biais de gagnant, les marchés tombent au hasard).
- **Stratégies vivantes muettes depuis 48 h : 53 sur 186.** Les raisons lues dans `published/data.json` (`abstentions`) sont
  des filtres qui attendent leur marché : `mots_prononces_nfl` (aucune question NFL ouverte avant dimanche), `jobs_favori_non` (hors
  fenêtre avant la publication), `box_office_favori`, `saison_non`, `candidats_non`, `detroits_non_normal`, `cross_market` (« aucun écart
  après frais » sur 50 paires), `manifold_reference` / `predictit_reference` (avantage net insuffisant). Seule `suivre_inities` (363
  marchés, « raison non notée ») est sourde : la piste est écartée (`inities.md`), le fantôme ne sert plus qu'à vérifier.
- `moins_de_cartes` (104 paris réglés) : 64,0 gagnés pour 58,6 attendus, z +1,08, +6,5 % par mise. **Avant le 25/10 20 h : 57 paris, +26,7 %,
  z +2,33 ; depuis : 47 paris, 23 gagnés pour 26,2, −10,1 %, z −0,96.** C'est ce que prévoit un effet de découverte qui se dissout :
  l'« indice » du 25/10 n'est pas confirmé sur les 47 paris suivants. Aucun défaut de code (copie fidèle vérifiée le 28/10).

## Correctif
Aucun défaut trouvé : rien à corriger dans le code. À regarder : `moins_de_cartes` reste un indice, pas une preuve (z par prix +1,08).

## Limites
Les raisons des 53 muettes sont lues sur un seul cycle (05 h 45 UTC) ; une muette qui attend un marché de dimanche (NFL) ou de vendredi
(App Store) n'est pas en panne. Le contrôle des 537 marchés ne couvre que les positions de plus de 3 jours.
