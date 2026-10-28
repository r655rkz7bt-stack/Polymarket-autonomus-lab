"""Réinitialisation manuelle du capital principal (workflow reset-capital, Etienne seul).

Fichier protégé et AUTONOME : il ne charge que du code protégé (ledger.py, safety_controller.py,
polymarket_agent/__init__.py) et la bibliothèque standard + PyYAML (requirements-noyau.txt).
Lancé avec `python -I`, il n'importe aucun fichier libre du dépôt : rien de modifiable par l'IA
ne s'exécute là où RESET_CODE est présent.

Les deux codes viennent de l'environnement, jamais de la ligne de commande : RESET_CODE (secret
de l'environnement GitHub `production`) et RESET_INPUT (le code tapé par Etienne). Aucun des deux
n'est jamais affiché. La comparaison à temps constant et l'écriture signée RESET sont faites
par ledger.py.

Usage : RESET_CODE=… RESET_INPUT=… LEDGER_KEY=… python -I scripts/reset_capital.py --reason "…"
Codes de sortie : 0 réinitialisé, 3 refusé, 2 journal illisible.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))  # en dernier : rien ne peut masquer la bibliothèque standard

from polymarket_agent.ledger import Ledger, LedgerError, ResetRefused, load_key_from_env  # noqa: E402
from polymarket_agent.safety_controller import RiskLimits  # noqa: E402

LEDGER = ROOT / "ledger" / "ledger.jsonl"
LOCK = ROOT / "ledger" / "BANKRUPT.lock"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reason", required=True, help="raison écrite, inscrite dans le journal")
    args = parser.parse_args()
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    try:
        ledger = Ledger.open(LEDGER, load_key_from_env(), LOCK)
    except LedgerError as exc:
        print(f"REFUS : journal illisible ({exc}). Aucune réinitialisation sur un journal douteux.")
        return 2
    try:
        record = ledger.reset(provided_code=os.environ.get("RESET_INPUT", ""),
                              expected_code=os.environ.get("RESET_CODE", ""),
                              reason=args.reason, initial_capital=limits.initial_capital)
    except ResetRefused as exc:
        print(f"REFUS : {exc}.")
        return 3
    print(f"Capital réinitialisé à {limits.initial_capital} (époque {ledger.state.epoch}, "
          f"écriture n°{record['seq']}). Raison : {args.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
