# `apres_echeance` achète pendant le match, huit jambes d'un coup (23/10/2026)

Passage chercheur du 23/10 (9 h 55 UTC), famille n° 6 puis contrôle des obligations de `published/rapports/enquete.md`.

## Constat
- Obligation `champion_sans_avantage` sur `apres_echeance_v1.0.0` (copiée par le principal) : 22 gagnés pour 28,9 attendus sur 30 opérations, −23,7 %.
- Journal du fantôme (173 achats, du 20/10 11 h au 23/10 02 h) : +123 € du 20 au 22/10, puis **−475 € le 23/10** (8 pertes sur 23 achats,
  1 242 € misés). Les 8 pertes sont **un seul match** : Cavaliers contre 76ers (NBA, coup d'envoi 22/10 23 h 00 UTC), joué par huit marchés
  (vainqueur, cinq écarts, total) achetés à 0,95-0,97 entre 00 h 02 et 00 h 52, soit **1 h à 1 h 52 après le coup d'envoi**.
  Le match n'était pas fini : les Cavaliers ont perdu.
- Par retard depuis le coup d'envoi (champ `depuis_coup_d_envoi_h` du journal), tous achats réglés :

  | retard | achats | gagnés | attendus par les prix | gain | misé |
  |---|---|---|---|---|---|
  | 1-2 h | 140 | 130 | 134,4 | **−381 €** (−7,8 %) | 4 905 € |
  | 2-3 h | 22 | 22 | 21,2 | +22 € | 551 € |
  | 3-4 h | 3 | 3 | 2,9 | +5 € | 107 € |
  | 6 h et plus | 1 | 1 | 1,0 | +1 € | 33 € |

  (Peu d'achats après 2 h : l'échantillon ne prouve rien sur l'après, seulement que « 1-2 h » est le mauvais moment.)
- Le principal copie `apres_echeance` (×0,33) : 17 achats, **−12 €** au total ; le soir du 23/10 il a pris trois jambes des Cavaliers (≈ 16 €)   (sa mise est le tiers de celle du fantôme).

## Cause
`ApresEcheance.candidates` (`strategies_v3.py`) prend les marchés `ended` du scanner (`end_date` dépassée). Pour un match, Gamma met comme
`endDate` le **coup d'envoi** (date placeholder, voir les astuces techniques de `docs/ROUTINE_CHERCHEUR.md`) : « échéance passée » veut dire « le match
a commencé », pas « le match est fini ». La stratégie fixe `est = 0,985` quel que soit le retard, et ne limite pas les jambes d'un même événement
(vainqueur, écarts et totaux tombent ensemble).

## Correctif
- `ApresEcheance` : paramètre `heures_apres_coup_d_envoi_min` (3 h dans `config/strategies.yaml`) : un marché de match n'est pas acheté tant que
  `maintenant − game_start` est plus court (abstention « match probablement en cours »). 3 h est un choix prudent (NBA ≈ 2 h 30, tennis 1-3 h,
  football ≈ 2 h) tiré du tableau ci-dessus, **pas une preuve** : le fantôme dira si les achats à 3 h et plus gardent leurs 100 %.
- Un seul pari par événement (`événement déjà joué`), pour les jambes d'un même match.
- Contrôle `jambes_meme_evenement` dans `enquete.py` : ≥ 3 marchés d'un même événement achetés par le même fantôme dans les 2 heures pour ≥ 100 €
  (hors arbitrages et teneurs de marché). Premier passage sur les journaux : 6 fantômes concernés, dont `apres_echeance` (9 marchés, 524 € sur le
  match NBA), `nf_court_soir` (277 €), `nf_court_prix_haut` (188 €) : pistes à surveiller, pas de perte anormale (naive_favorite et la championne :
  événements à plusieurs jambes = +64 € et +49 € sur 948 € et 480 € misés).

## Autre point : achat du principal sans jumeau (obligation `copie_fidele`)
`contrer_crypto_patiente`, 23/10 04:01 : le principal a eu 5,07 parts à 0,072 (0,36 €) d'un ordre posé copié du fantôme (identifiant `P67d9cdb4…`).
Le fantôme, passé avant lui dans le cycle, n'a pas été servi ce cycle-là ; son ordre est remplacé à 04:25 (0,065, 65 parts servies à 04:25 et 04:38).
Même pari, exécution décalée (le principal relit le carnet plus tard dans le cycle). Pas de défaut de copie : le contrôle classe maintenant un tel
cas (ordre posé, le fantôme achète le même jeton dans les 48 h) à « à regarder » et non « grave » ; un achat sans aucun jumeau reste grave
(`test_posted_order_copied_and_served_before_the_ghost_is_a_lead_not_grave`).

## Autres obligations (rien de neuf)
`nf_sport_patiente` : 3 paris = 126 % du gain et le 18/10 = 225 % : causes écrites le 22/10 (`2026-10-22_championne_biais_et_mises.md`).
`nf_sport_patiente_prix_850_875` : 25 gagnés pour 25,6 attendus (+1,5 %) : même mécanisme (mise ∝ 1/(1 − prix), aucun avantage mesuré).

## Contrôle à la main, famille n° 6 (ce qui ne tourne plus) : rien de cassé
Cycle local complet (`run_simulation.py --once --dev-key`, lignes « abstentions ») : 14 fantômes sans aucun achat depuis leur naissance.
- **Calendrier** : `cpi_tranches` (CPI du 11/11, fenêtre 20-170 h), `jobs_favori_non` (emploi du 6/11, fenêtre 4-72 h), `statu_quo_ia` (fenêtre
  12-35 jours : « best AI model end of October » est à 8 jours, « end of November » à 39) : leurs marchés existent sur Gamma, la fenêtre d'entrée
  n'est pas ouverte (le plus proche : statu_quo_ia vers le 27/10).
- **Pas d'écart à prendre** : `kalshi_reference` (260 relevés, écart d'achat maximal 0,016), `manifold_reference` (201 relevés, 0,036), tous
  sous `margin` 0,03-0,05 ; `predictit_reference` (781 relevés, 79 écarts > 0,04 mais jusqu'à 0,38 sur « prochain porte-parole de la Maison Blanche »)
  : les écarts > `max_gap` 0,20 sont refusés exprès (contrat mal rattaché plus probable qu'un vrai écart). `paire_oui_non`, `marches_jumeaux`,
  `coherence_match`, `implication_politique` : « paire cohérente : aucun écart après frais » (419, 2, 59, 6 abstentions).
- **Sans clé** : `cotes_tennis`, `football_trois_issues`, `futurs_bookmakers` (ODDS_API_KEY absente de la session locale ; en production le budget
  de cotes est étalé depuis le 22/10).
- À surveiller : `references: ok (kalshi 0, predictit 0, manifold 0 …)` dans la session locale (aucun marché rattaché sans historique de
  cycles) alors que la production en rattache (11, 35 et 12 marchés le 22/10) : normal, pas de défaut.
