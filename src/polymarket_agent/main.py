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
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from pathlib import Path
from typing import Callable

from polymarket_agent import strategy_health
from polymarket_agent.arena import run_arena
from polymarket_agent.correlation import correlation_group
from polymarket_agent.data_collector import _due
from polymarket_agent.execution_simulator import (simulate_buy, simulate_resting_buy,
                                                  simulate_resting_sell, simulate_sell)
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.ledger import Ledger, LedgerCorrupt, LedgerError, NotInitialized
from polymarket_agent.market_scanner import scan
from polymarket_agent.models import MarketInfo, OrderBook
from polymarket_agent.persistence import Database
from polymarket_agent.price_features import changes_in_window, price_at
from polymarket_agent.reporting import read_entries
from polymarket_agent.safety_controller import (MarketContext, Proposal, RiskLimits,
                                                assert_simulation_mode, evaluate)
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
    # Liquidité déjà prise par CE portefeuille pendant le cycle : {(jeton, sens): parts}. Chaque
    # fantôme est un scénario « et si cette stratégie tradait seule » : pas de partage entre eux.
    taken: dict = field(default_factory=dict)


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


class Weighted:
    """Une stratégie de l'arène vue par le capital principal : ses achats sont réduits à sa part
    du capital (somme des parts = 1). Ses ventes ne sont pas réduites : elles portent sur les
    parts que le principal détient réellement."""

    def __init__(self, strategy, weight: Decimal):
        self.inner, self.weight = strategy, weight
        self.strategy_id, self.version = strategy.strategy_id, strategy.version
        self.needs_price_history = getattr(strategy, "needs_price_history", False)
        if hasattr(strategy, "exits"):
            self.exits = strategy.exits

    def propose(self, *args, **kwargs):
        output = self.inner.propose(*args, **kwargs)
        output.proposals = self._scale(output.proposals)
        if getattr(output, "limit_orders", None):
            output.limit_orders = self._scale(output.limit_orders)
        return output

    def _scale(self, proposals: list) -> list:
        scaled = []
        for p in proposals:
            if p.side != "BUY":
                scaled.append(p)
                continue
            shares = (p.shares * self.weight).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            if shares > 0:
                scaled.append(dataclasses.replace(p, shares=shares))
        return scaled

    def __getattr__(self, name):
        return getattr(self.inner, name)


def competitor_name(strategy) -> str:
    return f"{strategy.strategy_id}_v{strategy.version}"


def run_cycle(deps: CycleDeps) -> CycleReport:
    started = deps.now()
    bucket = cycle_bucket(started, int(deps.settings["cycle"]["bucket_minutes"]))
    report = CycleReport(cycle_id=f"{bucket}-{started.strftime('%S%f')}")
    deps.db.start_cycle(report.cycle_id, started)
    if getattr(deps.db, "recovered_from", None):
        report.messages.append(f"base de données illisible mise de côté ({deps.db.recovered_from.name}), "
                               "base neuve créée ; ancrage anti-troncature perdu")
        log.critical("base de données illisible remplacée : %s", deps.db.recovered_from)
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


def _apply_health(deps: CycleDeps, competitors: dict, report: CycleReport, eliminated) -> set[str]:
    """Santé des stratégies (strategy_health.py) : prévisions jugées, mise prudente (achats réduits
    tant que rien n'est prouvé), suspension de celles qui ne gagnent pas leurs frais. Retourne
    les noms suspendus. Une erreur ici ne bloque jamais le cycle (les stratégies restent telles quelles)."""
    try:
        cfg = strategy_health.config(deps.settings)
        now = deps.now()
        items = {name: strategy_health.forecasts(read_entries(p.ledger)) for name, p in competitors.items()}
        if _due(deps.db, "bilan_previsions", 60, now):
            try:
                strategy_health.update_outcomes(deps.db, deps.gamma.get_market,
                                                [f for v in items.values() for f in v], now,
                                                int(cfg["outcomes_per_hour"]))
            except Exception as exc:  # noqa: BLE001 - une mesure ne bloque jamais le cycle
                log.warning("bilan des prévisions non mis à jour : %s", exc)
            deps.db.set_source_run("bilan_previsions", now)
        closed = {c["name"]: c["closed_trades"] for c in report.arena.get("classement", [])}
        suspended = set()
        for name, portfolio in competitors.items():
            sc = strategy_health.score(deps.db, items[name])
            factor = strategy_health.prudence(sc, cfg)
            reason = None if name in eliminated else strategy_health.suspension(
                portfolio.ledger.state, closed.get(name, 0), cfg)
            if reason:
                suspended.add(name)
                factor = 0.0
                log.info("SUSPENDUE %s : %s", name, reason)
            strategy_health.save(deps.db, name, dict(sc, prudence=factor, suspendue=reason))
            portfolio.strategies = [Weighted(s, Decimal(str(factor))) for s in portfolio.strategies]
        return suspended
    except Exception as exc:  # noqa: BLE001
        log.exception("santé des stratégies indisponible : %s", exc)
        return set()


