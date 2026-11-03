# 03/11/2026 (matin) : la Data API v1 de Polymarket est retirée (famille 6, « ce qui ne tourne plus »)

## Constat
- Enquête automatique : 7 stratégies « sans aucun achat depuis plus de 48 h », dont `suivre_inities` et `suivre_inities_seul`
  (nées le 27/10, 413 marchés vus, « aucun marché vu n'a la référence demandée »).
- `published/data.json` → `sources.etat.inities` : « indisponible : GET https://data-api.polymarket.com/trades : HTTP 410 ».
- `curl https://data-api.polymarket.com/trades?limit=2` → 410 `{"error":"Data API v1 has been retired","migration":".../v2/"}`
  (idem `/activity`, `/positions`, `/traded`). Les deux fantômes n'ont donc jamais pu voir un seul compte suspect depuis la
  retraite de la v1 ; rien n'avertissait (la source était « indisponible », pas un constat de l'enquête).

## Cause
`inities.py` (flux d'échanges, `/activity`, `/traded`) et `idea_test.fetch_event_trades` (tous les tests aux vrais échanges)
lisaient la v1. Une cinquantaine de scripts de `experiments/` aussi (relevés d'échanges) : **ils répondent 410 aujourd'hui**.

## Ce que la v2 change (relevé à la main le 03/11)
- Adresse `https://data-api.polymarket.com/v2/…` ; réponse `{"data": [...], "pagination": {"has_more", "next_cursor"}}`.
- Champs en snake_case : `proxy_wallet`, `token_id`, `condition_id` (v1 : `proxyWallet`, `asset`, `conditionId`).
- **Pages par curseur** (`cursor=`), plus d'`offset` (« 'offset' is not a query param ») : plus de plafond de 10 000 échanges.
- **Un paramètre inconnu est ignoré sans erreur** : `trades?market=<condition>` ou `?event=<id>` rendent les échanges de tout
  Polymarket. Seuls `event_id` / `eventId` et `condition` (alias `condition_id`, `conditionId`) filtrent. Piège pour tout script.
- `/traded` n'existe plus ; `/user-stats?user=` donne `join_date` et `trades` (nombre d'échanges, pas de marchés).
  `/activity` se trie par `sortBy=TIMESTAMP&sortDirection=ASC` comme avant.

## Correctif
- Nouveau `src/polymarket_agent/data_api.py` : lecture par curseur, lignes remises au format v1 (les deux écritures restent),
  `profil()` (via `/user-stats`). `inities.py` et `idea_test.py` l'utilisent. Une source qui échoue n'est plus mise en cache vide.
- Écart assumé : le « nombre de marchés » d'un compte devient son nombre d'échanges (toujours ≥ marchés) : le filtre « compte
  concentré » (`marches_max` 15) est plus strict qu'avant, jamais plus large. Essai en direct (Spotify, Billboard) : profils lus.
- Contrôle `sources_retirees` (GRAVE) dans `enquete.py` : toute source « indisponible » avec HTTP 404/410 devient une obligation.
- Tests : `test_data_api_v2_pages_by_cursor_and_filters_by_event_03_11` (curseur, filtre `event_id`, premier échec levé, profil),
  `test_a_retired_api_is_a_grave_finding_03_11`, tests d'`inities` passés au format v2. Suite complète : verte.

## Reste ouvert
- Les ~50 scripts de relevé d'`experiments/` lisent encore la v1 : à passer sur `data_api.lire` quand une piste les relance
  (ne pas pagner par `offset`, ne pas filtrer avec `market=`).
- `suivre_inities*` : voient les comptes à partir du prochain cycle ; premier jugement à leurs premiers paris.
