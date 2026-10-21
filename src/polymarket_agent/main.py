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
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from pathlib import Path
from typing import Callable

from polymarket_agent import strategy_health
from polymarket_agent.arena import family_map, mother_map, run_arena
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
from polymarket_agent.strategy_engine import StrategyOutput

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
    # Minutage par étape (secondes, 21/10/2026 : cycles de 220 à 285 s pour un créneau de 300 s),
    # rattachements des références, abstentions par portefeuille et par stratégie.
    timings: dict[str, float] = field(default_factory=dict)
    references: dict[str, int] = field(default_factory=dict)
    abstentions: dict[str, dict] = field(default_factory=dict)
    lap_at: float = 0.0


def _lap(report: CycleReport, name: str) -> None:
    """Ajoute à `report.timings[name]` le temps écoulé depuis l'étape précédente."""
    now = time.monotonic()
    report.timings[name] = round(report.timings.get(name, 0.0) + (now - (report.lap_at or now)), 2)
    report.lap_at = now


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
    # Paris du fantôme pendant ce cycle, copiés par le capital principal (copie fidèle, 18/10/2026) :
    # {stratégie: {"total": capital estimé du fantôme, "buys": [(proposition, parts exécutées)],
    #  "orders": [ordres posés]}}.
    copied: dict = field(default_factory=dict)


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
    parts que le principal détient réellement.

    Copie fidèle (18/10/2026) : avec `source` (le fantôme de la stratégie), le principal ne relance
    plus la stratégie sur son propre argent ; il refait les paris que le fantôme vient de faire dans
    ce cycle, mêmes marchés, mise à la même échelle (part × capital du principal / capital du
    fantôme). Avant, il prenait d'autres paris que ceux jugés par l'arène : à la promotion, il
    rachetait d'un coup des positions que le fantôme tenait depuis des heures, avec des mises 1,5 à
    3 fois plus grosses en proportion (−89 sur 12 opérations le 18/10, quand les fantômes copiés
    perdaient 2 à 4 % de leurs mises). Les sorties restent celles de la stratégie (`exits`), sur les
    positions du principal.

    Budget (18/10/2026) : réduire chaque mise ne suffisait pas, pari après pari une stratégie
    pouvait engager presque tout le capital (nf_court : 630 sur ≈ 1 000 pour une part d'environ 50 %).
    Désormais, ce qu'elle a déjà investi dans le principal (coût de ses positions ouvertes) plus
    ses nouveaux achats ne dépassent jamais part × capital total estimé ; le reste attend."""

    def __init__(self, strategy, weight: Decimal, source: Portfolio | None = None, base: Decimal | None = None):
        self.inner, self.weight, self.source = strategy, weight, source
        # Copie à la mise de BASE (21/10/2026, « grossir les gagnantes ») : la prudence du fantôme
        # (½ tant que rien n'est prouvé, entière, ¼, renfort) sert à l'arène ; le principal garde sa
        # propre mise, celle simulée avec Etienne (experiments/taille_des_mises.md) : il divise par la
        # prudence du fantôme et remultiplie par `base`. Son renfort à lui passe par l'arène
        # (arena.measured_stake), une seule fois.
        self.stake_adjust = Decimal("1")
        ghost_weight = getattr(strategy, "weight", None) if isinstance(strategy, Weighted) else None
        if source is not None and base is not None and ghost_weight and ghost_weight > 0 \
                and getattr(strategy, "forecasting", True):
            self.stake_adjust = Decimal(str(base)) / ghost_weight
        self.strategy_id, self.version = strategy.strategy_id, strategy.version
        self.needs_price_history = getattr(strategy, "needs_price_history", False)
        if hasattr(strategy, "exits"):
            self.exits = strategy.exits

    def propose(self, *args, **kwargs):
        state = kwargs.get("state", args[2] if len(args) > 2 else None)
        marks = kwargs.get("marks", args[5] if len(args) > 5 else None)
        if self.source is not None and state is not None:
            output, factor = self._copy(state, marks)
        else:
            output, factor = self.inner.propose(*args, **kwargs), self.weight
        budget = None
        if state is not None:
            invested = sum((pos.cost_basis for pos in state.positions.values() if pos.strategy_id == self.strategy_id),
                           Decimal("0"))
            budget = self.weight * state.total_estimated(marks) - invested
        output.proposals, budget = self._scale(output.proposals, budget, factor)
        if getattr(output, "limit_orders", None):
            output.limit_orders, budget = self._scale(output.limit_orders, budget, factor)
        return output

    def _copy(self, state, marks) -> tuple[StrategyOutput, Decimal]:
        """Les paris du fantôme dans ce cycle, et le facteur d'échelle de leurs mises."""
        out = StrategyOutput()
        seen = self.source.copied.get(self.strategy_id)
        ghost_total = seen["total"] if seen else Decimal("0")
        if ghost_total <= 0:
            return out, Decimal("0")
        factor = self.weight * state.total_estimated(marks) / ghost_total * self.stake_adjust
        out.proposals = [dataclasses.replace(p, shares=filled) for p, filled in seen["buys"]
                         if p.token_id not in state.positions]
        for order in seen["orders"]:
            held = state.positions.get(order.token_id)
            if order.side == "BUY" and held is None:
                out.limit_orders.append(order)
            elif order.side == "SELL" and held is not None:  # tenue de marché : revendre son stock
                shares = min(held.shares, (order.shares * factor).quantize(Decimal("0.01"), rounding=ROUND_DOWN))
                if shares > 0:
                    out.limit_orders.append(dataclasses.replace(order, shares=shares))
        return out, factor

    def _scale(self, proposals: list, budget: Decimal | None = None,
               factor: Decimal | None = None) -> tuple[list, Decimal | None]:
        factor = self.weight if factor is None else factor
        scaled = []
        for p in proposals:
            if p.side != "BUY":
                scaled.append(p)
                continue
            shares = (p.shares * factor).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            if budget is not None:  # plafond du total engagé par cette stratégie
                if budget <= 0 or p.max_price <= 0:
                    continue
                shares = min(shares, (budget / p.max_price).quantize(Decimal("0.01"), rounding=ROUND_DOWN))
            if shares > 0:
                scaled.append(dataclasses.replace(p, shares=shares))
                if budget is not None:
                    budget -= shares * p.max_price
        return scaled, budget

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

    report.lap_at = time.monotonic()
    _lap(report, "journal_principal")
    main = Portfolio("principal", ledger, [])  # stratégie fixée par l'arène (champion)
    portfolios = [main] + _open_shadows(deps, report, started)
    seq_at_open = {p.name: p.ledger.state.last_seq for p in portfolios}
    _lap(report, "journaux_fantomes")
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
    try:
        beats = json.loads(deps.db.get_value("battements_fantomes") or "{}")
    except (ValueError, TypeError):
        beats = {}
    for portfolio in portfolios:
        if not portfolio.ledger.state.bankrupt:
            for m in portfolio.ledger.record_milestones(finished):
                report.milestones.append(f"{portfolio.name} : palier {m['target']} en {m['seconds'] / 3600:.1f} h")
                log.info("PALIER %s atteint par %s", m["target"], portfolio.name)
        held = {t: m for t, m in portfolio.marks.items() if t in portfolio.ledger.state.positions}
        if portfolio is main or _ghost_beat_due(deps, portfolio, finished, seq_at_open, beats):
            portfolio.ledger.heartbeat(report.cycle_id, report.status, finished,
                                       total_estimated=portfolio.ledger.state.total_estimated(held))
            beats[portfolio.name] = finished.isoformat()
        if portfolio is not main:
            report.shadows[portfolio.name] = dict(portfolio.ledger.state.summary(held),
                                                  **portfolio.counts)
    deps.db.set_value("battements_fantomes", json.dumps(beats))
    deps.db.set_anchor(ledger.state.last_seq, ledger.state.last_hash, finished)
    _lap(report, "battements")
    report.timings["total"] = round((deps.now() - started).total_seconds(), 1)
    deps.db.set_value("durees_cycle", json.dumps({"cycle": report.cycle_id, "etapes": report.timings}))
    deps.db.set_value("abstentions", json.dumps({"cycle": report.cycle_id, "portefeuilles": report.abstentions}))
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
        entries = {name: read_entries(p.ledger) for name, p in competitors.items()}
        items = {name: strategy_health.forecasts(e) for name, e in entries.items()}
        settled = {name: strategy_health.settled_outcomes(e) for name, e in entries.items()}
        if _due(deps.db, "bilan_previsions", 60, now):
            try:  # Gamma seulement pour les prévisions que le journal ne règle pas (revendues, en cours)
                strategy_health.update_outcomes(deps.db, deps.gamma.get_market,
                                                [f for n, v in items.items() for f in v if f["token_id"] not in settled[n]],
                                                now, int(cfg["outcomes_per_hour"]))
            except Exception as exc:  # noqa: BLE001 - une mesure ne bloque jamais le cycle
                log.warning("bilan des prévisions non mis à jour : %s", exc)
            deps.db.set_source_run("bilan_previsions", now)
        rows = {c["name"]: c for c in report.arena.get("classement", [])}
        closed = {n: c["closed_trades"] for n, c in rows.items()}
        suspended = set()
        for name, portfolio in competitors.items():
            sc = strategy_health.score(deps.db, items[name], settled[name])
            factor, renfort = strategy_health.prudence(sc, cfg), 1.0
            if portfolio.strategies and not any(getattr(s, "forecasting", True) for s in portfolio.strategies):
                # Tenue de marché : aucune prévision à juger (son « estimation » est le prix du milieu) ;
                # sa prudence est dans ses propres réglages (part du capital par marché, stock maximal).
                factor = 1.0
            else:  # renfort : plus d'avantage prouvé que supposé → mise plus grosse, plafonnée
                renfort = strategy_health.boost(rows.get(name), cfg)
                factor *= renfort
            reason = None if name in eliminated else strategy_health.suspension(
                portfolio.ledger.state, closed.get(name, 0), cfg)
            if reason:
                suspended.add(name)
                factor = 0.0
                log.info("SUSPENDUE %s : %s", name, reason)
            strategy_health.save(deps.db, name, dict(sc, prudence=factor, renfort=renfort, suspendue=reason))
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


# Relecture d'un carnet juste avant d'exécuter (19/10/2026) : un carnet relu il y a moins de
# FRESH_BOOK_SECONDS par un autre portefeuille du même cycle est réutilisé. Plusieurs fantômes
# visent souvent le même marché : 148 relectures une à une prenaient 28 s sur un cycle de 141 s.
FRESH_BOOK_SECONDS = 20


def _reread_book(deps: CycleDeps, token_id: str, cache: dict | None) -> OrderBook:
    hit = cache.get(token_id) if cache is not None else None
    if hit is not None and hit.fetched_at is not None and (deps.now() - hit.fetched_at).total_seconds() <= FRESH_BOOK_SECONDS:
        return hit
    book = deps.clob.get_book(token_id)
    if cache is not None and book is not None:
        cache[token_id] = book
    return book


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

    # 3. Règlements : les marchés résolus libèrent le capital avant toute nouvelle entrée. Un marché
    #    détenu par plusieurs portefeuilles n'est lu qu'une fois par cycle (21/10/2026 : 948 positions,
    #    beaucoup en double, 16,7 s de règlements sur un cycle de 59 s).
    gamma_once = _OnceGamma(deps.gamma)
    # Lus d'abord par lots de 100 (21/10/2026 : 723 marchés détenus relus un par un = 79 s sur 131 s,
    # à cause de la pause de politesse de 0,2 s entre deux requêtes).
    gamma_once.prefetch({p.market_id for pf in portfolios if not pf.ledger.state.bankrupt
                         for p in pf.ledger.state.positions.values()},
                        int(deps.settings.get("cycle", {}).get("reglements_par_lot", 1) or 1))
    for portfolio in portfolios:
        if portfolio.ledger.state.positions and not portfolio.ledger.state.bankrupt:
            settled = settle_positions(portfolio.ledger, gamma_once, deps.now())
            portfolio.counts["settled"] = len(settled)
    _lap(report, "reglements")
    if main.ledger.state.bankrupt:
        report.status = "FAILLITE"
        return

    # 3 bis. Arène : classement, promotion du champion, élimination hebdomadaire.
    competitors = {p.name.removeprefix("fantome:"): p for p in portfolios[1:]}
    rewards, reward_days = _ranking_rewards(deps, competitors)
    report.arena = run_arena(main.ledger, {n: p.ledger for n, p in competitors.items()},
                             deps.settings["arena"], deps.now(), rewards=rewards, reward_days=reward_days,
                             families=family_map(), mothers=mother_map())
    deps.db.set_value("doublons_principal", json.dumps(report.arena.get("doublons") or {}))  # tableau de bord
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
    # Période d'essai et plafonds (arena.exposure) : seule une fraction de chaque part est engagée.
    alloc, engaged = report.arena.get("allocation", {}) or {champion: 1.0}, report.arena.get("engagement", {})
    shares = {n: w * min(1.0, engaged[n] / alloc[n]) if n in engaged and alloc.get(n) else w for n, w in shares.items()}
    shares = _steady_shares(deps, shares)
    base = Decimal(str(strategy_health.config(deps.settings)["base"]))
    main.strategies = [Weighted(s, Decimal(str(round(w, 6))), source=p, base=base) for n, p in competitors.items()
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
    _lap(report, "arene_et_sante")
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
    _lap(report, "scanner")

    # 4 bis. Marchés supplémentaires demandés par les stratégies (ex. échelles de seuils).
    eligible = [m for m in result.markets if m.eligible]
    live = [m for m in eligible if not m.ended]  # marchés échus : seulement pour `wants_ended` (20/10/2026)
    # Références externes (Kalshi, PredictIt, Manifold, tweets, champions, NHL, mentions) rattachées
    # à TOUS les marchés scannés, AVANT que les stratégies demandent leurs marchés (21/10/2026 :
    # sur les seuls 150 surveillés, elles ne trouvaient presque rien et 8 stratégies restaient muettes).
    report.references = _attach_references(deps, live, now)
    try:  # historique des références (paires de prix pour le chercheur), au plus une fois par heure
        from polymarket_agent import references as refs_mod
        cfg = deps.settings.get("references_historique") or {}
        written = refs_mod.record_history(live, deps.db, now, float(cfg.get("toutes_les_minutes", 0) or 0),
                                          float(cfg.get("garder_jours", 45)))
        if written:
            report.counts["historique_references"] = written
    except Exception as exc:  # noqa: BLE001 - un historique ne bloque jamais le cycle
        log.warning("historique des références non écrit : %s", exc)
    _lap(report, "references")
    known = {m.market_id for m in result.watchlist}
    max_extra = int(deps.settings["scanner"].get("max_extra_markets", 40))
    # Places réparties à tour de rôle (21/10/2026) : la première stratégie servie ne prend plus
    # toutes les places des suivantes.
    wishes = []
    for strategy in {id(s): s for p in portfolios for s in p.strategies}.values():
        pool = eligible if getattr(strategy, "wants_ended", False) else live
        wished = [m for m in getattr(strategy, "candidates", lambda ms: [])(pool)]
        strategy.asked_markets = {m.market_id for m in wished}  # marchés longs : vus par qui les demande (_visible)
        wishes.append(wished)
    for market in _round_robin(wishes):
        if max_extra <= 0:
            break
        if market.market_id not in known:
            result.watchlist.append(market)
            known.add(market.market_id)
            max_extra -= 1
    _lap(report, "candidats")

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
    _lap(report, "carnets")
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

    _lap(report, "ordres_poses")
    # 6. Historique de prix récent (seulement si une stratégie active en a besoin).
    if any(getattr(s, "needs_price_history", False) for p in portfolios for s in p.strategies):
        _attach_price_features(deps, result.watchlist, now)

    _lap(report, "historique_prix")
    # 6 bis. Sources d'information (étape 5). Une source en panne ne bloque rien (mode dégradé).
    if deps.collector is not None:
        try:
            report.sources = deps.collector(result.watchlist, now)
        except Exception as exc:  # noqa: BLE001 - la collecte ne doit jamais faire tomber le cycle
            report.sources = {"collecte": f"indisponible : {type(exc).__name__}: {exc}"[:200]}
            log.exception("collecte des sources en échec, cycle poursuivi sans elles")
    if report.references:
        report.sources["references"] = "ok (" + ", ".join(f"{k} {v}" for k, v in report.references.items()) + ")"
    _lap(report, "sources")

    # 7-11. Stratégies → propositions → contrôleur → exécution simulée, portefeuille par portefeuille.
    # Les fantômes d'abord : le capital principal copie ensuite les paris qu'ils viennent de faire.
    fresh_books: dict = {}  # carnets relus pendant ce cycle (_reread_book)
    for portfolio in portfolios[1:] + portfolios[:1]:
        if portfolio.ledger.state.bankrupt:
            continue  # un fantôme en faillite ne trade plus (le principal est vérifié plus haut)
        _execute(deps, portfolio, result.watchlist, books, report, bucket, result.markets, fresh_books)
        _lap(report, "principal" if portfolio is main else "fantomes")
        if main.ledger.state.bankrupt:
            break
    # 12. Récompenses ESTIMÉES (hors capital) : liquidité pour les ordres restés posés, détention
    #     pour les positions des marchés éligibles (holding_rewards.py, 19/10/2026).
    by_market = {m.market_id: m for m in result.markets} | {m.market_id: m for m in result.watchlist}
    rate = float((deps.settings.get("recompenses") or {}).get("detention_taux_annuel", 0) or 0)
    for portfolio in portfolios:
        try:
            _estimate_rewards(deps, portfolio, by_market, books, report, now)
            if rate > 0:
                from polymarket_agent import holding_rewards
                amounts = holding_rewards.accrue(portfolio.ledger.state.positions, portfolio.marks, by_market, rate,
                                                 float(deps.settings["cycle"]["bucket_minutes"]))
                if amounts:
                    total = holding_rewards.record(deps.db, report.cycle_id, now, portfolio.name, amounts)
                    portfolio.counts["detention_estimee"] = round(total, 6)
        except Exception as exc:  # noqa: BLE001 - une estimation ne doit jamais faire tomber le cycle
            log.warning("[%s] estimation des récompenses impossible : %s", portfolio.name, exc)
    report.status = "FAILLITE" if main.ledger.state.bankrupt else "OK"


def _steady_shares(deps: CycleDeps, shares: dict[str, float]) -> dict[str, float]:
    """Parts du capital principal recalculées au plus une fois par heure (décision d'Etienne,
    18/10/2026) : pas de va-et-vient toutes les 5 minutes. Une stratégie qui ENTRE ou SORT change
    la répartition tout de suite. Dernière répartition gardée en base (lue par le tableau de bord)."""
    now = deps.now()
    minutes = float(deps.settings["arena"].get("repartition", {}).get("recalcul_minutes", 60))
    try:
        prev = json.loads(deps.db.get_value("repartition_principal") or "{}")
        age = (now - datetime.fromisoformat(prev["date"])).total_seconds() / 60 if prev.get("date") else None
    except (ValueError, TypeError, KeyError):
        prev, age = {}, None
    old = prev.get("parts") or {}
    if age is not None and age < minutes and set(old) == set(shares):
        return {n: float(old[n]) for n in shares}
    deps.db.set_value("repartition_principal", json.dumps({"date": now.isoformat(timespec="seconds"),
                                                           "parts": {n: round(w, 6) for n, w in shares.items()}}))
    return shares


def _ranking_rewards(deps: CycleDeps, competitors: dict) -> tuple[dict[str, float], dict[str, int]]:
    """Option A d'Etienne (17/10/2026) : récompenses estimées comptées pour le CLASSEMENT de l'arène,
    jamais dans le capital des fantômes (liquidity_rewards.ranking_bonus), et nombre de journées
    versables (mode « recompenses » de l'arène)."""
    cfg = deps.settings.get("recompenses") or {}
    if not cfg.get("classement_arene"):
        return {}, {}
    from polymarket_agent import holding_rewards
    from polymarket_agent import liquidity_rewards as lr
    starts = {n: p.ledger.state.epoch_started_at for n, p in competitors.items()}
    try:
        prudence = float(cfg.get("prudence", 0.5))
        bonus = lr.ranking_bonus(deps.db, starts, prudence, deps.now())
        for name, amount in holding_rewards.ranking_bonus(deps.db, starts, prudence).items():  # détention (19/10)
            bonus[name] = round(bonus.get(name, 0.0) + amount, 4)
        return bonus, lr.payable_day_counts(deps.db, starts, deps.now())
    except Exception as exc:  # noqa: BLE001 - une estimation ne doit jamais bloquer l'arène
        log.warning("récompenses estimées illisibles pour le classement : %s", exc)
        return {}, {}


def _estimate_rewards(deps: CycleDeps, portfolio: Portfolio, by_market: dict[str, MarketInfo],
                      books: dict[str, OrderBook], report: CycleReport, now: datetime) -> None:
    """Part estimée de la cagnotte de chaque marché pour nos ordres ouverts, pendant un cycle
    (liquidity_rewards.py). Écrite dans la table `recompenses_estimees`, jamais dans le journal."""
    from polymarket_agent import liquidity_rewards as lr
    quotes: dict[str, list] = {}
    for order in deps.db.open_orders(portfolio.name):
        proposal = Proposal.from_dict(json.loads(order["proposal"]))
        market = by_market.get(proposal.market_id)
        if market is None or market.rewards_daily_rate <= 0:
            continue
        q = lr.to_quote(market, proposal.token_id, proposal.side, float(proposal.max_price), float(order["remaining"]))
        if q is not None:
            quotes.setdefault(market.market_id, []).append(q)
    minutes = float(deps.settings["cycle"]["bucket_minutes"])
    total = 0.0
    for market_id, qs in quotes.items():
        market = by_market[market_id]
        book = books.get(market.token_ids[0])
        est = lr.estimate(market, book, qs, minutes) if book is not None else None
        if est is not None and est.eligible:
            lr.record(deps.db, report.cycle_id, now, portfolio.name, market_id, est, market.rewards_daily_rate)
            total += est.amount
    if total:
        portfolio.counts["recompenses_estimees"] = round(total, 4)


def _execute(deps: CycleDeps, portfolio: Portfolio, watchlist: list[MarketInfo],
             books: dict[str, OrderBook], report: CycleReport, bucket: str,
             all_markets: list[MarketInfo] | None = None, fresh_books: dict | None = None) -> None:
    ledger, marks = portfolio.ledger, portfolio.marks
    by_market = {m.market_id: m for m in (all_markets or [])} | {m.market_id: m for m in watchlist}
    if portfolio.name != "principal":  # ce que le principal pourra copier (Weighted._copy)
        total = ledger.state.total_estimated(marks)
        portfolio.copied = {s.strategy_id: {"total": total, "buys": [], "orders": []} for s in portfolio.strategies}
    proposals, bought = [], set()
    for strategy in portfolio.strategies:
        seen = _visible(strategy, watchlist)
        output = strategy.propose(seen, books, ledger.state, deps.limits, bucket, marks)
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
        # Raisons d'abstention publiées (21/10/2026) : pourquoi une stratégie reste muette.
        report.abstentions.setdefault(portfolio.name, {})[strategy.strategy_id] = {
            "marches": len(seen), "propositions": len(output.proposals), "ordres": len(limit_orders),
            "raisons": dict(sorted(output.abstentions.items(), key=lambda kv: -kv[1])[:6])}
        if portfolio.name == "principal":
            # Plusieurs stratégies au principal (18/10/2026) : un marché déjà acheté dans ce cycle par
            # l'une n'est pas racheté par une autre (les stratégies sautent déjà les positions ouvertes).
            output.proposals = [p for p in output.proposals if p.side != "BUY" or p.market_id not in bought]
            limit_orders = [p for p in limit_orders if p.side != "BUY" or p.market_id not in bought]
            bought.update(p.market_id for p in output.proposals + limit_orders if p.side == "BUY")
            # Garde-fous du capital principal (settings.yaml → principal).
            output.proposals = _cap_main(deps, portfolio, output.proposals, by_market)
            limit_orders = _cap_main(deps, portfolio, limit_orders, by_market)
        proposals += output.proposals
        proposals += _place_resting(deps, portfolio, limit_orders, by_market, report, fresh_books)
    accepted = fills = 0

    for proposal in proposals:
        market = by_market.get(proposal.market_id)
        if market is None:  # marché sorti du scan : on garde la position jusqu'au règlement
            continue
        verdict = evaluate(proposal, ledger.state, market_context(market, books.get(proposal.token_id),
                                                                  proposal.token_id),
                           deps.limits, deps.now(), marks)
        # Carnet du début de cycle vieilli pendant les portefeuilles précédents (21/10/2026) : ce n'est pas un motif de
        # rejet, le carnet est relu juste après et contrôlé de nouveau (même plafond d'âge).
        if not verdict.accepted and not all(r.startswith("carnet périmé") for r in verdict.reasons):
            deps.db.save_decision(report.cycle_id, deps.now(), proposal, verdict)
            log.info("rejet %s : %s", proposal.op_id, verdict.reasons)
            continue

        # Relecture du carnet juste avant l'exécution, puis nouveau contrôle.
        try:
            fresh = _reread_book(deps, proposal.token_id, fresh_books)
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
        drop = _price_drop(deps, proposal, books.get(proposal.token_id), fresh)
        if drop is not None:
            verdict.accepted = False
            verdict.reasons.append(drop)
            deps.db.save_decision(report.cycle_id, deps.now(), proposal, verdict)
            log.info("rejet après relecture %s : %s", proposal.op_id, drop)
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
                           "horizon_hours": str(proposal.horizon_hours),
                           **_depuis_coup_d_envoi(market, deps.now())})
                fills += 1
                if proposal.strategy_id in portfolio.copied:
                    portfolio.copied[proposal.strategy_id]["buys"].append((proposal, fill.filled_shares))
                log.info("[%s] exécution simulée %s : %s parts à %s (+%s de frais), %s", portfolio.name,
                         proposal.op_id, fill.filled_shares, fill.avg_price, fill.fee, fill.status)
            except LedgerError as exc:
                fill.status, fill.reason = "REFUSE_JOURNAL", str(exc)
                log.warning("le journal refuse %s : %s", proposal.op_id, exc)
        deps.db.save_decision(report.cycle_id, deps.now(), proposal, verdict, fill)
        if ledger.state.bankrupt:
            break
    portfolio.counts.update(proposals=len(proposals), accepted=accepted, fills=fills)


