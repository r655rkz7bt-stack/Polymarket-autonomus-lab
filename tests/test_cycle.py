"""Cycle complet avec des API factices : flux de bout en bout et scénarios de panne."""

from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal

import pytest
import yaml

from conftest import KEY, NOW, ROOT, buy, make_book, raw_market
from polymarket_agent.config import load_settings
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.ledger import Ledger
from polymarket_agent.main import EXIT_HALT, CycleDeps, run_cycle
from polymarket_agent.persistence import Database
from polymarket_agent.safety_controller import RealModeForbidden
from polymarket_agent.strategy_engine import NaiveFavorite, PatientOrders, load_strategies


def crown(paths, name="naive_favorite_v1.0.0"):
    """Désigne la stratégie de test comme champion : le capital principal suit ses décisions."""
    Ledger.open(paths[0], KEY, paths[1]).record_promotion(name, "test", now=NOW)


def pipeline_strategy(mode="principal"):
    """Stratégie de test du pipeline (la référence naïve, qui trade facilement)."""
    s = NaiveFavorite("1.0.0", "2026-10-14", {
        "min_ask": D("0.80"), "max_ask": D("0.95"), "bias": D("0.05"), "uncertainty": D("0.015"),
        "min_net_edge": D("0.02"), "max_extra_ticks": D("2"), "max_proposals_per_cycle": D("3")})
    s.mode = mode
    return s

D = Decimal


class FakeGamma:
    def __init__(self, markets=None, fail=False):
        self.markets, self.fail, self.calls = markets or [], fail, 0

    def list_markets(self, **kwargs):
        self.calls += 1
        if self.fail:
            raise SourceUnavailable("Gamma en panne (test)")
        return self.markets

    def get_market(self, market_id):
        if self.fail:
            raise SourceUnavailable("Gamma en panne (test)")
        for raw in self.markets:
            if raw["id"] == market_id:
                return raw
        raise SourceUnavailable("marché inconnu (test)")


class FakeClob:
    def __init__(self, books, fresh=None, fail=False):
        self.books, self.fresh, self.fail = books, fresh, fail

    def get_books(self, token_ids):
        if self.fail:
            raise SourceUnavailable("CLOB en panne (test)")
        return {t: self.books[t] for t in token_ids if t in self.books}

    def get_book(self, token_id):
        return (self.fresh or self.books)[token_id]

    def get_price_history(self, token_id, start_ts, end_ts, fidelity=60):
        return []


@pytest.fixture
def env(tmp_path, ledger, paths, limits):
    db = Database(tmp_path / "state" / "market.sqlite")
    db.set_anchor(ledger.state.last_seq, ledger.state.last_hash, NOW)
    clock = {"now": NOW}

    def make(gamma, clob, settings=None, strategies=None):
        if settings is None:
            settings = load_settings()
            settings["arena"] = yaml.safe_load((ROOT / "config" / "promotion.yaml").read_text(encoding="utf-8"))
            # Le champion de test engage toute sa part (sans période d'essai, garde-fou par jour, mise
            # sur l'avantage mesuré ni plafond) : le principal copie alors les paris du fantôme à l'identique (18/10/2026).
            settings["arena"].update(essai={}, part_max_par_strategie=None, garde_fou_jour=None,
                                     mise_avantage_mesure=None)
            settings["fantomes"] = {}  # mise des fantômes non plafonnée : tests/test_deux_camps.py
        return CycleDeps(settings=settings, limits=limits,
                         strategies=strategies if strategies is not None else [pipeline_strategy()],
                         ledger_path=paths[0], lock_path=paths[1], key=KEY, db=db,
                         gamma=gamma, clob=clob, now=lambda: clock["now"],
                         shadow_dir=tmp_path / "fantome")
    yield make, db, clock
    db.close()


def good_book(token="tokA", ts=NOW):
    return make_book(token, bids=(("0.89", "500"),), asks=(("0.90", "40"), ("0.91", "500")), ts=ts)


def test_full_cycle_executes_and_books_a_simulated_trade(env, paths):
    make, db, _ = env
    crown(paths)
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()})))
    assert report.status == "OK", report.messages
    assert report.counts["fills"] == 1
    reopened = Ledger.open(paths[0], KEY, paths[1])
    pos = reopened.state.positions["tokA"]
    # À 0,91 l'avantage passe sous le plancher : prix limite 0,90, 40 parts affichées dont 25 %
    # accessibles (concurrence, délai) → 10 parts, exécution partielle, jamais au-delà du prix limite.
    assert pos.shares == D("10")
    assert reopened.state.fees_paid > 0
    assert reopened.state.cash + pos.cost_basis == D("1000")
    types = [json.loads(l)["type"] for l in paths[0].read_text().splitlines()]
    assert types == ["GENESIS", "PROMOTION", "BUY", "HEARTBEAT"]
    row = db.conn.execute("SELECT accepted, fill_status FROM decisions").fetchone()
    assert row["accepted"] == 1 and row["fill_status"] == "PARTIAL"
    assert db.get_anchor()[0] == reopened.state.last_seq


def test_rerun_in_same_bucket_does_not_double_book(env, paths):
    make, _, clock = env
    crown(paths)
    deps = make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}))
    run_cycle(deps)
    cash = Ledger.open(paths[0], KEY, paths[1]).state.cash
    clock["now"] = NOW + timedelta(seconds=30)
    run_cycle(deps)
    assert Ledger.open(paths[0], KEY, paths[1]).state.cash == cash


def test_unavailable_source_does_not_block_the_program(env, paths):
    make, _, clock = env
    crown(paths)
    report = run_cycle(make(FakeGamma(fail=True), FakeClob({})))
    assert report.status == "DEGRADE" and report.exit_code == 0
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({}, fail=True)))
    assert report.status == "DEGRADE"
    # Le cycle suivant, une fois la source revenue, fonctionne normalement.
    clock["now"] = NOW + timedelta(minutes=5)
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book(ts=clock["now"])})))
    assert report.status == "OK" and report.counts["fills"] == 1


