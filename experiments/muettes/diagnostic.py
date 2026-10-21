"""Pourquoi des stratégies n'achètent jamais rien (demande d'Etienne, 21/10/2026 : « réveiller les muettes »).

Pour chaque stratégie, on compare les marchés qu'elle DEMANDE (`candidates`) :
- parmi ceux que le scanner de production rend exploitables (mêmes réglages, config/settings.yaml) ;
- parmi TOUS les marchés ouverts de Polymarket (jusqu'à 900 jours, sans filtre de liquidité).
Pour les candidats vus seulement dans le second cas, on dit quel filtre du scanner les écarte.
Puis, avec les carnets réels, combien de propositions chaque stratégie ferait (essai à blanc, rien
n'est exécuté ni écrit dans un journal).

Usage : python experiments/muettes/diagnostic.py [--pages 60] [--seulement nom1,nom2]
"""

from __future__ import annotations

import argparse
import collections
import copy
import json
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, "src")
from polymarket_agent.config import load_settings  # noqa: E402
from polymarket_agent.http_client import HttpClient  # noqa: E402
from polymarket_agent.ledger import Ledger  # noqa: E402
from polymarket_agent.safety_controller import RiskLimits  # noqa: E402
from polymarket_agent.market_scanner import classify, scan  # noqa: E402
from polymarket_agent.sources.polymarket_clob import ClobClient  # noqa: E402
from polymarket_agent.sources.polymarket_gamma import GammaClient, parse_market  # noqa: E402
from polymarket_agent.strategy_engine import load_strategies  # noqa: E402

OUT = Path("experiments/muettes/donnees")


def horizon(m, now) -> str:
    if m.end_date is None:
        return "sans échéance"
    d = (m.end_date - now).total_seconds() / 86400
    return "< 1 j" if d < 1 else "1-7 j" if d < 7 else "7-30 j" if d < 30 else "30-90 j" if d < 90 else "> 90 j"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=60)
    ap.add_argument("--seulement", default="")
    ap.add_argument("--references", action="store_true", help="rattacher les références externes (Kalshi, tweets…)")
    args = ap.parse_args()
    settings = load_settings()
    now = datetime.now(timezone.utc)
    http = HttpClient(timeout=40, min_interval=0.1)
    gamma = GammaClient(http, settings["sources"]["polymarket_gamma"]["base_url"])
    import time
    t0 = time.time()
    prod = scan(gamma, now, settings["scanner"])
    print(f"scan de production : {time.time() - t0:.1f} s")
    live = [m for m in prod.markets if m.eligible and not m.ended]
    # Gamma refuse un décalage au-delà de 2 000 (vérifié le 21/10/2026) : on découpe l'univers par tranches d'échéance.
    raw = []
    for lo, hi in ((timedelta(minutes=30), timedelta(days=1)), (timedelta(days=1), timedelta(days=7)),
                   (timedelta(days=7), timedelta(days=30)), (timedelta(days=30), timedelta(days=90)),
                   (timedelta(days=90), timedelta(days=900))):
        try:
            raw += gamma.list_markets(end_min=now + lo, end_max=now + hi, page_size=100, max_pages=min(args.pages, 20))
        except Exception as exc:  # noqa: BLE001 - une tranche en panne : on continue avec les autres
            print("tranche", lo, hi, "illisible :", exc)
    seen, universe = set(), []
    for item in raw:
        m = parse_market(item)
        if m.market_id in seen:
            continue
        seen.add(m.market_id)
        m.exclusion = classify(m, now, settings["scanner"])
        universe.append(m)
    every = []
    for m in universe:  # tous rendus « exploitables » pour voir ce que la stratégie voudrait
        c = copy.copy(m)
        c.eligible = True
        every.append(c)
    print(f"production : {len(prod.markets)} marchés scannés, {len(live)} exploitables ; "
          f"univers : {len(universe)} marchés ouverts lus ({args.pages} pages)")
    print("filtres du scanner sur l'univers :", dict(collections.Counter(m.exclusion or "exploitable" for m in universe)))
    if args.references:  # comme le cycle : références rattachées à tous les marchés (base temporaire)
        import tempfile
        from polymarket_agent import references
        from polymarket_agent.persistence import Database
        db = Database(Path(tempfile.mkdtemp()) / "diag.sqlite")
        print("références (production) :", references.attach_all(live, db, now))
        print("références (univers) :", references.attach_all(every, db, now))
    strategies = load_strategies(Path("config/strategies.yaml"))
    only = {s for s in args.seulement.split(",") if s}
    clob = ClobClient(http, settings["sources"]["polymarket_clob"]["base_url"])
    report = {}
    for s in strategies:
        if only and s.strategy_id not in only:
            continue
        if not hasattr(s, "candidates"):
            continue
        try:
            a = s.candidates(live)
            b = s.candidates(every)
        except Exception as exc:  # noqa: BLE001 - diagnostic : on note et on continue
            report[s.strategy_id] = {"erreur": f"{type(exc).__name__}: {exc}"[:160]}
            continue
        ids_a = {m.market_id for m in a}
        extra = [m for m in b if m.market_id not in ids_a]
        report[s.strategy_id] = {
            "candidats_production": len(a), "candidats_univers": len(b),
            "ecartes_par": dict(collections.Counter(next((u.exclusion for u in universe if u.market_id == m.market_id), "?")
                                                    or "exploitable" for m in extra)),
            "horizon_univers": dict(collections.Counter(horizon(m, now) for m in b)),
            "exemples": [m.question[:90] for m in b[:3]]}
    # Essai à blanc avec carnets réels : sur les candidats de l'univers (au plus 40 par stratégie).
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    state = Ledger.create(tmp / "essai.jsonl", b"essai-a-blanc-sans-valeur-0123456789abcdef", tmp / "essai.lock", "1000", now=now).state
    limits = RiskLimits.from_file(Path("config/risk_limits.yaml"))
    if state is not None:
        for s in strategies:
            r = report.get(s.strategy_id)
            if not r or "erreur" in r or not r["candidats_univers"]:
                continue
            cands = s.candidates(every)[:40]
            tokens = [t for m in cands for t in m.token_ids]
            try:
                books = clob.get_books(tokens)
            except Exception as exc:  # noqa: BLE001
                r["essai"] = f"carnets indisponibles : {exc}"[:120]
                continue
            try:
                out = s.propose(cands, books, state, limits, "diag", {})
                r["propositions_essai"] = len(out.proposals) + len(getattr(out, "limit_orders", []) or [])
                r["raisons_essai"] = dict(out.abstentions)
            except Exception as exc:  # noqa: BLE001
                r["essai"] = f"{type(exc).__name__}: {exc}"[:160]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"diagnostic_{now:%Y%m%dT%H%M}.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    for name, r in sorted(report.items()):
        print(name, json.dumps(r, ensure_ascii=False)[:400])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
