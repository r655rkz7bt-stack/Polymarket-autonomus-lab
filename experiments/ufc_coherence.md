# Piste n° 6 : cohérence des paris UFC (KO/TKO + soumission + décision = 1) — 23/10/2026

Scripts : `experiments/ufc_coherence/scripts/` (`releve.py` puis `analyse.py`, `analyse2.py`) ; données dans `donnees/` (ignoré par Git).

## La question
Un combat UFC se termine par KO/TKO, soumission ou décision. Les trois marchés « Will the fight be won by KO or TKO? », « … by submission? » et
« Fight to Go the Distance? » doivent donc faire 1 en tout. Si leurs trois OUI coûtent ensemble moins de 1 − frais, on les achète (paie toujours 1) ;
si leurs trois NON coûtent moins de 2 − frais, on les achète (paie toujours 2). Y a-t-il de tels écarts **achetables** aux prix des vrais échanges ?

## Les données
- Gamma, série 38 (UFC) : **687 événements réglés** (novembre 2025 à octobre 2026), dont 611 avec les trois marchés.
- Data-api : tous les échanges de chaque événement (médiane 864 par événement, 1 seul événement sans échange).
- Frais : barème `feeSchedule` des marchés, taux 0,05 (frais = 0,05 × p × (1 − p) par part).

## Contrôle du règlement
Sur 549 combats dont les trois marchés sont réglés net à 1/0 : **548 fois exactement un des trois est gagnant** (228 KO, 97 soumissions, 223
décisions) ; 1 fois aucun (issue « autre »), 62 combats annulés ou réglés 50/50 écartés. L'identité tient : un panier OUI paie 1, un panier NON paie 2.

## Résultat
- Le volume des paris annexes est mince : médiane 496 $ par marché (744 des 1 833 jambes ont plus de 1 000 $).
- **Trois jambes qui s'échangent presque jamais ensemble.** Prix payé = premier échange preneur dans les `WIN` secondes qui suivent l'instant de décision,
  toutes les 10 minutes de −24 h à −5 min avant le coup d'envoi :

  | fenêtre | paniers OUI observables | paniers NON observables | sous le seuil (OUI) | sous le seuil (NON) |
  |---|---|---|---|---|
  | 2 min | 3 | 0 | 0 | 0 |
  | 5 min | 9 | 7 | 0 | 6 (5 combats) : gain moyen +0,14 |
  | 15 min | 63 | 20 | 0 | 11 (5 combats) : gain moyen +0,09 |

  Sur 611 combats, au plus 63 paniers OUI et 20 paniers NON sont réalisables dans 15 minutes. Les paniers OUI coûtent en moyenne **1,11 à 1,20**
  (les trois OUI sont vendus 11 à 20 points au-dessus de 1 : l'écart acheteur-vendeur des trois jambes, pas une aubaine). Les paniers NON coûtent
  en moyenne 1,98-2,00 : aucune marge à prendre en moyenne.
- Les rares paniers NON sous le seuil (5 combats : Mullarkey-Salkilld, Fiziev-Ruffy, Makhachev-Machado Garry, Finney-Malkoun, Coria-Rodriguez)
  rapportent 0,02-0,10 € par panier de ≈ 1,9 € (+1 à +5 %), avec des jambes de quelques dollars chacune : plafond de gain de l'ordre de **un euro par combat**,
  et 5 combats ne font pas un échantillon (`idea_test.verdict` demande 30 paris).
- Fenêtre large (2 h, première version `analyse.py`) : les « gains » de +0,3 à +0,4 par panier NON viennent de jambes lues à des moments différents
  (le combat commence pendant la fenêtre et les prix bougent) : non exécutable, **écarté comme artefact**. Même piège que les mentions et les tranches du 21-22/10.

## Verdict : **écartée**
Trois marchés trop minces pour être achetés en même temps ; les prix suivent déjà l'identité à l'écart de prix près. Rien dans l'arène.
Réglages essayés : 3 fenêtres (2, 5, 15 min ; 2 h écartée), 2 sens (OUI, NON), grille de décision toutes les 10 min (≈ 140 instants par combat), ≈ 8 réglages.
**Non testé** : l'identité par combattant (« A gagne par KO » + « B gagne par KO » = « KO ») des événements à 19 marchés (90 combats, volumes de quelques dollars)
et les écarts avec le moneyline (liquide, 800 000 $ pour un combat de prélim) ; si un jour une source de cotes de méthode de victoire est gratuite, voir là.
