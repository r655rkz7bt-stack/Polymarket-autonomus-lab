# 12/11/2026, passage de 1 h : principal au repos depuis le 07/11, sources relevées sans lecteur

Passage du chercheur, 00 h 55 UTC. Aucune « Enquête obligatoire » (seule obligation : idée radicalement différente,
traitée en partie B). Contrôle à la main : **famille 1** (12 mod 6 + 1 : le principal fait-il les paris qu'il doit faire ?),
puis un constat « à regarder » (`sources_vides`).

## 1. Famille 1 : copie du principal depuis la remise à zéro v2

- **Journal signé du principal** (`published_data/ledger/ledger.jsonl`, lu le 12/11 à 00 h 52) depuis le 07/11 :
  1 453 battements, 45 règlements, **5 achats, tous le 07/11 avant 15 h 17**, puis un `PROMOTION` du 07/11 à 18 h 21 :
  champion « » (« le champion ne bat plus ne rien faire »), ancien champion `compteur_tweets_v1.0.0`.
- **Fantômes v2** sur la même période : 141 achats (`non_aux_drames` 44, `compteur_tweets` 36,
  `favori_politique_quasi_certain` 24, `compteur_tweets_72_168h` 10, `compteur_truth` 10, `seismes_marche` 8,
  `convictions_claude` 4, `fleuves_prevision` 2, `auditeurs_spotify` 2, `seismes_pays` 1).
- **Attendu** : sans champion ni validée qualifiée (`config/promotion.yaml` : `validated_strategies: {}`, entrée à
  12 opérations clôturées, 12 h, croissance ≥ 0,02), le principal ne copie rien. Aucune stratégie v2 n'a 12 opérations
  clôturées (la plus avancée : `compteur_tweets`, 18, croissance −0,041). **0 copie sur 141 : conforme.**
- Capital du principal : 582,87 € disponibles, 663,27 € estimés (positions v1 qui attendent leur règlement, dont la
  Nouvelle-Zélande le 27/11). Rien de bloqué hors UMA.
- **Constat (pas un défaut de code)** : le principal n'a rien misé depuis 4,4 jours et ne misera pas avant qu'une stratégie v2
  ait 12 paris clos et +2 %. Les stratégies v2 parient sur des échéances longues (séismes du mois, fleuves au 15/11, Spotify au 30/11,
  `non_aux_drames` à 51-82 jours) : au rythme actuel, pas de champion avant fin novembre. C'est le prix d'une arène neuve ;
  ce n'est pas à moi de forcer une copie sans preuve (règle de l'arène : la preuve décide de la place au principal).

## 2. Constat « à regarder » : `sources_vides`

- `meteo_metar` (60 stations toutes les 15 min), `meteo_prevision` (toutes les heures), `mlb_stats`, `football_data`,
  `references_football` : « ok (0 …) ».
- **Vérifié** : aucune des 13 stratégies v2 ne lit ces sources (`strategies_v3.py`, `config/strategies.yaml` ; seule
  `suivre_inities` lit `inities`, muette pour la raison déjà élucidée le 09/11). Ce sont des restes de la v1 : la saison MLB
  est finie (0 match), les marchés météo n'ont plus de stratégie. Aucun euro faussé ; coût = temps de cycle et appels.
- **Pas de correctif** dans ce passage : `meteo_ensemble` (relevé utile à la recherche) dépend du même bloc météo, et couper
  une source sans lecteur ne change aucun résultat. À couper si le temps de cycle devient un problème.

## 3. Autres constats « à regarder »

- `positions_oubliees` (`favori_politique_quasi_certain`, 5 marchés de Nouvelle-Zélande) : relus sur Gamma à 00 h 58,
  `closed: false`, prix 0,986-0,9935 du côté acheté ; résultats officiels le 27/11 : voulu.
- `reglements_50_50` : 5 marchés de la v1 (21/10-04/11), déjà connus.
- `refus_controleur` (`seismes_pays`, « carnet périmé ») et `suivre_inities` muette : déjà élucidés
  (`proposals/2026-11-11_carnet_calme_juge_perime.md`, 09/11).

## 4. Deuxième contrôle à la main, famille 3 : 10 paris v2 tirés au hasard, relus sur Gamma

Tirage `random.seed(1112)` parmi les 141 achats des fantômes v2 ; marché brut relu (`/markets/<id>`, `/events/<id>`).

| achat | stratégie | pari | état Gamma (12/11 01 h) |
|---|---|---|---|
| 07/11 22 h | compteur_truth | NON « Trump 140-159 posts du 3 au 10/11 » à 0,844 | clos, NON gagné |
| 08/11 | non_aux_drames | NON « Aryeh Deri quitte la tête du Shas d'ici le 31/12 » à 0,905 | ouvert, 0,905 |
| 10/11 | seismes_marche | NON « 7 séismes ≥ 5,5 » à 0,88 | ouvert, 0,86 |
| 10/11 | favori_politique_quasi_certain | OUI « pourparlers Russie-Ukraine d'ici le 15/11 » à 0,985 | clos, OUI gagné |
| 07/11 | non_aux_drames | NON « Tusk out d'ici le 31/12 » à 0,96 | ouvert, 0,974 |
| 11/11 | compteur_tweets | OUI « Musk 240-259 du 6 au 13/11 » à 0,251 | ouvert, 0,2345 |
| 08/11 | non_aux_drames | NON « Polanski quitte la tête des Verts » à 0,95 | ouvert, 0,935 |
| 07/11 | compteur_tweets | OUI « Musk 90-114 du 7 au 9/11 » à 0,30 | clos, OUI gagné |
| 11/11 | non_aux_drames | NON « fewer than 215 House members vote to impeach Hegseth » à 0,96 | ouvert, 0,9815 |
| 08/11 | compteur_tweets | NON « Musk 1 000+ en novembre » à 0,12 | ouvert, NON à 0,265 |

- Le seul pari suspect à première vue (« fewer than 215 … impeach Hegseth », NON acheté par une stratégie « non aux drames ») est
  **conforme** : c'est une tranche d'une échelle (événement 1328044) qui a sa propre tranche « no House floor vote » (0,968) ;
  sans vote, « fewer than 215 » se règle NON. Le NON = « pas de vote, ou un vote à 215 ou plus » : bien le côté sans drame.
- 3 réglés sur 3 dans le sens attendu par la stratégie ; les 7 ouverts ont le bon type de pari, la bonne fenêtre, la bonne date.

## Bilan

Rien trouvé qui fausse un résultat ; vérifié : principal contre fantômes (0 copie attendue, 0 faite), sources relevées sans lecteur,
positions ouvertes du principal. Aucune modification du code.
