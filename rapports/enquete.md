# Enquête automatique — 2026-11-21T10:32+00:00

Défauts possibles trouvés dans les journaux publiés (enquete.py). « grave » = obligation de la feuille de mission ; « à regarder » = piste pour l'enquête manuelle (docs/ROUTINE_CHERCHEUR.md).

## [à regarder] seismes_queues_audace_v2.0.0 : 1 achat(s) estimés 30% ou plus au-dessus du prix payé (stratégie neuve, moins de 5 achats)

*Contrôle `estimation_perimee`* — Un écart aussi grand avec le marché vient plus souvent d'une source mal lue que d'un avantage : relire la source et le marché avant de croire l'estimation.

- 2026-11-21T09:52 « Yes » estimé 0.730, payé 0.080, mise 2 €

## [à regarder] favori_politique_quasi_certain_v2.0.0 : z = +0.67 sur 17 paris, mais choisie parmi 4 stratégies

*Contrôle `selection_multiple`* — P(hasard) corrigée = 1.00 (> 0.05) : le meilleur z de l'arène est +0.67, ce que 4 stratégies sans avantage donnent déjà. Ne pas confondre « première du classement » et « avantage prouvé » : confirmer sur de nouveaux paris (ou un test sur le passé).


## [à regarder] 2 fille(s) comparée(s) à leur mère sur la même période

*Contrôle `filles_periode`* — Juger une fille contre sa mère ENTIÈRE mélange deux périodes : une fille née un mauvais jour paraît mauvaise même si elle fait mieux que sa mère ce jour-là. Comparer ces chiffres-ci.

- compteur_tweets_72_168h +7.1% contre sa mère compteur_tweets -16.5% depuis le 2026-11-07 (19 et 50 opérations ; pondéré par la mise -20.0% contre -16.6% ; chez la mère, jetons gardés par la fille -18.6% (18) contre écartés -14.3% (32))
- compteur_truth -28.8% contre sa mère compteur_tweets -16.5% depuis le 2026-11-07 (15 et 50 opérations ; pondéré par la mise -23.9% contre -16.6% ; chez la mère, jetons gardés par la fille -22.1% (15) contre écartés -9.0% (35) ; COPIE CONFORME : 15 de ses 15 jetons chez la mère, même rendement pondéré sur ces jetons (-23.9% contre -22.1%) : un seul tirage compté deux fois, la couper si son filtre est un découpage a posteriori)

## [à regarder] 2 stratégie(s) sans aucun achat depuis plus de 48 h

*Contrôle `muettes`* — Une stratégie muette ne teste rien : lire ses abstentions (journal du cycle, tableau de bord) et corriger le filtre ou la source qui la bloque.

- el_nino_cpc_v2.1.0 (née le 2026-11-15) — dernier cycle : 329 marchés vus, 0 propositions ; aucun marché vu n'a la référence ou la forme demandée (raison non notée par la stratégie) ×329
- suivre_inities_v2.0.0 (née le 2026-11-07) — dernier cycle : 331 marchés vus, 0 propositions ; aucune grappe de comptes neufs et concentrés relevée sur ce marché ×329, personne ne parle de paris suspects sur cet événement ×2

## [à regarder] 9 stratégie(s) qui achetaient et n'achètent plus depuis plus de 72 h

*Contrôle `acheteuses_arretees`* — Une stratégie qui s'arrête peut attendre un calendrier (match, publication) ou avoir perdu son univers (famille de marchés, source, étiquette) : lire les raisons du dernier cycle, puis vérifier à la main un marché qu'elle aurait dû jouer.

