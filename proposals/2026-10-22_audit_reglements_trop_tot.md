# Proposition (noyau) : l'audit des règlements ne doit pas crier avant que Gamma affiche « closed » (22/10/2026)

Fichier concerné (protégé) : `scripts/audit_fills.py`, fonction `check_settlement` (et `tests/test_audit_fills.py`).

## Constat
`audit/etat.json` (branche data) contient **62 anomalies**, apparues d'un coup à partir du 21/10 à 16 h 15 UTC (13 minutes d'audit différentes jusqu'au 22/10 09 h) ;
**toutes** disent « réglé à X alors que le marché N n'est pas clos ». Chaque nouvelle anomalie fait échouer le job d'audit (code de sortie 1) donc envoie un e-mail à Etienne.

Vérification faite à la main le 22/10 (Gamma `/markets/<id>`, 62 règlements sur 62) :
- le marché est aujourd'hui `closed = true`, `umaResolutionStatus = resolved` ;
- le règlement du journal tombe **17 à 225 secondes (médiane 78 s) APRÈS le `closedTime`** de Gamma, jamais avant ;
- le paiement inscrit est **égal au prix final officiel** pour les 62.
Donc le cycle n'a rien réglé trop tôt (`settlement.resolution_payout` exige `closed is True` et une résolution finale) : c'est l'audit qui a lu `closed` avant qu'il apparaisse.
Cause probable : depuis le 21/10 après-midi, le cycle lit les marchés détenus par lots (PR « règlements par lots ») et règle dès la fermeture ; la lecture unitaire `/markets/<id>` de l'audit,
faite dans les secondes qui suivent, arrive parfois sur une réponse encore en cache.

## Proposition
Dans `check_settlement`, quand `raw.get("closed") is not True` et que le règlement a moins de 30 minutes (`age_seconds < 1800`), rendre `("réessayer", "marché pas encore affiché clos")` comme pour
« résolution pas encore définitive » ; au-delà, garder l'anomalie. Test : règlement de 60 s sur un marché `closed = false` → réessayer ; de 2 h → anomalie.
Effet : plus de faux e-mails ; une vraie faute (règlement sur un marché resté ouvert) reste détectée après 30 minutes.

Côté libre : le contrôle `audit_anomalies` de `enquete.py` classe déjà ces cas en « à regarder » et garde les autres anomalies « graves ».
