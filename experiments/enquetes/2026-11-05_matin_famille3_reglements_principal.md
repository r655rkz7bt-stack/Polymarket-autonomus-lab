# 05/11 (matin) — Famille 3 : règlements du principal relus sur Gamma

**Contrôle** : les 129 paris du principal réglés depuis le 31/10 (journal signé `ledger.jsonl`, un pari par jeton) ;
25 tirés au hasard (graine 5), marché relu sur `gamma-api.polymarket.com/markets/<id>` : marché clos et
`outcomePrices` du jeton égal au paiement par part du journal.

**Résultat** : 25 sur 25 conformes, aucun écart. Sur les 129 : mise 368,3 €, gain −3,1 €, 75,5 gagnés pour 74,9 attendus
par les prix payés (ni avantage ni défaut visible, comme attendu d'un principal qui copie des favoris).

**Autres constats du jour** (déjà documentés, pas de nouveau défaut) : `posees_en_jeu` (345 ordres posés servis en match,
−10,7 % par pari, z −3,3) = mesure connue du 28/10, le principal annule ces ordres ; `audit` « pas clos » = fausses
alertes d'audit trop précoce (proposition du 22/10).

**Défaut** : aucun. Script : un tirage de 25 jetons (non versionné, 20 lignes).
