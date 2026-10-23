---
name: nouvelle-strategie
description: Ajouter une stratégie ou une variante dans l'arène du labo - classe (strategies_v3.py), entrée config/strategies.yaml avec explication, tests, et cycle local pour vérifier qu'elle voit des marchés. À utiliser quand une piste est retenue ou mérite un fantôme, ou pour créer une fille ou une variante d'une stratégie existante.
---

# Ajouter une stratégie dans l'arène

Références : docs/METHODE.md (méthode de recherche, point 4) et ARCHITECTURE.md, qui priment en cas de
désaccord. Exemple récent et complet : `VagueVolume` dans `src/polymarket_agent/strategies_v3.py`.

## Avant d'écrire du code
- L'historique existe ? Le test sur le passé passe d'abord (skill `tester-une-piste`). Une stratégie non
  testée entre comme fantôme en le disant dans `hypothesis`.
- Une variante sans nouveau code suffit souvent : une entrée `strategies.yaml` avec `class: <stratégie
  existante>` et d'autres paramètres. Une fille d'une mère : `mere`, `morceau`, `filtres`
  (au plus 10 filles vivantes par mère, `config/promotion.yaml` → `filles`).
- Pas de nouvelle variante « _patiente » (ordres posés) d'une stratégie directionnelle sans avoir regardé
  son markout : les ordres posés sont surtout servis quand on a tort.

## Écrire la stratégie
1. **Classe** dans `src/polymarket_agent/strategies_v3.py` : `strategy_id`, `required` (paramètres
   obligatoires), `candidates(markets)`, `propose(...)` qui remplit les abstentions avec une raison claire
   (« carnet indisponible », « issue hors de la plage de prix »…), puis ajout dans `CLASSES`.
2. **Entrée** dans `config/strategies.yaml` : `explication` (une phrase pour un enfant de 6 ans,
   obligatoire), `class`, `enabled`, `version`, `created_at`, `hypothesis`, `params` avec
   `{value, min, max}`.
3. **Tests** dans `tests/test_strategies_v3.py`, sur des marchés construits comme les vrais (dont un cas
   qui ne doit RIEN proposer), et mise à jour de la liste attendue dans
   `tests/test_strategies.py::test_repository_config_loads`. La règle `kelly_fraction == 1` de ce test a
   une liste d'exceptions : ajoute-y le préfixe si tu choisis une autre fraction.
4. Une donnée de marché manquante (comme `volume_1wk`) : champ dans `models.Market`, lecture dans
   `sources/polymarket_gamma.parse_market`.

## Vérifier qu'elle voit des marchés (21/10/2026 : `cpi_tranches` et `jobs_favori_non` sont restées sourdes)
- `.venv/bin/python scripts/run_simulation.py --once --dev-key`, puis lis sa ligne
  `[<portefeuille>] <stratégie> v… : N propositions, M ordres à poser, abstentions {…}`.
  0 proposition et `{}` = elle ne voit rien : ajoute l'étiquette dans `scanner.tag_pages`
  (config/settings.yaml), ou fais-lui demander ses propres marchés, avec un test.
- Sur quelques candidats en direct, relis à la main le marché choisi et le côté acheté.

## Après
- `.venv/bin/python -m pytest -q` vert (skill `verification-before-completion` : montre la sortie).
- Raison de l'ajout dans `experiments/journal_recherche.md` (rubrique **Arène**).
- L'arène juge sur le rendement par mise, aux carnets réels ; le principal ne la copie qu'une fois les
  seuils de `config/promotion.yaml` passés. Ne baisse jamais ces seuils pour « débloquer » une stratégie.
