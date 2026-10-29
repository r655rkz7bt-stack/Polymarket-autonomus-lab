# Archive : journal de la stratégie dans le labo d'origine (lecture seule)

`nf_sport_patiente_prix_850_875_v1.0.0.jsonl.gz` : journal signé du fantôme `nf_sport_patiente_prix_850_875` dans
r655rkz7bt-stack/Polymarket-autonomus-lab, du 20/10/2026 15 h 51 au 28/10/2026 23 h 42 UTC (846 lignes : 119 achats,
85 règlements, battements). Il est signé avec la `LEDGER_KEY` du labo d'origine : il ne peut pas être importé dans le
journal de ce laboratoire (qui repart de 1 000 €), seulement relu pour comparer. Chiffres tirés de ce fichier : docs/CONTEXTE.md §2.
Format d'une ligne : `{"seq", "ts", "type": GENESIS|BUY|SETTLE|HEARTBEAT|MILESTONE, "data": {...}, "prev", "hash", "sig"}` ;
un achat porte `token_id`, `price`, `shares`, `fee`, `extra.depuis_coup_d_envoi_h` ; un règlement `payout_per_share` (1, 0 ou 0,5).
