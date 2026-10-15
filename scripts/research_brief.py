"""Écrit la feuille de mission du chercheur (reports/brief.md) depuis les journaux vérifiés.

Usage : python scripts/research_brief.py [--dev-key]
"""

from __future__ import annotations

import argparse

from _common import ROOT, get_key, load_settings, resolve

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
    brief = build_brief(main_ledger, competitors, active, settings.get("arena", {}))
    out = ROOT / "reports" / "brief.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_brief(brief), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