def _depuis_coup_d_envoi(market: MarketInfo, now: datetime) -> dict[str, str]:
    """Heures écoulées depuis le coup d'envoi (négatif : avant). `horizon_hours` est l'échéance Gamma, une
    date placeholder pour un match ; ce champ dit si l'achat a eu lieu avant ou pendant le jeu (enquête 20/10)."""
    if getattr(market, "game_start", None) is None:
        return {}
    return {"depuis_coup_d_envoi_h": f"{(now - market.game_start).total_seconds() / 3600:.2f}"}


class _OnceGamma:
    """`get_market` lu une seule fois par marché pendant un cycle (réponse ou erreur gardée)."""

    def __init__(self, gamma):
        self.gamma, self.cache = gamma, {}

    down = False  # Gamma en panne pendant ce cycle (prefetch) : pas de lecture une par une

    def get_market(self, market_id):
        market_id = str(market_id)
        if market_id not in self.cache and self.down:
            raise SourceUnavailable("Gamma indisponible pendant ce cycle (lots refusés)")
        if market_id not in self.cache:
            try:
                self.cache[market_id] = (True, self.gamma.get_market(market_id))
            except (SourceUnavailable, ValueError) as exc:
                self.cache[market_id] = (False, exc)
        ok, value = self.cache[market_id]
        if not ok:
            raise value
        return value

    def prefetch(self, market_ids, batch: int = 100) -> None:
        """Lit d'avance les marchés pas encore lus, par lots (`GammaClient.markets_by_ids`, fermés puis
        ouverts). Un lot refusé est coupé en deux (un marché supprimé ne bloque pas tout le lot). Si
        tout échoue, Gamma est jugé en panne pour ce cycle : les marchés non lus ne sont pas relus un
        par un (cela prenait plus de deux minutes) ; leur règlement attend le cycle suivant. Un marché
        simplement absent des lots est lu un par un, comme avant."""
        todo = [str(m) for m in market_ids if str(m) not in self.cache]
        if batch <= 1 or len(todo) < 2 or not hasattr(self.gamma, "markets_by_ids"):
            return
        for k in range(0, len(todo), batch):
            chunk, any_ok = todo[k:k + batch], False
            for closed in (True, False):
                rows, ok = self._lot(chunk, closed)
                any_ok = any_ok or ok
                for raw in rows:
                    if isinstance(raw, dict) and str(raw.get("id")) in chunk:
                        self.cache[str(raw["id"])] = (True, raw)
            if not any_ok:
                self.down = True
                log.warning("règlements : Gamma ne répond pas aux lots, règlements remis au cycle suivant")
                return

    def _lot(self, chunk: list[str], closed: bool, depth: int = 0) -> tuple[list, bool]:
        try:
            return self.gamma.markets_by_ids(chunk, closed=closed), True
        except (SourceUnavailable, ValueError) as exc:
            if len(chunk) < 8 or depth >= 3:
                log.warning("règlements : lot de %d marchés illisible (%s)", len(chunk), exc)
                return [], False
            half = len(chunk) // 2
            a, ok_a = self._lot(chunk[:half], closed, depth + 1)
            b, ok_b = self._lot(chunk[half:], closed, depth + 1)
            return a + b, ok_a or ok_b

    def __getattr__(self, name):
        return getattr(self.gamma, name)


