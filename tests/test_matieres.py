"""Barres touchées par l'or et l'argent (24/10/2026, experiments/commodites_toucher.md) : lecture de gold-api.com, journal des prix, chance de toucher une barre,
rattachement aux marchés, collecteur et stratégie `toucher_metaux`."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from conftest import raw_market
from test_sources import FakeHttp
from test_strategies_v3 import LIMITS, _books, _s, _state
from polymarket_agent import matieres as mt
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources import goldapi
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import ToucherMetaux

UTC = timezone.utc
CREATED = datetime(2026, 10, 23, 22, 0, tzinfo=UTC)
END = datetime(2026, 10, 30, 21, 0, tzinfo=UTC)
NOW = datetime(2026, 10, 27, 14, 0, tzinfo=UTC)
TITLE = "What will Gold (XAUUSD) hit Week of October 26 2026?"


def _market(mid, question, title=TITLE, created=CREATED, end=END):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", question=question, end=end, createdAt=created.isoformat(),
                                   events=[{"id": "ev" + title[-8:], "title": title}]))


def _prices(db, symbol="XAUUSD", start=CREATED + timedelta(hours=1), values=(4000.0, 4010.0, 4005.0), step_hours=24):
    rows = [{"symbole": symbol, "t": int((start + timedelta(hours=step_hours * i)).timestamp()), "prix": v} for i, v in enumerate(values)]
    last = NOW - timedelta(minutes=5)
    rows.append({"symbole": symbol, "t": int(last.timestamp()), "prix": values[-1]})
    return mt.record_prices(db, rows, NOW)


def test_parse_price_reads_the_real_gold_api_answer_and_skips_junk():
    row = goldapi.parse_price({"currency": "USD", "price": 3996.899902, "symbol": "XAU", "updatedAt": "2026-10-24T15:29:53Z"}, "XAU")
    assert row == {"symbole": "XAUUSD", "t": int(datetime(2026, 10, 24, 15, 29, 53, tzinfo=UTC).timestamp()), "prix": 3996.899902}
    assert goldapi.parse_price({"price": 0}, "XAU") is None and goldapi.parse_price({"error": "x"}, "XAU") is None and goldapi.parse_price(None, "XAU") is None
    assert goldapi.parse_price({"price": 54.0}, "XAG")["t"] is None


def test_fetch_prices_takes_both_metals_skips_a_broken_one_and_fails_when_all_are_down():
    ok = {"price": 4000.0, "updatedAt": "2026-10-24T15:00:00Z"}
    http = FakeHttp({"https://api.gold-api.com/price/XAU": ok, "https://api.gold-api.com/price/XAG": {"price": 54.0}})
    rows = goldapi.fetch_prices(http, NOW)
    assert {r["symbole"] for r in rows} == {"XAUUSD", "XAGUSD"} and [r for r in rows if r["symbole"] == "XAGUSD"][0]["t"] == int(NOW.timestamp())
    assert [r["symbole"] for r in goldapi.fetch_prices(FakeHttp({"https://api.gold-api.com/price/XAU": ok}, down=("https://api.gold-api.com/price/XAG",)), NOW)] == ["XAUUSD"]
    with pytest.raises(Exception):
        goldapi.fetch_prices(FakeHttp({}, down=("https://api.gold-api.com/price/",)), NOW)


def test_titles_and_bars_read_the_real_polymarket_wording():
    assert mt.symbol_of("What will Gold (XAUUSD) hit Week of October 26 2026?") == "XAUUSD"
    assert mt.symbol_of("What will Silver (XAGUSD) hit Week of October 26 2026?") == "XAGUSD"
    assert mt.symbol_of("What will WTI Crude Oil (WTI) hit Week of October 26 2026?") is None
    assert mt.symbol_of("What will Gold (XAUUSD) hit in October 2026?") is None
    assert mt.bar_of("Will Gold (XAUUSD) hit (HIGH) $4,300 Week of October 26 2026?") == ("HIGH", 4300.0)
    assert mt.bar_of("Will Silver (XAGUSD) hit (LOW) $52.5 Week of October 26 2026?") == ("LOW", 52.5)
    assert mt.bar_of("Will it rain?") is None


def test_hit_probability_matches_the_reflection_formula_and_grows_with_time_and_closeness():
    # d = 1 : 2 × (1 − Φ(1)) = 0,3173 ; τ = 24 × 23/24 = 23 heures, σ = 0,01 → écart de ln(K/S) = 0,01 × √23
    import math
    gap = 0.01 * math.sqrt(23)
    assert mt.hit_probability("HIGH", 1000 * math.exp(gap), 1000, 0.01, 24) == pytest.approx(0.3173, abs=1e-3)
    assert mt.hit_probability("LOW", 1000 * math.exp(-gap), 1000, 0.01, 24) == pytest.approx(0.3173, abs=1e-3)
    assert mt.hit_probability("HIGH", 1020, 1000, 0.003, 96) > mt.hit_probability("HIGH", 1020, 1000, 0.003, 48) > mt.hit_probability("HIGH", 1020, 1000, 0.003, 20)
    assert mt.hit_probability("HIGH", 1020, 1000, 0.003, 48) > mt.hit_probability("HIGH", 1040, 1000, 0.003, 48)


def test_bar_state_distinguishes_touched_uncertain_and_free():
    assert mt.bar_state("HIGH", 4300, 4301) == "touchee" and mt.bar_state("LOW", 3900, 3899) == "touchee"
    assert mt.bar_state("HIGH", 4300, 4298) == "incertaine"          # 0,05 % de la barre : une bougie d'1 minute a pu la toucher
    assert mt.bar_state("HIGH", 4300, 4200) == "libre"


def test_attach_needs_a_price_log_that_covers_the_market_since_its_creation(tmp_path):
    db = Database(tmp_path / "t.db")
    ms = [_market("hi", "Will Gold (XAUUSD) hit (HIGH) $4,100 Week of October 26 2026?"), _market("other", "Will it rain?", title="Weather")]
    assert mt.attach_matieres(ms, db, NOW) == 0                                            # pas de journal : rien
    _prices(db, start=CREATED + timedelta(days=2))                                         # le journal commence 2 jours après la création : pas de couverture
    assert mt.attach_matieres(ms, db, NOW) == 0
    db2 = Database(tmp_path / "t2.db")
    _prices(db2)
    assert mt.attach_matieres(ms, db2, NOW) == 1
    ref = ms[0].references["matieres"]
    assert 0.0 < ref["p"] < 0.6 and not ref["touchee"] and "XAUUSD" in ref["titre"] and "matieres" not in (ms[1].references or {})
    assert mt.attach_matieres(ms, db2, NOW + timedelta(hours=2)) == 0                      # dernier relevé vieux de plus de 30 minutes
    assert mt.attach_matieres(ms, db2, END - timedelta(hours=10)) == 0                      # moins de 18 h avant la fin : pas de loi


def test_attach_marks_a_touched_bar_and_skips_an_uncertain_one(tmp_path):
    db = Database(tmp_path / "t.db")
    _prices(db, values=(4000.0, 4120.0, 4050.0))                                           # maximum relevé 4 120
    ms = [_market("touched", "Will Gold (XAUUSD) hit (HIGH) $4,100 Week of October 26 2026?"),
          _market("close", "Will Gold (XAUUSD) hit (HIGH) $4,122 Week of October 26 2026?"),
          _market("low_ok", "Will Gold (XAUUSD) hit (LOW) $3,900 Week of October 26 2026?")]
    assert mt.attach_matieres(ms, db, NOW) == 2
    assert ms[0].references["matieres"]["touchee"] and ms[0].references["matieres"]["p"] == 0.99
    assert "matieres" not in (ms[1].references or {}) and not ms[2].references["matieres"]["touchee"]


def test_collector_logs_prices_and_survives_an_outage(tmp_path):
    db = Database(tmp_path / "t.db")
    rows = [{"symbole": "XAUUSD", "t": int(NOW.timestamp()), "prix": 4000.0}]
    cfg = {"sources": {"goldapi": {"enabled": True, "every_minutes": 5, "keep_days": 30}}}
    result = collect(cfg, None, db, [], NOW, {"goldapi": lambda c: rows})
    assert result.status["goldapi"].startswith("ok") and mt.history(db, "XAUUSD", 0) == [(int(NOW.timestamp()), 4000.0)]
    http = FakeHttp({}, down=("https://api.gold-api.com/price/",))
    down = collect(cfg, None, db, [], NOW + timedelta(minutes=6), {"goldapi": lambda c: goldapi.fetch_prices(http, NOW)})
    assert down.status["goldapi"].startswith("indisponible") and mt.history(db, "XAUUSD", 0) == [(int(NOW.timestamp()), 4000.0)]


def _case(mid, p, yes_mid, seen=NOW, event="e1"):
    m = _market(mid, "Will Gold (XAUUSD) hit (HIGH) $4,300 Week of October 26 2026?")
    m.token_ids, m.event_id = [f"{mid}Y", f"{mid}N"], event
    m.references = {"matieres": {"p": p, "titre": "test", "vu_le": seen.isoformat(), "touchee": False}}
    b = _books((f"{mid}Y", f"{yes_mid - 0.01:.3f}", f"{yes_mid + 0.01:.3f}"), (f"{mid}N", f"{1 - yes_mid - 0.01:.3f}", f"{1 - yes_mid + 0.01:.3f}"))
    for book in b.values():
        book.fetched_at = NOW
    return m, b


def test_strategy_buys_the_side_cheaper_than_the_law_and_skips_old_logs(tmp_path):
    s = _s(ToucherMetaux, min_net_edge=0.10, uncertainty=0.0, min_price=0.08, max_price=0.90, max_stale_hours=0.5,
           max_extra_ticks=1, max_proposals_per_cycle=6, max_per_event=6, kelly_fraction=0.25)
    cases = [_case("sous_cote", 0.60, 0.25), _case("sur_cote", 0.05, 0.40), _case("proche", 0.30, 0.28), _case("vieux", 0.60, 0.25, seen=NOW - timedelta(hours=2))]
    ms, books = [c[0] for c in cases], {}
    for _, b in cases:
        books.update(b)
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert {p.market_id: p.outcome for p in out.proposals} == {"sous_cote": "Yes", "sur_cote": "No"}
    assert all(p.strategy_id == "toucher_metaux" for p in out.proposals) and out.abstentions
    assert {m.market_id for m in s.candidates(ms)} == {"sous_cote", "sur_cote", "proche", "vieux"}


def test_strategy_takes_at_most_max_per_event_bars_best_edge_first(tmp_path):
    s = _s(ToucherMetaux, min_net_edge=0.05, uncertainty=0.0, min_price=0.08, max_price=0.90, max_stale_hours=0.5,
           max_extra_ticks=1, max_proposals_per_cycle=6, max_per_event=2, kelly_fraction=0.25)
    cases = [_case("a", 0.80, 0.20), _case("b", 0.70, 0.20), _case("c", 0.60, 0.20)]
    ms, books = [c[0] for c in cases], {}
    for _, b in cases:
        books.update(b)
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert {p.market_id for p in out.proposals} == {"a", "b"} and "déjà le maximum de barres de cet événement" in str(out.abstentions)
