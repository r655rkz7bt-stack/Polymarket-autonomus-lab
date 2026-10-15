"""Réinitialisation manuelle du capital principal (workflow reset-capital, Etienne seul).

Les deux codes viennent de l'environnement, jamais de la ligne de commande (qui peut être
journalisée) : RESET_CODE (secret de l'environnement GitHub `production`) et RESET_INPUT
(le code tapé par Etienne au lancement du workflow). Aucun des deux n'est jamais affiché.
La comparaison à temps constant et l'écriture signée RESET sont faites par ledger.py (protégé).

Usage : RESET_CODE=… RESET_INPUT=… python scripts/reset_capital.py --reason "…" [--dev-key]
Codes de sortie : 0 réinitialisé, 3 refusé, 2 journal illisible.
"""

from __future__ import annotations

import argparse
import os

from _common import ROOT, get_key, load_settings, resolve

from polymarket_agent.ledger import Ledger, LedgerError, ResetRefused
from polymarket_agent.persistence import Database
from polymarket_agent.safety_controller import RiskLimits, assert_simulation_mode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reason", required=True, help="raison écrite, inscrite dans le journal")
    parser.add_argument("--dev-key", action="store_true", help="clé locale de développement")
    args = parser.parse_args()
    settings = load_settings()
    assert_simulation_mode(settings.get("mode"))
    paths = settings["paths"]
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    try:
        ledger = Ledger.open(resolve(ROOT, paths["ledger"]), get_key(args.dev_key),
                             resolve(ROOT, paths["bankruptcy_lock"]))
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
    db = Database(resolve(ROOT, paths["database"]))
    try:
        db.set_anchor(ledger.state.last_seq, ledger.state.last_hash, ledger.state.last_ts)
    finally:
        db.close()
    print(f"Capital réinitialisé à {limits.initial_capital} (époque {ledger.state.epoch}, "
          f"écriture n°{record['seq']}). Raison : {args.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
