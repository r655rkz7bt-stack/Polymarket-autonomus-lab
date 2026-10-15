"""Recherche : calibration des prix Polymarket et stratégie qui en découle.

Protocole (fixé AVANT de regarder les résultats) :
  1. Échantillons : pour chaque marché résolu, le prix aux horizons 72 h … 1 h avant
     la limite de décision (jamais un prix postérieur à l'instant de décision).
  2. Découpage chronologique par événement : 60 % entraînement, 20 % validation,
     20 % test (le test ne sert qu'une fois, avec --final-test).
  3. Table de calibration ajustée sur l'entraînement uniquement.
  4. Stratégies comparées : « ne rien faire », la référence naïve v1, la stratégie
     calibrée. Mêmes limites de risque, même journal, même contrôleur.
  5. Sensibilité au coût d'exécution : demi-écart ×1, ×1,5, ×2.

Usage : python scripts/research_calibration.py [--final-test]
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from pathlib import Path

from _common import ROOT

from polymarket_agent import calibration
from polymarket_agent.backtest import (Decision, build_samples, cluster_mean_ci, fee_per_share,
                                       simulate, split_by_event)
from polymarket_agent.history import load_dataset
from polymarket_agent.safety_controller import RiskLimits

from polymarket_agent.lab_rules import (FLOOR, HALF_SPREAD, MIN_CHANGES, MIN_EVENTS,  # noqa: F401
                                        fit_reversion, make_calibrated, make_reversion, naive_v1,
                                        reversion_move)


def day(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d") if ts else "?"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-test", action="store_true", help="évalue UNE fois la période de test")
    parser.add_argument("--data", default=str(ROOT / "data" / "history"))
    parser.add_argument("--dry-run", action="store_true",
                        help="mise au point du script : n'écrit ni rapport ni table")
    args = parser.parse_args()
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    markets = load_dataset(Path(args.data))
    samples, outcomes = build_samples(markets)
    (train, val, test), bounds = split_by_event(samples)
    lines = [f"# Recherche calibration — {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC", ""]
    lines += [f"- Marchés résolus : {len(markets)} ; avec échantillons : {len(samples)}",
              f"- Entraînement : {len(train)} marchés ({day(bounds[0])} → {day(bounds[1])})",
              f"- Validation : {len(val)} marchés (→ {day(bounds[2])})",
              f"- Test : {len(test)} marchés (→ {day(bounds[3])})", ""]

    table = calibration.fit(train, outcomes, min_changes=MIN_CHANGES)
    lines += ["## Table de calibration (entraînement)", "",
              "δ = taux de victoire du favori − prix du favori. Intervalle à 90 % par bootstrap sur les événements, rétréci vers 0.", "",
              "| case | échantillons | événements | prix moyen | victoires | δ brut | δ bas | δ haut |", "|---|---|---|---|---|---|---|---|"]
    for key, c in sorted(table.items()):
        lines.append(f"| {key} | {c.n_samples} | {c.n_events} | {c.mean_price:.3f} | {c.win_rate:.3f} | "
                     f"{c.delta:+.4f} | {c.delta_low:+.4f} | {c.delta_high:+.4f} |")
    rev_table = fit_reversion(train, outcomes)
    lines += ["", "## Table « reversion » (entraînement) : favori après un mouvement >= 0,10 en 6 h", "",
              "| mouvement | échantillons | événements | prix moyen | δ brut | δ bas | δ haut |", "|---|---|---|---|---|---|---|"]
    for key, c in rev_table.items():
        lines.append(f"| {key} | {c.n_samples} | {c.n_events} | {c.mean_price:.3f} | {c.delta:+.4f} | "
                     f"{c.delta_low:+.4f} | {c.delta_high:+.4f} |")

    periods = [("validation", val)] + ([("test", test)] if args.final_test else [])
    results = {}
    for period_name, period in periods:
        lines += ["", f"## Simulation de portefeuille — {period_name}", "",
                  "| stratégie | demi-écart | opérations | événements | réussite | profit net | rendement | croissance log | drawdown max | rendement/€ misé [IC 90 %] | Brier strat. / marché |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for mult in (1.0, 1.5, 2.0):
            hs = HALF_SPREAD * mult
            for name, rule in [("ne_rien_faire", lambda s: None), ("naive_favorite_v1", naive_v1),
                               ("calibration_v1", make_calibrated(table, half_spread=hs)),
                               ("reversion_v1", make_reversion(rev_table, half_spread=hs))]:
                res = simulate(name, rule, period, outcomes, limits, half_spread=hs)
                m = res.metrics()
                results[(period_name, name, mult)] = m
                ci = m["ic90_rendement_par_euro"]
                lines.append(
                    f"| {name} | {hs:.3f} | {m['operations']} | {m['evenements']} | {m['taux_reussite']} | "
                    f"{m['profit_net']} | {m['rendement']} | {m['croissance_log']} | {m['drawdown_max']} | "
                    f"{m['rendement_moyen_par_euro_mise']} {ci} | {m['brier_strategie']} / {m['brier_marche']} |")
    if args.dry_run:
        print("\n".join(lines))
        return 0
    out = ROOT / "experiments" / f"calibration_{datetime.now(timezone.utc):%Y%m%d_%H%M}{'_TEST' if args.final_test else ''}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nRapport : {out}")
    if not args.final_test:
        calibration.save(rev_table, ROOT / "config" / "reversion_v1.json", {
            "version": "1", "fitted_on": "entraînement v2 (historique non biaisé, 40 jours)",
            "period": [day(bounds[0]), day(bounds[1])], "min_move": 0.10, "window_hours": 6,
            "min_changes_24h": MIN_CHANGES, "shrink_k": 200, "min_events": MIN_EVENTS,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        calibration.save(table, ROOT / "config" / "calibration_v2.json", {
            "version": "2", "fitted_on": "entraînement v2 (60 % des événements les plus anciens, 40 jours tirés au hasard, sans filtre de volume)",
            "min_changes_24h": MIN_CHANGES,
            "period": [day(bounds[0]), day(bounds[1])], "markets": len(train),
            "half_spread_assumption": HALF_SPREAD, "min_events": MIN_EVENTS, "shrink_k": 200,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
