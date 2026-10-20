"""Écrit la feuille de mission du chercheur (reports/brief.md) depuis les journaux vérifiés.

Usage : python scripts/research_brief.py [--dev-key]
"""

from __future__ import annotations

import argparse
import math

from _common import ROOT, get_key, load_settings_with_arena as load_settings, resolve

from polymarket_agent.brief import build_brief, render_brief
from polymarket_agent.ledger import Ledger
from polymarket_agent.main import competitor_name
from polymarket_agent.strategy_engine import load_strategies


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dev-key", action="store_true")
    args = parser.parse_args()
    settings = load_settings()
    paths = settings["paths"]
    key = get_key(args.dev_key)
    main_ledger = Ledger.open(resolve(ROOT, paths["ledger"]), key, resolve(ROOT, paths["bankruptcy_lock"]))
    shadow_dir = resolve(ROOT, paths["shadow_dir"])
    competitors = {}
    for path in sorted(shadow_dir.glob("*.jsonl")) if shadow_dir.exists() else []:
        competitors[path.stem] = Ledger.open(path, key, path.with_suffix(".BANKRUPT.lock"))
    active = [competitor_name(s) for s in load_strategies(ROOT / "config" / "strategies.yaml")]
    from polymarket_agent.learning_engine import analyze, categories_from_db
    from polymarket_agent.persistence import Database
    db = Database(resolve(ROOT, paths["database"]))
    try:
        learning = analyze(dict(competitors, principal=main_ledger), categories_from_db(db))
        reports = _pareto(competitors, main_ledger, db)
    finally:
        db.close()
    brief = build_brief(main_ledger, competitors, active, settings["arena"], learning=learning)
    from polymarket_agent import pareto
    brief["obligations"] += pareto.obligations(reports)
    out = ROOT / "reports" / "brief.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_brief(brief), encoding="utf-8")
    (ROOT / "reports" / "pareto.md").write_text(pareto.render(reports), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))
    return 0


def _pareto(competitors: dict, main_ledger, db) -> list[dict]:
    """Entonnoir 80/20 (pareto.py) de toutes les stratégies qui grandissent (20/10/2026)."""
    import yaml

    from polymarket_agent import pareto
    from polymarket_agent.arena import standing
    from polymarket_agent.reporting import read_entries
    configs = yaml.safe_load((ROOT / "config" / "strategies.yaml").read_text(encoding="utf-8")) or {}
    mothers = {k: str(v.get("mere")) for k, v in configs.items() if isinstance(v, dict) and v.get("mere")}
    growth = {n: standing(n, l, main_ledger.state.eliminated).log_growth for n, l in competitors.items()}
    growth = {n: math.exp(g) - 1 for n, g in growth.items() if g != float("-inf")}
    markets = pareto.market_labels(db)
    return pareto.analyse({n: read_entries(l) for n, l in competitors.items()}, growth, mothers, markets, configs)


if __name__ == "__main__":
    raise SystemExit(main())