def test_book_changed_before_execution_is_rechecked(env, paths):
    make, db, _ = env
    crown(paths)
    moved = make_book("tokA", bids=(("0.93", "500"),), asks=(("0.97", "500"),))
    report = run_cycle(make(FakeGamma([raw_market()]),
                            FakeClob({"tokA": good_book()}, fresh={"tokA": moved})))
    assert report.counts["fills"] == 0
    assert not Ledger.open(paths[0], KEY, paths[1]).state.positions


def test_price_crash_during_the_cycle_postpones_the_buy(env, paths):
    """Enquête du 20/10/2026 : estimation calculée sur le carnet du début de cycle (vente 0,90),
    prix effondré à la relecture (0,80) ; acheter « l'aubaine » avec une mise calculée sur
    l'ancien prix revenait à acheter une mauvaise nouvelle. On reporte au cycle suivant."""
    make, db, _ = env
    crown(paths)
    crashed = make_book("tokA", bids=(("0.79", "500"),), asks=(("0.80", "500"),))
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}, fresh={"tokA": crashed})))
    assert report.counts.get("fills", 0) == 0
    reasons = [r["reasons"] for r in db.conn.execute("SELECT reasons FROM decisions")]
    assert any("chuté" in r for r in reasons)


def test_a_one_cent_dip_during_the_cycle_still_trades(env, paths):
    make, _, _ = env
    crown(paths)
    dip = make_book("tokA", bids=(("0.88", "500"),), asks=(("0.89", "40"), ("0.90", "500")))
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}, fresh={"tokA": dip})))
    assert report.counts["fills"] == 1


def test_book_aged_by_earlier_portfolios_is_reread_not_rejected(env, paths):
    """21/10/2026 : un cycle de plusieurs minutes vieillit les carnets du début de cycle ; les portefeuilles passés en dernier
    voyaient leurs propositions rejetées « carnet périmé » avant même la relecture. Le carnet relu, frais, doit suffire."""
    make, _, _ = env
    crown(paths)
    old = good_book(ts=NOW - timedelta(minutes=4))
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": old}, fresh={"tokA": good_book()})))
    assert report.counts["fills"] == 1


def test_stale_book_on_reread_means_no_trade(env, paths):
    make, _, _ = env
    crown(paths)
    stale = good_book(ts=NOW - timedelta(minutes=10))
    report = run_cycle(make(FakeGamma([raw_market()]),
                            FakeClob({"tokA": good_book()}, fresh={"tokA": stale})))
    assert report.counts["fills"] == 0


def test_market_without_reliable_data_does_not_trade(env, paths):
    make, _, _ = env
    report = run_cycle(make(FakeGamma([raw_market(bestBid=None)]), FakeClob({"tokA": good_book()})))
    assert report.counts.get("fills", 0) == 0
    assert report.counts["watchlist"] == 0


def test_bankrupt_engine_does_not_trade_or_scan(env, ledger, paths):
    make, _, _ = env
    buy(ledger, "all-in", token="tokZ", shares="2000", price="0.5")
    gamma = FakeGamma([raw_market()])
    report = run_cycle(make(gamma, FakeClob({"tokA": good_book()})))
    assert report.status == "FAILLITE"
    assert gamma.calls == 0
    assert "tokA" not in Ledger.open(paths[0], KEY, paths[1]).state.positions


def test_corrupt_ledger_halts(env, paths):
    make, _, _ = env
    paths[0].write_text(paths[0].read_text().replace("1000", "9000"))
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({})))
    assert report.status == "CORROMPU" and report.exit_code == EXIT_HALT


def test_missing_ledger_halts_without_creating_capital(env, paths):
    make, _, _ = env
    paths[0].unlink()
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({})))
    assert report.status == "NON_INITIALISE" and report.exit_code == EXIT_HALT
    assert not paths[0].exists()


def test_truncated_ledger_is_detected_by_anchor(env, ledger, paths):
    make, db, _ = env
    buy(ledger, "op1", token="tokZ", shares="10", price="0.5")
    db.set_anchor(ledger.state.last_seq, ledger.state.last_hash, NOW)
    first = paths[0].read_text().splitlines()[0]
    paths[0].write_text(first + "\n")  # on revient au capital initial
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({})))
    assert report.status == "CORROMPU"


def test_real_mode_is_refused(env):
    make, _, _ = env
    settings = load_settings()
    settings["arena"] = yaml.safe_load((ROOT / "config" / "promotion.yaml").read_text(encoding="utf-8"))
    settings["mode"] = "real"
    with pytest.raises(RealModeForbidden):
        run_cycle(make(FakeGamma(), FakeClob({}), settings))


def test_cycle_settles_resolved_position_before_trading(env, paths):
    make, _, clock = env
    crown(paths)
    gamma = FakeGamma([raw_market()])
    run_cycle(make(gamma, FakeClob({"tokA": good_book()})))
    pos = Ledger.open(paths[0], KEY, paths[1]).state.positions["tokA"]
    # Le marché se résout en faveur de « Yes » (jeton tokA).
    gamma.markets = [raw_market(closed=True, active=False, umaResolutionStatus="resolved",
                                outcomePrices=json.dumps(["1", "0"]))]
    clock["now"] = NOW + timedelta(days=1)
    report = run_cycle(make(gamma, FakeClob({})))
    assert report.counts["settled"] == 1, report.messages
    state = Ledger.open(paths[0], KEY, paths[1]).state
    assert not state.positions
    assert state.cash == D("1000") - pos.cost_basis + pos.shares
    assert state.realized_pnl == pos.shares - pos.cost_basis


def test_shadow_portfolio_never_touches_main_capital(env, paths, tmp_path):
    make, _, _ = env
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}),
                            strategies=[pipeline_strategy("fantome")]))
    assert report.status == "OK", report.messages
    main = Ledger.open(paths[0], KEY, paths[1]).state
    assert main.cash == D("1000") and not main.positions
    shadow_path = tmp_path / "fantome" / "naive_favorite_v1.0.0.jsonl"
    shadow = Ledger.open(shadow_path, KEY, tmp_path / "fantome" / "x.lock").state
    assert "tokA" in shadow.positions
    assert report.shadows["fantome:naive_favorite_v1.0.0"]["fills"] == 1


