"""Stratégie de référence naïve et chargement des paramètres bornés."""

from __future__ import annotations

from decimal import Decimal

import pytest

from conftest import NOW, ROOT, make_book, raw_market
from polymarket_agent.safety_controller import evaluate
from polymarket_agent.main import market_context
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategy_engine import (NaiveFavorite, StrategyConfigError, load_params,
                                              load_strategies, make_op_id)

D = Decimal


def strategy(**overrides):
    params = {"min_ask": D("0.80"), "max_ask": D("0.95"), "bias": D("0.05"),
              "uncertainty": D("0.015"), "min_net_edge": D("0.02"), "max_extra_ticks": D("2"),
              "max_proposals_per_cycle": D("3")}
    params.update(overrides)
    return NaiveFavorite("1.0.0", "2026-10-14", params)


def test_repository_config_loads():
    loaded = load_strategies(ROOT / "config" / "strategies.yaml")
    assert [s.strategy_id for s in loaded] == ["naive_favorite"]
    assert loaded[0].version == "1.0.0"


def test_param_outside_bounds_is_refused():
    with pytest.raises(StrategyConfigError):
        load_params({"bias": {"value": 0.5, "min": 0, "max": 0.06}})


def test_proposes_buy_on_favorite_and_controller_accepts(ledger, limits):
    market = parse_market(raw_market())
    book = make_book("tokA", bids=(("0.89", "500"),), asks=(("0.90", "300"),))
    out = strategy().propose([market], {"tokA": book}, ledger.state, limits, "B1")
    assert len(out.proposals) == 1
    p = out.proposals[0]
    assert p.side == "BUY" and p.token_id == "tokA" and p.outcome == "Yes"
    assert p.prob_low < p.est_probability < p.prob_high
    assert p.net_edge >= limits.min_net_edge_floor
    verdict = evaluate(p, ledger.state, market_context(market, book, "tokA"), limits, NOW)
    assert verdict.accepted, verdict.reasons


def test_picks_no_token_when_no_is_favorite(ledger, limits):
    market = parse_market(raw_market(yes_price="0.1", best_bid=0.09, best_ask=0.10))
    book = make_book("tokB", bids=(("0.89", "500"),), asks=(("0.90", "300"),))
    out = strategy().propose([market], {"tokB": book}, ledger.state, limits, "B1")
    assert out.proposals[0].token_id == "tokB" and out.proposals[0].outcome == "No"


def test_abstains_without_data_or_edge(ledger, limits):
    market = parse_market(raw_market())
    s = strategy()
    assert s.propose([market], {}, ledger.state, limits, "B1").abstentions == {"carnet indisponible": 1}
    wide = make_book("tokA", bids=(("0.80", "500"),), asks=(("0.90", "300"),))  # milieu 0,85
    assert s.propose([market], {"tokA": wide}, ledger.state, limits, "B1").abstentions == {
        "avantage net insuffisant": 1}
    cheap = make_book("tokA", bids=(("0.50", "500"),), asks=(("0.51", "300"),))
    assert not s.propose([market], {"tokA": cheap}, ledger.state, limits, "B1").proposals


def test_never_proposes_below_the_floor_even_if_configured_lower(ledger, limits):
    market = parse_market(raw_market())
    book = make_book("tokA", bids=(("0.89", "500"),), asks=(("0.90", "300"),))
    out = strategy(min_net_edge=D("0"), bias=D("0.025")).propose(
        [market], {"tokA": book}, ledger.state, limits, "B1")
    assert all(p.net_edge >= limits.min_net_edge_floor for p in out.proposals)


def test_op_id_is_deterministic():
    assert make_op_id("B1", "s", "1", "t", "BUY") == make_op_id("B1", "s", "1", "t", "BUY")
    assert make_op_id("B1", "s", "1", "t", "BUY") != make_op_id("B2", "s", "1", "t", "BUY")


