"""Lancements de SpaceX (24/10/2026, experiments/spacex_cadence.md) : lecture de Launch Library 2, titres et tranches des marchés, lois du
compte, rattachement aux marchés, collecteur et stratégie `spacex_cumul`."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from conftest import raw_market
from test_sources import FakeHttp
from test_strategies_v3 import LIMITS, _books, _s, _state
from polymarket_agent import references as refs
from polymarket_agent import spacex as sx
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources import ll2
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import SpaceXCumul

UTC = timezone.utc
NOW = datetime(2026, 10, 24, 15, 0, tzinfo=UTC)


def _rows(n_before_now: int, per_day: float = 0.43, days: int = 430) -> list[dict]:
    """Lancements régulièrement espacés depuis `days` jours ; les `n_before_now` derniers jours d'octobre reçoivent leurs lancements."""
    out, t, i = [], NOW - timedelta(days=days), 0
    while t < NOW:
        out.append({"id": f"l{i}", "t": int(t.timestamp())})
        t += timedelta(days=1 / per_day)
        i += 1
    return out


def _market(mid, question, title, end, yes="Y", no="N"):
    return parse_market(raw_market(mid, yes_token=f"{mid}{yes}", no_token=f"{mid}{no}", question=question, end=end,
                                   events=[{"id": "e" + title[-6:], "title": title}]))


def test_parse_ll2_orders_by_launch_time_and_skips_broken_rows():
    data = {"results": [{"id": "b", "net": "2026-10-23T22:00:00Z"}, {"id": "a", "net": "2026-10-22T01:00:00Z"},
                        {"id": "c", "net": None}, {"id": "d", "net": "pas une date"}, "bruit"]}
    rows = ll2.parse_ll2(data)
    assert [r["id"] for r in rows] == ["a", "b"] and rows[0]["t"] == int(datetime(2026, 10, 22, 1, tzinfo=UTC).timestamp())
    assert ll2.parse_ll2(None) == []


def test_fetch_ll2_follows_next_pages_and_asks_for_spacex_only():
    page2 = {"results": [{"id": "z", "net": "2026-10-20T00:00:00Z"}], "next": None}
    http = FakeHttp({ll2.URL: {"results": [{"id": "y", "net": "2026-10-21T00:00:00Z"}], "next": "https://ll.example/page2"},
                     "https://ll.example/page2": page2})
    rows = ll2.fetch_ll2(http, NOW, days=430)
    assert [r["id"] for r in rows] == ["z", "y"]
    _, params, _ = http.calls[0]
    assert params["lsp__name"] == "SpaceX" and params["net__gte"] == "2025-08-20"


def test_titles_and_brackets_read_the_real_polymarket_wording():
    a, b = sx.period("How many SpaceX launches in October 2026?", None)
    assert a == datetime(2026, 10, 1, 4, tzinfo=UTC) and b == datetime(2026, 11, 1, 4, tzinfo=UTC)         # heure de l'Est (UTC−4)
    assert sx.period("How many SpaceX launches in January?", datetime(2026, 1, 31, 5, tzinfo=UTC))[0] == datetime(2026, 1, 1, 5, tzinfo=UTC)
    assert sx.period("How many SpaceX launches in 2026?", None)[1] == datetime(2027, 1, 1, 5, tzinfo=UTC)
    assert sx.period("How many SpaceX Starship launches reach space in 2026?", None) is None
    assert sx.bracket("Will SpaceX have fewer than 14 launches in October 2026?") == (0, 13)
    assert sx.bracket("Will SpaceX have exactly 14 launches in October 2026?") == (14, 14)
    assert sx.bracket("Will SpaceX have 17+ launches in October 2026?") == (17, 10 ** 6)
    assert sx.bracket("Will SpaceX have between 140-159 launches in 2026?") == (140, 159)
    assert sx.bracket("Will SpaceX have 200 or more launches in 2026?") == (200, 10 ** 6)
    assert sx.bracket("Will SpaceX have 12 or more launches in January?") == (12, 10 ** 6)
    assert sx.bracket("Will SpaceX have less than 100 launches in 2026?") == (0, 99)


def test_count_never_looks_past_now_and_impossible_brackets_get_zero():
    start, end = sx.period("How many SpaceX launches in 2026?", None)
    rows = [{"id": str(i), "t": int((start + timedelta(days=2 * i)).timestamp())} for i in range(122)]     # 122 déjà faits au 11/09
    now = start + timedelta(days=300)
    rows.append({"id": "futur", "t": int((now + timedelta(days=3)).timestamp())})                      # un lancement APRÈS maintenant : ignoré
    assert sx.count(rows, start, now) == 122
    assert sx.bracket_p(rows, start, end, now, (0, 99)) == (0.0, 0.0, 122)                              # déjà dépassée
    lo, hi, n = sx.bracket_p(rows, start, end, now, (200, 10 ** 6))
    assert n == 122 and hi < 1e-6                                                                       # 78 lancements en 65 jours : impossible
    assert sx.bracket_p(rows, start, end, end - timedelta(hours=12), (0, 999)) is None                  # dernier jour : pas de loi
    assert sx.bracket_p([], start, end, now, (0, 999)) is None