def test_corrupt_shadow_is_ignored_main_continues(env, paths, tmp_path):
    make, _, _ = env
    (tmp_path / "fantome").mkdir()
    (tmp_path / "fantome" / "naive_favorite_v1.0.0.jsonl").write_text("n'importe quoi\n")
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}),
                            strategies=[pipeline_strategy("fantome")]))
    assert report.status == "OK"
    assert any("fantôme" in m for m in report.messages)


def test_without_champion_main_capital_does_nothing(env, paths, tmp_path):
    """Aucune stratégie éligible (trop peu d'opérations clôturées) : le principal ne trade pas,
    mais chaque stratégie trade dans son fantôme."""
    make, _, _ = env
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()})))
    assert report.status == "OK"
    assert not Ledger.open(paths[0], KEY, paths[1]).state.positions
    assert report.shadows["fantome:naive_favorite_v1.0.0"]["fills"] == 1
    assert report.arena["champion"] == ""


def test_main_follows_the_champion_with_distinct_op_ids(env, paths, tmp_path):
    make, _, _ = env
    crown(paths)
    run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()})))
    main = Ledger.open(paths[0], KEY, paths[1]).state
    shadow = Ledger.open(tmp_path / "fantome" / "naive_favorite_v1.0.0.jsonl", KEY,
                         tmp_path / "fantome" / "x.lock").state
    assert "tokA" in main.positions and "tokA" in shadow.positions
    assert not (main.op_ids & shadow.op_ids)


def test_milestone_is_recorded_in_the_cycle(env, paths):
    make, _, clock = env
    crown(paths)
    gamma = FakeGamma([raw_market()])
    run_cycle(make(gamma, FakeClob({"tokA": good_book()})))
    # Le marché se résout à 1 : une énorme position gagnante ferait franchir 1 500…
    ledger = Ledger.open(paths[0], KEY, paths[1])
    ledger.record_buy(op_id="big", token_id="tokZ", market_id="mZ", event_id="eZ", outcome="Yes",
                      shares="1500", price="0.5", fee="0", strategy_id="t", strategy_version="0", now=NOW)
    ledger.record_settlement(op_id="sZ", token_id="tokZ", payout_per_share="1", resolution="Yes", now=NOW)
    clock["now"] = NOW + timedelta(hours=1)
    report = run_cycle(make(gamma, FakeClob({"tokA": good_book(ts=clock["now"])})))
    assert any("palier 1500" in m for m in report.milestones), report.milestones
    state = Ledger.open(paths[0], KEY, paths[1]).state
    assert state.next_target == D("2250")


def test_repository_config_competitors():
    loaded = load_strategies(ROOT / "config" / "strategies.yaml")
    assert len(loaded) >= 3  # innovation obligatoire : au moins 3 idées en test


def test_collector_crash_never_stops_the_cycle(env, paths):
    """Mode dégradé : même une panne totale de la collecte laisse le cycle trader."""
    make, _, _ = env
    deps = make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}))

    def broken(markets, now):
        raise RuntimeError("toutes les sources en panne")
    deps.collector = broken
    report = run_cycle(deps)
    assert report.status == "OK"
    assert report.sources["collecte"].startswith("indisponible")
    assert report.shadows["fantome:naive_favorite_v1.0.0"]["fills"] == 1
    # L'état des sources est conservé dans le résumé du cycle (affiché par le tableau de bord).
    summary = json.loads(deps.db.conn.execute("SELECT summary FROM cycles").fetchone()[0])
    assert summary["sources"]["collecte"].startswith("indisponible")


def test_cycle_executes_a_sell_from_strategy_exits(env, paths, tmp_path):
    """Une stratégie avec sorties vend réellement (relecture du carnet, contrôleur, journal signé)."""
    from polymarket_agent.strategies_v2 import MarketStructure
    make, _, clock = env
    s = MarketStructure("1.0.0", "2026-10-15", {
        "min_imbalance": D("0.6"), "max_spread": D("0.02"), "depth_window": D("0.03"), "stake_fraction": D("0.05"),
        "take_profit": D("0.02"), "stop_loss": D("0.03"), "max_hold_hours": D("6"), "max_extra_ticks": D("0"),
        "max_proposals_per_cycle": D("2")})
    gamma = FakeGamma([raw_market(yes_price="0.5", best_bid=0.49, best_ask=0.50)])
    pressure = make_book("tokA", bids=(("0.49", "5000"),), asks=(("0.50", "500"),))
    run_cycle(make(gamma, FakeClob({"tokA": pressure}), strategies=[s]))
    shadow_path = tmp_path / "fantome" / "market_structure_v1.0.0.jsonl"
    assert "tokA" in Ledger.open(shadow_path, KEY, tmp_path / "x.lock").state.positions
    clock["now"] = NOW + timedelta(minutes=30)
    risen = make_book("tokA", bids=(("0.55", "5000"),), asks=(("0.56", "500"),), ts=clock["now"])
    report = run_cycle(make(gamma, FakeClob({"tokA": risen}), strategies=[s]))
    state = Ledger.open(shadow_path, KEY, tmp_path / "x.lock").state
    assert "tokA" not in state.positions, report.messages
    assert state.realized_pnl > 0