def test_regression_default_config_can_trade_a_tight_favorite(ledger, limits):
    """Défaut du 14/10/2026 : avec biais 0,04 et incertitude 0,02, la borne basse
    (milieu + 0,02) ne pouvait jamais dépasser prix + frais + 0,02 : aucune position possible."""
    s = load_strategies(ROOT / "config" / "strategies.yaml")[0]
    market = parse_market(raw_market())
    book = make_book("tokA", bids=(("0.89", "500"),), asks=(("0.90", "300"),))
    assert len(s.propose([market], {"tokA": book}, ledger.state, limits, "B1").proposals) == 1


# --------------------------------------------------------------------------- calibration


def calibrated(tmp_path, delta, n_events=500, key="sports|13-72h|0.85-0.90", **params):
    from polymarket_agent import calibration
    from polymarket_agent.calibration import Cell
    from polymarket_agent.strategy_engine import CalibratedStrategy
    table = {key: Cell(key, 2000, n_events, 0.875, 0.875 + delta, delta, delta - 0.01, delta + 0.01, delta)}
    calibration.save(table, tmp_path / "table.json", {"version": "test"})
    base = {"min_events": D("150"), "min_net_edge": D("0.02"), "max_extra_ticks": D("2"),
            "max_proposals_per_cycle": D("3")}
    base.update(params)
    return CalibratedStrategy("1.0.0", "2026-10-14", base, tmp_path / "table.json")


def sports_market(**kw):
    raw = raw_market(feeType="sports_fees_v3",
                     schedule={"exponent": 1, "rate": 0.05, "takerOnly": True}, **kw)
    return parse_market(raw)


def books_for(yes_bid="0.87", yes_ask="0.88"):
    no_bid, no_ask = str(D(1) - D(yes_ask)), str(D(1) - D(yes_bid))
    return {"tokA": make_book("tokA", bids=((yes_bid, "500"),), asks=((yes_ask, "500"),)),
            "tokB": make_book("tokB", bids=((no_bid, "500"),), asks=((no_ask, "500"),))}


def test_calibrated_buys_underpriced_favorite(tmp_path, ledger, limits):
    s = calibrated(tmp_path, delta=0.06)  # le favori à 0,875 gagne en réalité 93,5 %
    out = s.propose([sports_market()], books_for(), ledger.state, limits, "B1")
    assert len(out.proposals) == 1
    p = out.proposals[0]
    assert p.token_id == "tokA" and p.outcome == "Yes"
    assert p.prob_low == D("0.925")
    market = sports_market()
    assert evaluate(p, ledger.state, market_context(market, books_for()["tokA"], "tokA"),
                    limits, NOW).accepted


def test_calibrated_buys_underdog_when_favorite_is_overpriced(tmp_path, ledger, limits):
    s = calibrated(tmp_path, delta=-0.07)  # le favori à 0,875 ne gagne que 80,5 %
    out = s.propose([sports_market()], books_for(), ledger.state, limits, "B1")
    assert out.proposals[0].token_id == "tokB" and out.proposals[0].outcome == "No"


def test_calibrated_abstains_without_measured_edge(tmp_path, ledger, limits):
    assert not calibrated(tmp_path, delta=0.0).propose(
        [sports_market()], books_for(), ledger.state, limits, "B1").proposals
    small = calibrated(tmp_path, delta=0.06, n_events=40)  # trop peu d'événements
    out = small.propose([sports_market()], books_for(), ledger.state, limits, "B1")
    assert out.abstentions == {"case de calibration absente ou trop petite": 1}
    # Horizon hors table (marché « crypto » : aucune case) → abstention.
    crypto = parse_market(raw_market(feeType="crypto_fees_v2",
                                     schedule={"exponent": 1, "rate": 0.07, "takerOnly": True}))
    assert not calibrated(tmp_path, delta=0.06).propose([crypto], books_for(), ledger.state,
                                                        limits, "B1").proposals


def test_calibrated_respects_dataset_volume_universe(tmp_path, ledger, limits):
    s = calibrated(tmp_path, delta=0.06, min_volume=D("200000"))
    out = s.propose([sports_market()], books_for(), ledger.state, limits, "B1")
    assert out.abstentions == {"volume cumulé sous le seuil de l'historique": 1}
