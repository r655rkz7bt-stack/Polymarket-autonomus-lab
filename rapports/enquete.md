# Enquête automatique — 2026-11-14T13:19+00:00

Défauts possibles trouvés dans les journaux publiés (enquete.py). « grave » = obligation de la feuille de mission ; « à regarder » = piste pour l'enquête manuelle (docs/ROUTINE_CHERCHEUR.md).

## [à regarder] taux_tresor_barriere_v2.0.0 : 3 achat(s) estimés 10% au-dessus de l'écart habituel (+0.159)

*Contrôle `estimation_perimee`* — L'estimation ne correspond pas au prix payé : carnet périmé (le prix a bougé pendant le cycle), mauvais marché rattaché, ou modèle qui s'emballe. La mise, calculée sur cette estimation, est trop grosse.

- 2026-11-13T00:05 « Yes » estimé 0.463, payé 0.088, mise 7 €
- 2026-11-13T00:08 « Yes » estimé 0.451, payé 0.130, mise 18 €
- 2026-11-13T00:05 « Yes » estimé 0.317, payé 0.060, mise 6 €

## [à regarder] 2 fille(s) comparée(s) à leur mère sur la même période

*Contrôle `filles_periode`* — Juger une fille contre sa mère ENTIÈRE mélange deux périodes : une fille née un mauvais jour paraît mauvaise même si elle fait mieux que sa mère ce jour-là. Comparer ces chiffres-ci.

- compteur_tweets_72_168h -14.4% contre sa mère compteur_tweets -17.0% depuis le 2026-11-07 (9 et 33 opérations)
- compteur_truth -27.9% contre sa mère compteur_tweets -17.0% depuis le 2026-11-07 (10 et 33 opérations)

## [à regarder] 3 stratégie(s) sans aucun achat depuis plus de 48 h

*Contrôle `muettes`* — Une stratégie muette ne teste rien : lire ses abstentions (journal du cycle, tableau de bord) et corriger le filtre ou la source qui la bloque.

- rougeole_compteur_v2.0.0 (née le 2026-11-12) — dernier cycle : 303 marchés vus, 0 propositions ; avantage net insuffisant ×2, issue hors de la plage de prix ou carnet vide ×1
- el_nino_cpc_v2.0.0 (née le 2026-11-12) — dernier cycle : 304 marchés vus, 0 propositions ; avantage net insuffisant ×3, issue hors de la plage de prix ou carnet vide ×1
- suivre_inities_v2.0.0 (née le 2026-11-07) — dernier cycle : 303 marchés vus, 0 propositions ; aucune grappe de comptes neufs et concentrés relevée sur ce marché ×303

## [à regarder] 1 stratégie(s) retirée(s) pour inactivité sans aucun achat

*Contrôle `retraits_inactifs`* — Retrait définitif d'une stratégie qui n'avait peut-être rien à faire (calendrier, arbitrage rare, source en panne). Si elle attend une date ou une rareté : l'ajouter à `jamais_retirer` (config/promotion.yaml) et relancer une nouvelle version ; si c'est un bug, le corriger avant.

- lid_agenda_v2.0.0 : retirée le 2026-11-13T21:15 (inactive : aucune opération ni position en 3 jours)

## [à regarder] 1 stratégie(s) qui achetaient et n'achètent plus depuis plus de 72 h

*Contrôle `acheteuses_arretees`* — Une stratégie qui s'arrête peut attendre un calendrier (match, publication) ou avoir perdu son univers (famille de marchés, source, étiquette) : lire les raisons du dernier cycle, puis vérifier à la main un marché qu'elle aurait dû jouer.

- compteur_truth_v2.0.0 : 10 achats, le dernier le 2026-11-10T13:11 — dernier cycle : 303 marchés vus ; compte écarté (seulement les posts Truth Social de Trump) ×28, rythmes en désaccord (le mélange dépasse 1,6 fois la médiane : rafale récente, régime changé) ×7

## [à regarder] 1 fantôme(s) sans argent disponible depuis plus de 48 h

*Contrôle `capital_bloque`* — Capital immobilisé dans des positions longues : le fantôme ne teste plus rien, et le comparer à une fille ou à une mère qui a de l'argent compare deux situations différentes (juger sur la même période ET avec le même argent disponible).

- favori_politique_quasi_certain_v2.0.0 : 0.06 € disponibles sur 1005 €, 23 positions ouvertes, dernier achat le 2026-11-13T10:14

## [à regarder] 5 marché(s) réglés à 50-50 où l'arène avait acheté (17 € perdus sur 47 € misés)

*Contrôle `reglements_50_50`* — Match annulé, abandonné ou walkover : chaque part vaut 0,50. Les tests sur le passé écartent ces marchés ; un achat avant le coup d'envoi (ou sur un sport à forts taux : UFC, CS2, doubles) paie ce risque sans l'avoir compté.

- 2026-10-21T16:51 marché 5971906 : 1 portefeuille(s), 29 € misés, perte 13 €
- 2026-10-22T12:55 marché 5731353 : 1 portefeuille(s), 11 € misés, perte 5 € (acheté avant le coup d envoi)
- 2026-11-03T15:56 marché 6597403 : 1 portefeuille(s), 2 € misés, perte 0 € (acheté avant le coup d envoi)
- 2026-11-03T15:08 marché 6575068 : 1 portefeuille(s), 3 € misés, perte 0 € (acheté avant le coup d envoi)
- 2026-11-04T10:55 marché 6662239 : 1 portefeuille(s), 3 € misés, perte 0 € (acheté avant le coup d envoi)

## [à regarder] favori_politique_quasi_certain_v2.0.0 : 5 position(s) ouverte(s) bien après l'échéance

*Contrôle `positions_oubliees`* — Marché contesté, règlement manqué ou mauvaise échéance : l'argent reste bloqué.

- 2026-11-07T22:51 « Yes » (marché 2118145, échéance dépassée de 152 h)
- 2026-11-08T00:41 « Yes » (marché 2116493, échéance dépassée de 152 h)
- 2026-11-08T00:41 « No » (marché 2116494, échéance dépassée de 152 h)
- 2026-11-08T01:21 « Yes » (marché 2117123, échéance dépassée de 152 h)
- 2026-11-08T01:52 « No » (marché 2117124, échéance dépassée de 152 h)