def test_regression_dethroned_champion_still_exits_its_main_positions(env, paths, tmp_path):
    """Constaté le 15/10/2026 : market_structure, champion 10 minutes, a acheté pour le principal puis a
    été destitué. Ses positions du principal n'avaient plus personne pour les vendre (stop, durée
    maximale) jusqu'à la résolution. La stratégie garde la main sur ses sorties, sans racheter."""
    from polymarket_agent.strategies_v2 import MarketStructure
    make, _, clock = env
    s = MarketStructure("1.0.0", "2026-10-15", {
        "min_imbalance": D("0.6"), "max_spread": D("0.02"), "depth_window": D("0.03"), "stake_fraction": D("0.05"),
        "take_profit": D("0.02"), "stop_loss": D("0.03"), "max_hold_hours": D("6"), "max_extra_ticks": D("0"),
        "max_proposals_per_cycle": D("2")})
    crown(paths, "market_structure_v1.0.0")
    gamma = FakeGamma([raw_market(yes_price="0.5", best_bid=0.49, best_ask=0.50)])
    pressure = make_book("tokA", bids=(("0.49", "5000"),), asks=(("0.50", "500"),))
    run_cycle(make(gamma, FakeClob({"tokA": pressure}), strategies=[s]))
    assert "tokA" in Ledger.open(paths[0], KEY, paths[1]).state.positions
    Ledger.open(paths[0], KEY, paths[1]).record_promotion("", "destitué (test)", now=NOW + timedelta(minutes=1))
    clock["now"] = NOW + timedelta(minutes=30)
    risen = make_book("tokA", bids=(("0.55", "5000"),), asks=(("0.56", "500"),), ts=clock["now"])
    report = run_cycle(make(gamma, FakeClob({"tokA": risen}), strategies=[s]))
    state = Ledger.open(paths[0], KEY, paths[1]).state
    assert state.champion == "" and "tokA" not in state.positions, report.messages
    assert state.realized_pnl > 0
    types = [json.loads(l)["type"] for l in paths[0].read_text().splitlines()]
    assert types.count("BUY") == 1  # aucun rachat après la destitution

def test_regression_corrupt_database_is_set_aside_and_cycle_trades(env, paths, tmp_path, limits):
    """Défaut du 15/10/2026 (étape 8) : une base SQLite illisible faisait planter tous les
    cycles, indéfiniment. Elle est maintenant mise de côté (jamais effacée) et remplacée."""
    make, _, _ = env
    bad = tmp_path / "state" / "abimee.sqlite"
    bad.write_bytes(b"ceci n'est pas une base sqlite " * 200)
    db = Database(bad)
    assert db.recovered_from is not None and db.recovered_from.exists()
    deps = make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}))
    deps.db = db
    report = run_cycle(deps)
    db.close()
    assert report.status == "OK"
    assert any("illisible" in m for m in report.messages)
    assert report.shadows["fantome:naive_favorite_v1.0.0"]["fills"] == 1


def test_crash_mid_cycle_then_clean_resume(env, paths):
    """Panne inattendue pendant un cycle : rien d'écrit à moitié, le cycle suivant reprend."""
    make, _, clock = env

    class CrashingClob(FakeClob):
        def get_books(self, token_ids):
            raise RuntimeError("panne imprévue (test)")
    report = run_cycle(make(FakeGamma([raw_market()]), CrashingClob({})))
    assert report.status == "ERREUR" and report.exit_code == 1
    before = Ledger.open(paths[0], KEY, paths[1]).state
    assert before.cash == D("1000") and not before.positions
    clock["now"] = NOW + timedelta(minutes=5)
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book(ts=clock["now"])})))
    assert report.status == "OK"
    assert report.shadows["fantome:naive_favorite_v1.0.0"]["fills"] == 1


def test_price_history_is_cached_and_budgeted(tmp_path):
    """150 marchés suivis : l'historique de prix est gardé 20 min et relu au plus 40 fois par cycle."""
    from types import SimpleNamespace
    from polymarket_agent import main as cycle
    from polymarket_agent.market_scanner import parse_market

    calls = []

    class Clob:
        def get_price_history(self, token_id, start_ts, end_ts, fidelity=60):
            calls.append(token_id)
            return [(end_ts - 7 * 3600, 0.4), (end_ts - 2 * 3600, 0.5), (end_ts - 60, 0.55)]
    db = Database(tmp_path / "db.sqlite")
    markets = [parse_market(raw_market(market_id=str(i), yes_token=f"y{i}", no_token=f"n{i}")) for i in range(60)]
    deps = SimpleNamespace(db=db, clob=Clob())
    cycle._attach_price_features(deps, markets, NOW)
    assert len(calls) == cycle.PRICE_FEATURES_PER_CYCLE
    assert markets[0].yes_price_6h_ago == 0.4 and markets[0].yes_price_1h_ago == 0.5
    calls.clear()
    fresh = [parse_market(raw_market(market_id=str(i), yes_token=f"y{i}", no_token=f"n{i}")) for i in range(60)]
    cycle._attach_price_features(deps, fresh, NOW + timedelta(minutes=5))
    assert len(calls) == 20  # seuls les 20 marchés jamais lus ; les autres viennent du cache
    assert all(m.yes_price_6h_ago == 0.4 for m in fresh)
    db.close()


# --------------------------------------------------------------------------- ordres posés

def _patient(max_proposals="3"):
    inner = pipeline_strategy()
    inner.params["max_proposals_per_cycle"] = D(max_proposals)
    s = PatientOrders(inner, 1)
    s.mode = "principal"
    return s


def _ledger_types(path):
    return [json.loads(l)["type"] for l in path.read_text().splitlines()]


