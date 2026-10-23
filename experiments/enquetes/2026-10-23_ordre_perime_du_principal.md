# 23/10/2026 : ordre posé périmé du principal (copie fidèle)

**Constat** (obligation « copie_fidele », grave) : le 23/10 à 04:01, le principal achète 5,07 parts « Yes » de `contrer_crypto_patiente`
(marché 5912695, BTC) à 0,072 (ordre `P67d9cdb4…`, posé à un cycle précédent). Le fantôme copié n'a **aucun** achat sur ce jeton à ce moment :
il n'achète qu'à 04:25 (65 parts) et 04:38 (40,82 parts), à **0,065**, avec un autre ordre (`1be98c5e…`). Le principal a donc payé 10 % plus cher un pari
que le fantôme n'avait pas encore fait. Ampleur : 1 achat, 0,37 €. Il n'y a eu qu'un cas sur 197 achats du principal, mais le mécanisme est général.

**Cause** (`main.py`, `_place_resting` / `persistence.add_pending_order`) : une stratégie à ordres posés remet son prix à jour à chaque cycle ; un
nouvel ordre sur le même jeton REMPLACE l'ancien du même portefeuille, mais seulement quand le nouveau est accepté. Côté fantôme l'ancien ordre a disparu
(remplacé, expiré ou annulé) ; côté principal, la copie du nouvel ordre n'a pas été posée (refus de poser, plafond), donc l'ancien ordre, à l'ancien prix,
est resté ouvert et s'est rempli seul au cycle suivant. Le journal du principal n'a donc plus de jumeau dans le fantôme.
(Les décisions du cycle ne sont pas publiées : je n'ai pas pu relire le refus exact. Le correctif ne dépend pas de sa raison.)

**Correctif** : `main._drop_orphan_copies`, appelée avant l'exécution des ordres posés : tout ordre posé du principal dont le fantôme copié n'a plus d'ordre
posé sur ce jeton et ce sens est annulé (« ANNULE »). Le principal ne peut plus acheter que ce que le fantôme a encore en attente.

**Test** : `tests/test_cycle.py::test_principal_order_is_dropped_when_the_copied_ghost_has_no_order_left` (échoue sans le correctif, passe avec).

**Contrôle automatique** : `copie_fidele` (déjà là) l'a trouvé ; rien à ajouter.

## Contrôle à la main de la famille 6 (« ce qui ne tourne plus »)
- 9 stratégies muettes depuis plus de 48 h : `paire_oui_non`, `coherence_match`, `implication_politique`, `marches_jumeaux` n'ont aucun écart après frais
  (421 marchés vus, normal : les paires cohérentes ne se désajustent presque jamais) ; `kalshi_reference`, `futurs_bookmakers` : avantage net insuffisant.
  `football_trois_issues` : « aucune raison notée » ; je vérifie qu'il existe des marchés qui passent ses motifs (WIN_ON / DRAW) : sur 2 294 marchés ouverts de
  6 ligues, 10 « Will X win on AAAA-MM-JJ? » et 5 « … end in a draw? ». La stratégie reçoit donc des candidats ; ce sont les cotes à trois issues (Odds API,
  budget étalé depuis le 22/10) qui manquent. Pas de défaut de code.
- Capital bloqué : `favori_politique*` (3 fantômes, 7-81 € disponibles, 15-20 positions ouvertes depuis le 16-17/10). Connu, politique à long terme.
- Positions après l'échéance : tout vient du marché 5167158 (litige UMA) et de deux marchés (5475240, 5767158) en attente de règlement. Rien de nouveau.
