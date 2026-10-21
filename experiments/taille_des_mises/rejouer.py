"""Essai à blanc : taille des mises du capital principal (demande d'Etienne, 21/10/2026).

Rejoue la semaine heure par heure avec la règle « mélange » (config/promotion.yaml du 21/10) :
le principal copie les fantômes qualifiés. Seule change la TAILLE de chaque pari copié :
- actuelle   : la mise du fantôme (Kelly complet sur un avantage supposé : estimation − prix) ;
- demi       : la moitié ;
- mesurée    : mise × (avantage mesuré / avantage supposé), bornée à [0, 1]. Avantage mesuré =
               Σ(gagné − prix payé) / (n + k) sur les paris clôturés AVANT, ramené vers 0 par k
               paris fictifs (k = 30 ou 60) : peu de paris → mise prudente.
Les fantômes, leurs classements et la règle d'entrée ne changent pas (ils continuent de mesurer).
Le résultat d'un pari est proportionnel à sa mise (approximation : une mise plus petite trouve
au moins autant de vendeurs dans le carnet).

Usage : python experiments/taille_des_mises/rejouer.py
"""

from __future__ import annotations

import glob
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from polymarket_agent.reporting import closed_trades  # noqa: E402

DATA = ROOT / "published_data" / "ledger" / "fantome"


def phi(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def load(skip_day: str | None = None) -> dict:
    out = {}
    for path in sorted(glob.glob(str(DATA / "*.jsonl"))):
        rows = [json.loads(line) for line in open(path) if line.strip()]
        start = next((datetime.fromisoformat(r["ts"]) for r in rows if r["type"] == "GENESIS"), None)
        trades = []
        for t in closed_trades(rows):
            cost, bought = float(t["cost"]), float(t["shares_bought"])
            if cost <= 0 or bought <= 0 or (skip_day and t["closed_at"].startswith(skip_day)):
                continue
            price = cost / bought
            est = t.get("est_probability")
            trades.append({"open": datetime.fromisoformat(t["opened_at"]), "close": datetime.fromisoformat(t["closed_at"]),
                           "cost": cost, "pnl": float(t["pnl"]), "price": price, "won": float(t["pnl"]) > 0,
                           "assumed": max(0.005, float(est) - price) if est not in (None, "") else 0.035})
        out[Path(path).stem] = {"start": start, "trades": trades}
    return out


def stats(trades: list[dict]) -> dict:
    n = len(trades)
    rets = [t["pnl"] / t["cost"] for t in trades]
    m = sum(rets) / n
    sd = math.sqrt(sum((r - m) ** 2 for r in rets) / (n - 1)) if n > 1 else 0.0
    days, var_model = defaultdict(float), 0.0
    for t in trades:
        p = min(max(t["price"], 0.01), 0.99)
        days[t["close"].date()] += t["won"] - p
        var_model += p * (1 - p)
    var = max(var_model, sum(e * e for e in days.values()))
    return {"n": n, "growth": math.log(max(1000 + sum(t["pnl"] for t in trades), 1) / 1000),
            "t": m / (sd / math.sqrt(n)) if sd > 0 else (99.0 if m > 0 else 0.0),
            "day_conf": phi(sum(days.values()) / math.sqrt(var)) if var > 0 else 0.5,
            "excess": sum(days.values())}


def shares(st: dict, held: set, now: datetime) -> dict:
    """Règle « mélange » telle que fusionnée le 21/10 (entrée 12 / 12 h / t 1,0 ; 70 % ; essai 50 % → 30)."""
    ok = {}
    for name, s in st.items():
        age = (now - s["start"]).total_seconds() / 3600 if s["start"] else 0
        if (s["n"] >= 12 and age >= 12 and s["growth"] >= 0.02 and s["t"] >= 1.0) or (
                name in held and s["growth"] > 0 and s["t"] >= 0):
            ok[name] = s
    best = sorted(ok, key=lambda k: -ok[k]["growth"])[:5]
    total = sum(ok[k]["growth"] for k in best)
    out = {}
    for k in best if total > 0 else []:
        s = ok[k]
        w = (0.5 / len(best) + 0.5 * s["growth"] / total) * min(1.0, max(0.5, s["n"] / 30))
        if s["day_conf"] < 0.8:
            w *= 0.5
        out[k] = min(w, 0.7)
    return out


def run(ghosts: dict, sizing: str, k: int = 30) -> dict:
    first = min(g["start"] for g in ghosts.values() if g["start"])
    end = max(t["close"] for g in ghosts.values() for t in g["trades"])
    now = first.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    held, pnl, peak, worst, days = set(), 0.0, 0.0, 0.0, defaultdict(float)
    while now <= end:
        st = {}
        for n, g in ghosts.items():
            past = [t for t in g["trades"] if t["close"] <= now]
            if past:
                st[n] = dict(stats(past), start=g["start"])
        sh = shares(st, held, now)
        held = set(sh)
        for n, w in sh.items():
            for t in ghosts[n]["trades"]:
                if not now <= t["open"] < now + timedelta(hours=1):
                    continue
                scale = 1.0
                if sizing == "demi":
                    scale = 0.5
                elif sizing == "mesuree":
                    edge = st[n]["excess"] / (st[n]["n"] + k)
                    scale = min(1.0, max(0.0, edge / t["assumed"]))
                gain = w * scale * t["pnl"]
                pnl += gain
                days[t["close"].date()] += gain
        peak = max(peak, pnl)
        worst = min(worst, pnl - peak)
        now += timedelta(hours=1)
    return {"pnl": pnl, "worst": worst, "days": dict(days)}


def main() -> int:
    for label, skip in (("semaine réelle (15-21/10)", None), ("la même sans le 18/10", "2026-10-18")):
        ghosts = load(skip)
        print(f"\n{label}")
        for name, sizing, k in (("mises actuelles", "actuelle", 0), ("demi-mises", "demi", 0),
                                ("mises sur l'avantage mesuré (k 30)", "mesuree", 30),
                                ("mises sur l'avantage mesuré (k 60)", "mesuree", 60)):
            r = run(ghosts, sizing, k)
            bad = min(r["days"].values()) if r["days"] else 0.0
            print(f"  {name:38s} {r['pnl']:+6.0f} €   pire repli {r['worst']:+5.0f} €   pire jour {bad:+5.0f} €")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