def test_resting_order_is_placed_then_filled_only_when_traded_through(env, paths, tmp_path):
    make, db, clock = env
    crown(paths)
    # Cycle 1 : écart 0,89 / 0,90 → achat posé à 0,89 (1 cran au-dessus de l'acheteur, sous le vendeur).
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}), strategies=[_patient()]))
    assert report.status == "OK", report.messages
    assert "BUY" not in _ledger_types(paths[0])  # rien n'est exécuté au moment de la pose
    orders = db.open_orders()
    assert len(orders) == 2 and {o["portfolio"] for o in orders} == {"principal", "fantome:naive_favorite_v1.0.0"}
    assert all(json.loads(o["proposal"])["max_price"] == "0.89" for o in orders)

    # Cycle 2 : le meilleur vendeur touche 0,89 → pas d'exécution (file d'attente inconnue).
    clock["now"] = NOW + timedelta(minutes=5)
    touch = make_book("tokA", bids=(("0.88", "500"),), asks=(("0.89", "500"),), ts=clock["now"])
    run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": touch}), strategies=[_patient()]))
    assert "BUY" not in _ledger_types(paths[0])

    # La stratégie a remis son prix à jour (0,88 / 0,89 → achat posé à 0,88) : l'ancien ordre est remplacé.
    assert {json.loads(o["proposal"])["max_price"] for o in db.open_orders()} == {"0.88"}
    assert db.conn.execute("SELECT COUNT(*) FROM pending_orders WHERE status='REMPLACE'").fetchone()[0] == 2

    # Cycle 3 : des vendeurs à 0,87 → le marché est passé au travers : 30 parts au prix posé 0,88.
    clock["now"] = NOW + timedelta(minutes=10)
    through = make_book("tokA", bids=(("0.86", "500"),), asks=(("0.87", "30"), ("0.95", "500")), ts=clock["now"])
    run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": through}), strategies=[_patient()]))
    state = Ledger.open(paths[0], KEY, paths[1]).state
    pos = state.positions["tokA"]
    # 30 parts passées au travers, moitié accessible : 15 au prix posé 0,88 (sans frais : barème
    # taker seulement).
    assert pos.shares == D("15") and pos.cost_basis == D("15") * D("0.88")
    assert state.fees_paid == 0
    buys = [json.loads(l) for l in paths[0].read_text().splitlines() if json.loads(l)["type"] == "BUY"]
    assert buys[0]["data"]["extra"]["order_type"] == "limite"


def test_resting_order_expires_and_never_fills_after(env, paths):
    make, db, clock = env
    crown(paths)
    settings = load_settings()
    settings["arena"] = yaml.safe_load((ROOT / "config" / "promotion.yaml").read_text(encoding="utf-8"))
    settings["arena"]["mise_avantage_mesure"] = None  # champion de test sans pari : copie entière
    settings["limit_orders"] = {"max_age_hours": 0.05, "max_open_per_portfolio": 30}  # 3 minutes
    run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}), settings, [_patient()]))
    assert len(db.open_orders()) == 2
    clock["now"] = NOW + timedelta(minutes=5)
    through = make_book("tokA", bids=(("0.70", "500"),), asks=(("0.71", "500"),), ts=clock["now"])
    run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": through}), settings, [pipeline_strategy()]))
    assert "BUY" not in [t for t in _ledger_types(paths[0])]
    statuses = {r["status"] for r in db.conn.execute("SELECT status FROM pending_orders")}
    assert statuses == {"EXPIRE"}


def test_resting_buys_cannot_reserve_more_than_the_cash(env, paths, tmp_path):
    make, db, _ = env
    crown(paths)
    markets = [raw_market(str(i), yes_token=f"y{i}", no_token=f"n{i}", event_id=f"e{i}") for i in range(6)]
    books = {f"y{i}": good_book(f"y{i}") for i in range(6)}
    settings = load_settings()
    settings["arena"] = yaml.safe_load((ROOT / "config" / "promotion.yaml").read_text(encoding="utf-8"))
    settings["arena"]["mise_avantage_mesure"] = None  # champion de test sans pari : copie entière
    settings["sante_strategies"] = {"base": 1.0}  # mise entière : la réservation doit refuser un ordre
    settings["fantomes"] = {}  # mise non plafonnée : c'est la réservation de l'argent qui est testée
    run_cycle(make(FakeGamma(markets), FakeClob(books), settings, [_patient("6")]))
    for name in ("principal", "fantome:naive_favorite_v1.0.0"):
        reserved = sum(D(o["remaining"]) * D(json.loads(o["proposal"])["max_price"])
                       for o in db.open_orders(name))
        assert 0 < reserved <= D("1000")
    reasons = [r[0] for r in db.conn.execute("SELECT reasons FROM decisions WHERE accepted = 0")]
    assert any("réservé" in r for r in reasons)  # Kelly complet : le 2e ordre ne tient plus dans le solde




def test_each_shadow_is_an_independent_scenario_for_liquidity(env, paths, tmp_path):
    """Chaque fantôme répond à « et si cette stratégie tradait seule » : il ne perd pas la liquidité
    prise par le principal (sinon l'arène pénaliserait la stratégie servie en dernier)."""
    make, _, _ = env
    crown(paths)
    run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()})))
    main = Ledger.open(paths[0], KEY, paths[1]).state
    shadow = Ledger.open(tmp_path / "fantome" / "naive_favorite_v1.0.0.jsonl", KEY, tmp_path / "fantome" / "x.lock").state
    assert main.positions["tokA"].shares == shadow.positions["tokA"].shares == D("10")  # 25 % des 40 parts


def test_orders_of_the_same_portfolio_share_the_book_in_a_cycle(env, paths, tmp_path):
    """Deux stratégies d'un même portefeuille sur le même jeton, au même cycle : la seconde ne
    retrouve pas la liquidité déjà prise par la première."""
    from polymarket_agent.main import CycleReport, Portfolio, _execute
    from polymarket_agent.models import MarketInfo  # noqa: F401
    from polymarket_agent.sources.polymarket_gamma import parse_market
    make, _, _ = env
    first, second = pipeline_strategy(), pipeline_strategy()
    second.strategy_id = "naive_bis"
    deps = make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}), strategies=[first, second])
    ledger = Ledger.create(tmp_path / "p.jsonl", KEY, tmp_path / "p.lock", "1000", now=NOW)
    portfolio = Portfolio("fantome:test", ledger, [first, second])
    market = parse_market(raw_market())
    _execute(deps, portfolio, [market], {"tokA": good_book()}, CycleReport("c1"), "b1", [market])
    assert ledger.state.positions["tokA"].shares == D("10")  # 10 au total (25 % de 40), pas 20