def _halt(deps: CycleDeps, report: CycleReport, status: str, message: str) -> CycleReport:
    log.critical("ARRÊT %s : %s", status, message)
    report.status, report.exit_code = status, EXIT_HALT
    report.messages.append(message)
    deps.db.finish_cycle(report.cycle_id, deps.now(), status, error=message)
    return report


PRICE_FEATURES_MAX_AGE = 20 * 60   # secondes : au-delà, l'historique d'un marché est relu
PRICE_FEATURES_PER_CYCLE = 40      # relectures au plus par cycle (150 marchés suivis)


def _attach_price_features(deps: CycleDeps, watchlist: list[MarketInfo], now: datetime) -> None:
    """Prix de l'issue n°0 il y a 6 h et 1 h, et activité sur 24 h, calculés comme dans le
    backtest. Avec 150 marchés suivis, l'historique de chaque marché est gardé en base et relu
    au plus toutes les 20 minutes (les plus anciens d'abord). Une erreur laisse le marché sans
    caractéristiques : les stratégies qui en ont besoin s'abstiennent."""
    ts = int(now.timestamp())
    cached = {}
    for market in watchlist:
        if market.token_ids:
            raw = deps.db.get_value(f"prix:{market.token_ids[0]}")
            cached[market.market_id] = json.loads(raw) if raw else None
    stale = sorted((m for m in watchlist if m.token_ids),
                   key=lambda m: (cached[m.market_id] or {}).get("ts", 0))
    budget = PRICE_FEATURES_PER_CYCLE
    for market in stale:
        entry = cached[market.market_id]
        if (entry is None or ts - entry.get("ts", 0) > PRICE_FEATURES_MAX_AGE) and budget > 0:
            budget -= 1
            try:
                points = deps.clob.get_price_history(market.token_ids[0], ts - 31 * 3600, ts)
            except (SourceUnavailable, ValueError) as exc:
                log.warning("historique de prix indisponible pour %s : %s", market.market_id, exc)
                continue
            entry = {"ts": ts, "p6": _f(price_at(points, ts - 6 * 3600)),
                     "p1": _f(price_at(points, ts - 3600)), "changes": changes_in_window(points, ts)}
            deps.db.set_value(f"prix:{market.token_ids[0]}", json.dumps(entry))
        if entry is None:
            continue
        market.yes_price_6h_ago = entry["p6"]
        market.yes_price_1h_ago = entry["p1"]
        market.changes_24h = entry["changes"]


def _f(value):
    return None if value is None else float(value)


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
    suspended = _apply_health(deps, competitors, report, main.ledger.state.eliminated)
    # Le capital principal suit les meilleures stratégies, chacune pour sa part (arena.allocation).
    shares = {n: w for n, w in report.arena.get("allocation", {}).items() if n not in suspended}
    total_w = sum(shares.values())
    shares = {n: w / total_w for n, w in shares.items()} if total_w > 0 else {}
    champion = main.ledger.state.champion
    if not shares and champion and champion not in main.ledger.state.eliminated:
        shares = {champion: 1.0}  # champion en titre sans part calculée : il garde tout le capital
    main.strategies = [Weighted(s, Decimal(str(round(w, 6)))) for n, p in competitors.items()
                       if n in shares for w in [shares[n]] for s in p.strategies]
    # Positions orphelines : une stratégie retirée du capital principal (champion destitué, part
    # nulle) garde la main sur SES sorties (prise de bénéfice, stop, durée maximale), sans racheter.
    held = {pos.strategy_id for pos in main.ledger.state.positions.values()}
    active = {s.strategy_id for s in main.strategies}
    main.strategies += [Weighted(s, Decimal("0")) for s in deps.strategies
                        if hasattr(s, "exits") and s.strategy_id in held and s.strategy_id not in active]
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
    wanted += [o["token_id"] for o in deps.db.open_orders() if o["token_id"] not in wanted]
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

    # 5 bis. Ordres à cours limité posés aux cycles précédents : exécutés avec ces carnets
    #        (relus APRÈS leur pose) si le marché est passé au travers de leur prix.
    by_market = {m.market_id: m for m in result.markets} | {m.market_id: m for m in result.watchlist}
    for portfolio in portfolios:
        if not portfolio.ledger.state.bankrupt:
            _fill_resting(deps, portfolio, by_market, books, report, now)
        if main.ledger.state.bankrupt:
            report.status = "FAILLITE"
            return

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
        limit_orders = list(getattr(output, "limit_orders", []))
        if portfolio.name == "principal":
            # Identifiants distincts de ceux du fantôme du champion (même stratégie, autre journal).
            output.proposals = [dataclasses.replace(p, op_id="P" + p.op_id[:23]) for p in output.proposals]
            limit_orders = [dataclasses.replace(p, op_id="P" + p.op_id[:23]) for p in limit_orders]
        log.info("[%s] %s v%s : %d propositions, %d ordres à poser, abstentions %s", portfolio.name,
                 strategy.strategy_id, strategy.version, len(output.proposals), len(limit_orders),
                 output.abstentions)
        proposals += output.proposals
        proposals += _place_resting(deps, portfolio, limit_orders, by_market, report)
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
            key = (proposal.token_id, "SELL")
            fill = simulate_sell(fresh, proposal.shares, proposal.max_price, market.fees,
                                 portfolio.taken.get(key, Decimal("0")))
            if fill.executed:
                portfolio.taken[key] = portfolio.taken.get(key, Decimal("0")) + fill.filled_shares
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
        key = (proposal.token_id, "BUY")
        fill = simulate_buy(fresh, proposal.shares, proposal.max_price, market.fees,
                            portfolio.taken.get(key, Decimal("0")))
        if fill.executed:
            portfolio.taken[key] = portfolio.taken.get(key, Decimal("0")) + fill.filled_shares
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


