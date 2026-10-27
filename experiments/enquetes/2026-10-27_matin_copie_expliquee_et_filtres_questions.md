# 27/10/2026 (matin) — l'obligation `copie_fidele` rouvrait un défaut déjà corrigé ; filtres de question relus

## Obligation de la feuille de mission : `copie_fidele`, « 1 achat sans jumeau »
- L'achat signalé (2026-10-25 22:35, `nf_sport_patiente_6_24h`, « Team Yandex », 5,43 parts à 0,83 = 4,5 €) est **exactement** celui de
  l'enquête du 26/10 ([ordre posé périmé](2026-10-26_ordre_pose_perime_du_principal.md)) : l'ancien ordre posé du principal restait ouvert quand
  le fantôme changeait de prix. Correctif déjà en place (`_place_resting(source_orders=…)`, PR #153).
- Le contrôle le comptait encore « grave » à chaque passage tant que l'achat reste dans la fenêtre d'analyse : une obligation qui ne mène à rien
  détourne le chercheur (même cas que `AUDIT_EXPLIQUEES`, 26/10).
- **Correctif** : `enquete.COPIE_EXPLIQUEES` (minute + stratégie → fiche) ; l'achat est listé « à regarder, déjà expliqué », plus une obligation.
  Un **autre** achat sans jumeau reste « grave ». Test : `test_orphan_already_explained_is_not_an_obligation`.

## Contrôle à la main, famille 4 (27 mod 6 + 1) : le filtre ne filtre pas ? (script `scripts/filtres_questions_27_10.py`)
- Les contrôles du 24 et du 25/10 couvraient le prix et les fenêtres de temps. Restaient les filtres **sur la question** : `disciplines`, `issue`,
  `question_contient`, `question_exclut`, `sources`.
- 37 fantômes à filtres de ce genre, **1 663 achats** relus sur la question de la sauvegarde (`market_rules`) avec les mêmes fonctions que le moteur
  (`pareto.discipline`, `domain_of`) : **0 achat hors filtre** (213 achats dont le marché n'est plus dans la sauvegarde, non contrôlables).
- Non contrôlable depuis les journaux : `types_pari` (le type de pari Gamma `sportsMarketType` n'est pas dans la sauvegarde), `ecart_max` (écart non journalisé),
  `heures_min/max` (heure du coup d'envoi non gardée). Reste ouvert : journaliser `game_start` et `spread` dans `extra` des achats pour pouvoir les relire.

## Constat « à regarder » mené jusqu'au bout : `crypto_threshold_prix_bas` (+228 € mais −4,0 % par mise ; 24/10 = 82 % du gain)
- 16 paris, 389 € misés. **Un seul pari fait le gain** : « Bitcoin dip to 80 000 le 24/10 », OUI à 0,18, 277 parts, +224 €. Sans lui +4 €.
  Les autres : +39,8 (NON à 0,77), +36,0, +34,6 contre −32,9 (le NON à 0,001 déjà expliqué le 24/10), −31,3, −16,7, −13,3.
- Pas de défaut de code : le prix 0,18 est un vrai prix du carnet (audit propre), le pari a gagné parce que Bitcoin a touché 80 000. Une loterie à 1 gagnant :
  même mécanisme que `compteur_tweets` (3 paris = 88 %). Ne pas l'appeler avantage.
