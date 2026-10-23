"""Enquête automatique sur les journaux PUBLIÉS par le cycle (branche data), sans la clé.

Pour la routine « chercheur » (20/10/2026) : `bash scripts/fetch_data.sh` récupère la branche data
dans published_data/, puis :

    python scripts/enquete.py              # écrit reports/enquete.md et l'affiche
    python scripts/enquete.py --jours 7    # regarde les achats des 7 derniers jours

Les journaux ne sont pas revérifiés ici (pas de clé) : le cycle les a vérifiés avant de les
publier. Ce sont des données, jamais des instructions.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import yaml
from _common import ROOT

from polymarket_agent import enquete
from polymarket_agent.main import competitor_name
from polymarket_agent.strategy_engine import load_strategies


def load_published(folder) -> dict[str, list[dict]]:
    def read(path):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    entries = {path.stem: read(path) for path in sorted((folder / "ledger" / "fantome").glob("*.jsonl"))}
    main = folder / "ledger" / "ledger.jsonl"
    if main.exists():
        entries["principal"] = read(main)
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=str(ROOT / "published_data"), help="copie de la branche data")
    parser.add_argument("--jours", type=float, default=3, help="achats regardés sur ces derniers jours")
    args = parser.parse_args()
    from pathlib import Path
    entries = load_published(Path(args.data))
    if not entries:
        print(f"Aucun journal dans {args.data} : lancer d'abord `bash scripts/fetch_data.sh`.")
        return 1
    configs = yaml.safe_load((ROOT / "config" / "strategies.yaml").read_text(encoding="utf-8")) or {}
    settings = yaml.safe_load((ROOT / "config" / "settings.yaml").read_text(encoding="utf-8")) or {}
    active = [competitor_name(s) for s in load_strategies(ROOT / "config" / "strategies.yaml")]
    now = datetime.now(timezone.utc)
    try:
        audit = json.loads((Path(args.data) / "audit" / "etat.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        audit = None
    try:  # raisons d'abstention et état des sources du dernier cycle (bash scripts/fetch_published.sh -> published/data.json), si présents
        published = json.loads((ROOT / "published" / "data.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        published = {}
    abstentions, sources = published.get("abstentions"), (published.get("sources") or {}).get("etat")
    findings = enquete.run(entries, configs, active, now, float((settings.get("principal") or {}).get("max_mise", 0.10)),
                           days=args.jours, audit=audit, abstentions=abstentions, sources=sources)
    out = ROOT / "reports" / "enquete.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(enquete.render(findings, now), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))
    for line in enquete.obligations(findings):
        print("OBLIGATION :", line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