def _ghost_beat_due(deps: CycleDeps, portfolio: Portfolio, now: datetime, seq_at_open: dict, beats: dict) -> bool:
    """Battement d'un fantôme (21/10/2026) : s'il a écrit pendant le cycle (achat, vente, règlement),
    sinon au plus toutes les `cycle.battement_fantomes_minutes` minutes. Les battements faisaient
    92,5 % des lignes des journaux fantômes (85 579 sur 92 496), relues et vérifiées à chaque cycle."""
    if portfolio.ledger.state.last_seq != seq_at_open.get(portfolio.name):
        return True
    minutes = float(deps.settings.get("cycle", {}).get("battement_fantomes_minutes", 0) or 0)
    last = beats.get(portfolio.name)
    if minutes <= 0 or not last:
        return True
    try:
        return (now - datetime.fromisoformat(last)).total_seconds() >= minutes * 60 - 30
    except ValueError:
        return True


def _attach_references(deps: CycleDeps, markets: list[MarketInfo], now: datetime) -> dict[str, int]:
    """references.attach_all sur tous les marchés scannés ; une erreur ne bloque jamais le cycle."""
    from polymarket_agent import references
    try:
        return references.attach_all(markets, deps.db, now)
    except Exception as exc:  # noqa: BLE001 - un rattachement ne bloque jamais le cycle
        log.warning("références non rattachées : %s", exc)
        return {}


