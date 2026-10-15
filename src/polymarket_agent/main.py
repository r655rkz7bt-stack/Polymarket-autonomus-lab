"""Un cycle complet de simulation (ARCHITECTURE.md §2).

journal → faillite ? → règlements → scanner → carnets → historique de prix →
stratégies → contrôleur → relecture du carnet → simulation → journal → battement de cœur.

Arène (décision d'Etienne, 15/10/2026) :
  - chaque stratégie active trade dans son propre portefeuille FANTÔME (`ledger/fantome/`,
    1 000 virtuels, vrais carnets) : c'est sa note en conditions réelles ;
  - le portefeuille PRINCIPAL (règle « à 0 € tu meurs ») suit les décisions du CHAMPION,
    choisi automatiquement par `arena.py` (aucun champion = ne rien faire) ;
  - chaque palier franchi (cliquet ×1,5) est inscrit dans le journal signé.
"""

from __future__ import annotations

import dataclasses
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from pathlib import Path
from typing import Callable

from polymarket_agent.arena import run_arena
from polymarket_agent.correlation import correlation_group
from polymarket_agent.execution_simulator import simulate_buy, simulate_sell
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.ledger import Ledger, LedgerCorrupt, LedgerError, NotInitialized
from polymarket_agent.market_scanner import scan
from polymarket_agent.models import MarketInfo, OrderBook
from polymarket_agent.persistence import Database
from polymarket_agent.price_features import changes_in_window, price_at
from polymarket_agent.safety_controller import (MarketContext, RiskLimits, assert_simulation_mode,
                                                evaluate)
from polymarket_agent.settlement import settle_positions
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
    shadow_dir: Path | None = None  # dossier des journaux fantômes
    # Étape 5 : collecte des sources (None = pas de collecte, ex. dans les tests du pipeline).
    collector: Callable | None = None


@dataclass
class CycleReport:
    cycle_id: str
    status: str = "EN_COURS"
    exit_code: int = EXIT_OK
    counts: dict[str, int] = field(default_factory=dict)
    summary: dict[str, str] = field(default_factory=dict)
    shadows: dict[str, dict] = field(default_factory=dict)
    arena: dict = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)
    milestones: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)


@dataclass
class Portfolio:
    name: str
    ledger: Ledger
    strategies: list
    marks: dict[str, Decimal] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)


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
        correlation_group=correlation_group(market),
    )


def _open_shadows(deps: CycleDeps, report: CycleReport, now: datetime) -> list[Portfolio]:
    """Un journal par stratégie fantôme, créé à la première utilisation. Un journal fantôme
    illisible est ignoré (journalisé) : il ne bloque jamais le portefeuille principal."""
    shadows = []
    for strategy in deps.strategies:
        if deps.shadow_dir is None:
            continue
        name = competitor_name(strategy)
        path = deps.shadow_dir / f"{name}.jsonl"
        lock = deps.shadow_dir / f"{name}.BANKRUPT.lock"
        try:
            ledger = (Ledger.open(path, deps.key, lock) if path.exists()
                      else Ledger.create(path, deps.key, lock, deps.limits.initial_capital, now))
        except LedgerError as exc:
            report.messages.append(f"fantôme {name} ignoré : {exc}")
            log.error("journal fantôme %s inutilisable : %s", name, exc)
            continue
        shadows.append(Portfolio(f"fantome:{name}", ledger, [strategy]))
    return shadows


def competitor_name(strategy) -> str:
    return f"{strategy.strategy_id}_v{strategy.version}"