- pib_canada_anticipe_v2.0.0 : 3 achats, le dernier le 2026-11-12T11:32 — dernier cycle : 329 marchés vus ; aucun marché vu n'a la référence ou la forme demandée (raison non notée par la stratégie) ×329
- encheres_estimation_v2.0.0 : 4 achats, le dernier le 2026-11-13T04:47 — dernier cycle : 329 marchés vus ; aucun marché vu n'a la référence ou la forme demandée (raison non notée par la stratégie) ×329
- taux_tresor_barriere_v2.0.0 : 17 achats, le dernier le 2026-11-13T06:12 — dernier cycle : 334 marchés vus ; taux du Trésor : chance donnée de 00 à 12 h UTC seulement (séance américaine), barrière déjà touchée, ou relevé du Trésor trop vieux ×210, avantage net insuffisant ×43, déjà en position ×17
- seismes_marche_v2.0.0 : 13 achats, le dernier le 2026-11-16T14:41 — dernier cycle : 329 marchés vus ; semaine ou jour hors de la fenêtre testée (semaine : 0,5 à 6,6 jours avant la fin), ou catalogue absent ×272, déjà deux tranches de cet événement ×9, déjà en position ×4
- seismes_pays_v2.0.0 : 3 achats, le dernier le 2026-11-16T21:27 — dernier cycle : 329 marchés vus ; avantage net insuffisant ×3, déjà en position ×2
- seismes_annee_v2.0.0 : 4 achats, le dernier le 2026-11-16T22:38 — dernier cycle : 329 marchés vus ; déjà en position ×4, avantage net insuffisant ×4, issue hors de la plage de prix ou carnet vide ×2
- openrouter_semaine_v2.0.0 : 4 achats, le dernier le 2026-11-17T12:57 — dernier cycle : 329 marchés vus ; OpenRouter : historique révisé par la source (semaine précédente 211.3 → 171.2 T) : jours du journal lus avant la révision ×3
- rt_compte_critiques_v2.0.0 : 8 achats, le dernier le 2026-11-17T20:37 — dernier cycle : 329 marchés vus ; issue hors de la plage de prix ou carnet vide ×11, déjà en position ×4, déjà deux tranches de cet événement ×4

## [à regarder] 1 fantôme(s) sans argent disponible depuis plus de 48 h

*Contrôle `capital_bloque`* — Capital immobilisé dans des positions longues : le fantôme ne teste plus rien, et le comparer à une fille ou à une mère qui a de l'argent compare deux situations différentes (juger sur la même période ET avec le même argent disponible).

- favori_politique_quasi_certain_v2.0.0 : 43.33 € disponibles sur 1019 €, 31 positions ouvertes, dernier achat le 2026-11-21T07:12

## [à regarder] 5 marché(s) réglés à 50-50 où l'arène avait acheté (17 € perdus sur 47 € misés)

*Contrôle `reglements_50_50`* — Match annulé, abandonné ou walkover : chaque part vaut 0,50. Les tests sur le passé écartent ces marchés ; un achat avant le coup d'envoi (ou sur un sport à forts taux : UFC, CS2, doubles) paie ce risque sans l'avoir compté.

- 2026-10-21T16:51 marché 5971906 : 1 portefeuille(s), 29 € misés, perte 13 €
- 2026-10-22T12:55 marché 5731353 : 1 portefeuille(s), 11 € misés, perte 5 € (acheté avant le coup d envoi)
- 2026-11-03T15:56 marché 6597403 : 1 portefeuille(s), 2 € misés, perte 0 € (acheté avant le coup d envoi)
- 2026-11-03T15:08 marché 6575068 : 1 portefeuille(s), 3 € misés, perte 0 € (acheté avant le coup d envoi)
- 2026-11-04T10:55 marché 6662239 : 1 portefeuille(s), 3 € misés, perte 0 € (acheté avant le coup d envoi)

## [à regarder] favori_politique_quasi_certain_v2.0.0 : 5 position(s) ouverte(s) bien après l'échéance

*Contrôle `positions_oubliees`* — Marché contesté, règlement manqué ou mauvaise échéance : l'argent reste bloqué.

- 2026-11-07T22:51 « Yes » (marché 2118145, échéance dépassée de 318 h)
- 2026-11-08T00:41 « Yes » (marché 2116493, échéance dépassée de 318 h)
- 2026-11-08T00:41 « No » (marché 2116494, échéance dépassée de 318 h)
- 2026-11-08T01:21 « Yes » (marché 2117123, échéance dépassée de 318 h)
- 2026-11-08T01:52 « No » (marché 2117124, échéance dépassée de 318 h)
