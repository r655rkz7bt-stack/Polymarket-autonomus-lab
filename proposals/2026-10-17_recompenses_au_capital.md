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

## Ce qu'Etienne aurait à faire
- Me répondre **« récompenses : oui »** (avec la prudence à 0,5) ou **« récompenses : non »**.
- Si c'est oui, je prépare la pull request du noyau avec ses tests. Je te guide ensuite pour la
  fusionner, comme pour l'audit des règlements : désactiver la règle `protection-main`,
  fusionner, puis la réactiver.

En attendant, rien ne change : les récompenses restent affichées à part, dans la section
« Ordres posés » du tableau de bord.