def test_strategy_health_halves_bets_until_proven_and_suspends_fee_burners(env, paths, tmp_path):
    """Mise prudente (½ Kelly tant qu'aucune prévision n'est jugée) et suspension d'une stratégie
    qui ne gagne pas ses frais : elle n'ouvre plus rien, ses sorties continuent."""
    from polymarket_agent import strategy_health
    make, db, clock = env
    deep = {"tokA": make_book("tokA", bids=(("0.89", "5000"),), asks=(("0.90", "100000"),))}
    full = load_settings()
    full["arena"] = yaml.safe_load((ROOT / "config" / "promotion.yaml").read_text(encoding="utf-8"))
    full["sante_strategies"] = {"base": 1.0}
    full["fantomes"] = {}  # mise non plafonnée : on compare ½ Kelly à Kelly complet
    run_cycle(make(FakeGamma([raw_market()]), FakeClob(deep), full))
    shadow_path = tmp_path / "fantome" / "naive_favorite_v1.0.0.jsonl"
    whole = Ledger.open(shadow_path, KEY, tmp_path / "x.lock").state.positions["tokA"].shares
    shadow_path.unlink()
    for f in (tmp_path / "fantome").glob("*"):
        f.unlink()
    run_cycle(make(FakeGamma([raw_market()]), FakeClob(deep)))  # réglage du dépôt : ½ Kelly au départ
    half = Ledger.open(shadow_path, KEY, tmp_path / "x.lock").state.positions["tokA"].shares
    assert abs(half - whole / 2) <= D("0.02")
    health = strategy_health.load(db, "naive_favorite_v1.0.0")
    assert health["prudence"] == 0.5 and health["jugees"] == 0 and health["suspendue"] is None


def test_forecast_score_beats_or_trails_the_market(tmp_path):
    from polymarket_agent import strategy_health
    db = Database(tmp_path / "db.sqlite")
    items = [{"token_id": f"t{i}", "market_id": f"m{i}", "p": 0.9, "price": 0.6, "ts": "x"} for i in range(4)]
    markets = {f"m{i}": raw_market(f"m{i}", f"t{i}", f"n{i}", closed=True,
                                   outcomePrices=json.dumps(["1", "0"] if i < 3 else ["0", "1"])) for i in range(4)}
    assert strategy_health.update_outcomes(db, markets.__getitem__, items, NOW) == 4
    s = strategy_health.score(db, items)
    assert s["jugees"] == 4 and s["brier"] == round((3 * 0.01 + 0.81) / 4, 4)
    assert s["avance"] == round(((3 * 0.16 + 0.36) - (3 * 0.01 + 0.81)) / 4, 4)  # 3 bons paris sur 4 à 0,9
    cfg = strategy_health.config({"sante_strategies": {"min_resolved": 4}})
    assert strategy_health.prudence(s, cfg) == (1.0 if s["avance"] > 0 else 0.25)
    assert strategy_health.prudence(dict(s, jugees=1), cfg) == 0.5
    db.close()


def test_fee_burner_is_suspended_only_after_enough_trades():
    from types import SimpleNamespace
    from polymarket_agent import strategy_health
    cfg = strategy_health.config({})
    burner = SimpleNamespace(realized_pnl=D("-40"), fees_paid=D("60"))   # brut +20, frais 60
    honest_loser = SimpleNamespace(realized_pnl=D("-40"), fees_paid=D("5"))  # brut −35 : perd avant frais
    winner = SimpleNamespace(realized_pnl=D("30"), fees_paid=D("60"))
    assert strategy_health.suspension(burner, 25, cfg) and not strategy_health.suspension(burner, 5, cfg)
    assert strategy_health.suspension(honest_loser, 25, cfg) is None  # l'élimination hebdomadaire s'en charge
    assert strategy_health.suspension(winner, 25, cfg) is None


def test_market_maker_quotes_both_sides_estimates_rewards_and_fills_when_traded_through(env, paths, tmp_path):
    """Tenue de marché (16/10/2026) : deux ordres posés (OUI et NON), récompense ESTIMÉE à part
    (jamais dans le journal), puis exécution du côté que le marché traverse."""
    from polymarket_agent.strategies_v2 import MarketMaker
    make, db, clock = env
    mm = MarketMaker("1.0.0", "2026-10-16", {
        "min_days_to_end": D("3"), "min_mid": D("0.15"), "max_mid": D("0.85"), "max_move_6h": D("0.03"),
        "min_reward_rate": D("5"), "improve_ticks": D("0"), "min_pair_margin": D("0.02"),
        "market_fraction": D("0.06"), "max_net_quotes": D("2"), "stop_loss": D("0.10"),
        "quote_hours": D("0.2"), "max_markets": D("12"), "max_candidates": D("30")})
    mm.mode = "fantome"
    raw = raw_market("mm", yes_token="Y", no_token="N", yes_price="0.485", best_bid=0.47, best_ask=0.50,
                     end=NOW + timedelta(days=10), rewardsMinSize=20, rewardsMaxSpread=3.5,
                     clobRewards=[{"rewardsDailyRate": 50}])

    def books(ybid, yask, ts):
        return {"Y": make_book("Y", bids=((ybid, "300"),), asks=((yask, "300"),), ts=ts),
                "N": make_book("N", bids=((str(D(1) - D(yask)), "300"),), asks=((str(D(1) - D(ybid)), "300"),), ts=ts)}
    report = run_cycle(make(FakeGamma([raw]), FakeClob(books("0.47", "0.50", NOW)), strategies=[mm]))
    assert report.status == "OK", report.messages
    orders = {(o["token_id"], o["side"]): json.loads(o["proposal"])["max_price"] for o in db.open_orders()}
    assert orders == {("Y", "BUY"): "0.47", ("N", "BUY"): "0.50"}
    est = db.conn.execute("SELECT part, montant FROM recompenses_estimees").fetchall()
    assert len(est) == 1 and est[0][0] > 0 and est[0][1] > 0
    shadow = tmp_path / "fantome" / "market_maker_v1.0.0.jsonl"
    assert "BUY" not in _ledger_types(shadow)

    # Cycle 2 : des vendeurs du OUI à 0,45 (le prix chute) → notre achat du OUI à 0,47 est servi.
    clock["now"] = NOW + timedelta(minutes=5)
    run_cycle(make(FakeGamma([raw]), FakeClob(books("0.44", "0.45", clock["now"])), strategies=[mm]))
    state = Ledger.open(shadow, KEY, tmp_path / "fantome" / "x.lock").state
    assert state.positions["Y"].cost_basis / state.positions["Y"].shares == D("0.47")
    assert state.fees_paid == 0  # ordre posé : pas de frais (barème preneur seulement)


