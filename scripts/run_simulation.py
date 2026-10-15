"""Lance un cycle de simulation (ou une boucle locale).

Usage :
  python scripts/run_simulation.py --once [--dev-key]
  python scripts/run_simulation.py --loop --interval 300 [--dev-key]

Codes de sortie : 0 = OK / dégradé / faillite ; 1 = erreur ; 2 = journal corrompu ou absent.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone

from _common import ROOT, get_key, load_settings, resolve, setup_logging

from polymarket_agent.http_client import HttpClient
from polymarket_agent.intel_pipeline import make_collector
from polymarket_agent.main import CycleDeps, run_cycle
from polymarket_agent.persistence import Database
from polymarket_agent.safety_controller import RiskLimits, assert_simulation_mode
from polymarket_agent.sources.polymarket_clob import ClobClient
from polymarket_agent.sources.polymarket_gamma import GammaClient
from polymarket_agent.strategy_engine import load_strategies

STALE_LOCK_SECONDS = 15 * 60


def acquire_lock(path) -> bool:
    """Un seul cycle à la fois, même en local."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and time.time() - path.stat().st_mtime > STALE_LOCK_SECONDS:
        path.unlink()
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    return True


def one_cycle(settings: dict, key: bytes) -> int:
    paths = settings["paths"]
    lock = resolve(ROOT, paths["cycle_lock"])
    if not acquire_lock(lock):
        print("Un autre cycle est en cours : abandon.")
        return 0
    try:
        http_cfg = settings["http"]
        http = HttpClient(timeout=http_cfg["timeout_seconds"], max_retries=http_cfg["max_retries"],
                          backoff=http_cfg["backoff_seconds"],
                          min_interval=http_cfg["min_interval_seconds"],
                          user_agent=http_cfg["user_agent"])
        src = settings["sources"]
        db = Database(resolve(ROOT, paths["database"]))
        try:
            deps = CycleDeps(
                settings=settings,
                limits=RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml"),
                strategies=load_strategies(ROOT / "config" / "strategies.yaml"),
                ledger_path=resolve(ROOT, paths["ledger"]),
                lock_path=resolve(ROOT, paths["bankruptcy_lock"]),
                shadow_dir=resolve(ROOT, paths["shadow_dir"]),
                key=key, db=db,
                gamma=GammaClient(http, src["polymarket_gamma"]["base_url"]),
                clob=ClobClient(http, src["polymarket_clob"]["base_url"],
                                batch_size=src["polymarket_clob"]["books_batch_size"]),
                collector=make_collector(settings, http, db),
            )
            report = run_cycle(deps)
        finally:
            db.close()
        print(json.dumps({"cycle": report.cycle_id, "statut": report.status,
                          "compteurs": report.counts, "capital": report.summary,
                          "fantomes": report.shadows, "sources": report.sources,
                          "arene": report.arena.get("events", []), "paliers": report.milestones,
                          "messages": report.messages},
                         ensure_ascii=False, indent=2))
        return report.exit_code
    finally:
        lock.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true", help="un seul cycle")
    mode.add_argument("--loop", action="store_true", help="boucle locale (Ctrl+C pour arrêter)")
    parser.add_argument("--interval", type=int, default=300, help="secondes entre deux cycles")
    parser.add_argument("--dev-key", action="store_true", help="clé locale de développement")
    args = parser.parse_args()
    settings = load_settings()
    assert_simulation_mode(settings.get("mode"))
    setup_logging(settings)
    key = get_key(args.dev_key)
    if args.once:
        return one_cycle(settings, key)
    while True:
        started = datetime.now(timezone.utc)
        code = one_cycle(settings, key)
        if code == 2:
            return code
        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        time.sleep(max(args.interval - elapsed, 5))


if __name__ == "__main__":
    raise SystemExit(main())
