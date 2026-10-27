# Enquête du 27/10/2026 : le renfort du principal n'a jamais joué ; l'entonnoir cherchait dans la chance

Session avec Etienne (« plus de liberté, ne sois pas paralysé par les pertes »). Familles : 1 (le principal ne joue pas ce
que l'arène mesure) et 2 (la mesure récompense la chance). Analyses complètes : `experiments/audace.md`.

## 1. Le renfort du principal était annulé
- **Constat** : depuis le 21/10 (« grossir les gagnantes », PR #119), `arena.exposure` peut donner à une stratégie qui prouve
  plus d'avantage qu'elle n'en suppose un engagement SUPÉRIEUR à sa part (mise mesurée jusqu'à `part_max`, 2 puis 3).
- **Cause** : `main._trade` multipliait chaque part par `min(1.0, engagement / part)` (ligne écrite le 17/10, PR #61, pour
  la seule période d'essai, qui ne fait que réduire). Tout renfort au-dessus de 1 était coupé : le principal n'a jamais misé
  plus que sa part sur une gagnante. Le test de l'époque (`test_principal_stake_goes_above_one_only_for_proven_winners`)
  ne vérifiait que `arena.exposure`, pas ce que le cycle en faisait.
- **Ampleur** : nulle aujourd'hui (mises mesurées des championnes au 26/10 : 0,20 à 1,00 ; `moins_de_cartes` est à 1,00 mais
  sa confiance par jour, 0,79, est sous les 0,80 exigés) ; le levier « miser plus gros sur ce qui gagne » n'existait pas.
- **Correctif** : `main._engaged_shares` (sans plafond à 1 ; le plafond par stratégie reste `part_max_par_strategie`) ; test
  `test_principal_weight_follows_the_renfort_above_its_share`. Le texte du tableau de bord ne dit plus « 130 % du capital
  engagé » quand la somme des parts dépasse 100 %.

## 2. Une mise pouvait vider le solde disponible
- **Constat** : la faillite tombe dès que le solde DISPONIBLE touche 0, même avec des positions qui valent quelque chose. Le
  contrôleur refuse un coût supérieur au solde, mais pas un achat qui le vide presque : dans le test, avec 65 € disponibles et
  935 € en positions, un pari laissait **0,07 €** disponibles.
- **Correctif** : `principal.reserve_liquidites` (3 %) et `main._cash_room` : achat au comptant réduit ou abandonné, ordre
  posé refusé, ordre servi seulement quand l'argent est revenu ; test `test_principal_keeps_a_cash_reserve_so_no_bet_can_empty_it`
  (30,00 € restent disponibles).

## 3. L'entonnoir 80/20 et l'enquête automatique récompensaient la chance
- **Constat** : l'entonnoir disséquait les stratégies qui grandissent en EUROS (la taille des mises) et proposait tout morceau
  à z ≥ 0 : 61 filles le 27/10, presque toutes des favoris, alors que nos 58 stratégies de favoris ne diffèrent pas
  réellement (Q 58,7 pour 57 degrés de liberté). Ses prix étaient découpés en une seule tranche 0-0,80, qui cachait les billets
  sous 0,10 (3 gagnés pour 10,8 attendus) et la tranche 0,10-0,45 des « contrer » de la crypto (58 pour 39,3). La stratégie qui
  bat le plus ses prix (`contrer_crypto_patiente`, z +1,91) n'était jamais regardée : elle perd en euros (−28 €).
  L'enquête automatique faisait de « chance » et « championne sans avantage » des obligations (7 sur 9 le 27/10).
- **Correctif** : `promotion.yaml` → `entonnoir: {z_morceau: 2.0, z_strategie: 1.5}`, `pareto.PRICE_BANDS` découpées sous 0,80
  (4 filles au lieu de 61, dont 0,10-0,20 de `contrer_crypto_patiente`, z +3,19) ; « chance » et « championne sans avantage »
  passent « à regarder ». Tests : `test_funnel_looks_for_slices_that_beat_their_prices_not_for_lucky_euros`,
  `test_a_gain_made_in_one_day_is_reported_but_no_longer_an_obligation`.

## Contrôle automatique
Pas de nouveau contrôle dans `enquete.py` : les trois défauts sont gardés par des tests unitaires. À ajouter si un jour une
stratégie a droit au renfort : vérifier dans le journal du principal que ses copies dépassent bien sa part.
