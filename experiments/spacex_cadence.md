# Lancements de SpaceX : « combien de lancements ce mois-ci / cette année ? » (24/10/2026, après-midi)

Source nouvelle (chantier n°7 de `CHANTIERS.md`) : Launch Library 2 (`ll.thespacedevs.com`, sans clé, ~15 appels par heure). Marchés : « How many SpaceX launches in
<mois> / <année> ? », réglés sur spacex.com/launches (tranches de nombre de lancements, frais nuls à 4 % selon l'événement). Même mécanisme que les séismes : le compte
ne fait que monter et la source qui tranche se lit en direct.

## En bref
- **Question.** Le marché cote-t-il bien les tranches quand on connaît déjà le compte et la cadence (≈ 0,43 lancement par jour, 8 à 17 par mois) ?
- **Contrôle du règlement : 9 sur 9.** Le compte de Launch Library 2 (heure de l'Est) tombe dans la tranche officiellement gagnante pour l'année 2025 (170 dans « 160-179 »)
  et pour janvier (13), février (12), mars (15), avril (12), mai (12), juin (14), août (13), septembre (8) 2026. (Juillet : événement introuvable par la recherche.)
- **Verdict (`idea_test.verdict`) : écartée au sens strict (moins de 30 paris), INDICE FAIBLE pour les paris quasi sûrs → fantôme `spacex_cumul` (quart de Kelly).**
  - Modèle : compte déjà fait (lancements avant l'instant de décision) + reste sous trois lois (Poisson, loi régulière de variance 0,5 × moyenne, fenêtres empiriques
    de même durée sur les 365 derniers jours), cadence des 120 derniers jours. Décision chaque jour à 12 h UTC, achat au premier échange réel dans les 2 h.
  - 9 événements, 1 466 à 6 886 échanges chacun. 9 réglages (3 lois × 3 seuils de 0,03 / 0,05 / 0,10).
  - Tous réglages : 13 à 27 paris, rendement −17 % à +35 % (un seul réglage positif, 13 paris) : **le modèle ne bat pas le marché dans l'ensemble**.
  - Les paris à chance modeste (0,1 à 0,5 pour un prix de 0,03 à 0,3) perdent : 20 paris, −19 %. Les paris quasi sûrs (chance ≥ 0,96, prix 0,84-0,93) gagnent :
    loi régulière 7 paris sur 7 (+10 %, 3 événements), Poisson 3 sur 3 (+9 %), fenêtres 8 sur 9 (0 %). Trop peu pour conclure : d'où `min_price 0,50` (seulement le côté probable).
- **En direct le 24/10** (122 lancements faits en 2026, 68 jours restants) : « 140-159 » de l'année cotée 0,78 (chance 0,94 à 1,00 : il faut 18 à 37 lancements de plus, la cadence en
  donne ≈ 29) ; le fantôme l'a achetée dans le premier cycle local (24,7 parts à 0,780, chance prudente 0,945, avantage net 0,163, relue à la main). « 120-139 » et « 160-179 »
  sont vendues 0,12 et 0,03 : pas d'avantage une fois le plafond de certitude (0,97) posé.

## Pourquoi ça peut rater
- spacex.com ne compte pas comme Launch Library 2 (le compteur du site peut oublier un vol d'essai) : 9/9 ne couvre pas un écart d'un lancement près d'une frontière de tranche.
- Une pause de la flotte de plusieurs semaines (accident) : la loi des 120 derniers jours ne le voit pas. Les trois lois divergent alors peu : la stratégie prend la plus prudente.
- Capital bloqué 68 jours sur l'année (rendement par jour faible) et marchés minces (20 à 170 parts par niveau de prix).

## Fichiers
`experiments/spacex_cadence/scripts/releve.py` (relevé LL2 et événements Gamma), `backtest.py` (le test ci-dessus), `src/polymarket_agent/spacex.py` et
`sources/ll2.py` (production), `tests/test_spacex.py`. Données : `donnees/` (ignoré par Git).
