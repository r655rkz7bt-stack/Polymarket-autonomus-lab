"""Étape 6 : les cinq nouvelles familles de stratégies."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from conftest import NOW, buy, make_book, raw_market
from polymarket_agent.safety_controller import evaluate
from polymarket_agent.main import market_context
from polymarket_agent.social_intelligence import MarketIntel
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v2 import (CrossMarketLadder, InformationAdvantage, MarketStructure,
                                            NewsMomentum, SocialSentiment)

D = Decimal
FEES = {"feeType": "crypto_fees_v2", "schedule": {"exponent": 1, "rate": 0.07, "takerOnly": True}}


def ladder_market(mid, k, yes, no, end_h=24):
    raw = raw_market(market_id=mid, yes_token=yes, no_token=no, event_id=f"e{mid}",
                     question=f"Will the price of Bitcoin be above ${k:,} on October 15?",
                     end=NOW + timedelta(hours=end_h), **FEES)
    return parse_market(raw)


def two_sided(token_yes, token_no, yes_bid, yes_ask):
    return {token_yes: make_book(token_yes, bids=((yes_bid, "1000"),), asks=((yes_ask, "1000"),)),
            token_no: make_book(token_no, bids=((str(D(1) - D(yes_ask)), "1000"),),
                                asks=((str(D(1) - D(yes_bid)), "1000"),))}


def cross():
    return CrossMarketLadder("1.0.0", "2026-10-15", {"min_net_edge": D("0.005"), "stake_fraction": D("0.2"),
                                                       "max_proposals_per_cycle": D("3")})


def test_cross_market_buys_both_legs_of_a_ladder_violation(ledger, limits):
    low = ladder_market("1", 80000, "L1", "L0")    # « au-dessus de 80 k »
    high = ladder_market("2", 82000, "H1", "H0")   # « au-dessus de 82 k », plus cher : incohérent
    books = two_sided("L1", "L0", "0.40", "0.41") | two_sided("H1", "H0", "0.60", "0.61")
    assert {m.market_id for m in cross().candidates([low, high])} == {"1", "2"}
    out = cross().propose([low, high], books, ledger.state, limits, "B1")
    tokens = sorted(p.token_id for p in out.proposals)
    assert tokens == ["H0", "L1"]  # Oui(80 k) + Non(82 k) : au moins l'un paie toujours 1
    assert len({p.shares for p in out.proposals}) == 1  # même nombre de parts sur les deux jambes
    cost = D("0.41") + D("0.40")  # + frais
    assert cost < 1
    for p in out.proposals:
        assert evaluate(p, ledger.state, market_context(low if p.token_id == "L1" else high,
                                                        books[p.token_id], p.token_id), limits, NOW).accepted


def test_cross_market_ignores_consistent_ladders(ledger, limits):
    low = ladder_market("1", 80000, "L1", "L0")
    high = ladder_market("2", 82000, "H1", "H0")
    books = two_sided("L1", "L0", "0.70", "0.71") | two_sided("H1", "H0", "0.30", "0.31")
    assert not cross().propose([low, high], books, ledger.state, limits, "B1").proposals


def structure():
    return MarketStructure("1.0.0", "2026-10-15", {
        "min_imbalance": D("0.6"), "max_spread": D("0.02"), "depth_window": D("0.03"),
        "stake_fraction": D("0.05"), "take_profit": D("0.02"), "stop_loss": D("0.03"),
        "max_hold_hours": D("6"), "max_extra_ticks": D("0"), "max_proposals_per_cycle": D("2")})


def test_market_structure_buys_on_book_pressure_and_exits(ledger, limits):
    m = parse_market(raw_market(yes_price="0.5", best_bid=0.49, best_ask=0.50))
    pressure = {"tokA": make_book("tokA", bids=(("0.49", "5000"), ("0.48", "3000")), asks=(("0.50", "500"),)),
                "tokB": make_book("tokB", bids=(("0.50", "500"),), asks=(("0.51", "5000"),))}
    out = structure().propose([m], pressure, ledger.state, limits, "B1")
    assert out.proposals and out.proposals[0].token_id == "tokA"
    assert out.proposals[0].shares == D("100.00")  # 5 % de 1 000 à 0,50
    balanced = {"tokA": make_book("tokA", bids=(("0.49", "500"),), asks=(("0.50", "500"),)),
                "tokB": make_book("tokB", bids=(("0.50", "500"),), asks=(("0.51", "500"),))}
    assert not structure().propose([m], balanced, ledger.state, limits, "B1").proposals
    # Sorties
    buy(ledger, "b1", token="tokA", shares="100", price="0.50")
    pos = {"tokA": ledger.state.positions["tokA"]}
    pos["tokA"].strategy_id = "market_structure"
    markets = {pos["tokA"].market_id: m}
    up = {"tokA": make_book("tokA", bids=(("0.53", "500"),), asks=(("0.54", "500"),))}
    assert structure().exits(pos, markets, up, "B2", NOW)[0].invalidation == "objectif atteint"
    down = {"tokA": make_book("tokA", bids=(("0.46", "500"),), asks=(("0.47", "500"),))}
    assert structure().exits(pos, markets, down, "B2", NOW)[0].invalidation == "stop"
    flat = {"tokA": make_book("tokA", bids=(("0.50", "500"),), asks=(("0.51", "500"),))}
    assert structure().exits(pos, markets, flat, "B2", NOW) == []
    assert structure().exits(pos, markets, flat, "B2", NOW + timedelta(hours=7))[0].invalidation == "durée maximale"


def intel(**kw):
    base = dict(market_id="1", mentions_24h=20, spike=5.0, independent_sources=3, signal=True)
    base.update(kw)
    return MarketIntel(**base)


def news():
    return NewsMomentum("1.0.0", "2026-10-15", {
        "min_spike": D("3"), "min_move": D("0.05"), "continuation": D("0.06"), "uncertainty": D("0.02"),
        "min_net_edge": D("0.01"), "max_proposals_per_cycle": D("2")})


def market_with(mid_yes, before_6h=None, before_1h=None, **intel_kw):
    m = parse_market(raw_market(yes_price=str(mid_yes)))
    m.intel = intel(**intel_kw)
    m.yes_price_6h_ago, m.yes_price_1h_ago = before_6h, before_1h
    return m


def books_mid(yes_bid, yes_ask):
    return two_sided("tokA", "tokB", yes_bid, yes_ask)


def test_news_momentum_follows_a_confirmed_move(ledger, limits):
    m = market_with(0.6, before_6h=0.50)
    out = news().propose([m], books_mid("0.595", "0.60"), ledger.state, limits, "B1")
    assert out.proposals[0].token_id == "tokA"
    assert not news().propose([market_with(0.6, before_6h=0.5, signal=False)], books_mid("0.595", "0.60"),
                              ledger.state, limits, "B1").proposals
    assert not news().propose([market_with(0.6, before_6h=0.58)], books_mid("0.595", "0.60"),
                              ledger.state, limits, "B1").proposals  # pas encore bougé
    contrary = market_with(0.6, before_6h=0.5, stance=-0.8)
    assert news().propose([contrary], books_mid("0.595", "0.60"), ledger.state, limits, "B1").abstentions == {
        "direction de l'IA contraire au mouvement": 1}


def info():
    return InformationAdvantage("1.0.0", "2026-10-15", {
        "max_age_minutes": D("60"), "min_stance": D("0.5"), "impact": D("0.10"), "uncertainty": D("0.04"),
        "max_reaction": D("0.02"), "min_net_edge": D("0.02"), "max_proposals_per_cycle": D("2")})


def test_information_advantage_needs_direction_and_unreacted_price(ledger, limits):
    books = books_mid("0.495", "0.50")
    no_ai = market_with(0.5, before_1h=0.5, official_minutes=10, official_stance=0.0)
    assert info().propose([no_ai], books, ledger.state, limits, "B1").abstentions == {
        "direction de l'annonce inconnue (Gemini inactif ou neutre)": 1}
    fresh = market_with(0.5, before_1h=0.5, official_minutes=10, official_stance=0.9)
    assert info().propose([fresh], books, ledger.state, limits, "B1").proposals[0].token_id == "tokA"
    reacted = market_with(0.5, before_1h=0.42, official_minutes=10, official_stance=0.9)
    assert not info().propose([reacted], books, ledger.state, limits, "B1").proposals


def test_social_sentiment_fades_unconfirmed_crowd(ledger, limits):
    s = SocialSentiment("1.0.0", "2026-10-15", {"min_stance": D("0.7"), "min_mentions": D("10"), "fade": D("0.03"),
                                                "uncertainty": D("0.0"), "min_net_edge": D("0.01"),
                                                "max_proposals_per_cycle": D("2")})
    books = books_mid("0.495", "0.50")
    crowd = market_with(0.5, stance=0.9, signal=False)
    assert s.propose([crowd], books, ledger.state, limits, "B1").proposals[0].token_id == "tokB"  # contre la foule
    confirmed = market_with(0.5, stance=0.9, signal=True)
    assert not s.propose([confirmed], books, ledger.state, limits, "B1").proposals