# --------------------------------------------------------------------------- ordres posés

def _place_resting(deps: CycleDeps, portfolio: Portfolio, orders: list[Proposal],
                   by_market: dict[str, MarketInfo], report: CycleReport) -> list[Proposal]:
    """Pose les ordres à cours limité (base de données, pas d'argent). Un ordre déjà exécutable
    (achat >= meilleur vendeur, vente <= meilleur acheteur) est renvoyé pour le circuit taker
    habituel : il serait exécuté tout de suite sur le vrai marché."""
    cfg = deps.settings.get("limit_orders", {})
    max_open = int(cfg.get("max_open_per_portfolio", 30))
    max_age = float(cfg.get("max_age_hours", 6))
    ledger, now = portfolio.ledger, deps.now()
    open_orders = deps.db.open_orders(portfolio.name)
    marketable = []
    for order in orders:
        market = by_market.get(order.market_id)
        if market is None:
            continue
        try:  # carnet relu au moment de la pose (celui du début du cycle peut avoir vieilli)
            book = deps.clob.get_book(order.token_id)
        except (SourceUnavailable, ValueError) as exc:
            log.info("[%s] ordre non posé %s : carnet non relu (%s)", portfolio.name, order.op_id, exc)
            continue
        if book is not None and ((order.side == "BUY" and book.best_ask is not None
                                  and order.max_price >= book.best_ask)
                                 or (order.side == "SELL" and book.best_bid is not None
                                     and order.max_price <= book.best_bid)):
            marketable.append(order)
            continue
        verdict = evaluate(order, ledger.state, market_context(market, book, order.token_id),
                           deps.limits, now, portfolio.marks)
        others = [o for o in open_orders if not (o["token_id"] == order.token_id and o["side"] == order.side)]
        if verdict.accepted and len(others) >= max_open:
            verdict.accepted = False
            verdict.reasons.append(f"trop d'ordres posés ({max_open} au plus)")
        if verdict.accepted and order.side == "BUY":
            # Réservation : les achats posés ne peuvent pas promettre plus que le solde disponible.
            reserved = sum((Decimal(o["remaining"]) * Decimal(json.loads(o["proposal"])["max_price"])
                            for o in others if o["side"] == "BUY"), Decimal("0"))
            if reserved + Decimal(verdict.checks.get("cost_bound", "0")) > ledger.state.cash:
                verdict.accepted = False
                verdict.reasons.append(f"solde déjà réservé par les ordres posés ({reserved:.2f})")
        verdict.checks["order_type"] = "limite"
        if verdict.accepted:
            hours = min(max(float(order.horizon_hours), 0.0), max_age)
            if deps.db.add_pending_order(portfolio.name, order, now, now + timedelta(hours=hours)):
                portfolio.counts["orders_placed"] = portfolio.counts.get("orders_placed", 0) + 1
                open_orders = deps.db.open_orders(portfolio.name)
                log.info("[%s] ordre posé %s : %s %s parts à %s", portfolio.name, order.op_id,
                         order.side, order.shares, order.max_price)
        deps.db.save_decision(report.cycle_id, now, order, verdict)
    return marketable


