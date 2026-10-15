# Proposition — ordres à cours limité posés dans le carnet (point 6)

Date : 15/10/2026. Demandée par Etienne (« Oui applique tout, y compris le point 6 »).
Touche le noyau protégé (règles du jeu) : `execution_simulator.py` et son test
`tests/test_execution_simulator.py`. Rien d'autre du noyau ne change (ni `ledger.py`, ni
`safety_controller.py`, ni `fees.py`, ni les workflows, ni les mots de passe).

## Pourquoi

Aujourd'hui l'outil ne peut qu'acheter « au vendeur » (ordre taker) : il paie l'écart entre
acheteurs et vendeurs, plus les frais taker. Sur le vrai Polymarket, on peut aussi POSER un
ordre (« j'achète à 0,88 ») et attendre. C'est moins cher, mais on n'est servi que si quelqu'un
vient nous vendre à ce prix. Cela ouvre de nouvelles stratégies (patience, « market making »).

## Ce qui change dans le noyau (règle prudente du « passage au travers »)

Nouvelles fonctions `simulate_resting_buy` / `simulate_resting_sell` / `maker_fee` :
- un ordre posé au cycle t n'est jamais exécuté avec le carnet du cycle t (pas de regard en
  arrière) : seulement avec un carnet relu APRÈS la pose ;
- un achat posé à P n'est exécuté que si le carnet montre des vendeurs à P − 1 cran ou moins
  (le marché est passé au travers de notre prix : même derniers de la file, nous aurions été
  servis), pour la quantité affichée, au prix P, jamais mieux ; symétrique pour une vente ;
- un simple « toucher » (meilleur vendeur = P) ne suffit pas : notre place dans la file est inconnue ;
- tout ce qui s'échange entre deux relectures est ignoré (on rate des exécutions : prudent) ;
- frais nuls seulement si le barème du marché dit explicitement « taker seulement » ; sinon les
  frais taker sont comptés. Aucune remise n'est jamais comptée.
Les fonctions taker existantes ne changent pas.

## Ce qui ne change pas (règle n°1 intacte)

Chaque exécution d'un ordre posé repasse par le contrôleur (`evaluate`) et par le journal signé
(`record_buy` / `record_sell`), exactement comme un ordre taker : solde, doublon, faillite et
gains latents sont vérifiés par le même code. Un ordre en attente n'est PAS de l'argent : il vit
dans la base de données ; si elle est perdue, l'ordre disparaît, rien d'autre. Les achats posés
ne peuvent pas réserver plus que le solde disponible.

## Partie libre (dans la même pull request)

`main.py` (pose, exécution, expiration, annulation, remplacement), `persistence.py` (table
`pending_orders`), `strategy_engine.py` (mode « patient » `limit_ticks`, variantes `class:`),
première variante `calibration_patiente`, réglages `limit_orders`, prudence sur `takerOnly`
absent (frais comptés), tests du cycle complet.

## Ce qu'Etienne doit faire

`guard` bloque cette pull request (noyau). Pour la fusionner : désactiver un instant le ruleset
`protection-main`, fusionner, puis le réactiver (marche à suivre donnée dans la conversation).
