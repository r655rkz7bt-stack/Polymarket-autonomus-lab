# 11/11/2026, passage de 21 h : « cycle arrêté » (panne de GitHub Actions) et `fleuves_prevision` faussement sourde

Passage du chercheur, 20 h 55 UTC. Familles 6 (ce qui ne tourne plus).

## 1. Obligation `cycle_arrete` : dernier cycle du principal à 20 h 17 UTC

- **Constat** : l'enquête automatique (`scripts/enquete.py`, 20 h 55) donne « dernier cycle du principal le 2026-11-11T20:17 ».
- **Vérifié** : exécutions du workflow `cycle` (API GitHub, lecture seule) : toutes « success » jusqu'à celle de 20 h 10 ;
  celle de 20 h 15 reste « queued », celles de 20 h 20 → 20 h 45 finissent en **`startup_failure`**, 20 h 50 et 20 h 55 « queued ».
  Même commit (`1d77762`, fusionné à 16 h 47) que les ≈ 40 exécutions réussies d'avant : rien n'a changé dans le code.
  Le déploiement GitHub Pages de 20 h 17 (workflow de GitHub lui-même, pas le nôtre) échoue aussi en `startup_failure`.
- **Cause** : panne chez GitHub. `www.githubstatus.com` (20 h 58 UTC) : « Actions : major_outage », « Pages : partial_outage »,
  incident ouvert à 20 h 48 (« Actions is experiencing degraded availability »).
- **Chiffre** : aucun ordre, aucun euro ; positions ouvertes (Rhin, Danube, séismes) réglées plus tard, aucune échéance avant le 15/11.
  Le cycle ne relève plus les sources pendant la panne : trou dans `fleuves:histo`, `lid:histo`, `appstore:histo` de la durée de la panne.
- **Correctif** : rien à corriger chez nous (ni `cycle.yml`, noyau, ni le code). Le texte du contrôle `cycle_arrete`
  (`enquete.py`) dit maintenant de regarder `githubstatus.com` d'abord quand les exécutions sont en `startup_failure` / `queued`
  sur un commit qui marchait. Effet de bord : la pull request de ce passage ne peut pas passer `guard` et `tests` tant que la panne dure.

## 2. Constat à la main : `fleuves_prevision` « aucun marché vu n'a la référence » ×224

- **Constat** : abstentions du cycle de 20 h 15 (`published/data.json`) : 0 proposition, raison par défaut (« raison non notée »),
  comme une stratégie sourde.
- **Vérifié** : source `fleuves` « ok (2 prix relevés) » ; relu en direct (`fetch_fleuves` + `market_window` sur les 10 marchés ouverts) :
  seuls « avant le 15/11 » du Rhin (0,3955 calculé) et du Danube (0,726) sont chiffrables (les autres tranches finissent après la
  fin des prévisions, voulu). Ces deux marchés sont **déjà en position** (achats de 16 h) ; `SeismesMarche.propose` les sautait
  sans rien écrire.
- **Correctif** : abstention « déjà en position » (`strategies_v3.SeismesMarche.propose`, hérité par `seismes_pays`,
  `fleuves_prevision`) ; test `test_fleuves.py::test_market_already_held_is_noted_as_such_not_as_deaf`.
- Prix au passage : Danube « avant le 15/11 » 0,54 au milieu (acheté 0,292), Rhin 0,58 (NON acheté 0,362).

## 3. Autres constats « à regarder »

- `positions_oubliees` (`favori_politique_quasi_certain`, 5 marchés) : élection néo-zélandaise, Gamma `closed: false`,
  résultats officiels le 27/11 : voulu, déjà noté le 11/11 au matin.
- `suivre_inities` muette : déjà élucidée le 09/11 (aucun groupe de comptes suspects).
