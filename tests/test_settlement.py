"""Règlements des marchés résolus et groupes de corrélation."""

from __future__ import annotations

import json
from decimal import Decimal

import pytest

from conftest import NOW, buy, raw_market
from polymarket_agent.correlation import correlation_group
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.settlement import resolution_payout, settle_positions
from polymarket_agent.sources.polymarket_gamma import parse_market

D = Decimal


def resolved(prices=("1", "0"), status="resolved", closed=True, tokens=("tokA", "tokB")):
    return {"closed": closed, "umaResolutionStatus": status, "outcomes": json.dumps(["Yes", "No"]),
            "outcomePrices": json.dumps(list(prices)), "clobTokenIds": json.dumps(list(tokens))}


@pytest.mark.parametrize("prices,token,payout", [
    (("1", "0"), "tokA", D("1")), (("1", "0"), "tokB", D("0")),
    (("0", "1"), "tokB", D("1")), (("0.5", "0.5"), "tokA", D("0.5")),
])
def test_final_payouts(prices, token, payout):
    assert resolution_payout(resolved(prices), token)[0] == payout


@pytest.mark.parametrize("raw", [
    resolved(closed=False), resolved(status="proposed"), resolved(status="disputed"),
    resolved(prices=("0.9995", "0.0005")), resolved(prices=("1", "1")), resolved(tokens=("x", "y")),
])
def test_not_yet_settled_waits(raw):
    assert resolution_payout(raw, "tokA") is None


class Gamma:
    def __init__(self, markets, fail=()):
        self.markets, self.fail = markets, set(fail)

    def get_market(self, market_id):
        if market_id in self.fail:
            raise SourceUnavailable("test")
        return self.markets[market_id]


def test_settle_positions_books_win_loss_and_skips_unresolved(ledger):
    buy(ledger, "b1", token="tokA", shares="100", price="0.9", fee="0.36")   # gagne
    buy(ledger, "b2", token="tokC", shares="50", price="0.8", fee="0.32")    # perd
    buy(ledger, "b3", token="tokE", shares="10", price="0.5")                # pas encore réglé
    buy(ledger, "b4", token="tokG", shares="10", price="0.5")                # Gamma en panne
    gamma = Gamma({"m-tokA": resolved(("1", "0"), tokens=("tokA", "tokB")),
                   "m-tokC": resolved(("0", "1"), tokens=("tokC", "tokD")),
                   "m-tokE": resolved(status="proposed", tokens=("tokE", "tokF"))},
                  fail={"m-tokG"})
    cash_before = ledger.state.cash
    settled = settle_positions(ledger, gamma, NOW)
    assert {s["token_id"] for s in settled} == {"tokA", "tokC"}
    assert ledger.state.cash == cash_before + D("100")
    assert set(ledger.state.positions) == {"tokE", "tokG"}
    assert ledger.state.realized_pnl == (D("100") - D("90.36")) + (D("0") - D("40.32"))
    # Relancer ne règle pas deux fois.
    assert settle_positions(ledger, gamma, NOW) == []


def test_crypto_markets_share_a_correlation_group():
    btc1 = parse_market(raw_market("1", question="Will Bitcoin dip to $80,000 on October 14?"))
    btc2 = parse_market(raw_market("2", event_id="ev2", slug="btc-above-80k-oct-15",
                                   question="Will the price of BTC be above $80,000 on October 15?"))
    eth = parse_market(raw_market("3", event_id="ev3", question="Will Ethereum reach $5,000?"))
    match = parse_market(raw_market("4", event_id="ev4", question="Will Real Madrid win?"))
    assert correlation_group(btc1) == correlation_group(btc2) == "crypto:btc"
    assert correlation_group(eth) == "crypto:eth"
    assert correlation_group(match) == "ev4"
    # « sol » ne doit pas être reconnu dans un mot quelconque.
    assert correlation_group(parse_market(raw_market("5", event_id="ev5",
                                                     question="Will Solange release an album?"))) == "ev5"