def test_principal_never_buys_the_same_market_twice_for_two_strategies(env, paths):
    """Plusieurs stratégies au principal (18/10/2026) : si deux d'entre elles veulent le même marché
    dans le même cycle, seule la première l'achète."""
    from polymarket_agent.main import CycleReport, Portfolio, Weighted, _execute
    from polymarket_agent.sources.polymarket_gamma import parse_market
    make, _, _ = env
    deep = make_book("tokA", bids=(("0.89", "5000"),), asks=(("0.90", "5000"),))  # assez pour les deux
    deps = make(FakeGamma([raw_market()]), FakeClob({"tokA": deep}))
    twin = pipeline_strategy()
    twin.strategy_id = "nf_jumelle"
    main = Portfolio("principal", Ledger.open(paths[0], KEY, paths[1]),
                     [Weighted(pipeline_strategy(), D("0.5")), Weighted(twin, D("0.5"))])
    _execute(deps, main, [parse_market(raw_market())], {"tokA": deep}, CycleReport(cycle_id="c1"), "b1")
    buys = [json.loads(l)["data"] for l in paths[0].read_text().splitlines() if json.loads(l)["type"] == "BUY"]
    assert [b["strategy_id"] for b in buys] == ["naive_favorite"]


def test_a_book_reread_by_one_portfolio_is_reused_by_the_next_within_seconds(env):
    """19/10/2026 : plusieurs fantômes visent le même marché ; un carnet relu il y a moins de
    20 s dans le même cycle n'est pas relu une deuxième fois."""
    from polymarket_agent.main import _reread_book
    make, _, clock = env

    class Counting(FakeClob):
        reads = 0

        def get_book(self, token_id):
            Counting.reads += 1
            return good_book(ts=clock["now"])
    deps = make(FakeGamma([raw_market()]), Counting({"tokA": good_book()}))
    cache = {}
    assert _reread_book(deps, "tokA", cache) is _reread_book(deps, "tokA", cache) and Counting.reads == 1
    clock["now"] = NOW + timedelta(seconds=30)  # trop vieux : relu
    _reread_book(deps, "tokA", cache)
    _reread_book(deps, "tokA", None)  # sans mémoire : toujours relu
    assert Counting.reads == 3


def test_idle_ghost_beats_only_every_half_hour_and_cycle_publishes_timings(env, paths, tmp_path):
    """21/10/2026 : les battements faisaient 92,5 % des lignes des journaux fantômes. Un fantôme
    qui n'a rien écrit pendant le cycle ne bat plus qu'à intervalle (`cycle.battement_fantomes_minutes`) ;
    le principal bat à chaque cycle. Le minutage et les abstentions sont publiés dans la base."""
    make, db, clock = env
    deps = make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}),
                strategies=[pipeline_strategy("fantome")])
    shadow_path = tmp_path / "fantome" / "naive_favorite_v1.0.0.jsonl"

    def beats(path):
        return sum(json.loads(l)["type"] == "HEARTBEAT" for l in path.read_text().splitlines())
    run_cycle(deps)  # achat du fantôme : il a écrit, il bat
    assert beats(shadow_path) == 1 and beats(paths[0]) == 1
    clock["now"] = NOW + timedelta(minutes=5)
    run_cycle(deps)  # rien écrit, battement récent : pas de battement
    assert beats(shadow_path) == 1 and beats(paths[0]) == 2
    clock["now"] = NOW + timedelta(minutes=31)
    run_cycle(deps)
    assert beats(shadow_path) == 2 and beats(paths[0]) == 3
    timings = json.loads(db.get_value("durees_cycle"))["etapes"]
    assert {"reglements", "scanner", "references", "carnets", "fantomes", "total"} <= set(timings)
    reasons = json.loads(db.get_value("abstentions"))["portefeuilles"]["fantome:naive_favorite_v1.0.0"]
    assert reasons["naive_favorite"]["marches"] == 1


def test_round_robin_and_once_gamma():
    from polymarket_agent.main import _OnceGamma, _round_robin
    assert _round_robin([["a1", "a2"], ["b1"], [], ["c1", "c2", "c3"]]) == ["a1", "b1", "c1", "a2", "c2", "c3"]
    gamma = FakeGamma([raw_market("m1")])
    calls = []
    real = gamma.get_market
    gamma.get_market = lambda mid: calls.append(mid) or real(mid)
    once = _OnceGamma(gamma)
    assert once.get_market("m1") is once.get_market("m1") and calls == ["m1"]
    for _ in range(2):  # l'erreur aussi est gardée : un seul appel
        with pytest.raises(SourceUnavailable):
            once.get_market("inconnu")
    assert calls == ["m1", "inconnu"]
    assert once.list_markets() == gamma.markets  # le reste passe au vrai client


