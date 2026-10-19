# Proposition (noyau) : récompense de détention et remise aux ordres posés dans le capital (19/10/2026)

AMELIORATION du 19/10/2026, idées n°1 et n°6 (réponse d'Etienne : « Tout »). Ce texte complète
`proposals/2026-10-17_recompenses_au_capital.md` : **la même écriture signée `REWARD`** servirait
aux trois programmes publics de Polymarket. Les fichiers du noyau concernés sont `ledger.py`,
`scripts/audit_fills.py` et leurs tests. Seul Etienne peut les modifier : je n'y ai pas touché.

## Les deux nouveaux programmes
1. **Récompense de détention** : Polymarket verse un taux annuel sur la **valeur** des positions
   des marchés éligibles. Ce taux était de 4,00 % le 19/10/2026 ; il est variable et Polymarket
   peut le plafonner. La valeur est mesurée chaque heure et le versement est quotidien.
   - L'éligibilité est donnée marché par marché par Gamma (`holdingRewardsEnabled`). Vérifié en
     direct le 19/10 : 11 des 100 marchés les plus échangés, surtout la politique à long terme.
   - Estimée depuis le 19/10 par `holding_rewards.py` : valeur au meilleur acheteur × taux × durée
     du cycle, dans la table `recompenses_detention`. Elle compte déjà pour le **classement** de
     l'arène (× prudence 0,5, comme l'option A), jamais dans le capital d'un fantôme.
2. **Remise aux ordres posés** (« maker rebates ») : une partie des frais payés par ceux qui
   achètent tout de suite est reversée chaque jour à ceux dont les ordres posés ont été exécutés
   (20 à 25 % selon la catégorie, d'après la documentation de 2026).
   - `fees.py` ne la compte pas (prudence, noyau). Nos ordres posés exécutés ne paient pas de
     frais, mais ne reçoivent rien non plus.

## Pourquoi c'est maintenant utile
- Le **déclencheur** fixé le 17/10 est atteint : depuis le 18/10 à 21 h 38, la championne
  nf_sport_patiente fait passer **tous** ses achats par des ordres posés, et le principal les
  copie.
- 78 % du capital principal dort (617 € sur 794 € le 19/10). Placé sur des favoris politiques
  éligibles, il toucherait environ 4 % par an, soit environ 24 € par an sur 600 €. Sans cette
  modification du noyau, la récompense n'existe que dans une estimation.

## Ce qu'il faudrait écrire (noyau, avec l'accord d'Etienne, depuis un ordinateur)
1. `ledger.py` : l'écriture `REWARD` de la proposition du 17/10, avec un champ `source` parmi
   `liquidite`, `detention` et `remise_maker`.
   - Une écriture par portefeuille, par jour **et par source** : `op_id`
     `REWARD-<source>-AAAA-MM-JJ`.
   - Mêmes refus : faillite, journée non terminée, jour déjà crédité, montant ≤ 0 ou supérieur
     à 5 % du capital réalisé.
2. `main.py` (libre) : une fois par jour, crédite au **seul journal principal** les montants
   suivants de la veille :
   - **détention** : somme de `recompenses_detention` pour « principal » × prudence 0,5 ;
   - **remise** : pour chaque ordre posé exécuté du principal dans un marché à frais, frais qu'un
     preneur aurait payés (`taker_fee` sur les mêmes parts et le même prix) × taux de remise de la
     catégorie (Gamma `feeSchedule.rebateRate`) × prudence 0,5. C'est une estimation : la vraie
     remise dépend du volume des autres.
3. `scripts/audit_fills.py` : chaque `REWARD` doit correspondre aux estimations enregistrées, et
   une `REWARD` dans un journal fantôme est une anomalie.
4. **Règle n°1 inchangée** : rien n'est crédité avant la fin de la journée, et une récompense n'est
   jamais un gain latent.

## Côté libre, déjà fait (PR du 19/10/2026)
- `MarketInfo.holding_rewards` (Gamma `holdingRewardsEnabled`) ;
- `holding_rewards.py` : estimation et bonus de classement, avec la récompense estimée du
  principal affichée à part sur le tableau de bord (« hors capital ») ;
- stratégie fantôme `parking_politique` : favoris politiques de 0,93 à 0,99, au moins 2 semaines
  avant la fin, marchés éligibles seulement. L'avantage compte la récompense attendue (au plus
  1 an × 4 %). Elle est jugée sur la valeur de ses positions (mode « valeur », part maximale 30 %).
