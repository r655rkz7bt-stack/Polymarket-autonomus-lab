# 2026-10-24 (après-midi, 3e enquête) : le NON d'un marché « touche X » déjà touché, acheté 0,001 (obligation « audit »)

Obligation de la feuille de mission (publiée à 15 h 57 UTC) : « 2 anomalies d'audit autres que marché pas clos » (famille 3 : la donnée n'est pas celle qu'on croit).

## Constat
- Audit (`published_data/audit/etat.json`, 15 h 17 UTC) : `crypto_threshold_non` et `crypto_threshold_prix_bas` ont acheté **à 0,0010 le NON du marché 6104848** (« Will Ethereum dip to $2,300 on October 24? »), « plus bas prix observé 0,2695 ».
- Les deux écritures sont réelles, pas un défaut du simulateur : le marché était **déjà décidé** (réglé OUI depuis, `outcomePrices [1, 0]`) : ETH avait touché 2 300 $ plus tôt dans la journée, le OUI valait 0,999 et le NON 0,001 dans le carnet. L'historique public de prix (pas de 10 minutes) n'avait pas encore enregistré
  la chute du NON (plus bas 0,2695) : d'où « prix impossible ». Fausse alerte côté prix, **vrai défaut côté stratégie**.
- Les achats : 29 895 parts (29,9 €) et 30 552 parts (30,8 €) à 0,001, chance estimée 0,35 ; réglés à 0 (−32 € et −33 €).
- Même défaut avant : sur les 17 achats de la famille `crypto_threshold*` dans des marchés « touche » (reach / dip to), **7 achats du NON à 0,001-0,05 ont tous perdu** (−75 € ; 21/10 07:30 et 14:53, 22/10 16:52 ×2, 24/10 14:29, 15:17 ×2) : les marchés étaient déjà décidés.
  Les achats du OUI (`crypto_threshold_prix_bas` : 9 réglés, +257 €) ne sont pas touchés par ce défaut.

## Cause
`crypto_model.probability` (`touch_up` / `touch_down`) calcule la chance de toucher la barre **d'ici la fin** à partir du prix d'aujourd'hui et des heures restantes (`2 × (1 − Φ(z))`) et ignore que la barre a pu être touchée plus tôt dans la fenêtre du marché
(« on October 24 » = toute la journée, de 0 h ET). Quand le prix est remonté, le modèle croit encore à 35 % de NON ; le marché, qui a vu la bougie, cote le NON 0,001. (`strategy_engine.CryptoThresholdStrategy.propose`.) Même famille que la lacune corrigée le même jour pour
les barres de l'or (`matieres.py`, extrêmes relevés depuis la création du marché) : un modèle de barrière a besoin du maximum / minimum DÉJÀ atteints.

## Ampleur
7 achats, 75 € de pertes sur 3 jours (petits montants : le prix est de 0,001-0,05) ; mais 30 000 parts à 0,001 montrent le danger : si le NON avait été gagnant (quasi impossible) le fantôme aurait empoché 30 000 €, et un prix de quelques millièmes fait exploser le nombre de parts.

## Correctif et contrôle
- `strategy_engine.TOUCH_MIN_ASK = 0,05` : sur un marché « touche », un jeton vendu à moins de 0,05 n'est pas acheté sur le seul modèle (abstention « jeton de marché « touche » quasi sans valeur : la barre est peut-être déjà touchée »). Les achats du OUI à 0,11-0,55 (gagnants) ne bougent pas.
- Test de non-régression qui reproduit le cas réel (ETH 2 350, NON 0,001, OUI 0,999, 30 000 parts à 0,002 dans le carnet) : `tests/test_intel.py::test_crypto_threshold_does_not_buy_the_worthless_side_of_a_touch_market_already_decided` (échoue sans le garde-fou, vérifié).
- Contrôle automatique : `enquete.jetons_sans_valeur` (achat à 0,03 ou moins d'une issue estimée à plus de 15 %), test `tests/test_enquete.py::test_tokens_sold_for_almost_nothing_but_estimated_high_are_flagged` ; il retrouve les deux achats du jour sur le rapport publié.

## Reste ouvert
Un vrai modèle « touche » pour la crypto du jour demanderait les extrêmes déjà atteints depuis le début de la fenêtre (bougies Binance de la journée) : le garde-fou évite le pire, mais les marchés « touche » à prix 0,05-0,5 déjà touchés partiellement ne sont pas traités (les achats de OUI gagnent aujourd'hui).
