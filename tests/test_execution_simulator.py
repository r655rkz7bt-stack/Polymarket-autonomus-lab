"""Simulateur d'exécution (taker et ordres posés) et frais."""

from __future__ import annotations

from decimal import Decimal

import pytest

from conftest import make_book
from polymarket_agent.execution_simulator import (maker_fee, simulate_buy, simulate_resting_buy,
                                                  simulate_resting_sell, simulate_sell)
from polymarket_agent.fees import UnknownFees, taker_fee
from polymarket_agent.models import FeeSchedule

D = Decimal
FEES = FeeSchedule(enabled=True, rate=D("0.04"), exponent=D("1"))
NO_FEES = FeeSchedule(enabled=False, rate=None, exponent=None)


def test_buy_walks_the_book_with_slippage_and_fees():
    book = make_book(asks=(("0.90", "100"), ("0.91", "200")))
    fill = simulate_buy(book, D("150"), D("0.92"), FEES)
    assert fill.status == "FILLED"
    assert fill.filled_shares == D("150")
    assert fill.notional == D("90") + D("45.5")
    assert fill.avg_price > D("0.90")  # slippage : on paie plus que le meilleur prix
    expected_fee = taker_fee(D("100"), D("0.90"), FEES) + taker_fee(D("50"), D("0.91"), FEES)
    assert fill.fee == expected_fee > 0


def test_partial_fill_when_depth_is_missing():
    book = make_book(asks=(("0.90", "100"), ("0.95", "500")))
    fill = simulate_buy(book, D("300"), D("0.92"), FEES)
    assert fill.status == "PARTIAL"
    assert fill.filled_shares == D("100")


def test_order_not_executed_is_not_executed():
    book = make_book(asks=(("0.90", "100"),))
    fill = simulate_buy(book, D("50"), D("0.89"), FEES)
    assert fill.status == "UNFILLED"
    assert not fill.executed
    assert fill.filled_shares == 0 and fill.fee == 0
    empty = make_book(asks=())
    assert not simulate_buy(empty, D("50"), D("0.99"), FEES).executed


def test_sell_walks_bids():
    book = make_book(bids=(("0.89", "30"), ("0.88", "100")))
    fill = simulate_sell(book, D("50"), D("0.85"), FEES)
    assert fill.filled_shares == D("50")
    assert fill.notional == D("30") * D("0.89") + D("20") * D("0.88")


def test_fee_formula_and_rounding():
    # 100 parts à 0,50, taux 0,04 : 100 × 0,04 × 0,25 = 1
    assert taker_fee(D("100"), D("0.5"), FEES) == D("1.0000")
    # arrondi vers le haut au 1/10 000
    assert taker_fee(D("1"), D("0.9"), FEES) == D("0.0036")
    assert taker_fee(D("0.01"), D("0.5"), FEES) == D("0.0001")
    assert taker_fee(D("100"), D("0.5"), NO_FEES) == 0


def test_unknown_fees_raise():
    with pytest.raises(UnknownFees):
        taker_fee(D("1"), D("0.5"), FeeSchedule(enabled=None, rate=None, exponent=None))
    with pytest.raises(UnknownFees):
        taker_fee(D("1"), D("0.5"), FeeSchedule(enabled=True, rate=None, exponent=None))


def test_simulation_is_deterministic():
    book = make_book(asks=(("0.90", "100"), ("0.91", "200")))
    results = {simulate_buy(book, D("123.456"), D("0.95"), FEES).fee for _ in range(5)}
    assert len(results) == 1
    assert simulate_buy(book, D("123.456"), D("0.95"), FEES).filled_shares == D("123.45")


# --------------------------------------------------------------------------- ordres posés
TAKER_ONLY = FeeSchedule(enabled=True, rate=D("0.04"), exponent=D("1"), taker_only=True)
MAKER_PAYS = FeeSchedule(enabled=True, rate=D("0.04"), exponent=D("1"), taker_only=False)


def test_resting_buy_needs_the_market_to_trade_through():
    """Toucher notre prix ne suffit pas (file d'attente inconnue) : il faut des vendeurs
    un tick SOUS notre prix limite."""
    touch = make_book(asks=(("0.50", "500"),))  # tick 0,01
    assert simulate_resting_buy(touch, D("100"), D("0.50"), TAKER_ONLY).status == "UNFILLED"
    above = make_book(asks=(("0.52", "500"),))
    assert not simulate_resting_buy(above, D("100"), D("0.50"), TAKER_ONLY).executed
    through = make_book(asks=(("0.49", "60"), ("0.50", "500")))
    fill = simulate_resting_buy(through, D("100"), D("0.50"), TAKER_ONLY)
    assert fill.status == "PARTIAL" and fill.filled_shares == D("60")  # seulement la quantité passée au travers
    assert fill.avg_price == D("0.50")  # au prix limite, jamais mieux (0,49 n'est pas gagné)
    assert fill.fee == 0 and fill.levels == [("0.50", "60.00")]


def test_resting_sell_symmetry_and_consumed_depth():
    book = make_book(bids=(("0.62", "80"), ("0.61", "40"), ("0.60", "1000")))
    assert not simulate_resting_sell(book, D("50"), D("0.62"), TAKER_ONLY).executed  # toucher
    fill = simulate_resting_sell(book, D("200"), D("0.60"), TAKER_ONLY)
    assert fill.filled_shares == D("120") and fill.avg_price == D("0.60")
    # La même contrepartie ne sert pas deux fois au même portefeuille pendant un cycle.
    again = simulate_resting_sell(book, D("200"), D("0.60"), TAKER_ONLY, consumed=D("100"))
    assert again.filled_shares == D("20")
    assert not simulate_resting_sell(book, D("10"), D("0.60"), TAKER_ONLY, consumed=D("120")).executed


def test_maker_fee_is_zero_only_when_schedule_says_taker_only():
    assert maker_fee(D("100"), D("0.5"), TAKER_ONLY) == 0
    assert maker_fee(D("100"), D("0.5"), NO_FEES) == 0
    assert maker_fee(D("100"), D("0.5"), MAKER_PAYS) == taker_fee(D("100"), D("0.5"), MAKER_PAYS) > 0
    with pytest.raises(UnknownFees):
        maker_fee(D("1"), D("0.5"), FeeSchedule(enabled=None, rate=None, exponent=None))
    book = make_book(asks=(("0.40", "100"),))
    fill = simulate_resting_buy(book, D("100"), D("0.50"), MAKER_PAYS)
    assert fill.fee == taker_fee(D("100"), D("0.50"), MAKER_PAYS)


def test_resting_order_rejects_bad_tick_and_zero_size():
    book = make_book(asks=(("0.40", "100"),))
    assert simulate_resting_buy(book, D("0.001"), D("0.50"), TAKER_ONLY).reason == "taille nulle"
    book.tick_size = D("0")
    assert "tick" in simulate_resting_buy(book, D("10"), D("0.50"), TAKER_ONLY).reason