def test_settlement_reads_held_markets_by_batches():
    """21/10/2026 : 723 marchés détenus relus un par un (pause de 0,2 s entre deux requêtes) = 79 s
    de règlements. Lus par lots (fermés puis ouverts) ; un marché absent des lots ou un lot en erreur
    retombe sur la lecture une par une."""
    from polymarket_agent.main import _OnceGamma

    class Batch(FakeGamma):
        def __init__(self, markets):
            super().__init__(markets)
            self.batches, self.singles = [], []

        def markets_by_ids(self, ids, *, closed):
            self.batches.append((len(ids), closed))
            if closed and len(ids) == 1:
                raise SourceUnavailable("lot en panne (test)")
            return [m for m in self.markets if m["id"] in ids and bool(m.get("closed")) == closed]

        def get_market(self, market_id):
            self.singles.append(market_id)
            return super().get_market(market_id)
    gamma = Batch([dict(raw_market("1"), closed=True), raw_market("2"), raw_market("3")])
    once = _OnceGamma(gamma)
    once.prefetch(["1", "2", "3", "absent"], batch=3)
    assert gamma.batches == [(3, True), (3, False), (1, True), (1, False)]
    assert once.get_market("1")["closed"] is True and once.get_market("2")["id"] == "2" and gamma.singles == []
    with pytest.raises(SourceUnavailable):
        once.get_market("absent")  # absent des lots : lu une fois seul (inconnu du faux Gamma)
    assert gamma.singles == ["absent"]
    once.prefetch(["1"], batch=1)  # lot d'un seul : rien à gagner, lecture normale
    assert len(gamma.batches) == 4

    class Poisoned(Batch):  # Gamma refuse tout lot qui contient un marché supprimé
        def markets_by_ids(self, ids, *, closed):
            self.batches.append((len(ids), closed))
            if "mort" in ids:
                raise SourceUnavailable("HTTP 404 (test)")
            return [m for m in self.markets if m["id"] in ids and bool(m.get("closed")) == closed]
    ids = [str(i) for i in range(16)] + ["mort"]
    poisoned = Poisoned([dict(raw_market(i), closed=True) for i in ids if i != "mort"])
    once = _OnceGamma(poisoned)
    once.prefetch(ids, batch=100)
    # Coupé en deux (deux fois) : 12 marchés lus par lots ; le petit lot du marché supprimé est lu un par un.
    assert len(once.cache) == 12 and not once.down
    assert once.get_market("15")["id"] == "15" and poisoned.singles == ["15"]

    class Down(Batch):
        def markets_by_ids(self, ids, *, closed):
            self.batches.append((len(ids), closed))
            raise SourceUnavailable("HTTP 404 (panne, test)")
    down = Down([raw_market("1")])
    once = _OnceGamma(down)
    once.prefetch([str(i) for i in range(250)], batch=100)
    assert once.down and len(down.batches) <= 30  # premier lot seulement, puis arrêt
    with pytest.raises(SourceUnavailable):
        once.get_market("1")
    assert down.singles == []  # pas 250 lectures une par une pendant une panne


def test_settled_bets_are_judged_from_the_journal_and_proven_winners_bet_more(tmp_path):
    """« Grossir les gagnantes » (Etienne, 21/10/2026) : une prévision réglée dans le journal du fantôme
    est jugée tout de suite (avant : 15 vérifications par heure pour toute l'arène, personne n'atteignait
    20 jugées) ; renfort jusqu'à 2 pour qui prouve plus d'avantage qu'il n'en suppose."""
    from polymarket_agent import strategy_health
    db = Database(tmp_path / "db.sqlite")
    entries = [{"type": "SETTLE", "data": {"token_id": "t1", "payout_per_share": "1"}},
               {"type": "SETTLE", "data": {"token_id": "t2", "payout_per_share": "0"}},
               {"type": "RESET", "data": {}},
               {"type": "SETTLE", "data": {"token_id": "t3", "payout_per_share": "1"}}]
    assert strategy_health.settled_outcomes(entries) == {"t3": 1.0}  # une remise à zéro repart de rien
    items = [{"token_id": f"t{i}", "market_id": f"m{i}", "p": 0.9, "price": 0.8, "ts": "x"} for i in range(25)]
    settled = {f"t{i}": 1.0 for i in range(25)}
    s = strategy_health.score(db, items, settled)
    assert s["jugees"] == 25 and s["avance"] > 0
    cfg = strategy_health.config({"sante_strategies": {"renfort": {"min_operations": 30, "confiance_jour_min": 0.8,
                                                                   "paris_fictifs": 30, "max": 2.0}}})
    assert strategy_health.prudence(s, cfg) == 1.0  # prouvée : mise entière (au lieu de ½)
    row = {"closed_trades": 60, "excess_wins": 6.8, "assumed_edge": 0.0509, "day_confidence": 0.95}
    assert strategy_health.boost(row, cfg) == round(6.8 / 90 / 0.0509, 4)  # contrer_crypto_patiente : ≈ 1,48
    assert strategy_health.boost(dict(row, excess_wins=40), cfg) == 2.0  # plafond
    assert strategy_health.boost(dict(row, excess_wins=1.0), cfg) == 1.0  # moins que supposé : pas de renfort
    assert strategy_health.boost(dict(row, closed_trades=20), cfg) == 1.0  # trop tôt
    assert strategy_health.boost(dict(row, day_confidence=0.7), cfg) == 1.0  # une belle journée ne suffit pas
    assert strategy_health.boost(row, strategy_health.config({})) == 1.0  # sans réglage : aucun renfort
    real = strategy_health.config(load_settings())
    assert real["renfort"]["max"] == 2.0 and real["renfort"]["min_operations"] == 30


def test_principal_order_is_dropped_when_the_copied_ghost_has_no_order_left(env, paths):
    """Enquête 23/10/2026 (contrer_crypto_patiente) : le fantôme remplace son ordre posé à chaque cycle ; si le
    principal garde l'ancien (copie du nouveau refusée), il achète à l'ancien prix un pari que le fantôme n'a pas fait."""
    make, db, clock = env
    crown(paths)
    run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}), strategies=[_patient()]))
    ghost = "fantome:naive_favorite_v1.0.0"
    ghost_order = db.open_orders(ghost)[0]
    db.update_order(ghost_order["op_id"], remaining=ghost_order["remaining"], fills=0, status="REMPLACE", now=NOW)
    assert len(db.open_orders("principal")) == 1

    clock["now"] = NOW + timedelta(minutes=5)
    through = make_book("tokA", bids=(("0.80", "500"),), asks=(("0.85", "500"),), ts=clock["now"])
    run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": through}), strategies=[_patient()]))
    assert "BUY" not in _ledger_types(paths[0])
    statuses = [r["status"] for r in db.conn.execute(
        "SELECT status FROM pending_orders WHERE portfolio='principal' AND op_id=?", (db.conn.execute(
            "SELECT op_id FROM pending_orders WHERE portfolio='principal' ORDER BY created_at LIMIT 1").fetchone()[0],))]
    assert statuses == ["ANNULE"]
