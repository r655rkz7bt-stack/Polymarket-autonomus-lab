# 12/11/2026 (soir) — la remise à zéro du capital passait pour un écart de trésorerie

## Constat
Obligation `tresorerie_rejouee` (GRAVE) au passage de 16 h : « principal : trésorerie rejouée 582,87 € contre 1 000,00 € notés le 2026-11-12T15:52 ».

## Chiffrage
- Journal du principal : écriture `RESET` n° 9394 à 13 h 54 UTC (« Départ du labo v2 », capital 1 000), faite par Etienne avec le workflow `reset-capital`.
- Avant le RESET, le rejeu tombait juste : 582,87 € rejoués = 582,8689 € notés au battement de 13 h 52 (le contrôle était muet).
- Après : 25 battements à 1 000 €, aucun achat, aucun règlement. Aucun euro faussé : le capital est bon, c'est le contrôle qui se trompait.
- Positions ouvertes effacées par le RESET : ≈ 68 € de valeur estimée (650,88 − 582,87) ; `ledger.py` vide `positions`, aucun règlement de ces jetons n'est attendu (vérifié : 0 SETTLE après 13 h 54).

## Cause
`src/polymarket_agent/enquete.py`, `tresorerie_rejouee` : seule l'écriture `GENESIS` remettait la trésorerie au capital initial ; `RESET` était ignoré, alors que `ledger.py` (`_apply`, branche `RESET`) remet trésorerie, positions et résultats à zéro. Les autres contrôles qui rejouent le journal (`capital_series`, l. ≈ 324, 789, 1327) traitaient déjà `RESET`.

## Correctif
- `RESET` traité comme `GENESIS` : trésorerie = capital donné, positions et jetons déjà réglés oubliés (un jeton réglé avant et après une remise à zéro n'est pas un « règlement en double »).
- Test du cas réel : `tests/test_enquete.py::test_replayed_cash_restarts_at_a_reset`.
- Enquête relancée : plus d'obligation.

## Contrôle à la main (famille 1 : le principal fait-il ce qu'il doit ?)
Champion « aucun » depuis le 07/11 : 5 achats le 07/11 (avant la promotion à « aucun »), puis seulement des règlements d'anciennes positions v1 (47) jusqu'au RESET, 0 achat depuis. Conforme.
`positions_oubliees` (5 positions Nouvelle-Zélande de `favori_politique_quasi_certain`) : déjà connu, résultats officiels le 27/11 (Gamma : `closed: false`, prix 0,96-0,99).

## Deuxième contrôle à la main (famille 3 : relire des paris au hasard)
10 achats des fantômes v2 tirés au hasard (graine 1112, hors convictions) relus sur Gamma (question, issue achetée contre jeton,
échéance, règlement) : `compteur_truth` (60-79 posts, NON 0,886, réglé NON), `non_aux_drames` ×4 (Deri, Tusk, Polanski, « fewer
than 215 House members vote to impeach Hegseth »), `seismes_marche` (« ≤ 6 séismes ≥ 5,5 », OUI 0,332), `favori_politique_quasi_certain`
×2 (pourparlers Russie-Ukraine réglé OUI en avance ; Hegseth parti d'ici le 30/11, NON 0,969), `compteur_tweets` ×2. **0 écart** :
chaque jeton est bien l'issue notée, chaque règlement relu est juste. Point relu de près : « fewer than 215 … vote to impeach » a
une tranche « no House floor vote » à part (0,967) ; le NON acheté à 0,96 couvre donc « pas de vote » ET « ≥ 215 », comme le prix.
Le « drame » n'est pas toujours le OUI : à surveiller si `non_aux_drames` élargit ses mots-clés.
