"""Rejouer l'arène avec plusieurs règles de promotion (AMELIORATION n°1, 17/10/2026).

À chaque heure, à partir des journaux fantômes réels (branche data), on calcule quelles stratégies
la règle aurait mises dans le capital principal (et avec quelle part), puis ce que le principal
aurait gagné en copiant leur valeur : V(t+1) = V(t) × (1 + Σ part × rendement horaire du fantôme),
valeur des fantômes = capital total estimé de leurs battements de cœur (positions ouvertes au prix
du carnet, donc pertes latentes comprises). Approximation « copie de portefeuille », sans les
plafonds du principal : sert à comparer les règles entre elles, pas à prédire un montant.

Usage : python experiments/promotion/rejouer.py <dossier contenant ledger/fantome/*.jsonl>
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from polymarket_agent.reporting import closed_trades  # noqa: E402

INITIAL = 1000.0


def load(folder: Path) -> dict[str, list[dict]]:
    out = {}
    for p in sorted((folder / "ledger" / "fantome").glob("*.jsonl")):
        out[p.stem] = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
    return out


def t_stat(pnls: list[float]) -> float:
    n = len(pnls)
    if n < 2:
        return 0.0
    m = sum(pnls) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in pnls) / (n - 1))
    return m / (sd / math.sqrt(n)) if sd > 0 else (float("inf") if m > 0 else 0.0)


def allocation(stats: dict, rule: dict, previous: dict | None = None) -> dict[str, float]:
    ok = {}
    for name, s in stats.items():
        kept = name in (previous or {}) and s["growth"] > 0  # maintien (hystérésis), comme arena.py
        if not kept and (s["n"] < rule["trades"] or s["age_h"] < 24 or s["growth"] < 0.02):
            continue
        if not kept and rule.get("t_min") is not None and s["t"] < rule["t_min"]:
            continue
        ok[name] = s
    best = sorted(ok, key=lambda n: ok[n]["growth"], reverse=True)[:5]
    total = sum(ok[n]["growth"] for n in best)
    shares = {n: ok[n]["growth"] / total for n in best} if total > 0 else {}
    if rule.get("ramp"):  # période d'essai : part réduite tant que les preuves sont minces
        shares = {n: w * min(1.0, max(rule.get("floor", 0.25), ok[n]["n"] / rule["ramp"])) for n, w in shares.items()}
    return shares


def replay(ledgers: dict[str, list[dict]], rule: dict, start: datetime, end: datetime) -> dict:
    trades = {n: closed_trades(e) for n, e in ledgers.items()}
    born = {n: datetime.fromisoformat(e[0]["ts"]) for n, e in ledgers.items() if e}
    hist, t = [], start
    while t <= end:
        stats = {}
        for n, tr in trades.items():
            closed = [x for x in tr if datetime.fromisoformat(x["closed_at"]) <= t]
            done = [float(x["pnl"]) for x in closed]
            if n not in born or born[n] > t:
                continue
            real = INITIAL + sum(done)
            # Score de confiance sur les euros (avant le 18/10 au soir) ou sur le rendement par mise.
            rets = [float(x["pnl"]) / float(x["cost"]) for x in closed if float(x["cost"]) > 0]
            stats[n] = {"n": len(done), "growth": math.log(real / INITIAL) if real > 0 else -9,
                        "age_h": (t - born[n]).total_seconds() / 3600,
                        "t": t_stat(rets) if rule.get("rendement") else t_stat(done)}
        hist.append((t, allocation(stats, rule, hist[-1][1] if hist else None)))
        t += timedelta(hours=1)
    value, used = INITIAL, {}
    for (t0, alloc), (t1, _) in zip(hist, hist[1:]):
        r = 0.0
        for n, w in alloc.items():
            a, b = equity(ledgers[n], t0), equity(ledgers[n], t1)
            if a and b:
                r += w * (b / a - 1)
                used[n] = used.get(n, 0) + 1
        value *= 1 + r
    return {"pnl": round(value - INITIAL, 2), "strategies": used}


_EQ: dict[int, list[tuple[datetime, float]]] = {}


def equity(entries: list[dict], t: datetime) -> float | None:
    """Capital total estimé au dernier battement de cœur avant t."""
    key = id(entries)
    if key not in _EQ:
        _EQ[key] = [(datetime.fromisoformat(e["ts"]), float(e["data"]["total_estimated"]))
                    for e in entries if e["type"] == "HEARTBEAT" and e["data"].get("total_estimated")]
    last = None
    for ts, v in _EQ[key]:
        if ts > t:
            break
        last = v
    return last


def main() -> None:
    ledgers = load(Path(sys.argv[1]))
    first = min(datetime.fromisoformat(e[0]["ts"]) for e in ledgers.values() if e)
    end = max(datetime.fromisoformat(e[-1]["ts"]) for e in ledgers.values() if e)
    rules = {
        "actuelle (20 op., +2 %)": {"trades": 20},
        "+ t ≥ 1,0": {"trades": 20, "t_min": 1.0},
        "+ t ≥ 1,5": {"trades": 20, "t_min": 1.5},
        "+ t ≥ 2,0": {"trades": 20, "t_min": 2.0},
        "+ t ≥ 1,5 + essai (n/60)": {"trades": 20, "t_min": 1.5, "ramp": 60},
        "actuelle + essai (n/60)": {"trades": 20, "ramp": 60},
        "30 op., +2 %": {"trades": 30},
        "t ≥ 1,5 sur le rendement + essai": {"trades": 20, "t_min": 1.5, "ramp": 60, "rendement": True},
    }
    print(f"Période : {first:%d/%m %H:%M} → {end:%d/%m %H:%M} UTC, {len(ledgers)} fantômes")
    # Ce que voit chaque règle au moment de la vraie promotion (17/10 08:32) et maintenant.
    for when in (datetime(2026, 10, 17, 8, 32, tzinfo=timezone.utc), end):
        for n, e in ledgers.items():
            done = [float(x["pnl"]) for x in closed_trades(e) if datetime.fromisoformat(x["closed_at"]) <= when]
            if len(done) >= 10 and sum(done) > 0:
                print(f"  {when:%d/%m %H:%M} {n:34} {len(done):3} op. résultat {sum(done):+8.2f} t = {t_stat(done):5.2f}")
    for name, rule in rules.items():
        r = replay(ledgers, rule, first.replace(minute=0, second=0, microsecond=0), end)
        print(f"{name:28} résultat du principal {r['pnl']:+8.2f}  stratégies suivies : {r['strategies']}")


if __name__ == "__main__":
    main()
