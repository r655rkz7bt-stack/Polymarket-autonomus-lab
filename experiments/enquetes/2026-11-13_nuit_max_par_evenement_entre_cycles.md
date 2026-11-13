# 13/11/2026 (passage de 1 h) : `max_per_event` ne valait que pour le cycle en cours

## Point de départ
Constat « à regarder » de l'enquête automatique (`estimation_perimee`) : `taux_tresor_barriere` a acheté entre 00 h 05 et 00 h 27 UTC
16 « Yes » de barrières de taux (136 € sur 1 000), dont « 2 ans ≥ 5,02 % en novembre » estimé 0,463 et payé 0,088, « 5 ans ≥ 5,25 %
avant 2027 » estimé 0,451 et payé 0,13.

## Ce que j'ai vérifié
1. **Rattachement** : les 16 marchés relus sur Gamma (`/markets/<id>`) : bonne durée, bon niveau, bon sens (« hit »), bonne fenêtre.
2. **Chance** : clôtures du Trésor relues (CSV de l'année) : 2 ans 4,56 (09/11) → 4,73 (10/11) → 4,86 (12/11), 10 ans 4,88 → 5,10,
   30 ans 5,26 → 5,43. Écart-type des 60 jours 0,064 (2 ans) × 1,3 = 0,083 par jour, 11 clôtures restantes : il manque 0,16 point
   pour 5,02, soit ≈ 0,58 écart-type sur la période → barrière ≈ 0,46. **Le modèle calcule ce qu'il dit.**
3. **Le marché** : l'échelle du 2 ans est elle-même serrée : 4,88 (milieu 0,78), 4,92 (0,59), 4,97 (0,30), 5,02 (0,05, vendeur 0,082,
   13 $ échangés dans la journée). Le marché met 25 % de chance sur un maximum entre 4,97 et 5,02 : il suppose un écart-type par jour
   ≈ 0,03-0,04, moitié du nôtre, alors que les deux dernières séances ont bougé de +0,17 et +0,13. Désaccord de modèle (c'est
   l'expérience), pas un défaut de donnée. À suivre au règlement (30/11).

## Défaut trouvé : le plafond par événement ne comptait pas les positions déjà tenues
`SeismesMarche.propose` (`strategies_v3.py`), dont héritent 13 stratégies, limitait les tranches d'un même événement à
`max_per_event` **dans le cycle** ; au cycle suivant, le compteur repartait de 0. Le même défaut existait dans `SiegesCoherence`,
`ToucherMetaux` et `SpaceXCumul` (retirées).

**Chiffrage** (journaux v2 publiés, positions tenues au moment de l'achat) : 6 achats au-delà du plafond, ≈ 123 € de mises :

| stratégie | plafond | événement | achat en trop |
|---|---|---|---|
| `taux_tresor_barriere` | 2 | 1310160 (10 ans, novembre) | 13/11 00 h 16, 6,5 parts à 0,409 (2,7 €) |
| | 2 | 1310158 (30 ans, novembre) | 13/11 00 h 16, 20 parts à 0,088 (1,8 €) |
| | 2 | 1310114 (5 ans, novembre) | 13/11 00 h 27, 46,8 parts à 0,399 (18,7 €) |
| `seismes_marche` | 2 | 1326719 (semaine ≥ 5,5) | 11/11 07 h 17, 53 parts à 0,88 (46,7 €) |
| | 2 | 1326718 (semaine ≥ 6,5) | 12/11 08 h 26, 5 parts à 0,89 (4,5 €) |
| `auditeurs_spotify` | 1 | 1274351 | 11/11 21 h 41, 248 parts à 0,196 (48,7 €) |

Effet : des paris liés (« une seule trajectoire », « un seul tirage ») comptés comme indépendants : la mise réelle sur un même tirage
dépassait celle que l'hypothèse de la stratégie annonçait (famille 4 : le filtre ne filtre pas, et famille 5 : paris liés).

## Correctif
- `strategies_v3._held_per_event(state)` : nombre de marchés distincts déjà tenus par événement (le `Position` du journal porte
  `event_id`), point de départ du compteur dans les quatre classes.
- Test du cas réel : `tests/test_taux_tresor.py::test_max_per_event_counts_positions_already_held` (deux seuils de l'événement
  1310160 tenus → plus d'achat, abstention « déjà deux tranches de cet événement »).
- Contrôle **`plafond_par_evenement`** dans `enquete.py` (grave) : rejoue achats, ventes et règlements de chaque fantôme qui a un
  `max_per_event` et signale tout achat qui porte au-delà le nombre de marchés tenus ; ne regarde que les achats d'après le correctif
  (`PLAFOND_EVENEMENT_DEPUIS`, 13/11 03 h UTC) ; sans cette date, il retrouve les 6 achats ci-dessus. `jambes_meme_evenement`
  (≥ 3 marchés en 2 h pour ≥ 100 €) ne les voyait pas. Test : `tests/test_enquete.py::test_more_markets_held_in_one_event_than_max_per_event_is_grave`.
- Les positions déjà prises restent (journal signé) ; elles se règlent normalement.

## Contrôle à la main, famille 2 (la mesure récompense la chance ; jour 13 → famille 2)
Paris v2 réglés, gagnés (paiement 0 / 0,5 / 1) contre attendus (prix payés), z par événement, gain sans les 3 meilleurs :

| fantôme | paris | événements | gagnés / attendus | z par événement | gain | sans les 3 meilleurs |
|---|---|---|---|---|---|---|
| `compteur_tweets` | 19 | 7 | 11,0 / 11,8 | −0,43 | −37,2 € | −54,7 € |
| `compteur_truth` | 4 | 1 | 3,0 / 3,3 | −0,42 | −11,6 € | −25,0 € |
| `seismes_marche` | 3 | 2 | 0 / 2,4 | −3,68 | −144,5 € | — |
| `non_aux_drames` | 2 | 2 | 1 / 1,7 | −1,47 | −8,4 € | — |
| `convictions_claude` | 1 | 1 | 0 / 0,5 | −0,98 | −14,6 € | — |
| `favori_politique_quasi_certain` | 2 | 1 | 2 / 2,0 | +0,20 | +0,7 € | — |
| `compteur_tweets_72_168h` | 1 | 1 | 1 / 0,6 | +0,85 | +3,0 € | — |

Aucune stratégie v2 ne bat ses prix ; la première de l'arène (`compteur_tweets_72_168h`, +3 €) n'a qu'un pari : rien à promouvoir
(le principal reste au repos, conforme). `seismes_marche` (0 pour 2,4, estimations 0,85-0,97) : déjà expliqué le 11/11 (catalogue
USGS en retard, garde EMSC ajoutée) ; ses 3 achats d'après la garde ne sont pas encore réglés.