def run_cycle(deps: CycleDeps) -> CycleReport:
    started = deps.now()
    bucket = cycle_bucket(started, int(deps.settings["cycle"]["bucket_minutes"]))
    report = CycleReport(cycle_id=f"{bucket}-{started.strftime('%S%f')}")
    deps.db.start_cycle(report.cycle_id, started)
    assert_simulation_mode(deps.settings.get("mode"))

    # 1. Journal principal : vérification complète (signatures, chaîne, comptabilité).
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

    main = Portfolio("principal", ledger, [])  # stratégie fixée par l'arène (champion)
    portfolios = [main] + _open_shadows(deps, report, started)
    try:
        _trade(deps, portfolios, report, bucket)
    except LedgerError as exc:  # garde-fou : jamais d'état à moitié écrit
        report.status, report.exit_code = "ERREUR_JOURNAL", EXIT_ERROR
        report.messages.append(str(exc))
        log.error("erreur du journal : %s", exc)
    except Exception as exc:  # noqa: BLE001 - un cycle ne doit jamais planter sans trace
        report.status, report.exit_code = "ERREUR", EXIT_ERROR
        report.messages.append(f"{type(exc).__name__}: {exc}")
        log.exception("erreur inattendue pendant le cycle")

    finished = deps.now()
    for portfolio in portfolios:
        if not portfolio.ledger.state.bankrupt:
            for m in portfolio.ledger.record_milestones(finished):
                report.milestones.append(f"{portfolio.name} : palier {m['target']} en {m['seconds'] / 3600:.1f} h")
                log.info("PALIER %s atteint par %s", m["target"], portfolio.name)
        held = {t: m for t, m in portfolio.marks.items() if t in portfolio.ledger.state.positions}
        portfolio.ledger.heartbeat(report.cycle_id, report.status, finished,
                                   total_estimated=portfolio.ledger.state.total_estimated(held))
        if portfolio is not main:
            report.shadows[portfolio.name] = dict(portfolio.ledger.state.summary(held),
                                                  **portfolio.counts)
    deps.db.set_anchor(ledger.state.last_seq, ledger.state.last_hash, finished)
    report.summary = ledger.state.summary(
        {t: m for t, m in main.marks.items() if t in ledger.state.positions})
    report.counts.update(main.counts)
    deps.db.finish_cycle(report.cycle_id, finished, report.status, counts=report.counts,
                         summary=dict(report.summary, fantomes=report.shadows, sources=report.sources),
                         error="; ".join(report.messages) or None)
    deps.db.prune(float(deps.settings["database"]["max_megabytes"]))
    return report


def _halt(deps: CycleDeps, report: CycleReport, status: str, message: str) -> CycleReport:
    log.critical("ARRÊT %s : %s", status, message)
    report.status, report.exit_code = status, EXIT_HALT
    report.messages.append(message)
    deps.db.finish_cycle(report.cycle_id, deps.now(), status, error=message)
    return report


def _attach_price_features(deps: CycleDeps, watchlist: list[MarketInfo], now: datetime) -> None:
    """Prix de l'issue n°0 il y a 6 h et activité sur 24 h, calculés comme dans le backtest.
    Une erreur sur un marché le laisse sans caractéristiques (les stratégies s'abstiennent)."""
    ts = int(now.timestamp())
    for market in watchlist:
        if not market.token_ids:
            continue
        try:
            points = deps.clob.get_price_history(market.token_ids[0], ts - 31 * 3600, ts)
        except (SourceUnavailable, ValueError) as exc:
            log.warning("historique de prix indisponible pour %s : %s", market.market_id, exc)
            continue
        market.yes_price_6h_ago = price_at(points, ts - 6 * 3600)
        market.yes_price_1h_ago = price_at(points, ts - 3600)
        market.changes_24h = changes_in_window(points, ts)


