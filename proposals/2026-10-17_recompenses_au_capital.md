# Proposition (noyau) : compter les récompenses de liquidité dans le capital (17/10/2026)

Point n°1 de la réponse « AMELIORATION » du 17/10/2026 (réponse d'Etienne : « Tout »). Le fichier
du noyau concerné est `src/polymarket_agent/ledger.py`, avec son test `tests/test_ledger.py`. Seul
Etienne peut le modifier : je n'ai rien touché.

## Pourquoi
Les bots qui gagnent durablement sur Polymarket sont des « faiseurs » payés par la plateforme
(rapport `experiments/veille_bots/`). Notre tenue de marché gagne ces récompenses, mais seulement
dans une **estimation** à part (`liquidity_rewards.py`, table `recompenses_estimees`). Le journal
signé ne les voit pas. Conséquences :
- l'arène juge `market_maker` sans son revenu principal ;
- la stratégie ne peut jamais devenir championne pour ce qu'elle rapporte vraiment.

Estimations publiées le 17/10/2026 à 09:48 UTC, sur 2 jours :

| Portefeuille | Récompense estimée | Dont jours ≥ 1 $ |
|---|---|---|
| market_maker | 24,73 | 24,73 |
| market_maker_serre | 20,70 | 20,70 |
| meteo_prevision_patiente | 14,85 | 14,85 |

Cela fait environ **1,2 % du capital par jour** pour `market_maker`. C'est un ordre de grandeur, pas une certitude.

## Pourquoi c'est sans doute trop optimiste (à corriger avant de compter)
- On ne photographie le carnet que **toutes les 5 minutes**, alors que Polymarket le fait chaque minute.
- On ne connaît pas notre **place dans la file d'attente**.
- Le **multiplicateur « en match »** de la formule officielle n'est pas documenté, donc il est ignoré.
- On ne peut pas comparer nos estimations aux **vrais versements** : il faudrait un compte.

## Proposition
1. **Nouvelle écriture signée `REWARD` dans `ledger.py`** : elle crédite le solde disponible, comme un
   règlement. Champs : jour (UTC), montant, origine (« récompenses de liquidité estimées »), méthode.
2. **Une fois par jour**, après minuit UTC, `main.py` (fichier libre) inscrit pour chaque
   portefeuille la récompense estimée de la veille, si elle atteint au moins 1 $ (règle de versement
   de Polymarket), multipliée par un **coefficient de prudence de 0,5**. Ce coefficient est réglable
   dans `settings.yaml`.
3. **Garde-fous** :
   - une seule écriture par portefeuille et par jour ;
   - un montant jamais supérieur à la cagnotte quotidienne du marché ;
   - le total crédité reste visible à part dans le tableau de bord (« dont récompenses ») ;
   - l'audit indépendant vérifie que chaque `REWARD` correspond bien aux estimations enregistrées.
4. **Règle n°1 inchangée** : une récompense n'est jamais un gain latent. Elle n'est créditée qu'une
   fois le jour terminé, comme un versement réel.

## Décision d'Etienne (17/10/2026)
« Je veux que ça soit intégré, mais que pour le portefeuille public, évidemment. On ne va pas
prendre les portefeuilles de l'arène et tout ajouter au capital. » Puis : option **A**, et
« crée un fichier et une pull request […] qu'on va ajouter plus tard ».

Donc :
- **seul le journal principal** reçoit des écritures `REWARD` (prudence 0,5) ;
- l'arène classe les stratégies avec leurs récompenses estimées (option A), **sans jamais** les
  ajouter au capital d'un fantôme (partie libre, `arena.py` et `liquidity_rewards.ranking_bonus`) ;
- le versement au capital public sera ajouté **plus tard**, avec la modification du noyau.

## État au 17/10/2026 au soir : en attente (choix d'Etienne : « on attend »)
- L'option A est en place (PR #55).
- La partie noyau est reportée. Aujourd'hui, le principal ne pose aucun ordre : il ne toucherait
  rien. Le système de sécurité de la session de Claude bloquait en plus les tests et l'envoi
  d'une modification du noyau.
- **Déclencheur** : une stratégie qui pose des ordres (`market_maker`, `*_patiente`) reçoit une
  part du capital principal. Alors, le faire depuis un ordinateur : le menu du mode de session
  (« Accept edits ») y est visible et permet à Etienne d'autoriser chaque commande.

## Ce qu'il faudra écrire plus tard (noyau, avec l'accord d'Etienne)
1. `ledger.py` : type `REWARD` (dans `ENTRY_TYPES` et `MONEY_TYPES`). Champs `op_id`
   (`REWARD-AAAA-MM-JJ`), `day`, `amount`, `source`, et en option `method` et `details`
   (par marché : montant, cagnotte). Refus si :
   - faillite ;
   - journée non terminée (`day` ≥ date de l'écriture) ou antérieure au capital actuel ;
   - jour déjà crédité ;
   - montant ≤ 0, ou supérieur à 5 % du capital réalisé (plafond contre une estimation folle).

   Effet : le solde disponible et les gains réalisés augmentent du montant. Nouveaux champs
   d'état `rewards_total` et `reward_days` (à recopier dans `clone`). `summary()` gagne
   `recompenses_recues`. Nouvelle méthode `record_reward(day, amount, source, method, details, now)`.
2. `tests/test_ledger.py` : crédit, refus de chaque cas ci-dessus, rechargement à l'identique,
   `clone` équivalent à `deepcopy`.
3. `scripts/audit_fills.py` (+ test) : une `REWARD` dans un journal **fantôme** est une
   anomalie (seul le principal en reçoit). Dans le principal, le montant ne doit pas dépasser
   la somme des `details` × prudence, et chaque marché ne doit pas dépasser sa cagnotte.
4. Partie libre (`main.py`, après l'étape 12) : pour chaque journée terminée des 3 derniers
   jours qui n'a pas encore été versée, total estimé du portefeuille `principal`
   (`liquidity_rewards.payable_days` : jours ≥ 1 $, plafonnés à la cagnotte) × prudence, puis
   `ledger.record_reward(...)`. Rien n'est fait tant que le noyau ne connaît pas `REWARD`.

Limite à connaître : le principal ne touche de récompenses que si une stratégie qui pose des
ordres (tenue de marché, stratégies « patientes ») a une part de son capital. Ses ordres sont
alors réduits à cette part : sous la taille minimale du marché (`rewardsMinSize`), ils ne
rapportent rien.

## Ce qu'Etienne aurait à faire
- Me répondre **« récompenses : oui »** (avec la prudence à 0,5) ou **« récompenses : non »**.
- Si c'est oui, je prépare la pull request du noyau avec ses tests. Je te guide ensuite pour la
  fusionner, comme pour l'audit des règlements : désactiver la règle `protection-main`,
  fusionner, puis la réactiver.

En attendant, rien ne change : les récompenses restent affichées à part, dans la section
« Ordres posés » du tableau de bord.

## 21/10/2026 : pull request du noyau (AMELIORATION n°7, réponse d'Etienne : « Tout »)
Le déclencheur est atteint depuis le 18/10 : la championne nf_sport_patiente pose tous ses achats
et le principal les copie. Contenu de la pull request :
- `ledger.py` : écriture signée `REWARD` (`record_reward`), sources `liquidite`, `detention`,
  `remise_maker` ; identifiant `REWARD-<source>-<jour>` (une seule fois par source et par jour) ;
  refus en faillite, pour une journée non terminée ou antérieure au capital actuel, pour un montant
  ≤ 0 ou supérieur à 5 % du capital réalisé. Le solde et les gains réalisés augmentent ;
  `rewards_by_source` dans l'état (recopié par `clone`, remis à zéro par `RESET`) ;
  `summary()["recompenses_recues"]`.
- `tests/test_ledger.py` : crédit et rechargement, 6 refus, identifiant forgé, faillite.
- `scripts/audit_fills.py` (+ test) : une `REWARD` dans un fantôme est une anomalie ; dans le
  principal, le montant ne dépasse pas la somme de ses détails, ni un marché sa cagnotte.
- Partie libre : `main._credit_rewards` (étape 3 bis, juste après les règlements) crédite au seul
  principal les journées terminées des 3 derniers jours : liquidité (journées ≥ 1 $, marchés
  plafonnés à leur cagnotte) et détention, × prudence 0,5 (`settings.yaml → recompenses`,
  `verser_au_principal`). Tableau de bord : « dont récompenses créditées (estimées) ».
- La remise aux ordres posés (`remise_maker`) est acceptée par le noyau mais pas encore calculée :
  il faudra le taux de remise de chaque catégorie (Gamma `feeSchedule`).
