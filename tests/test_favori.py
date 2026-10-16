"""Options de naive_favorite (16/10/2026, experiments/favori.md) : famille, fenêtre, outsider, shrink."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal as D

from conftest import KEY, NOW, ROOT, make_book, raw_market
from polymarket_agent.ledger import Ledger
from polymarket_agent.safety_controller import RiskLimits
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategy_engine import NaiveFavorite, load_strategies, market_family

BASE = {"min_ask": D("0.85"), "max_ask": D("0.97"), "bias": D("0"), "uncertainty": D("0.01"),
        "min_net_edge": D("0.01"), "max_extra_ticks": D("2"), "max_proposals_per_cycle": D("3"),
        "kelly_fraction": D("0.5")}


def _setup(tmp_path, fee_type="politics_fees", enabled=True, end_hours=48, bid="0.90", ask="0.91", **raw):
    m = parse_market(raw_market("p1", yes_token="Y", no_token="N", yes_price="0.905", best_bid=float(bid),
                                best_ask=float(ask), end=NOW + timedelta(hours=end_hours), fees_enabled=enabled,
                                feeType=fee_type, **raw))
    books = {"Y": make_book("Y", bids=((bid, "500"),), asks=((ask, "500"),)),
             "N": make_book("N", bids=((str(1 - D(ask)), "500"),), asks=((str(1 - D(bid)), "500"),))}
    ledger = Ledger.create(tmp_path / "l.jsonl", KEY, tmp_path / "l.lock", "1000", now=NOW)
    return m, books, ledger, RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")


def _strategy(families=(), **params):
    s = NaiveFavorite("1.0.0", "2026-10-16", dict(BASE, **{k: D(str(v)) for k, v in params.items()}))
    s.families = tuple(families)
    return s


def test_market_family_comes_from_the_fee_schedule(tmp_path):
    assert market_family(_setup(tmp_path)[0]) == "politics"
    assert market_family(_setup(tmp_path / "b", fee_type="sports_fees_v3")[0]) == "sports"
    assert market_family(_setup(tmp_path / "c", fee_type=None, enabled=False)[0]) == "sans_frais"


def test_shrink_estimate_family_filter_and_time_window(tmp_path):
    m, books, ledger, limits = _setup(tmp_path)
    # Milieu 0,905 ; shrink 0,5 → estimation 0,905 + 0,5 × 0,095 = 0,9525 ; achat du OUI à 0,91.
    out = _strategy(("politics", "sans_frais"), shrink=0.5).propose([m], books, ledger.state, limits, "b")
    assert len(out.proposals) == 1 and out.proposals[0].token_id == "Y"
    assert out.proposals[0].est_probability == D("0.905") + D("0.5") * D("0.095")
    assert not _strategy(("sports",), shrink=0.5).propose([m], books, ledger.state, limits, "b").proposals
    # Fenêtre : pas dans les 6 dernières heures, ni au-delà de max_hours.
    assert not _strategy(shrink=0.5, min_hours=72).propose([m], books, ledger.state, limits, "b").proposals
    assert _strategy(shrink=0.5, min_hours=6, max_hours=720).propose([m], books, ledger.state, limits, "b").proposals
    near, nb, nl, _ = _setup(tmp_path / "n", end_hours=3)
    assert not _strategy(shrink=0.5, min_hours=6).propose([near], nb, nl.state, limits, "b").proposals


def test_underdog_option_buys_the_cheaper_side_before_the_game(tmp_path):
    start = NOW + timedelta(hours=5)
    m, books, ledger, limits = _setup(tmp_path, fee_type="sports_fees_v3", end_hours=24 * 7,
                                      bid="0.86", ask="0.87", gameStartTime=start.strftime("%Y-%m-%d %H:%M:%S+00"))
    assert m.game_start == start
    s = _strategy(("sports",), underdog=1, min_ask=0.08, max_ask=0.20, bias=0.03, uncertainty=0.015, min_net_edge=0,
                  min_hours=0.5, max_hours=24, kelly_fraction=1)
    out = s.propose([m], books, ledger.state, limits, "b")
    assert len(out.proposals) == 1 and out.proposals[0].token_id == "N"  # NON à 0,14 : l'outsider
    # Pendant le match (coup d'envoi passé) : rien, même si l'échéance affichée est lointaine.
    late = _setup(tmp_path / "l", fee_type="sports_fees_v3", end_hours=24 * 7, bid="0.86", ask="0.87",
                  gameStartTime=(NOW - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S+00"))
    assert not s.propose([late[0]], late[1], late[2].state, limits, "b").proposals


def test_repository_variants_carry_their_families():
    loaded = {s.strategy_id: s for s in load_strategies(ROOT / "config" / "strategies.yaml")}
    assert loaded["favori_politique"].families == ("politics", "sans_frais")
    assert loaded["favori_politique_patiente"].inner.families == ("politics", "sans_frais")
    assert loaded["outsider_sport_patiente"].inner.families == ("sports",)
    assert loaded["naive_favorite"].families == ()  # l'originale ne change pas


def _move_strategy(direction, families=("politics", "sans_frais")):
    from polymarket_agent.strategies_v2 import PriceMove
    s = PriceMove("1.0.0", "2026-10-16", {
        "direction": D(direction), "min_move": D("0.05"), "min_price": D("0.15"), "max_price": D("0.90"),
        "edge_prior": D("0.05"), "uncertainty": D("0.02"), "min_net_edge": D("0.01"), "min_hours": D("2"),
        "max_hours": D("720"), "max_extra_ticks": D("1"), "max_proposals_per_cycle": D("3"), "kelly_fraction": D("0.5")})
    s.families = tuple(families)
    return s


def test_price_move_follows_or_fades_a_six_hour_move(tmp_path):
    m, books, ledger, limits = _setup(tmp_path, bid="0.60", ask="0.61")
    m.yes_price_6h_ago = 0.50  # le OUI est passé de 0,50 à 0,605 en 6 h
    follow = _move_strategy(1).propose([m], books, ledger.state, limits, "b")
    assert [p.token_id for p in follow.proposals] == ["Y"]  # suivre : acheter le OUI qui monte
    fade = _move_strategy(-1).propose([m], books, ledger.state, limits, "b")
    assert [p.token_id for p in fade.proposals] == ["N"]  # contrer : acheter le NON à 0,40
    assert not _move_strategy(1, ("crypto",)).propose([m], books, ledger.state, limits, "b").proposals
    m.yes_price_6h_ago = 0.58  # mouvement de 0,025 : trop petit
    assert not _move_strategy(1).propose([m], books, ledger.state, limits, "b").proposals
    m.yes_price_6h_ago = None  # sans historique : abstention
    assert _move_strategy(1).propose([m], books, ledger.state, limits, "b").abstentions


def test_excluded_words_skip_markets():
    from polymarket_agent.strategy_engine import excluded
    loaded = {s.strategy_id: s for s in load_strategies(ROOT / "config" / "strategies.yaml")}
    words = loaded["contrer_crypto"].exclude_words
    assert words == ("up or down",) and loaded["contrer_crypto_patiente"].inner.exclude_words == words
    m = parse_market(raw_market("c", question="Bitcoin Up or Down on October 17?"))
    assert excluded(m, words) and not excluded(parse_market(raw_market("d", question="Will BTC hit $90k?")), words)