def _trade(deps: CycleDeps, portfolios: list[Portfolio], report: CycleReport, bucket: str) -> None:
    """Corps du cycle. Le portefeuille principal en faillite arrête TOUT le trading."""
    main = portfolios[0]
    # 2. Règle n°1 : à 0 € tu meurs.
    if main.ledger.state.bankrupt:
        report.status = "FAILLITE"
        report.messages.append(main.ledger.state.bankrupt_reason)
        log.critical("FAILLITE : %s — aucun trading", main.ledger.state.bankrupt_reason)
        return

    # 3. Règlements : les marchés résolus libèrent le capital avant toute nouvelle entrée.
    for portfolio in portfolios:
        if portfolio.ledger.state.positions and not portfolio.ledger.state.bankrupt:
            settled = settle_positions(portfolio.ledger, deps.gamma, deps.now())
            portfolio.counts["settled"] = len(settled)
    if main.ledger.state.bankrupt:
        report.status = "FAILLITE"
        return

    # 3 bis. Arène : classement, promotion du champion, élimination hebdomadaire.
    competitors = {p.name.removeprefix("fantome:"): p for p in portfolios[1:]}
    report.arena = run_arena(main.ledger, {n: p.ledger for n, p in competitors.items()},
                             deps.settings["arena"], deps.now())
    for name, portfolio in competitors.items():
        if name in main.ledger.state.eliminated:
            portfolio.strategies = []  # éliminée : ne trade plus (ses positions se règlent)
    champion = main.ledger.state.champion
    main.strategies = [s for n, p in competitors.items() if n == champion for s in p.strategies]
    for event in report.arena.get("events", []):
        log.info("ARÈNE : %s", event)

    # 4. Scanner.
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

    # 4 bis. Marchés supplémentaires demandés par les stratégies (ex. échelles de seuils).
    eligible = [m for m in result.markets if m.eligible]
    known = {m.market_id for m in result.watchlist}
    max_extra = int(deps.settings["scanner"].get("max_extra_markets", 40))
    for strategy in {id(s): s for p in portfolios for s in p.strategies}.values():
        for market in getattr(strategy, "candidates", lambda ms: [])(eligible):
            if market.market_id not in known and max_extra > 0:
                result.watchlist.append(market)
                known.add(market.market_id)
                max_extra -= 1

    # 5. Carnets : les deux issues de chaque marché surveillé + positions détenues
    #    (tous portefeuilles) pour les prix de marque.
    wanted = [t for market in result.watchlist if len(market.token_ids) == 2 for t in market.token_ids]
    for portfolio in portfolios:
        wanted += [t for t in portfolio.ledger.state.positions if t not in wanted]
    try:
        books = deps.clob.get_books(wanted) if wanted else {}
    except (SourceUnavailable, ValueError) as exc:
        report.status = "DEGRADE"
        report.messages.append(f"carnets indisponibles : {exc}")
        log.warning("carnets indisponibles, cycle sans trading : %s", exc)
        return
    deps.db.save_books(report.cycle_id, books.values())
    for portfolio in portfolios:
        portfolio.marks.update({t: b.best_bid for t, b in books.items()
                                if t in portfolio.ledger.state.positions and b.best_bid is not None})

    # 6. Historique de prix récent (seulement si une stratégie active en a besoin).
    if any(getattr(s, "needs_price_history", False) for p in portfolios for s in p.strategies):
        _attach_price_features(deps, result.watchlist, now)

    # 6 bis. Sources d'information (étape 5). Une source en panne ne bloque rien (mode dégradé).
    if deps.collector is not None:
        try:
            report.sources = deps.collector(result.watchlist, now)
        except Exception as exc:  # noqa: BLE001 - la collecte ne doit jamais faire tomber le cycle
            report.sources = {"collecte": f"indisponible : {type(exc).__name__}: {exc}"[:200]}
            log.exception("collecte des sources en échec, cycle poursuivi sans elles")

    # 7-11. Stratégies → propositions → contrôleur → exécution simulée, portefeuille par portefeuille.
    for portfolio in portfolios:
        if portfolio.ledger.state.bankrupt:
            continue  # un fantôme en faillite ne trade plus (le principal est vérifié plus haut)
        _execute(deps, portfolio, result.watchlist, books, report, bucket, result.markets)
        if main.ledger.state.bankrupt:
            break
    report.status = "FAILLITE" if main.ledger.state.bankrupt else "OK"