def _visible(strategy, watchlist: list[MarketInfo]) -> list[MarketInfo]:
    """Marchés montrés à une stratégie : pas les marchés échus (sauf `wants_ended`), et les marchés
    longs des pages longues (`extra_only`, 21/10/2026) seulement si ELLE les a demandés : sinon le
    favori de base, sans fenêtre de temps, achèterait un favori de 2028 et bloquerait son fantôme
    deux ans (experiments/muettes.md)."""
    asked = getattr(strategy, "asked_markets", None) or set()
    ended_ok = getattr(strategy, "wants_ended", False)
    return [m for m in watchlist if (ended_ok or not m.ended) and (not m.extra_only or m.market_id in asked)]


def _round_robin(lists: list[list]) -> list:
    """[a1, a2], [b1], [c1, c2, c3] → a1, b1, c1, a2, c2, c3 (chaque stratégie à son tour)."""
    out, depth = [], max((len(x) for x in lists), default=0)
    for i in range(depth):
        out += [x[i] for x in lists if i < len(x)]
    return out


def _price_drop(deps: CycleDeps, proposal: Proposal, before: OrderBook | None, fresh: OrderBook | None) -> str | None:
    """Enquête du 20/10/2026 (experiments/enquetes/2026-10-20_carnet_perime.md) : l'estimation
    d'une stratégie est calculée sur le carnet lu au début du cycle ; si le prix de vente a chuté
    de plus de `relecture.chute_max` avant l'exécution (mauvaise nouvelle en plein match), cette
    estimation est périmée et la mise, calculée sur elle, trop grosse (Moyuka Uchijima : estimée
    0,98, payée 0,817, 23 % du fantôme et 8,9 % du principal). On ne joue pas : la stratégie
    redécidera au cycle suivant avec un carnet frais. Les jambes d'arbitrage (`relecture.sauf`)
    ne sont pas concernées : une jambe moins chère rend la paire meilleure."""
    cfg = deps.settings.get("relecture") or {}
    if (proposal.side != "BUY" or not cfg or proposal.strategy_id in set(cfg.get("sauf") or [])
            or before is None or fresh is None or before.best_ask is None or fresh.best_ask is None):
        return None
    fall = before.best_ask - fresh.best_ask
    if fall > Decimal(str(cfg.get("chute_max", "1"))):
        return (f"le prix a chuté de {before.best_ask} à {fresh.best_ask} pendant le cycle : "
                "estimation périmée, décision reportée au prochain cycle")
    return None


