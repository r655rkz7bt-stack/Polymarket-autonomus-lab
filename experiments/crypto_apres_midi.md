# Juste après midi (Est), le gagnant d'une échelle crypto quotidienne est-il encore bon marché ? (27/10/2026)

**Verdict : ÉCARTÉE.** Idée : les échelles « Bitcoin / Ethereum / Solana / XRP above ___ on <date> ? » se règlent sur la bougie Binance 1 minute de 12 h (Est) ; une minute après, le résultat est connu, mais le règlement UMA prend des heures :
si le gagnant se paie encore 0,95-0,97, on gagne 3-5 % presque sans risque (même idée que `apres_echeance`, testée sur le sport le 23/10 : écartée).

## Données (`experiments/crypto_apres_midi/scripts/`)
`releve.py` (étiquette multi-strikes 102516 par `/events/keyset` : 11 157 événements dont **972 échelles quotidiennes** du 21/02 au 27/10/2026, 4 actifs × 243 jours, 10 à 11 marchés chacune) et `echanges.py` (tous les vrais échanges, data-api, 972 / 972).
`analyse.py` : côté gagnant = règlement Gamma (en direct il se lirait sur la bougie : à contrôler), prix payé = premier échange de preneur qui ACHÈTE le gagnant entre midi + 60 s et midi + 5, 15 ou 60 minutes ; on écarte les marchés dont le gagnant était déjà coté ≥ 0,985 à midi − 60 s (rien à gagner).

## Résultats (`resultats.txt`)
- Sur ~10 700 marchés, **216** n'avaient pas encore leur gagnant à 0,985 une minute avant midi (les autres sont loin du seuil). Pour **53** d'entre eux un preneur achète le gagnant dans l'heure qui suit midi + 60 s ; **34 de ces 53 à 1,00, 9 à 0,99, 6 à 0,97-0,98** : les robots ont ramené le prix à 0,99-1,00 dans la première minute.
  Gain d'un achat à 0,97-0,99 : +1 à +3 % sur quelques centaines de parts, une quinzaine de fois en 243 jours.
- 4 échanges « gagnant à 0,001-0,59 » (ETH 2 400 le 22/10 : 0,001 pour 40 parts ; BTC 78 000 le 24/04 : 0,01 ; XRP 1,10 le 23/06 ; ETH 2 300 le 20/04) : ce sont des fautes de frappe ou des résultats surprenants, de 40 à 9 400 parts, pas des prix qu'on peut viser (aucune règle ne les repère avant coup).
- Le prix médian du gagnant juste après midi est 0,999. **Aucune marge exploitable** : les échelles quotidiennes de crypto sont suivies par des robots à la minute près (déjà noté dans `PISTES.md`).
