# Proposition (noyau) : l'audit des prix ne doit pas crier quand le marché s'est décidé entre deux points de l'historique (24/10/2026)

Fichier concerné (protégé) : `scripts/audit_fills.py`, fonction `check_entry` (et `tests/test_audit_fills.py`).

## Constat
Deux anomalies d'audit le 24/10/2026 à 15 h 17 UTC (`audit/etat.json`) : `fantome:crypto_threshold_non_v1.0.0` et `fantome:crypto_threshold_prix_bas_v1.0.0`, « achat à 0,0010, plus bas prix observé 0,2695 ».
Relu à la main : l'écriture est **juste**. Le marché 6104848 (« Ethereum plonge à 2 300 $ le 24/10 ? ») était déjà décidé : le OUI valait 0,999 et le NON 0,001 dans le carnet réel (le marché s'est réglé OUI depuis). L'historique public de prix
(`prices-history`, un point toutes les 10 minutes, retard de quelques minutes) n'avait pas encore enregistré la chute du NON : plus bas observé 0,2695. L'achat de la stratégie était un défaut de stratégie (corrigé côté libre le 24/10,
`experiments/enquetes/2026-10-24_touche_deja_touchee_non_a_0_001.md`), mais **pas** une écriture impossible : le message « prix impossible » est une fausse alerte du même genre que celles du 22/10 (règlements).

## Proposition
Dans `check_entry`, avant de rendre « anomalie » pour un achat sous `lo − TOLERANCE`, demander à l'API publique de transactions (`data-api.polymarket.com/trades?market=<conditionId>` ou `eventId`) les échanges des 30 minutes autour de l'exécution
(sans clé, déjà utilisée par la recherche) : si un échange réel sur ce jeton (ou l'achat de l'autre issue) a eu lieu à un prix inférieur ou égal au prix de l'écriture + `TOLERANCE`, rendre « ok » avec le détail « prix confirmé par un échange réel ».
Sans échange dans la fenêtre : garder « anomalie ». Test : historique plat à 0,27 et échange réel à 0,001 → ok ; historique plat à 0,27, aucun échange → anomalie.
Variante plus simple si l'API de transactions est jugée trop lourde : n'émettre l'alerte qu'après un deuxième passage de l'audit (30 minutes plus tard, l'historique a rattrapé son retard), comme pour la résolution UMA (« réessayer » puis anomalie).

Effet : plus de faux e-mails sur les marchés qui se décident en quelques secondes (barres « touche » de crypto ou de matières, matchs finis) ; une vraie faute (achat à un prix que personne n'a jamais payé) reste détectée.
