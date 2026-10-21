"""Simulation des 30 prochains jours (demande d'Etienne, 21/10/2026) : capital principal composé,
paris tirés parmi les vrais paris de la championne (prix payé, mise en part de son capital,
avantage supposé), selon l'avantage RÉEL inconnu (0, +1, +2, +3,5 points de chance de gagner).

Le principal engage 70 % des mises de la championne (plafond de la règle « mélange »).
Tailles comparées : actuelle, demi, mesurée (avantage mesuré / supposé, k = 30 paris fictifs,
départ sur ses 94 paris réels). 5 000 trajectoires par cas, graine fixe.

Usage : python experiments/taille_des_mises/simuler.py
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from polymarket_agent.reporting import closed_trades  # noqa: E402

GHOST = ROOT / "published_data" / "ledger" / "fantome" / "nf_sport_patiente_v1.0.0.jsonl"
DAYS, RUNS, ENGAGED, K = 30, 5000, 0.7, 30


def profile() -> tuple[list[tuple[float, float, float]], float, int, float]:
    rows = [json.loads(line) for line in open(GHOST) if line.strip()]
    capital, bets = 1000.0, []
    for t in closed_trades(rows):
        cost, bought = float(t["cost"]), float(t["shares_bought"])
        if cost <= 0 or bought <= 0:
            continue
        p = cost / bought
        est = t.get("est_probability")
        assumed = max(0.005, float(est) - p) if est not in (None, "") else 0.035
        bets.append((p, cost / capital, assumed))
        capital += float(t["pnl"])
    excess = sum((float(t["pnl"]) > 0) - float(t["cost"]) / float(t["shares_bought"])
                 for t in closed_trades(rows) if float(t["cost"]) > 0)
    first, last = rows[0]["ts"][:10], rows[-1]["ts"][:10]
    n_days = max(1, len({t["closed_at"][:10] for t in closed_trades(rows)}))
    return bets, excess, len(bets), len(bets) / n_days


def simulate(bets, excess0, n0, per_day, true_edge, sizing, rng):
    capital, excess, n = 868.0, excess0, n0
    low = capital
    for _ in range(DAYS):
        day_gain = 0.0
        for _ in range(max(1, round(per_day))):
            p, frac, assumed = rng.choice(bets)
            scale = {"actuelle": 1.0, "demi": 0.5}.get(sizing)
            if scale is None:
                scale = min(1.0, max(0.0, (excess / (n + K)) / assumed))
            stake = min(capital, ENGAGED * frac * scale * capital)
            won = rng.random() < min(0.999, p + true_edge)
            day_gain += stake * (1 / p - 1) if won else -stake
            excess += won - p
            n += 1
        capital = max(0.0, capital + day_gain)
        low = min(low, capital)
    return capital, low


def main() -> int:
    bets, excess0, n0, per_day = profile()
    print(f"{n0} paris réels, {per_day:.0f} par jour, mise moyenne {100 * statistics.mean(b[1] for b in bets):.1f} % "
          f"du capital, avantage supposé moyen {100 * statistics.mean(b[2] for b in bets):.1f} points, "
          f"mesuré {100 * excess0 / n0:.1f} points\n")
    print("avantage réel | taille      | capital médian à 30 j | 1 chance sur 10 sous | passe sous 700 €")
    for edge in (0.0, 0.01, 0.02, 0.035):
        for sizing in ("actuelle", "demi", "mesuree"):
            rng = random.Random(42)
            res = [simulate(bets, excess0, n0, per_day, edge, sizing, rng) for _ in range(RUNS)]
            finals = sorted(r[0] for r in res)
            under = sum(r[1] < 700 for r in res) / RUNS
            print(f"  {100 * edge:+4.1f} pt     | {sizing:11s} | {statistics.median(finals):8.0f} €"
                  f"            | {finals[RUNS // 10]:6.0f} €            | {100 * under:4.0f} %")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
