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
    assert sorted(s.strategy_id for s in loaded) == [
        "calibration", "cross_market", "crypto_threshold", "information_advantage", "market_structure",
        "naive_favorite", "news_momentum", "reversion", "social_sentiment"]
    assert all(s.params["kelly_fraction"] == 1 for s in loaded if "kelly_fraction" in s.params)


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
    assert p.net_edge >= D("0.02")  # le min_net_edge de la stratégie
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


def test_strategy_is_free_to_lower_its_own_edge_threshold(ledger, limits):
    """Liberté totale : plus de plancher imposé, la stratégie choisit son seuil."""
    market = parse_market(raw_market())
    book = make_book("tokA", bids=(("0.89", "500"),), asks=(("0.90", "300"),))
    strict = strategy(min_net_edge=D("0.02"), bias=D("0.03"))
    free = strategy(min_net_edge=D("0"), bias=D("0.03"))
    assert not strict.propose([market], {"tokA": book}, ledger.state, limits, "B1").proposals
    assert free.propose([market], {"tokA": book}, ledger.state, limits, "B1").proposals


def test_op_id_is_deterministic():
    assert make_op_id("B1", "s", "1", "t", "BUY") == make_op_id("B1", "s", "1", "t", "BUY")
    assert make_op_id("B1", "s", "1", "t", "BUY") != make_op_id("B2", "s", "1", "t", "BUY")


def test_regression_default_config_can_trade_a_tight_favorite(ledger, limits):
    """Défaut du 14/10/2026 : avec biais 0,04 et incertitude 0,02, la borne basse
    (milieu + 0,02) ne pouvait jamais dépasser prix + frais + 0,02 : aucune position possible."""
    s = strategy()  # paramètres de config/strategies.yaml au 14/10/2026 (biais 0,05, incertitude 0,015)
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


# --------------------------------------------------------------------------- reversion


def reversion(tmp_path, delta_drop=0.15):
    from polymarket_agent import calibration
    from polymarket_agent.calibration import Cell
    from polymarket_agent.strategy_engine import ReversionStrategy
    table = {"baisse": Cell("baisse", 5000, 1800, 0.6, 0.6 + delta_drop, delta_drop,
                            delta_drop - 0.03, delta_drop + 0.01, delta_drop - 0.01),
             "hausse": Cell("hausse", 20000, 4000, 0.84, 0.83, -0.013, -0.018, -0.008, -0.013)}
    calibration.save(table, tmp_path / "rev.json", {"version": "test"})
    params = {"min_move": D("0.10"), "min_changes_24h": D("4"), "min_events": D("150"),
              "min_net_edge": D("0.02"), "max_extra_ticks": D("2"), "max_proposals_per_cycle": D("3")}
    return ReversionStrategy("1.0.0", "2026-10-14", params, tmp_path / "rev.json")


def moved_market(before, changes=10):
    m = sports_market()
    m.yes_price_6h_ago, m.changes_24h = before, changes
    return m


def test_reversion_buys_favorite_after_sharp_drop(tmp_path, ledger, limits):
    out = reversion(tmp_path).propose([moved_market(0.75)], books_for("0.59", "0.60"),
                                      ledger.state, limits, "B1")
    assert len(out.proposals) == 1
    p = out.proposals[0]
    assert p.token_id == "tokA" and p.prob_low == D("0.7150")
    assert "reversion:baisse" in p.sources


def test_reversion_abstains_without_move_history_or_activity(tmp_path, ledger, limits):
    s = reversion(tmp_path)
    books = books_for("0.59", "0.60")
    assert s.propose([moved_market(0.62)], books, ledger.state, limits, "B1").abstentions == {
        "pas de mouvement brusque": 1}
    assert s.propose([moved_market(None)], books, ledger.state, limits, "B1").abstentions == {
        "historique de prix indisponible": 1}
    assert s.propose([moved_market(0.75, changes=2)], books, ledger.state, limits, "B1").abstentions == {
        "marché trop peu actif sur 24 h": 1}


def test_reversion_uses_real_book_not_history(tmp_path, ledger, limits):
    """Le piège du backtest : un prix historique bas sans vendeur réel à ce prix.
    En réel, l'ask du carnet est haut (0,74) : aucun avantage, aucune proposition."""
    out = reversion(tmp_path).propose([moved_market(0.75)], books_for("0.46", "0.74"),
                                      ledger.state, limits, "B1")
    assert not out.proposals
