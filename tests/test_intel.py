"""Intelligence des sources et modèle crypto : les règles du cahier des charges."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest

from conftest import NOW, make_book, raw_market
from polymarket_agent.crypto_model import ThresholdQuestion, parse_question, probability, probability_band
from polymarket_agent.observations import Observation, mark_duplicates
from polymarket_agent.social_intelligence import keywords, match, summarize
from polymarket_agent.sources.crypto_prices import CryptoQuote
from polymarket_agent.sources.polymarket_gamma import parse_market

D = Decimal


def o(text, domain, minutes=30, engagement=0, source="gdelt"):
    return Observation(source, f"{domain}-{text}", NOW - timedelta(minutes=minutes), NOW, f"https://{domain}",
                       text, "", domain=domain, engagement=engagement).finalize()


def market(question="Will Real Madrid beat Roma?"):
    return parse_market(raw_market(question=question))


def test_keywords_and_matching():
    m = market()
    assert {"real", "madrid", "roma"} <= set(keywords(m))
    items = [o("Real Madrid edge Roma in Champions League", "bbc.co.uk"), o("Weather in Madrid", "x.com")]
    match(items, [m])
    assert items[0].market_ids == [m.market_id] and items[1].market_ids == []


def test_isolated_viral_post_is_never_a_signal():
    m = market()
    viral = [o("Real Madrid will crush Roma, trust me", "bsky.app", engagement=1_000_000, source="bluesky")]
    match(viral, [m])
    intel = summarize(m.market_id, viral, NOW, [])
    assert not intel.signal and "une seule source" in intel.reasons[0]


def test_absence_of_information_is_not_a_signal():
    intel = summarize("m1", [], NOW, [])
    assert not intel.signal and intel.stance == 0 and intel.mentions_24h == 0


def test_two_independent_reliable_sources_make_a_signal_copies_do_not():
    m = market()
    text = "Real Madrid confirm Mbappe injured before Roma match"
    copies = [o(text, "a.com", source="bluesky"), o(text, "b.com", source="bluesky")]
    mark_duplicates(copies, set())
    match(copies, [m])
    assert copies[1].duplicate_of  # copie exacte détectée, même depuis un autre compte
    assert not summarize(m.market_id, copies, NOW, []).signal
    news = [o("Real Madrid confirm Mbappe injured before Roma match", "bbc.co.uk"),
            o("Roma vs Real Madrid: Mbappe ruled out with injury", "lemonde.fr", source="rss")]
    mark_duplicates(news, set())
    match(news, [m])
    intel = summarize(m.market_id, news, NOW, ["gdelt"])
    assert intel.signal and intel.independent_sources == 2
    assert "gdelt" in intel.sources_down and any("x_api" in s for s in intel.sources_down)


def test_crypto_question_parsing():
    assert parse_question("Will Bitcoin dip to $81,000 on October 14?") == ThresholdQuestion("touch_down", 81000)
    assert parse_question("Will the price of Bitcoin be above $80,000 on October 15?") == ThresholdQuestion("above", 80000)
    assert parse_question("Will Bitcoin reach $100k in October?") == ThresholdQuestion("touch_up", 100000)
    assert parse_question("Will Ethereum be between $3,000 and $3,200?") is None
    assert parse_question("Will the White House announce $5 tariffs?") is None  # « white » ≠ « hit »


def test_crypto_probabilities_are_sane():
    above = ThresholdQuestion("above", 80000)
    assert probability(above, 90000, 0.005, 24) > 0.99
    assert abs(probability(above, 80000, 0.005, 24) - 0.5) < 1e-9
    touch = ThresholdQuestion("touch_down", 81000)
    p_touch = probability(touch, 82000, 0.006, 12)
    p_end = probability(ThresholdQuestion("below", 81000), 82000, 0.006, 12)
    assert p_touch == pytest.approx(min(1, 2 * p_end))
    assert probability(touch, 80000, 0.006, 12) is None  # déjà touché : issue connue
    low, est, high = probability_band(above, 81000, 0.005, 24)
    assert low <= est <= high


def test_crypto_threshold_strategy_uses_independent_probability(ledger, limits):
    from polymarket_agent.strategy_engine import CryptoThresholdStrategy
    s = CryptoThresholdStrategy("1.0.0", "2026-10-15", {
        "min_net_edge": D("0.03"), "max_extra_ticks": D("2"), "max_proposals_per_cycle": D("3"),
        "max_quote_age_minutes": D("20"), "min_hours": D("0.5")})
    m = market("Will the price of Bitcoin be above $80,000 on October 15?")
    m.crypto_quote = CryptoQuote("btc", 88000.0, 0.004, NOW, "coinbase")  # loin au-dessus : P(Oui) ≈ 1
    books = {"tokA": make_book("tokA", bids=(("0.85", "500"),), asks=(("0.86", "500"),)),
             "tokB": make_book("tokB", bids=(("0.13", "500"),), asks=(("0.14", "500"),))}
    out = s.propose([m], books, ledger.state, limits, "B1")
    assert out.proposals and out.proposals[0].token_id == "tokA"
    m.crypto_quote = CryptoQuote("btc", 88000.0, 0.004, NOW - timedelta(hours=2), "coinbase")
    assert s.propose([m], books, ledger.state, limits, "B1").abstentions == {"prix crypto périmé": 1}
