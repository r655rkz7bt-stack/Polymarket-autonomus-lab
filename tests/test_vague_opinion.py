"""Vague d'opinion (idée d'Etienne, 18/10/2026) : acheter au début d'une vague d'attention sur un
marché long, revendre quand elle est passée (jamais jusqu'au règlement)."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal as D

from conftest import KEY, NOW, ROOT, make_book, raw_market
from polymarket_agent.ledger import Ledger, Position
from polymarket_agent.safety_controller import RiskLimits
from polymarket_agent.social_intelligence import MarketIntel
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v2 import OpinionWave

PARAMS = {"min_days_left": 7, "min_spike": 2.0, "min_mentions": 4, "min_sources": 2, "min_stance": 0.3,
          "min_drift": 0.02, "max_move": 0.08, "push": 0.04, "uncertainty": 0.02, "min_net_edge": 0.01,
          "stake_fraction": 0.03, "take_profit": 0.05, "stop_loss": 0.05, "max_hold_hours": 120,
          "min_hold_hours": 6, "max_extra_ticks": 1, "max_proposals_per_cycle": 3}


def _strategy():
    return OpinionWave("1.0.0", "2026-10-18", {k: D(str(v)) for k, v in PARAMS.items()})


def _market(days=30, drift=0.03, stance=0.0, spike=3.0, mentions=8, sources=3):
    m = parse_market(raw_market("v1", yes_token="Y", no_token="N", end=NOW + timedelta(days=days)))
    m.yes_price_6h_ago = 0.40 - drift
    m.intel = MarketIntel("v1", mentions_24h=mentions, spike=spike, independent_sources=sources, stance=stance)
    books = {"Y": make_book("Y", bids=(("0.40", "500"),), asks=(("0.41", "500"),)),
             "N": make_book("N", bids=(("0.59", "500"),), asks=(("0.60", "500"),))}
    return m, books


def _state(tmp_path, name="l"):
    return Ledger.create(tmp_path / f"{name}.jsonl", KEY, tmp_path / f"{name}.lock", "1000", now=NOW).state


def test_buys_at_the_start_of_a_wave_on_long_markets_only(tmp_path):
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    m, books = _market()
    out = _strategy().propose([m], books, _state(tmp_path), limits, "b1")
    assert len(out.proposals) == 1 and out.proposals[0].outcome == "Yes"      # le prix commence à monter
    m, books = _market(drift=-0.03)
    assert _strategy().propose([m], books, _state(tmp_path, "b"), limits, "b1").proposals[0].outcome == "No"
    m, books = _market(drift=0.0, stance=0.6)                                 # sens donné par l'IA
    assert _strategy().propose([m], books, _state(tmp_path, "c"), limits, "b1").proposals[0].outcome == "Yes"
    for kw in ({"days": 3}, {"spike": 1.2}, {"sources": 1}, {"drift": 0.15}, {"drift": 0.0},
               {"drift": -0.03, "stance": 0.6}):
        m, books = _market(**kw)
        assert not _strategy().propose([m], books, _state(tmp_path, str(kw).replace(" ", "")[:20].replace(":", "_")
                                                          .replace("'", "").replace("{", "").replace("}", "")
                                                          .replace(",", "_").replace(".", "")),
                                       limits, "b1").proposals, kw


def test_resells_when_the_wave_has_passed_never_waits_for_resolution():
    s = _strategy()
    m, books = _market()
    opened = (NOW - timedelta(hours=10)).isoformat()
    pos = {"Y": Position("Y", "v1", "ev1", "Yes", D("10"), D("3.40"), opened, "vague_opinion", "1.0.0")}  # payé 0,34
    assert s.exits(pos, {"v1": m}, books, "b1", NOW)[0].invalidation == "objectif atteint"   # 0,40 − 0,34 ≥ 0,05
    pos["Y"].cost_basis = D("4.60")                                                           # payé 0,46
    assert s.exits(pos, {"v1": m}, books, "b1", NOW)[0].invalidation == "stop"
    pos["Y"].cost_basis = D("3.90")                                                           # payé 0,39 : +0,01
    assert s.exits(pos, {"v1": m}, books, "b1", NOW) == []                                    # la vague continue
    m.intel.spike = 0.5
    assert s.exits(pos, {"v1": m}, books, "b1", NOW)[0].invalidation == "vague retombée"
    m.intel.spike = 3.0
    pos["Y"].opened_at = (NOW - timedelta(hours=130)).isoformat()
    assert s.exits(pos, {"v1": m}, books, "b1", NOW)[0].invalidation == "durée maximale"


def test_a_wide_spread_makes_the_round_trip_too_expensive(tmp_path):
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    m, books = _market()
    books["Y"] = make_book("Y", bids=(("0.38", "500"),), asks=(("0.42", "500"),))  # 4 centimes d'écart
    out = _strategy().propose([m], books, _state(tmp_path), limits, "b1")
    assert not out.proposals and "aller-retour trop cher pour la poussée attendue" in out.abstentions
