"""Crée le journal comptable (écriture GENESIS) et la base SQLite.

Refuse de s'exécuter si un journal, un verrou de faillite ou un ancrage existe déjà :
on ne peut pas recréer du capital en effaçant le journal.

Usage : python scripts/initialize.py [--dev-key]
"""

from __future__ import annotations

import argparse

from _common import ROOT, get_key, load_settings, resolve

from polymarket_agent.ledger import Ledger
from polymarket_agent.persistence import Database
from polymarket_agent.safety_controller import RiskLimits, assert_simulation_mode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dev-key", action="store_true", help="clé locale de développement")
    args = parser.parse_args()
    settings = load_settings()
    assert_simulation_mode(settings.get("mode"))
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    paths = settings["paths"]
    ledger_path, lock_path = resolve(ROOT, paths["ledger"]), resolve(ROOT, paths["bankruptcy_lock"])
    db = Database(resolve(ROOT, paths["database"]))
    if db.get_anchor() is not None:
        print("REFUS : la base contient l'ancrage d'un journal existant. "
              "Seul le workflow reset-capital peut repartir de zéro.")
        return 2
    key = get_key(args.dev_key)
    ledger = Ledger.create(ledger_path, key, lock_path, limits.initial_capital)
    db.set_anchor(ledger.state.last_seq, ledger.state.last_hash, ledger.state.last_ts)
    print(f"Journal créé : {ledger_path} — capital virtuel initial {limits.initial_capital}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
