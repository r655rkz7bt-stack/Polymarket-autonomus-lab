"""Budget de temps d'un passage du chercheur (config/chercheur.yaml, docs/ROUTINE_CHERCHEUR.md).

Usage : python scripts/budget_chercheur.py debut   → durée visée de ce passage (et note l'heure)
        python scripts/budget_chercheur.py fin     → ajoute le passage à experiments/budget_chercheur.csv
        python scripts/budget_chercheur.py etat    → état de la semaine, sans rien écrire
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from polymarket_agent import budget_chercheur as bc  # noqa: E402

CONFIG = ROOT / "config" / "chercheur.yaml"
LOG = ROOT / "experiments" / "budget_chercheur.csv"
STAMP = Path("/tmp/debut_passage_chercheur")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=["debut", "fin", "etat"])
    args = parser.parse_args()
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    now = datetime.now(timezone.utc)
    if args.action == "fin":
        try:
            start = datetime.fromisoformat(STAMP.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            print("Heure de début introuvable (lancer « debut » au début du passage) : rien n'est noté.")
            return 1
        minutes = bc.append_row(LOG, start, now)
        print(f"Passage noté : {minutes:.0f} min ({start:%H:%M} → {now:%H:%M} UTC) dans {LOG.relative_to(ROOT)}.")
        return 0
    info = bc.target(now, cfg, bc.read_rows(LOG))
    if args.action == "debut":
        STAMP.write_text(now.isoformat(timespec="seconds"), encoding="utf-8")
    print(info["texte"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