def _fill_resting(deps: CycleDeps, portfolio: Portfolio, by_market: dict[str, MarketInfo],
                  books: dict[str, OrderBook], report: CycleReport, now: datetime) -> None:
    """Exécute les ordres posés dont le prix a été traversé (execution_simulator, règle prudente).
    Chaque exécution repasse par le contrôleur et le journal, comme un ordre taker."""
    ledger = portfolio.ledger
    consumed = portfolio.taken  # partagé avec les ordres taker du même portefeuille pendant le cycle
    for order in deps.db.open_orders(portfolio.name):
        proposal = Proposal.from_dict(json.loads(order["proposal"]))
        remaining, n = Decimal(order["remaining"]), int(order["fills"])
        while f"{proposal.op_id}-L{n + 1}" in ledger.state.op_ids:
            n += 1  # exécution déjà au journal (cycle interrompu avant la mise à jour de la base)

        def close(status: str) -> None:
            deps.db.update_order(order["op_id"], remaining=remaining, fills=n, status=status, now=now)

        if now >= datetime.fromisoformat(order["expires_at"]):
            close("EXPIRE")
            continue
        if portfolio.name != "principal" and not portfolio.strategies:
            close("ANNULE")  # stratégie éliminée
            continue
        market, book = by_market.get(proposal.market_id), books.get(proposal.token_id)
        if market is not None and (market.closed or not market.active or not market.accepting_orders):
            close("ANNULE")
            continue
        if market is None or book is None or book.fetched_at <= datetime.fromisoformat(order["created_at"]):
            continue  # pas de carnet relu après la pose : on attend
        shares = remaining
        if proposal.side == "SELL":
            position = ledger.state.positions.get(proposal.token_id)
            if position is None:
                close("ANNULE")
                continue
            shares = min(shares, position.shares)
        simulate = simulate_resting_buy if proposal.side == "BUY" else simulate_resting_sell
        key = (proposal.token_id, proposal.side)
        fill = simulate(book, shares, proposal.max_price, market.fees, consumed.get(key, Decimal("0")))
        if not fill.executed:
            continue
        part = dataclasses.replace(proposal, op_id=f"{proposal.op_id}-L{n + 1}", shares=fill.filled_shares)
        verdict = evaluate(part, ledger.state, market_context(market, book, part.token_id),
                           deps.limits, now, portfolio.marks)
        verdict.checks["order_type"] = "limite"
        if not verdict.accepted:
            deps.db.save_decision(report.cycle_id, now, part, verdict, fill)
            log.info("[%s] exécution d'ordre posé refusée %s : %s", portfolio.name, part.op_id, verdict.reasons)
            continue
        extra = {"cycle_id": report.cycle_id, "portfolio": portfolio.name, "order_type": "limite",
                 "resting_order": proposal.op_id, "fill_status": fill.status, "levels": fill.levels}
        try:
            if proposal.side == "BUY":
                ledger.record_buy(
                    op_id=part.op_id, token_id=part.token_id, market_id=part.market_id,
                    event_id=part.event_id, outcome=part.outcome, shares=fill.filled_shares,
                    price=proposal.max_price, fee=fill.fee, strategy_id=part.strategy_id,
                    strategy_version=part.strategy_version, now=now, group=correlation_group(market),
                    extra=dict(extra, est_probability=str(part.est_probability), prob_low=str(part.prob_low),
                               prob_high=str(part.prob_high), net_edge=str(part.net_edge),
                               horizon_hours=str(part.horizon_hours)))
            else:
                ledger.record_sell(op_id=part.op_id, token_id=part.token_id, shares=fill.filled_shares,
                                   price=proposal.max_price, fee=fill.fee, now=now,
                                   extra=dict(extra, strategy_id=part.strategy_id, reason=part.invalidation))
        except LedgerError as exc:
            fill.status, fill.reason = "REFUSE_JOURNAL", str(exc)
            deps.db.save_decision(report.cycle_id, now, part, verdict, fill)
            log.warning("le journal refuse %s : %s", part.op_id, exc)
            continue
        consumed[key] = consumed.get(key, Decimal("0")) + fill.filled_shares
        remaining, n = remaining - fill.filled_shares, n + 1
        close("EXECUTE" if remaining <= 0 else "OUVERT")
        portfolio.counts["resting_fills"] = portfolio.counts.get("resting_fills", 0) + 1
        deps.db.save_decision(report.cycle_id, now, part, verdict, fill)
        log.info("[%s] ordre posé exécuté %s : %s parts à %s (+%s de frais)", portfolio.name, part.op_id,
                 fill.filled_shares, proposal.max_price, fill.fee)
        if ledger.state.bankrupt:
            break
