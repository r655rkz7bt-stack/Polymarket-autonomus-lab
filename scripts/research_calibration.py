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
import json
from datetime import datetime, timezone

from _common import ROOT

from polymarket_agent import calibration
from polymarket_agent.backtest import (Decision, build_samples, cluster_mean_ci, fee_per_share,
                                       simulate, split_by_event)
from polymarket_agent.history import load_dataset
from polymarket_agent.safety_controller import RiskLimits

HALF_SPREAD = 0.01
MIN_EVENTS = 150
FLOOR = 0.02


def naive_v1(sample):
    """Référence naïve v1 (biais a priori non calibré : milieu + 0,05 ± 0,015)."""
    fav = 0 if sample.price_yes >= 0.5 else 1
    f = sample.price_yes if fav == 0 else 1 - sample.price_yes
    if not 0.80 <= f + HALF_SPREAD <= 0.95:
        return None
    est = min(f + 0.05, 0.99)
    return Decision(fav, est - 0.015, est, min(est + 0.015, 0.995))


def make_calibrated(table, half_spread=HALF_SPREAD, min_events=MIN_EVENTS, floor=FLOOR):
    def rule(sample):
        fav = 0 if sample.price_yes >= 0.5 else 1
        f = sample.price_yes if fav == 0 else 1 - sample.price_yes
        key = calibration.cell_key(sample.category, sample.horizon_h, f)
        cell = table.get(key) if key else None
        if cell is None or cell.n_events < min_events:
            return None
        ask_fav = f + half_spread
        low = f + cell.delta_low
        if ask_fav < 1 and low - ask_fav - fee_per_share(ask_fav, sample.fee_rate) >= floor:
            est = f + cell.delta_shrunk
            return Decision(fav, low, est, min(f + cell.delta_high, 0.995))
        dog = 1 - f
        ask_dog = dog + half_spread
        low_dog = 1 - (f + cell.delta_high)
        if low_dog - ask_dog - fee_per_share(ask_dog, sample.fee_rate) >= floor:
            est = 1 - (f + cell.delta_shrunk)
            return Decision(1 - fav, low_dog, est, min(1 - (f + cell.delta_low), 0.995))
        return None
    return rule


def day(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d") if ts else "?"


def momentum_report(samples, outcomes):
    """Analyse secondaire : un favori qui vient de monter / baisser de >= 0,10 en 6 h."""
    groups = {"favori en hausse >= 0,10 sur 6 h": {}, "favori en baisse >= 0,10 sur 6 h": {}}
    for market_id, rows in samples.items():
        winner = outcomes[market_id].winner
        for s in rows:
            if s.price_yes_6h_ago is None:
                continue
            fav = 0 if s.price_yes >= 0.5 else 1
            f = s.price_yes if fav == 0 else 1 - s.price_yes
            f_before = s.price_yes_6h_ago if fav == 0 else 1 - s.price_yes_6h_ago
            move = f - f_before
            if abs(move) < 0.10:
                continue
            name = list(groups)[0 if move > 0 else 1]
            groups[name].setdefault(s.event_id, []).append((1 if winner == fav else 0) - f)
    return {k: cluster_mean_ci(v) for k, v in groups.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-test", action="store_true", help="évalue UNE fois la période de test")
    args = parser.parse_args()
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    markets = load_dataset(ROOT / "data" / "history")
    samples, outcomes = build_samples(markets)
    (train, val, test), bounds = split_by_event(samples)
    lines = [f"# Recherche calibration — {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC", ""]
    lines += [f"- Marchés résolus : {len(markets)} ; avec échantillons : {len(samples)}",
              f"- Entraînement : {len(train)} marchés ({day(bounds[0])} → {day(bounds[1])})",
              f"- Validation : {len(val)} marchés (→ {day(bounds[2])})",
              f"- Test : {len(test)} marchés (→ {day(bounds[3])})", ""]

    table = calibration.fit(train, outcomes)
    lines += ["## Table de calibration (entraînement)", "",
              "δ = taux de victoire du favori − prix du favori. Intervalle à 90 % par bootstrap sur les événements, rétréci vers 0.", "",
              "| case | échantillons | événements | prix moyen | victoires | δ brut | δ bas | δ haut |", "|---|---|---|---|---|---|---|---|"]
    for key, c in sorted(table.items()):
        lines.append(f"| {key} | {c.n_samples} | {c.n_events} | {c.mean_price:.3f} | {c.win_rate:.3f} | "
                     f"{c.delta:+.4f} | {c.delta_low:+.4f} | {c.delta_high:+.4f} |")
    lines += ["", "## Analyse secondaire : mouvements récents (entraînement)", ""]
    for name, (mean, lo, hi, n) in momentum_report(train, outcomes).items():
        lines.append(f"- {name} : δ = {mean:+.4f} [{lo:+.4f} ; {hi:+.4f}], {n} événements")

    periods = [("validation", val)] + ([("test", test)] if args.final_test else [])
    results = {}
    for period_name, period in periods:
        lines += ["", f"## Simulation de portefeuille — {period_name}", "",
                  "| stratégie | demi-écart | opérations | événements | réussite | profit net | rendement | croissance log | drawdown max | rendement/€ misé [IC 90 %] | Brier strat. / marché |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for mult in (1.0, 1.5, 2.0):
            hs = HALF_SPREAD * mult
            for name, rule in [("ne_rien_faire", lambda s: None), ("naive_favorite_v1", naive_v1),
                               ("calibration_v1", make_calibrated(table, half_spread=hs))]:
                res = simulate(name, rule, period, outcomes, limits, half_spread=hs)
                m = res.metrics()
                results[(period_name, name, mult)] = m
                ci = m["ic90_rendement_par_euro"]
                lines.append(
                    f"| {name} | {hs:.3f} | {m['operations']} | {m['evenements']} | {m['taux_reussite']} | "
                    f"{m['profit_net']} | {m['rendement']} | {m['croissance_log']} | {m['drawdown_max']} | "
                    f"{m['rendement_moyen_par_euro_mise']} {ci} | {m['brier_strategie']} / {m['brier_marche']} |")
    out = ROOT / "experiments" / f"calibration_{datetime.now(timezone.utc):%Y%m%d_%H%M}{'_TEST' if args.final_test else ''}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nRapport : {out}")
    if not args.final_test:
        calibration.save(table, ROOT / "config" / "calibration_v1.json", {
            "version": "1", "fitted_on": "entraînement (60 % des événements les plus anciens)",
            "period": [day(bounds[0]), day(bounds[1])], "markets": len(train),
            "half_spread_assumption": HALF_SPREAD, "min_events": MIN_EVENTS, "shrink_k": 200,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