def _execute(deps: CycleDeps, portfolio: Portfolio, watchlist: list[MarketInfo],
             books: dict[str, OrderBook], report: CycleReport, bucket: str,
             all_markets: list[MarketInfo] | None = None) -> None:
    ledger, marks = portfolio.ledger, portfolio.marks
    by_market = {m.market_id: m for m in (all_markets or [])} | {m.market_id: m for m in watchlist}
    proposals = []
    for strategy in portfolio.strategies:
        output = strategy.propose(watchlist, books, ledger.state, deps.limits, bucket, marks)
        # Sorties (ventes) : seulement sur les positions ouvertes par cette stratégie.
        if hasattr(strategy, "exits"):
            mine = {t: p for t, p in ledger.state.positions.items() if p.strategy_id == strategy.strategy_id}
            output.proposals += strategy.exits(mine, by_market, books, bucket, deps.now())
        if portfolio.name == "principal":
            # Identifiants distincts de ceux du fantôme du champion (même stratégie, autre journal).
            output.proposals = [dataclasses.replace(p, op_id="P" + p.op_id[:23]) for p in output.proposals]
        log.info("[%s] %s v%s : %d propositions, abstentions %s", portfolio.name,
                 strategy.strategy_id, strategy.version, len(output.proposals), output.abstentions)
        proposals += output.proposals
    accepted = fills = 0

    for proposal in proposals:
        market = by_market.get(proposal.market_id)
        if market is None:  # marché sorti du scan : on garde la position jusqu'au règlement
            continue
        verdict = evaluate(proposal, ledger.state, market_context(market, books.get(proposal.token_id),
                                                                  proposal.token_id),
                           deps.limits, deps.now(), marks)
        if not verdict.accepted:
            deps.db.save_decision(report.cycle_id, deps.now(), proposal, verdict)
            log.info("rejet %s : %s", proposal.op_id, verdict.reasons)
            continue

        # Relecture du carnet juste avant l'exécution, puis nouveau contrôle.
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
        if proposal.side == "SELL":
            fill = simulate_sell(fresh, proposal.shares, proposal.max_price, market.fees)
            if fill.executed:
                try:
                    ledger.record_sell(op_id=proposal.op_id, token_id=proposal.token_id,
                                       shares=fill.filled_shares,
                                       price=fill.avg_price.quantize(PRICE_QUANTUM, rounding=ROUND_DOWN),
                                       fee=fill.fee, now=deps.now(),
                                       extra={"cycle_id": report.cycle_id, "portfolio": portfolio.name,
                                              "strategy_id": proposal.strategy_id, "reason": proposal.invalidation,
                                              "fill_status": fill.status, "levels": fill.levels})
                    fills += 1
                    log.info("[%s] vente simulée %s : %s parts à %s, %s", portfolio.name, proposal.op_id,
                             fill.filled_shares, fill.avg_price, proposal.invalidation)
                except LedgerError as exc:
                    fill.status, fill.reason = "REFUSE_JOURNAL", str(exc)
            deps.db.save_decision(report.cycle_id, deps.now(), proposal, verdict, fill)
            continue
        fill = simulate_buy(fresh, proposal.shares, proposal.max_price, market.fees)
        if fill.executed:
            # Écriture signée. Le journal revérifie solde, doublon et faillite.
            try:
                ledger.record_buy(
                    op_id=proposal.op_id, token_id=proposal.token_id, market_id=proposal.market_id,
                    event_id=proposal.event_id, outcome=proposal.outcome,
                    shares=fill.filled_shares,
                    price=fill.avg_price.quantize(PRICE_QUANTUM, rounding=ROUND_UP),
                    fee=fill.fee, strategy_id=proposal.strategy_id,
                    strategy_version=proposal.strategy_version, now=deps.now(),
                    group=correlation_group(market),
                    extra={"cycle_id": report.cycle_id, "portfolio": portfolio.name,
                           "fill_status": fill.status, "levels": fill.levels,
                           "est_probability": str(proposal.est_probability),
                           "prob_low": str(proposal.prob_low), "prob_high": str(proposal.prob_high),
                           "net_edge": str(proposal.net_edge),
                           "horizon_hours": str(proposal.horizon_hours)})
                fills += 1
                log.info("[%s] exécution simulée %s : %s parts à %s (+%s de frais), %s", portfolio.name,
                         proposal.op_id, fill.filled_shares, fill.avg_price, fill.fee, fill.status)
            except LedgerError as exc:
                fill.status, fill.reason = "REFUSE_JOURNAL", str(exc)
                log.warning("le journal refuse %s : %s", proposal.op_id, exc)
        deps.db.save_decision(report.cycle_id, deps.now(), proposal, verdict, fill)
        if ledger.state.bankrupt:
            break
    portfolio.counts.update(proposals=len(proposals), accepted=accepted, fills=fills)
