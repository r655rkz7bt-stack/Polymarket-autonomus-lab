"""L'entonnoir 80/20 avant et après le recentrage du 27/10/2026 (experiments/audace.md) : filles proposées sur les journaux
publiés, sans les étiquettes de marchés de la base (discipline et type de pari inconnus ici).

Usage : bash scripts/fetch_data.sh ; .venv/bin/python experiments/audace/entonnoir_avant_apres.py
"""

from __future__ import annotations

import glob
import json
from pathlib import Path

import yaml
from commun import ROOT

from polymarket_agent import pareto
from polymarket_agent.reporting import closed_trades


def main() -> None:
    entries = {Path(p).stem: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
               for p in sorted(glob.glob(str(ROOT / "published_data" / "ledger" / "fantome" / "*.jsonl")))}
    growth = {n: sum(float(t["pnl"]) for t in closed_trades(e)) / 1000 for n, e in entries.items()}
    configs = yaml.safe_load((ROOT / "config" / "strategies.yaml").read_text(encoding="utf-8"))
    mothers = {k: str(v.get("mere")) for k, v in configs.items() if isinstance(v, dict) and v.get("mere")}
    rules = yaml.safe_load((ROOT / "config" / "promotion.yaml").read_text(encoding="utf-8")).get("entonnoir") or {}
    for titre, kw in (("avant (morceau z ≥ 0)", {}),
                      ("après (promotion.yaml → entonnoir)", {"min_z": rules.get("z_morceau"), "z_strategy": rules.get("z_strategie")})):
        reports = pareto.analyse(entries, growth, mothers, {}, configs, **kw)
        todo = sorted((p for r in reports for p in r["filles"] if not p.get("existe")), key=lambda p: -p["pnl"])
        print(f"\n{titre} : {len(reports)} stratégies disséquées, {len(todo)} filles proposées")
        for p in todo[:8]:
            print(f"   {p['strategie']:34s} {p['morceau'][:44]:44s} {p['n']:3d} paris, {p['gagnes']} / {p['attendus']}, "
                  f"z {p['z']:+.2f}, {p['pnl']:+.0f} €")


if __name__ == "__main__":
    main()
