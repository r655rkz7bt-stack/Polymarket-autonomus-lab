# 25/10/2026 (soir) — tirage de 30 paris réglés (famille 3) et fenêtres de temps (famille 4)

Aucun défaut trouvé. Ce qui a été vérifié, et comment (scripts : `scripts/tirage_famille3_25_10.py`, `scripts/fenetres_25_10.py`).

## Obligations de la feuille de mission
Les mêmes que ce midi (`2026-10-25_midi_tirage_sans_5050_et_chance.md`) : `nf_sport_patiente` et `nf_tennis_12_18h_vainqueur` sans avantage
(26 gagnés pour 26,3 attendus ; 25 pour 26,1), 3 paris = 120 % du gain, un jour = 214 %, 2 anomalies d'audit (achats à 0,001 déjà corrigés le 24/10).
Même mécanisme que ce midi (mises ∝ 1/(1 − prix) sur des favoris à 0,85-0,95) : non refaites.

## Famille 3 — la donnée est-elle celle qu'on croit ?
- 4 742 paris réglés de 118 fantômes ; tirage au hasard (graine 25) de 30 paris réglés depuis le 20/10, relus un à un sur Gamma (`/markets/<id>`) :
  le paiement du journal (0 ou 1) = le prix final officiel du jeton acheté, **30 sur 30**. Questions relues : tennis, e-sport, football (« Will X win »,
  spreads, score exact), UFC, rallyes (« Will Trump say … »), températures, Bitcoin/Ethereum : chaque pari est bien du type que sa stratégie vise
  ; une réserve : `cotes_bookmakers` a acheté un handicap « Spread: FC Barcelona (−2,5) » le 18/10 à 04 h 23, **avant** le correctif du 19/10 (vainqueur seulement, PR #81) ; son journal ne contient aucun achat après le 19/10 à 04 h 24 (20 achats en tout) : normal, la stratégie est **coupée** (`enabled: false`, éliminée par l'arène le 21/10) et `odds_api` rend 0 observation.
- Le journal des fantômes ne porte aucune clé de référence externe (`ref:`…) : on ne peut pas relire a posteriori le rattachement Kalshi/PredictIt/cotes d'un pari ; seules `est_probability`, `net_edge`, `horizon_hours` sont gardées.

## Famille 4 — le filtre ne filtre pas ?
- 716 premiers achats de 19 stratégies à fenêtre (`echeance_min/max`, `heure_utc`) : horizon dans la fenêtre (±0,5 h) pour tous.
- `heure_utc` : 4 achats (`outsider_sport_apres_midi` ×2, `nf_sport_patiente_matin` ×2) hors fenêtre : ce sont des **ordres posés** (`order_type: limite`) posés dans la fenêtre et servis plus tard.
  Voulu (le filtre porte sur le moment de la décision) ; le contrôle `filtre_delai` de l'enquête automatique le sait déjà.

## Constat de suivi (ce passage)
`moins_de_cartes` : 47 paris réglés (42 à midi), 33,5 gagnés pour 26,7 attendus (z 2,0), +19,7 %. Aucun autre fantôme à z > 2 parmi 80 de plus de 15 paris, sauf `compteur_tweets` (24 paris, z 2,2) :
le test de sélection multiple (≈ 80 stratégies) dit qu'un z de 2 est attendu pour la première sans aucun avantage.
