"""Un cycle complet de simulation (ARCHITECTURE.md §2).

Étape 3 (prototype) : journal → faillite ? → scanner → carnets → stratégie →
contrôleur → relecture du carnet → simulation → journal → battement de cœur.
Les sources externes, les règlements et le tableau de bord arrivent aux étapes 4 à 7.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_UP
from pathlib import Path
from typing import Callable

from polymarket_agent.execution_simulator import simulate_buy
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.ledger import Ledger, LedgerCorrupt, LedgerError, NotInitialized
from polymarket_agent.market_scanner import scan
from polymarket_agent.models import MarketInfo, OrderBook
from polymarket_agent.persistence import Database
from polymarket_agent.safety_controller import (MarketContext, RiskLimits, assert_simulation_mode,
                                                evaluate)
from polymarket_agent.sources.polymarket_clob import ClobClient
from polymarket_agent.sources.polymarket_gamma import GammaClient

log = logging.getLogger(__name__)
PRICE_QUANTUM = Decimal("0.00000001")

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_HALT = 2  # journal corrompu ou absent : GitHub enverra un e-mail d'échec


@dataclass
class CycleDeps:
    settings: dict
    limits: RiskLimits
    strategies: list
    ledger_path: Path
    lock_path: Path
    key: bytes
    db: Database
    gamma: GammaClient
    clob: ClobClient
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)


@dataclass
class CycleReport:
    cycle_id: str
    status: str = "EN_COURS"
    exit_code: int = EXIT_OK
    counts: dict[str, int] = field(default_factory=dict)
    summary: dict[str, str] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)


def cycle_bucket(now: datetime, minutes: int) -> str:
    now = now.astimezone(timezone.utc)
    floored = now.replace(minute=now.minute - now.minute % minutes, second=0, microsecond=0)
    return floored.strftime("%Y%m%dT%H%MZ")


def market_context(market: MarketInfo, book: OrderBook | None, token_id: str) -> MarketContext:
    return MarketContext(
        token_id=token_id,
        active=market.active,
        closed=market.closed,
        accepting_orders=market.accepting_orders,
        data_ok=market.data_ok and book is not None and book.token_id == token_id,
        best_bid=book.best_bid if book else None,
        best_ask=book.best_ask if book else None,
        # Prudence : on retient le plus ancien des deux horodatages.
        book_time=(min(book.timestamp, book.fetched_at) if book and book.timestamp else None),
        fees_enabled=market.fees.enabled,
        fee_rate=market.fees.rate,
        fee_exponent=market.fees.exponent,
        min_order_size=max(market.min_order_size, book.min_order_size if book else Decimal("0")),
        issues=tuple(market.issues),
    )


def run_cycle(deps: CycleDeps) -> CycleReport:
    started = deps.now()
    bucket = cycle_bucket(started, int(deps.settings["cycle"]["bucket_minutes"]))
    report = CycleReport(cycle_id=f"{bucket}-{started.strftime('%S%f')}")
    deps.db.start_cycle(report.cycle_id, started)
    assert_simulation_mode(deps.settings.get("mode"))

    # 1. Journal : vérification complète (signatures, chaîne, comptabilité).
    try:
        ledger = Ledger.open(deps.ledger_path, deps.key, deps.lock_path)
    except NotInitialized as exc:
        return _halt(deps, report, "NON_INITIALISE", str(exc))
    except LedgerCorrupt as exc:
        return _halt(deps, report, "CORROMPU", str(exc))
    anchor = deps.db.get_anchor()
    if anchor is not None:
        seq, digest = anchor
        if seq > ledger.state.last_seq or ledger.hash_at(seq) != digest:
            return _halt(deps, report, "CORROMPU",
                         f"le journal ne contient plus l'écriture n°{seq} déjà vue : troncature ou remplacement")

    marks: dict[str, Decimal] = {}
    try:
        _trade(deps, ledger, report, bucket, marks)
    except LedgerError as exc:  # garde-fou : jamais d'état à moitié écrit
        report.status, report.exit_code = "ERREUR_JOURNAL", EXIT_ERROR
        report.messages.append(str(exc))
        log.error("erreur du journal : %s", exc)
    except Exception as exc:  # noqa: BLE001 - un cycle ne doit jamais planter sans trace
        report.status, report.exit_code = "ERREUR", EXIT_ERROR
        report.messages.append(f"{type(exc).__name__}: {exc}")
        log.exception("erreur inattendue pendant le cycle")

    finished = deps.now()
    ledger.heartbeat(report.cycle_id, report.status, finished)
    deps.db.set_anchor(ledger.state.last_seq, ledger.state.last_hash, finished)
    report.summary = ledger.state.summary(
        {t: m for t, m in marks.items() if t in ledger.state.positions})
    deps.db.finish_cycle(report.cycle_id, finished, report.status, counts=report.counts,
                         summary=report.summary, error="; ".join(report.messages) or None)
    deps.db.prune(float(deps.settings["database"]["max_megabytes"]))
    return report


def _halt(deps: CycleDeps, report: CycleReport, status: str, message: str) -> CycleReport:
    log.critical("ARRÊT %s : %s", status, message)
    report.status, report.exit_code = status, EXIT_HALT
    report.messages.append(message)
    deps.db.finish_cycle(report.cycle_id, deps.now(), status, error=message)
    return report


def _trade(deps: CycleDeps, ledger: Ledger, report: CycleReport, bucket: str,
           marks: dict[str, Decimal]) -> None:
    """Corps du cycle. Remplit `marks` (prix de marque = meilleur bid) au passage."""
    # 2. Règle n°1 : à 0 € tu meurs.
    if ledger.state.bankrupt:
        report.status = "FAILLITE"
        report.messages.append(ledger.state.bankrupt_reason)
        log.critical("FAILLITE : %s — aucun trading", ledger.state.bankrupt_reason)
        return

    # 3. Scanner.
    now = deps.now()
    try:
        result = scan(deps.gamma, now, deps.settings["scanner"])
    except (SourceUnavailable, ValueError) as exc:
        report.status = "DEGRADE"
        report.messages.append(f"scanner indisponible : {exc}")
        log.warning("scanner indisponible, cycle sans trading : %s", exc)
        return
    # Scan complet archivé toutes les N minutes ; sinon, seulement la liste de surveillance
    # (taille de la base : environ 10 Mo par jour au lieu de 35).
    full_every = int(deps.settings["scanner"].get("full_snapshot_every_minutes", 30))
    full = now.minute % full_every < int(deps.settings["cycle"]["bucket_minutes"])
    deps.db.save_markets(report.cycle_id, now, result.markets if full else result.watchlist)
    report.counts.update(markets=len(result.markets), watchlist=len(result.watchlist))

    # 4. Carnets : favori de chaque marché surveillé + positions détenues (prix de marque).
    wanted = []
    for market in result.watchlist:
        if len(market.outcome_prices) == 2:
            idx = 0 if market.outcome_prices[0] >= market.outcome_prices[1] else 1
            wanted.append(market.token_ids[idx])
    wanted += [t for t in ledger.state.positions if t not in wanted]
    try:
        books = deps.clob.get_books(wanted) if wanted else {}
    except (SourceUnavailable, ValueError) as exc:
        report.status = "DEGRADE"
        report.messages.append(f"carnets indisponibles : {exc}")
        log.warning("carnets indisponibles, cycle sans trading : %s", exc)
        return
    deps.db.save_books(report.cycle_id, books.values())
    marks.update({t: b.best_bid for t, b in books.items()
                  if t in ledger.state.positions and b.best_bid is not None})

    # 5-9. Stratégies → propositions → contrôleur.
    by_market = {m.market_id: m for m in result.watchlist}
    proposals = []
    for strategy in deps.strategies:
        output = strategy.propose(result.watchlist, books, ledger.state, deps.limits, bucket, marks)
        log.info("%s v%s : %d propositions, abstentions %s", strategy.strategy_id,
                 strategy.version, len(output.proposals), output.abstentions)
        proposals += output.proposals
    report.counts["proposals"] = len(proposals)
    accepted = fills = 0

    for proposal in proposals:
        market = by_market[proposal.market_id]
        verdict = evaluate(proposal, ledger.state, market_context(market, books.get(proposal.token_id),
                                                                  proposal.token_id),
                           deps.limits, deps.now(), marks)
        if not verdict.accepted:
            deps.db.save_decision(report.cycle_id, deps.now(), proposal, verdict)
            log.info("rejet %s : %s", proposal.op_id, verdict.reasons)
            continue

        # 10. Relecture du carnet juste avant l'exécution, puis nouveau contrôle.
        try:
            fresh = deps.clob.get_book(proposal.token_id)
        except (SourceUnavailable, ValueError) as exc:
            verdict.accepted = False
            verdict.reasons.append(f"carnet non relu : {exc}")
            deps.db.save_decision(report.cycle_id, deps.now(), proposal, verdict)
            continue
        verdict = evaluate(proposal, ledger.state, market_context(market, fresh, proposal.token_id),
                           deps.limits, deps.now(), marks)
        if not verdict.accepted:
            deps.db.save_decision(report.cycle_id, deps.now(), proposal, verdict)
            log.info("rejet après relecture %s : %s", proposal.op_id, verdict.reasons)
            continue
        accepted += 1
        fill = simulate_buy(fresh, proposal.shares, proposal.max_price, market.fees)
        if fill.executed:
            # 11. Écriture signée. Le journal revérifie solde, doublon et faillite.
            try:
                ledger.record_buy(
                    op_id=proposal.op_id, token_id=proposal.token_id, market_id=proposal.market_id,
                    event_id=proposal.event_id, outcome=proposal.outcome,
                    shares=fill.filled_shares,
                    price=fill.avg_price.quantize(PRICE_QUANTUM, rounding=ROUND_UP),
                    fee=fill.fee, strategy_id=proposal.strategy_id,
                    strategy_version=proposal.strategy_version, now=deps.now(),
                    extra={"cycle_id": report.cycle_id, "fill_status": fill.status,
                           "levels": fill.levels, "est_probability": str(proposal.est_probability)})
                fills += 1
                log.info("exécution simulée %s : %s parts à %s (+%s de frais), %s",
                         proposal.op_id, fill.filled_shares, fill.avg_price, fill.fee, fill.status)
            except LedgerError as exc:
                fill.status, fill.reason = "REFUSE_JOURNAL", str(exc)
                log.warning("le journal refuse %s : %s", proposal.op_id, exc)
        deps.db.save_decision(report.cycle_id, deps.now(), proposal, verdict, fill)
        if ledger.state.bankrupt:
            break

    report.counts.update(accepted=accepted, fills=fills)
    report.status = "FAILLITE" if ledger.state.bankrupt else "OK"