def _cap_main(deps: CycleDeps, portfolio: Portfolio, proposals: list[Proposal],
              by_market: dict[str, MarketInfo]) -> list[Proposal]:
    """Capital principal (17/10/2026, AMELIORATION n°6) : un achat ne dépasse pas `max_mise` du
    capital estimé, et l'argent engagé dans une même famille de marchés (météo, sport… : paris liés,
    une même vague de chaleur peut tous les faire perdre) ne dépasse pas `max_famille`. Les
    fantômes ne sont pas plafonnés : l'arène mesure chaque stratégie telle qu'elle est."""
    from polymarket_agent.strategy_engine import market_family
    cfg = deps.settings.get("principal", {})
    if not cfg:
        return proposals
    state = portfolio.ledger.state
    total = state.total_estimated(portfolio.marks)
    max_bet = Decimal(str(cfg.get("max_mise", 1))) * total
    max_family = Decimal(str(cfg.get("max_famille", 1))) * total
    exposure: dict[str, Decimal] = {}
    for pos in state.positions.values():
        held = by_market.get(pos.market_id)
        fam = market_family(held) if held is not None else "inconnue"
        exposure[fam] = exposure.get(fam, Decimal("0")) + pos.cost_basis
    out = []
    for p in proposals:
        market = by_market.get(p.market_id)
        if p.side != "BUY" or market is None or p.max_price <= 0:
            out.append(p)
            continue
        fam = market_family(market)
        room = min(max_bet, max_family - exposure.get(fam, Decimal("0")))
        shares = min(p.shares, (room / p.max_price).quantize(Decimal("0.01"), rounding=ROUND_DOWN)) if room > 0 else Decimal("0")
        if shares <= 0:
            log.info("[principal] %s écarté : famille %s déjà à %s (plafond %s)", p.op_id, fam,
                     exposure.get(fam), max_family.quantize(Decimal("0.01")))
            continue
        if shares < p.shares:
            p = dataclasses.replace(p, shares=shares)
        exposure[fam] = exposure.get(fam, Decimal("0")) + shares * p.max_price
        out.append(p)
    return out


# --------------------------------------------------------------------------- ordres posés

def _place_resting(deps: CycleDeps, portfolio: Portfolio, orders: list[Proposal],
                   by_market: dict[str, MarketInfo], report: CycleReport,
                   fresh_books: dict | None = None) -> list[Proposal]:
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
            book = _reread_book(deps, order.token_id, fresh_books)
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
                if order.strategy_id in portfolio.copied:
                    portfolio.copied[order.strategy_id]["orders"].append(order)
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
                               horizon_hours=str(part.horizon_hours), **_depuis_coup_d_envoi(market, now)))
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