def test_sure_bracket_is_taken_by_the_most_cautious_law_and_probabilities_cover_all_cases():
    start, end = sx.period("How many SpaceX launches in 2026?", None)
    rows = [{"id": str(i), "t": int((start + timedelta(days=2.3 * i)).timestamp())} for i in range(129)]
    rows = [r for r in rows if r["t"] < NOW.timestamp()]
    cuts = [(0, 99), (100, 119), (120, 139), (140, 159), (160, 179), (180, 199), (200, 10 ** 6)]
    lows = [sx.bracket_p(rows, start, end, NOW, c) for c in cuts]
    assert all(l[0] <= l[1] for l in lows)
    assert sum(l[0] for l in lows) <= 1 + 1e-9 <= sum(l[1] for l in lows) + 1e-9                       # chance la plus basse ≤ 1 ≤ la plus haute, tranche par tranche


def test_attach_marks_matching_markets_only_and_needs_a_catalog(tmp_path):
    db = Database(tmp_path / "t.db")
    start, end = sx.period("How many SpaceX launches in 2026?", None)
    markets = [_market("m1", "Will SpaceX have between 140-159 launches in 2026?", "How many SpaceX launches in 2026?", end),
               _market("m2", "Will SpaceX have fewer than 100 launches in 2026?", "How many SpaceX launches in 2026?", end),
               _market("m3", "Will it rain?", "Weather", end)]
    assert sx.attach_spacex(markets, db, NOW) == 0                                                   # pas de relevé : rien
    rows = [{"id": str(i), "t": int((start + timedelta(days=2.3 * i)).timestamp())} for i in range(129)]
    refs._save(db, "ref:ll2", [r for r in rows if r["t"] < NOW.timestamp()], NOW)
    assert sx.attach_spacex(markets, db, NOW) == 2
    assert markets[1].references["spacex"]["p_max"] == 0.0 and markets[0].references["spacex"]["p_min"] > 0.5
    assert "spacex" not in (markets[2].references or {})


def test_collector_stores_the_catalog_and_survives_an_outage(tmp_path):
    db = Database(tmp_path / "t.db")
    rows = [{"id": "a", "t": 1_700_000_000}]
    cfg = {"sources": {"ll2": {"enabled": True, "every_minutes": 120, "days": 430}}}
    result = collect(cfg, None, db, [], NOW, {"ll2": lambda c: rows})
    assert result.status["ll2"] == "ok (1 prix relevés)" and refs._load(db, "ref:ll2")[1] == rows
    http = FakeHttp({}, down=(ll2.URL,))
    down = collect(cfg, None, db, [], NOW + timedelta(minutes=121), {"ll2": lambda c: ll2.fetch_ll2(http, NOW)})
    assert down.status["ll2"].startswith("indisponible") and refs._load(db, "ref:ll2")[1] == rows


def _case(mid, p_min, p_max, yes_mid, seen=NOW, event="e1"):
    m = _market(mid, "Will SpaceX have between 140-159 launches in 2026?", "How many SpaceX launches in 2026?", NOW + timedelta(days=68))
    m.token_ids, m.event_id = [f"{mid}Y", f"{mid}N"], event
    m.references = {"spacex": {"p_min": p_min, "p_max": p_max, "titre": "test", "vu_le": seen.isoformat()}}
    b = _books((f"{mid}Y", f"{yes_mid - 0.01:.3f}", f"{yes_mid + 0.01:.3f}"), (f"{mid}N", f"{1 - yes_mid - 0.01:.3f}", f"{1 - yes_mid + 0.01:.3f}"))
    for book in b.values():
        book.fetched_at = NOW
    return m, b


def test_strategy_buys_only_the_probable_side_when_cheaper_than_the_cautious_law(tmp_path):
    s = _s(SpaceXCumul, min_net_edge=0.03, uncertainty=0.0, min_price=0.50, max_price=0.97, max_stale_hours=6,
           max_extra_ticks=1, max_proposals_per_cycle=6, max_per_event=5, kelly_fraction=0.25)
    cases = [_case("sur_oui", 0.95, 1.0, 0.78), _case("sur_non", 0.0, 0.02, 0.10), _case("proche", 0.50, 0.55, 0.52),
             _case("modeste", 0.30, 0.45, 0.05), _case("vieux", 0.95, 1.0, 0.78, seen=NOW - timedelta(hours=9))]
    ms, books = [c[0] for c in cases], {}
    for _, b in cases:
        books.update(b)
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert {p.market_id: p.outcome for p in out.proposals} == {"sur_oui": "Yes", "sur_non": "No"}
    assert all(p.strategy_id == "spacex_cumul" for p in out.proposals) and out.abstentions
    assert {m.market_id for m in s.candidates(ms)} == {"sur_oui", "sur_non", "proche", "modeste", "vieux"}


def test_strategy_takes_at_most_max_per_event_buckets_best_edge_first(tmp_path):
    s = _s(SpaceXCumul, min_net_edge=0.02, uncertainty=0.0, min_price=0.50, max_price=0.97, max_stale_hours=6,
           max_extra_ticks=1, max_proposals_per_cycle=6, max_per_event=2, kelly_fraction=0.25)
    cases = [_case("a", 0.97, 1.0, 0.60), _case("b", 0.97, 1.0, 0.70), _case("c", 0.97, 1.0, 0.80)]
    ms, books = [c[0] for c in cases], {}
    for _, b in cases:
        books.update(b)
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert {p.market_id for p in out.proposals} == {"a", "b"} and "déjà deux tranches de cet événement" in str(out.abstentions)
