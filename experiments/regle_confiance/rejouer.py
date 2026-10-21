"""Essai à blanc (21/10/2026, demande d'Etienne) : règle actuelle contre « confiance progressive ».

Rejoue heure par heure, depuis le début des journaux, les paris RÉELS des fantômes (journaux publiés,
branche data : `bash scripts/fetch_data.sh`). À chaque heure, chaque règle donne une part du capital
principal à chaque stratégie, d'après les seules opérations clôturées AVANT cette heure. Le principal
simulé reçoit, pour chaque pari ouvert pendant l'heure : part × (mise du fantôme / capital du fantôme)
× rendement du pari × capital du principal (approximation de la copie fidèle, sans frais ni carnet).

Règle actuelle (approchée) : ≥ 20 opérations, ≥ 24 h, croissance ≥ +2 %, confiance t ≥ 1,5 (garde tant
que croissance > 0 et t ≥ 0) ; 5 places, moitié à égalité moitié au mérite, période d'essai, 50 % au
plus. Doublons et familles ignorés.

Règle proposée : confiance = gagnés contre attendus (prix payé), écart regroupé par jour (variance au
moins égale à l'écart des journées), avec un léger scepticisme (z − 0,5) ; ≥ 15 opérations, ≥ 24 h,
croissance > 0 ; sous 80 % : rien ; 80-95 % : 5 à 20 % ; au-delà de 95 % : part normale (comme
aujourd'hui), 50 % au plus.

Usage : .venv/bin/python experiments/regle_confiance/rejouer.py [--sceptique 0.5]
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from polymarket_agent.reporting import closed_trades  # noqa: E402

DATA = ROOT / "published_data" / "ledger"


def ts(x: str) -> datetime:
    return datetime.fromisoformat(x)


def load() -> dict:
    out = {}
    for path in sorted(glob.glob(str(DATA / "fantome" / "*.jsonl"))):
        rows = [json.loads(line) for line in open(path) if line.strip()]
        start = next((ts(r["ts"]) for r in rows if r["type"] in ("GENESIS",)), None)
        trades = []
        for t in closed_trades(rows):
            cost, bought = float(t["cost"]), float(t["shares_bought"])
            if cost <= 0 or bought <= 0:
                continue
            trades.append({"open": ts(t["opened_at"]), "close": ts(t["closed_at"]), "cost": cost,
                           "pnl": float(t["pnl"]), "price": cost / bought, "won": float(t["pnl"]) > 0})
        out[Path(path).stem] = {"start": start, "trades": trades}
    return out


def phi(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def stats(trades: list[dict]) -> dict:
    n = len(trades)
    pnl = sum(t["pnl"] for t in trades)
    rets = [t["pnl"] / t["cost"] for t in trades]
    m = sum(rets) / n if n else 0.0
    sd = math.sqrt(sum((r - m) ** 2 for r in rets) / (n - 1)) if n > 1 else 0.0
    t_stat = m / (sd / math.sqrt(n)) if sd > 0 else (99.0 if m > 0 else 0.0)
    days = defaultdict(lambda: [0.0, 0.0])
    var_model = 0.0
    for t in trades:
        p = min(max(t["price"], 0.01), 0.99)
        days[t["close"].date()][0] += t["won"] - p
        var_model += p * (1 - p)
    resid = [d[0] for d in days.values()]
    var = max(var_model, sum(e * e for e in resid))
    z = sum(resid) / math.sqrt(var) if var > 0 else 0.0
    return {"n": n, "growth": math.log(max(1000 + pnl, 1) / 1000), "t": t_stat, "z": z}


def current_rule(st: dict, held: set, now: datetime) -> dict:
    ok = {}
    for name, s in st.items():
        age = (now - s["start"]).total_seconds() / 3600 if s["start"] else 0
        enters = s["n"] >= 20 and age >= 24 and s["growth"] >= 0.02 and s["t"] >= 1.5
        stays = name in held and s["growth"] > 0 and s["t"] >= 0
        if enters or stays:
            ok[name] = s
    best = sorted(ok, key=lambda k: -ok[k]["growth"])[:5]
    total = sum(ok[k]["growth"] for k in best)
    if total <= 0:
        return {}
    out = {}
    for k in best:
        w = 0.5 / len(best) + 0.5 * ok[k]["growth"] / total
        w *= min(1.0, max(0.25, ok[k]["n"] / 60))  # période d'essai
        out[k] = min(w, 0.5)
    return out


def new_rule(st: dict, now: datetime, skeptic: float) -> dict:
    small, full = {}, {}
    for name, s in st.items():
        age = (now - s["start"]).total_seconds() / 3600 if s["start"] else 0
        if s["n"] < 15 or age < 24 or s["growth"] <= 0:
            continue
        c = phi(s["z"] - skeptic)
        if c >= 0.95:
            full[name] = s
        elif c >= 0.80:
            small[name] = 0.05 + (c - 0.80) / 0.15 * 0.15
    out = dict(small)
    room = max(0.0, 1 - sum(small.values()))
    best = sorted(full, key=lambda k: -full[k]["growth"])[:5]
    total = sum(full[k]["growth"] for k in best)
    for k in best:
        w = room * (0.5 / len(best) + 0.5 * full[k]["growth"] / total) if total > 0 else 0
        out[k] = min(w, 0.5)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sceptique", type=float, default=0.5)
    args = ap.parse_args()
    ghosts = load()
    first = min(g["start"] for g in ghosts.values() if g["start"])
    end = max(t["close"] for g in ghosts.values() for t in g["trades"])
    now = first.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    pnl = {"actuelle": 0.0, "proposee": 0.0}
    exposure = {"actuelle": [], "proposee": []}
    held: set = set()
    shares_log = defaultdict(lambda: defaultdict(float))
    while now <= end:
        st = {}
        for name, g in ghosts.items():
            done = [t for t in g["trades"] if t["close"] <= now]
            if done:
                st[name] = dict(stats(done), start=g["start"])
        rules = {"actuelle": current_rule(st, held, now), "proposee": new_rule(st, now, args.sceptique)}
        held = set(rules["actuelle"])
        for rule, shares in rules.items():
            exposure[rule].append(sum(shares.values()))
            for name, w in shares.items():
                shares_log[rule][name] += w
                for t in ghosts[name]["trades"]:
                    if now <= t["open"] < now + timedelta(hours=1):
                        pnl[rule] += w * (t["cost"] / 1000) * (t["pnl"] / t["cost"]) * 1000
        now += timedelta(hours=1)
    hours = len(exposure["actuelle"])
    print(f"Période : {first:%d/%m %H:%M} → {end:%d/%m %H:%M} UTC ({hours} heures), scepticisme {args.sceptique}")
    for rule in ("actuelle", "proposee"):
        avg = sum(exposure[rule]) / hours if hours else 0
        top = sorted(shares_log[rule].items(), key=lambda kv: -kv[1])[:5]
        print(f"\nRègle {rule} : principal simulé {pnl[rule]:+.0f} €, part engagée moyenne {avg:.0%}")
        for name, w in top:
            print(f"  {name:42s} part moyenne {w / hours:.1%}")
    print("\nConfiance proposée au dernier instant (meilleures) :")
    st = {n: stats(g["trades"]) for n, g in ghosts.items() if len(g["trades"]) >= 15}
    for name, s in sorted(st.items(), key=lambda kv: -kv[1]["z"])[:8]:
        print(f"  {name:42s} {s['n']:3d} paris  confiance actuelle {phi(s['t']):.0%}  proposée {phi(s['z'] - args.sceptique):.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
