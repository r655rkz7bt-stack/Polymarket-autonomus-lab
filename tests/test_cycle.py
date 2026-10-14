"""Cycle complet avec des API factices : flux de bout en bout et scénarios de panne."""

from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal

import pytest

from conftest import KEY, NOW, ROOT, buy, make_book, raw_market
from polymarket_agent.config import load_settings
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.ledger import Ledger
from polymarket_agent.main import EXIT_HALT, CycleDeps, run_cycle
from polymarket_agent.persistence import Database
from polymarket_agent.safety_controller import RealModeForbidden
from polymarket_agent.strategy_engine import load_strategies

D = Decimal


class FakeGamma:
    def __init__(self, markets=None, fail=False):
        self.markets, self.fail, self.calls = markets or [], fail, 0

    def list_markets(self, **kwargs):
        self.calls += 1
        if self.fail:
            raise SourceUnavailable("Gamma en panne (test)")
        return self.markets


class FakeClob:
    def __init__(self, books, fresh=None, fail=False):
        self.books, self.fresh, self.fail = books, fresh, fail

    def get_books(self, token_ids):
        if self.fail:
            raise SourceUnavailable("CLOB en panne (test)")
        return {t: self.books[t] for t in token_ids if t in self.books}

    def get_book(self, token_id):
        return (self.fresh or self.books)[token_id]


@pytest.fixture
def env(tmp_path, ledger, paths, limits):
    db = Database(tmp_path / "state" / "market.sqlite")
    db.set_anchor(ledger.state.last_seq, ledger.state.last_hash, NOW)
    clock = {"now": NOW}

    def make(gamma, clob, settings=None):
        return CycleDeps(settings=settings or load_settings(), limits=limits,
                         strategies=load_strategies(ROOT / "config" / "strategies.yaml"),
                         ledger_path=paths[0], lock_path=paths[1], key=KEY, db=db,
                         gamma=gamma, clob=clob, now=lambda: clock["now"])
    yield make, db, clock
    db.close()


def good_book(token="tokA", ts=NOW):
    return make_book(token, bids=(("0.89", "500"),), asks=(("0.90", "40"), ("0.91", "500")), ts=ts)


def test_full_cycle_executes_and_books_a_simulated_trade(env, paths):
    make, db, _ = env
    report = run_cycle(make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()})))
    assert report.status == "OK", report.messages
    assert report.counts["fills"] == 1
    reopened = Ledger.open(paths[0], KEY, paths[1])
    pos = reopened.state.positions["tokA"]
    # À 0,91 l'avantage passe sous le plancher : prix limite 0,90, seules 40 parts
    # y sont disponibles → exécution partielle, jamais au-delà du prix limite.
    assert pos.shares == D("40")
    assert reopened.state.fees_paid > 0
    assert reopened.state.cash + pos.cost_basis == D("1000")
    types = [json.loads(l)["type"] for l in paths[0].read_text().splitlines()]
    assert types == ["GENESIS", "BUY", "HEARTBEAT"]
    row = db.conn.execute("SELECT accepted, fill_status FROM decisions").fetchone()
    assert row["accepted"] == 1 and row["fill_status"] == "PARTIAL"
    assert db.get_anchor()[0] == reopened.state.last_seq


def test_rerun_in_same_bucket_does_not_double_book(env, paths):
    make, _, clock = env
    deps = make(FakeGamma([raw_market()]), FakeClob({"tokA": good_book()}))
    run_cycle(deps)
    cash = Ledger.open(paths[0], KEY, paths[1]).state.cash
    clock["now"] = NOW + timedelta(seconds=30)
    run_cycle(deps)
    assert Ledger.open(paths[0], KEY, paths[1]).state.cash == cash


def test_unavailable_source_does_not_block_the_program(env, paths):
    make, _, clock = env
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
    moved = make_book("tokA", bids=(("0.93", "500"),), asks=(("0.97", "500"),))
    report = run_cycle(make(FakeGamma([raw_market()]),
                            FakeClob({"tokA": good_book()}, fresh={"tokA": moved})))
    assert report.counts["fills"] == 0
    assert not Ledger.open(paths[0], KEY, paths[1]).state.positions


def test_stale_book_on_reread_means_no_trade(env, paths):
    make, _, _ = env
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
    settings["mode"] = "real"
    with pytest.raises(RealModeForbidden):
        run_cycle(make(FakeGamma(), FakeClob({}), settings))
