"""Construit (ou complète) l'historique des marchés résolus.

Étape 1 : catalogue des marchés résolus, jour par jour (Gamma /events/keyset).
Étape 2 : série de prix horaire sur 72 h pour chacun (CLOB /prices-history).
Étape 3 : export compact dans data/history/markets_AAAA-MM.jsonl.gz (versionné).

Reprenable : le cache state/history_cache.sqlite garde ce qui est déjà récupéré.

Usage : python scripts/build_history.py --start 2026-04-01 --end 2026-10-13
"""

from __future__ import annotations

import argparse
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

from _common import ROOT, load_settings, setup_logging

from polymarket_agent.history import HistoryStore, collect_day, export_monthly, fetch_points
from polymarket_agent.http_client import HttpClient, SourceUnavailable

log = logging.getLogger("build_history")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="premier jour d'échéance (AAAA-MM-JJ)")
    parser.add_argument("--end", required=True, help="dernier jour d'échéance (inclus)")
    parser.add_argument("--min-volume", type=float, default=5000)
    parser.add_argument("--threads", type=int, default=6)
    parser.add_argument("--export-only", action="store_true")
    args = parser.parse_args()
    settings = load_settings()
    setup_logging(settings)
    http_cfg, src = settings["http"], settings["sources"]
    gamma_url = src["polymarket_gamma"]["base_url"]
    clob_url = src["polymarket_clob"]["base_url"]

    def client() -> HttpClient:
        return HttpClient(timeout=http_cfg["timeout_seconds"], max_retries=4, backoff=2.0,
                          min_interval=0.2, user_agent=http_cfg["user_agent"])

    store = HistoryStore(ROOT / "state" / "history_cache.sqlite")
    if not args.export_only:
        http = client()
        day = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
        last = datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc)
        while day <= last:
            key = day.strftime("%Y-%m-%d")
            if not store.day_done(key):
                try:
                    metas = collect_day(http, gamma_url, day, args.min_volume)
                    store.save_day(key, metas)
                    log.info("catalogue %s : %d marchés résolus retenus", key, len(metas))
                except (SourceUnavailable, ValueError) as exc:
                    log.warning("catalogue %s : échec (%s), sera repris au prochain lancement", key, exc)
            day += timedelta(days=1)

        todo = store.missing_histories()
        log.info("historiques à récupérer : %d", len(todo))
        local = threading.local()
        lock = threading.Lock()

        def work(meta):
            if not hasattr(local, "http"):
                local.http = client()
            return meta["id"], fetch_points(local.http, clob_url, meta)

        done, failed, started = 0, 0, time.time()
        with ThreadPoolExecutor(max_workers=args.threads) as pool:
            futures = [pool.submit(work, m) for m in todo]
            for future in as_completed(futures):
                try:
                    market_id, points = future.result()
                except (SourceUnavailable, ValueError) as exc:
                    failed += 1
                    log.warning("historique : échec (%s)", exc)
                    continue
                with lock:
                    store.save_history(market_id, points)
                    done += 1
                    if done % 500 == 0:
                        store.commit()
                        rate = done / (time.time() - started)
                        log.info("historiques : %d/%d (%.0f/s), %d échecs", done, len(todo), rate, failed)
        store.commit()
    counts = export_monthly(store, ROOT / "data" / "history")
    log.info("export : %s (total %d marchés avec historique)", counts, sum(counts.values()))
    store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
