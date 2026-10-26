# 26/10/2026 (soir) : le principal ne pouvait pas copier `moins_de_cartes` (famille 1 : le principal ne joue pas ce que l'arène mesure)

Point de départ : en lisant la répartition du capital principal (`published/data.json` → `arene[].part_principal`), `moins_de_cartes` (la seule stratégie à mécanisme expliqué et à gain
positif en direct : 62 paris, +28 %) a **14,6 % du capital**. Le journal du principal, lui, ne contient **aucun** de ses paris.

## Constat (`scripts/copie_sous_minimum_26_10.py`, journaux signés du 26/10)
Jetons achetés par le fantôme, et jetons que le principal a achetés avec le même `strategy_id` :

| stratégie | part du principal | facteur de copie | jetons du fantôme | copie ≥ 5 parts | copiés par le principal |
|---|---|---|---|---|---|
| `moins_de_cartes` | 14,6 % | 0,033 | 70 | **0** | **0** |
| `compteur_tweets` | 14,4 % | 0,189 | 52 | 12 | 1 |
| `favori_politique` | 13,1 % | 0,092 | 23 | 15 | 0 |
| `nf_sport_patiente_prix_850_875` | 22,2 % | 0,055 | 56 | 26 | 7 |
| `nf_sport_925_950` | 11,8 % | 0,036 | 79 | 38 | 17 |

(Parts : 76 % du capital principal. Depuis le 24/10, les achats du principal viennent de `nf_sport_prix_haut_3_6h` (166 €), `nf_sport_925_950` (165 €), `nf_tennis_12_18h_vainqueur`, `nf_court_football_soir`, `850_875` (38 €),
1 pari de `compteur_tweets` (7 €), aucun de `moins_de_cartes` ni de `favori_politique`.) La décision publiée du principal le dit : *« compteur_tweets … acceptee: false, raisons : taille inférieure au minimum du marché (5) »* (26/10, 15 h 47).

## Cause
`main.Weighted._copy` : mise du principal = parts du fantôme × **part × capital du principal / capital du fantôme × (base 0,5 / prudence du fantôme)**. Pour `moins_de_cartes` :
0,146 × 742 / 1 082 × (0,5 / 1,545) = **0,033** ; le fantôme mise 15 parts en moyenne (44 au plus : quart de Kelly sur 9 € par pari), soit **0,5 part** (1,4 au plus) pour le principal.
Le contrôle de sécurité (`safety_controller`, noyau) rejette tout ordre sous le minimum du marché (5 parts). Aucune copie n'a donc jamais pu partir : l'argent de la part est resté inutilisé,
et la stratégie que l'arène juge la mieux étayée jouait seule pendant que le principal (−25 %) gardait 14,6 % de son capital dessus sans effet.
Même mécanisme en moindre mesure pour `compteur_tweets` (40 jetons sur 52 sous le minimum), `nf_sport_*` (30 et 41 jetons sous le minimum) et `favori_politique` (8).

## Correctif
`Weighted(..., floor=(5 parts, 1 % du capital))` pour la copie du principal (`settings.yaml` → `principal.plancher_copie`) : quand la copie à l'échelle tombe sous le minimum du marché, le principal achète
le minimum (5 parts) **si cela coûte au plus 1 % de son capital (7 €) et reste dans le budget de la part** (`part × capital − déjà investi`) ; sinon pas d'achat, comme avant. Le contrôle de sécurité, les
plafonds de mise (10 %) et de famille (40 %) et les prix restent ceux du noyau, intacts.
Exposition attendue pour `moins_de_cartes` : ≈ 3 € par pari (5 parts à 0,60), une dizaine de paris en cours au plus (≈ 4 % du capital), à comparer à sa part de 14,6 %.
Tests : `test_a_copy_below_the_market_minimum_is_raised_to_the_minimum_within_budget` (2,4 parts → 5 ; coût au-dessus du plafond → inchangé ; budget insuffisant → pas d'achat ; fantôme → pas de plancher).

## Contrôle ajouté
`enquete.copie_absente` (paramètre `parts` : `published/data.json` ou clé `repartition_principal` de la base) : une stratégie qui a une part du capital principal et dont le principal ne copie **aucun** jeton
des 3 derniers jours (au moins 10 jetons côté fantôme) est une obligation « grave » ; moins de 20 % de copie = « à regarder ». Il trouve aujourd'hui `moins_de_cartes` (0 sur 50) et `compteur_tweets` (1 sur 16).
Test : `test_a_strategy_with_a_share_but_no_copy_is_grave`.

## Diagnostic ajouté au tableau de bord
`published/data.json` → `refus_principal` : refus du principal par stratégie et par raison sur 48 h (ordres préfixés « P » de la table `decisions`), pour que le prochain passage ne dépende plus des 25 dernières
décisions. Test : `test_principal_refusals_are_counted_by_strategy_and_reason`. Premier usage : `favori_politique` (13,1 %) n'a pas été copié le 26/10 à 12 h 13 alors que 2 de ses 7 paris dépassaient 5 parts
à l'échelle (9,2 et 10,3) ; la raison n'est pas dans les journaux publiés (soit un refus du principal, soit la part encore en essai).

## Reste ouvert
- À relire demain : `bash scripts/fetch_data.sh` puis `scripts/enquete.py` : `copie_absente` doit se vider pour `moins_de_cartes` (premiers paris copiés dès le prochain cycle où le fantôme achète). Les achats
  copiés se retrouvent dans le journal du principal avec `strategy_id: moins_de_cartes`.
- Les copies à 5 parts exactes n'ont pas la taille « de la part » : elles surpondèrent un peu les paris que le fantôme mise petit. Si le gain en direct de `moins_de_cartes` se dégrade (z < 0 sur 50 nouveaux paris), le plancher est à retirer
  (`plancher_copie` dans `settings.yaml`) avant la part.
- Le contrôle `copie_fidele` (« copie à 100 % sur une exécution partielle ») peut signaler un pari dont le fantôme n'a obtenu que ≤ 5 parts : c'est le plancher, pas un défaut.
