# Séismes : achat contre un marché qui savait déjà (catalogue USGS en retard) — 11/11/2026, passage de 6 h

Famille 3 (« la donnée n'est pas celle qu'on croit » : source en retard), puis 6 (« ce qui ne tourne plus » : outil d'enquête aveugle).
Point de départ : le contrôle à la main des positions ouvertes de l'arène v2 (`published/data.json`) ; `seismes_marche` v2 porte
deux paris presque perdus (−117 € latents) que l'enquête automatique ne signalait pas.

## Constat 1 : un achat fait 19 minutes après un séisme que notre catalogue n'avait pas encore

- Marché 6581738 « Will there be 7 earthquakes of 5.5 or above magnitude worldwide? » (semaine du 02/11 0 h au 08/11 24 h, heure de l'Est).
  NON acheté le 07/11 à 23 h 36 UTC : 91,22 parts à 0,79 (72 €), chance notée 0,931.
- `historique_references` (base sauvegardée) : relevé USGS lu à 23 h 25 → « 4 déjà vus, loi 0,069 pour le OUI ». Le 5,8 de la ride
  médio-atlantique (us7000twun) avait eu lieu à **23 h 17** ; il n'apparaît qu'au relevé suivant (« 5 déjà vus » à 00 h 25).
- Avec 5 séismes, la loi de `seismes.weekly_p` donne 0,199 pour le OUI → NON 0,801 : **aucun avantage** au prix payé de 0,79.
  Le marché, lui, le savait déjà : à 22 h 35 le OUI se vendait 0,12-0,16 ; au cycle de 23 h 35 on achète le NON à 0,79 (OUI à ≈ 0,21).
- Fin de l'histoire : deux autres séismes (6,4 à 03 h 34 et 5,7 à 04 h 52 le 09/11, 1 h avant la fin) portent le compte à 7 ;
  le OUI vaut 0,92 aujourd'hui. Perte attendue ≈ −65 € (−72 € latents) ; elle aurait eu lieu même sans le retard, mais le pari
  n'aurait **jamais été pris** (écart 0,01 < `min_net_edge` 0,05).

## Ampleur (script `experiments/enquetes/scripts/seismes_retard_catalogue_11_11.py`)

Les 47 achats de `seismes_marche` (v1 et v2) refaits avec le catalogue USGS d'aujourd'hui, à l'instant exact de l'achat :
- 40 achats : chance recalculée = chance notée (±0,002) : le modèle lit bien son catalogue ;
- 6 achats du 24/10 (v1) : écarts dus au doublon entre réseaux `pt`/`us`, déjà corrigé ce jour-là (`max_ecart_doublon`) ;
- **1 achat (07/11 23 h 36) : 0,931 noté, 0,801 réel** : le seul cas de retard du catalogue, et le plus gros pari perdant du v2.
Un seul cas sur 47, mais il revient à chaque séisme >= 5,3 publié pendant qu'un marché séismes est ouvert (≈ 1 par jour) : la
fenêtre dure 10 à 30 minutes, le cycle tourne toutes les 5 minutes, et le marché bouge dans la minute.

## Cause

`sources/usgs.py` lit le catalogue toutes les 10 minutes ; `max_stale_hours` (0,25) ne vérifie que l'âge de NOTRE lecture, pas
que le catalogue est complet. L'USGS publie un séisme lointain 10 à 30 minutes après son heure d'origine ; d'autres réseaux
(EMSC, GFZ, alertes) le donnent plus tôt, et les acheteurs du marché les lisent.

## Correctif

- Nouvelle source `emsc` (`sources/emsc.py`, `seismicportal.eu`, sans clé, toutes les 10 minutes, `settings.yaml`) : témoin, pas arbitre.
- `seismes.attach_seismes` calcule aussi `p_rapide` : la même loi en ajoutant les séismes vus par l'EMSC et sans séisme USGS à
  moins de 2 minutes (`seismes.unmatched`), si le relevé EMSC a moins de 30 minutes.
- `seismes_marche` s'abstient (« séisme vu par l'EMSC, pas encore par l'USGS ») si `|p_rapide − p|` > `max_ecart_rapide` (0,03).
- `vu` : chaque séisme des deux relevés garde l'heure de sa première lecture (`seismes.first_seen`) : dans une semaine, on saura
  laquelle des deux sources publie la première, et de combien. **Non vérifié aujourd'hui** : que l'EMSC soit plus rapide que
  l'USGS pour les séismes lointains (sa date de première publication n'est pas dans son catalogue). Si `vu` montre le contraire,
  le témoin ne sert à rien et il faudra une autre idée (par exemple : ne pas acheter le côté « peu de séismes » quand le marché a
  bougé contre nous depuis le cycle précédent).

## Tests (cas réels)

- `test_real_case_of_7_november_a_quake_missing_from_usgs_makes_the_strategy_abstain` : les 4 séismes USGS et le 5,8 de 23 h 17
  vu par l'EMSC → `p` 0,069 (NON 0,931, ce que le cycle a cru), `p_rapide` 0,199 (NON 0,80).
- `test_strategy_abstains_when_the_fast_catalog_sees_a_missing_quake`, `test_emsc_without_new_quake_or_stale_changes_nothing`,
  `test_first_seen_keeps_the_first_sighting_of_each_quake`, `test_parse_emsc_reads_iso_origin_time_and_unid`.

## Contrôle automatique

`enquete.catalogue_en_retard` : tout achat `seismes_marche` fait après l'heure d'origine d'un séisme >= 5,25 mais avant notre première
lecture de ce séisme (`vu`). Lit `ref:usgs` dans la base (production : `research_brief`, local : la sauvegarde). Test
`test_earthquake_buy_made_while_usgs_had_not_yet_published_a_quake_is_flagged`. Il ne voit que les achats à partir d'aujourd'hui
(le champ `vu` n'existait pas).

## Constat 2 (famille 6) : l'enquête locale ne lisait plus aucune stratégie vivante

`scripts/enquete.py` (`load_published`) lisait `published_data/ledger/fantome/`, où ne restent que les journaux v1 éteints ; les
fantômes du labo v2 écrivent dans `fantome_v2/` depuis le 07/11. Du 07 au 11/11, `.venv/bin/python scripts/enquete.py` (étape 0.3
de la routine) rendait 60+ constats sur les stratégies v1 et aucun sur les 9 stratégies vivantes. L'enquête publiée par le cycle
(`research_brief`) n'était pas touchée. Correctif : `fantome_v2` d'abord ; test `test_local_investigation_reads_the_v2_ghost_ledgers`.

## Autres vérifications de ce passage

- `positions_oubliees` (5 positions de `favori_politique_quasi_certain`) : élection néo-zélandaise du 07/11, réglée sur les
  résultats OFFICIELS de la Commission électorale, attendus le 27/11 (≈ 400 000 votes spéciaux) : attente normale, pas un défaut.
- `estimation_perimee` de `compteur_tweets` (« 200+ » de Trump, 08/11) : le faux 0,95 de la rafale, traité le 08/11 (`desaccord_max`).

## Constat 3 (famille 6) : des refus du contrôleur invisibles

Au cycle local, `seismes_pays` a proposé le NON « États-Unis » et le contrôleur l'a refusé « carnet périmé (25 790 s > 120 s) » :
l'horodatage d'un carnet de la CLOB est celui de sa dernière modification, et ce marché calme n'avait pas bougé depuis 7 h
(`proposals/2026-11-11_carnet_calme_juge_perime.md`, décision d'Etienne : c'est l'entrée d'un contrôle du noyau). Ce refus n'apparaissait
que dans le journal du cycle : ni dans `abstentions` publiées, ni dans l'enquête. Correctif : `main._note_refus` ajoute « refusé par le
contrôleur : <motif> » aux raisons d'abstention (avant et après relecture), contrôle `enquete.refus_controleur` ; tests
`test_controller_refusals_show_up_in_the_published_abstentions`, `test_controller_refusals_published_in_abstentions_are_a_lead`.
