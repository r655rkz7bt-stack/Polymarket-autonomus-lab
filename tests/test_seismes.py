"""Séismes (24/10/2026, experiments/seismes.md) : lecture du catalogue USGS, tranches des marchés, lois du jour et de la semaine,
rattachement aux marchés, collecteur et stratégie `seismes_marche`."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal as D

import pytest

from conftest import ROOT, raw_market
from test_sources import FakeHttp
from test_strategies_v3 import LIMITS, _books, _s, _state
from polymarket_agent import references as refs
from polymarket_agent import seismes as sm
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources import usgs
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import SeismesMarche

UTC = timezone.utc
DAY = datetime(2026, 10, 22, tzinfo=UTC)


def _row(when: datetime, mag: float, ident: str = "x") -> dict:
    return {"id": f"{ident}{int(when.timestamp())}", "t": int(when.timestamp()), "mag": mag}


def _daily_market(mid, question, day=DAY, yes="Y", no="N"):
    title = f"What will the biggest earthquake be on {day:%B} {day.day}, {day.year}?"
    return parse_market(raw_market(mid, yes_token=f"{mid}{yes}", no_token=f"{mid}{no}", question=question,
                                   end=day + timedelta(days=1, hours=18), events=[{"id": "e1", "title": title}]))


def test_parse_usgs_keeps_origin_time_and_magnitude_and_skips_broken_rows():
    data = {"features": [{"id": "b", "properties": {"time": 1_700_000_100_000, "mag": 5.4}},
                         {"id": "a", "properties": {"time": 1_700_000_000_000, "mag": 6.1}},
                         {"id": "c", "properties": {"time": 1_700_000_200_000, "mag": None}},
                         {"id": "d", "properties": {"time": None, "mag": 5.2}}, "bruit"]}
    assert usgs.parse_usgs(data) == [{"id": "a", "t": 1_700_000_000, "mag": 6.1}, {"id": "b", "t": 1_700_000_100, "mag": 5.4}]
    assert usgs.parse_usgs(None) == []


def test_daily_titles_and_brackets_read_the_real_polymarket_wording():
    assert sm.daily_target("What will the biggest earthquake be on October 22, 2026?") == DAY
    assert sm.daily_target("How many 5.5 or above earthquakes worldwide October 12 - October 18?") is None
    assert sm.daily_bracket("Will the biggest earthquake on October 22, 2026 be under 5.3?") == (-1.0, 5.25)
    assert sm.daily_bracket("Will the biggest earthquake on October 22, 2026 be 5.3 to 5.4?") == (5.25, 5.45)
    assert sm.daily_bracket("Will the biggest earthquake on October 22, 2026 be 6.1 or more?") == (6.05, 99.0)


def test_weekly_window_is_eastern_time_and_follows_daylight_saving():
    end = datetime(2026, 10, 19, 3, 59, tzinfo=UTC)  # fin du marché d'octobre : dimanche 23 h 59 heure de l'Est (UTC-4)
    mag, a, b = sm.weekly_target("How many 5.5 or above earthquakes worldwide October 12 - October 18?", end)
    assert (mag, a, b) == (5.5, datetime(2026, 10, 12, 4, tzinfo=UTC), datetime(2026, 10, 19, 4, tzinfo=UTC))
    _, a, b = sm.weekly_target("How many 6.5 or above earthquakes worldwide October 26 - November 1?", datetime(2026, 11, 2, 4, 59, tzinfo=UTC))
    assert (a, b) == (datetime(2026, 10, 26, 4, tzinfo=UTC), datetime(2026, 11, 2, 5, tzinfo=UTC))  # l'heure d'hiver arrive le 1er novembre
    assert sm.weekly_target("How many 6.5 or above earthquakes April 6 - 12?", datetime(2026, 4, 12, 23, 59, tzinfo=UTC))[1:] == (
        datetime(2026, 4, 6, 4, tzinfo=UTC), datetime(2026, 4, 13, 4, tzinfo=UTC))
    assert sm.weekly_target("Quelque chose d'autre", end) is None


@pytest.mark.parametrize("question,bracket", [
    ("Will there be ≤6 earthquakes of 5.5 or above magnitude worldwide?", (0, 6)),
    ("Will there be 8 or fewer earthquakes of magnitude 5.5 or higher worldwide from June 29 - July 5?", (0, 8)),
    ("Will there be exactly 10 earthquakes of magnitude 5.5 or higher worldwide from June 29 - July 5?", (10, 10)),
    ("Will there be 1 earthquake of 6.5 or above magnitude worldwide?", (1, 1)),
    ("Will there be 0 earthquakes of 6.5 or above magnitude worldwide?", (0, 0)),
    ("Will there be more than 13 earthquakes of 5.5 or above magnitude worldwide?", (14, 10 ** 6))])
def test_weekly_brackets(question, bracket):
    assert sm.weekly_bracket(question) == bracket


def test_daily_law_sums_to_one_and_keeps_the_biggest_quake_already_seen():
    now = DAY + timedelta(hours=12)
    empty = [sm.daily_p([], DAY, now, b) for b in sm.DAILY_BRACKETS.values()]
    assert sum(empty) == pytest.approx(1.0) and all(p > 0.05 for p in empty)
    seen_6_2 = [_row(DAY + timedelta(hours=3), 6.2)]  # 6,2 déjà vu : la tranche « 6,1 ou plus » est acquise, les autres sont perdues
    assert sm.daily_p(seen_6_2, DAY, now, (6.05, 99.0)) == pytest.approx(1.0)
    assert sm.daily_p(seen_6_2, DAY, now, (5.25, 5.45)) == 0.0
    seen_5_6 = [_row(DAY + timedelta(hours=3), 5.6)]
    assert sm.daily_p(seen_5_6, DAY, now, (5.45, 5.65)) > sm.daily_p([], DAY, now, (5.45, 5.65))
    assert sm.daily_p(seen_5_6, DAY, now, (-1.0, 5.25)) == 0.0
    assert sm.daily_p([], DAY, DAY + timedelta(hours=3), (6.05, 99.0)) is None      # avant 6 h : pas testé sur le passé
    assert sm.daily_p([], DAY, DAY + timedelta(hours=23, minutes=59), (6.05, 99.0)) is None
    assert sm.daily_p([_row(DAY + timedelta(days=1, hours=1), 7.5)], DAY, now, (6.05, 99.0)) < 0.2   # un séisme du lendemain ne compte pas


def test_weekly_law_counts_what_was_seen_and_is_a_distribution():
    start, end = datetime(2026, 10, 12, 4, tzinfo=UTC), datetime(2026, 10, 19, 4, tzinfo=UTC)
    now = start + timedelta(days=4)
    rows = [_row(start + timedelta(hours=h), 6.6, "m") for h in (5, 30, 60)] + [_row(start + timedelta(hours=7), 5.9, "f")]
    total = sum(sm.weekly_p(rows, 6.5, start, end, now, (k, k))[0] for k in range(0, 40))
    assert total == pytest.approx(1.0, abs=1e-6)
    p_less, n = sm.weekly_p(rows, 6.5, start, end, now, (0, 2))
    assert n == 3 and p_less == 0.0                                                  # 3 déjà vus : « 2 ou moins » est perdue
    assert sm.weekly_p(rows, 5.5, start, end, now, (4, 4))[1] == 4                   # 4 séismes >= 5,5 (le 5,9 compte)
    only_more, _ = sm.weekly_p(rows, 6.5, start, end, now, (4, 10 ** 6))
    assert 0.05 < only_more < 0.6
    assert sm.weekly_p(rows, 6.5, start, end, end - timedelta(days=1), (3, 3)) is not None
    assert sm.weekly_p(rows, 6.5, start, end, end - timedelta(hours=6), (3, 3)) is None      # moins d'un demi-jour : hors de la plage testée
    assert sm.weekly_p(rows, 6.5, start, end, end + timedelta(hours=1), (3, 3)) is None   # fenêtre finie
    assert sm.weekly_p(rows, 6.5, start, end, start - timedelta(hours=1), (3, 3)) is None


def test_attach_marks_only_yes_no_earthquake_markets_with_a_fresh_catalog(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    now = DAY + timedelta(hours=18)
    markets = [_daily_market("hi", "Will the biggest earthquake on October 22, 2026 be 6.1 or more?"),
               _daily_market("lo", "Will the biggest earthquake on October 22, 2026 be 5.3 to 5.4?"),
               parse_market(raw_market("autre", question="Will it rain?"))]
    assert sm.attach_seismes(markets, db, now) == 0                                   # pas de catalogue : rien
    refs._save(db, "ref:usgs", [_row(DAY + timedelta(hours=3), 7.0)], now)
    assert sm.attach_seismes(markets, db, now) == 2
    assert markets[0].references["seismes"]["p"] == 1.0 and markets[1].references["seismes"]["p"] == 0.0
    assert "seismes" not in (markets[2].references or {})


def test_collector_saves_the_catalog_and_survives_an_outage(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    feed = {"features": [{"id": "u1", "properties": {"time": 1_792_000_000_000, "mag": 5.6}}]}
    cfg = {"sources": {"usgs": {"enabled": True, "every_minutes": 10, "days": 10}}}
    now = DAY + timedelta(hours=18)
    result = collect(cfg, None, db, [], now, {"usgs": lambda c: usgs.parse_usgs(feed)})
    assert result.status["usgs"] == "ok (1 prix relevés)"
    seen, rows = refs._load(db, "ref:usgs")
    assert seen is not None and rows == [{"id": "u1", "t": 1_792_000_000, "mag": 5.6}]
    http = FakeHttp({}, down=(usgs.URL,))
    down = collect(cfg, None, db, [], now + timedelta(minutes=11), {"usgs": lambda c: usgs.fetch_usgs(http, now)})
    assert down.status["usgs"].startswith("indisponible") and refs._load(db, "ref:usgs")[1] == rows


def test_fetch_usgs_asks_for_the_last_days_of_magnitude_5():
    http = FakeHttp({usgs.URL: {"features": []}})
    assert usgs.fetch_usgs(http, DAY, days=10) == []
    _, params, _ = http.calls[0]
    assert params["minmagnitude"] == 5.0 and params["starttime"] == "2026-10-12T00:00:00" and params["format"] == "geojson"


def test_strategy_buys_the_side_cheaper_than_the_law_and_skips_old_catalogs(tmp_path):
    s = _s(SeismesMarche, min_net_edge=0.05, uncertainty=0.0, min_price=0.04, max_price=0.96, max_stale_hours=1,
           max_extra_ticks=1, max_proposals_per_cycle=4, kelly_fraction=0.25)
    now = datetime(2026, 10, 14, 12, 0, tzinfo=UTC)   # NOW des carnets de test

    def mk(mid, p, yes_mid, seen=now):
        m = _daily_market(mid, "Will the biggest earthquake on October 22, 2026 be 6.1 or more?", yes=f"Y", no="N")
        m.token_ids = [f"{mid}Y", f"{mid}N"]
        m.references = {"seismes": {"p": p, "titre": "test", "vu_le": seen.isoformat()}}
        return m, _books((f"{mid}Y", f"{yes_mid - 0.01:.3f}", f"{yes_mid + 0.01:.3f}"), (f"{mid}N", f"{1 - yes_mid - 0.01:.3f}", f"{1 - yes_mid + 0.01:.3f}"))
    cases = [mk("sure", 1.0, 0.60), mk("trop_cher", 0.0, 0.40), mk("proche", 0.50, 0.49), mk("billet", 0.30, 0.02),
             mk("vieux", 1.0, 0.60, seen=now - timedelta(hours=5))]
    ms, books = [c[0] for c in cases], {}
    for _, b in cases:
        books.update(b)
    for _, b in cases:
        for book in b.values():
            book.fetched_at = now
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert {p.market_id: p.outcome for p in out.proposals} == {"sure": "Yes", "trop_cher": "No"}
    assert all(p.strategy_id == "seismes_marche" for p in out.proposals) and out.abstentions
    assert {m.market_id for m in s.candidates(ms)} == {"sure", "trop_cher", "proche", "billet", "vieux"}


def test_tables_are_complete():
    t = sm.tables()
    assert set(t["jour"]) == {str(h) for h in range(25)} and set(t["semaine"]) == {"5.5", "6.5"}
    assert all(set(v) == {str(x) for x in sm.DAILY_THRESHOLDS} for v in t["jour"].values())
    assert t["jour"]["24"]["6.05"] == 1.0 and t["jour"]["12"]["5.25"] < t["jour"]["18"]["5.25"] < 1.0


def test_strategy_takes_at_most_two_buckets_of_the_same_event_best_edge_first(tmp_path):
    s = _s(SeismesMarche, min_net_edge=0.02, uncertainty=0.0, min_price=0.04, max_price=0.96, max_stale_hours=1,
           max_extra_ticks=1, max_proposals_per_cycle=6, max_per_event=2, kelly_fraction=0.25)
    now = datetime(2026, 10, 14, 12, 0, tzinfo=UTC)
    ms, books = [], {}
    for mid, p, yes in (("a", 0.95, 0.60), ("b", 0.80, 0.60), ("c", 0.70, 0.60)):    # écarts 0,35 / 0,20 / 0,10, même événement
        m = _daily_market(mid, "Will the biggest earthquake on October 22, 2026 be 6.1 or more?")
        m.references = {"seismes": {"p": p, "titre": "test", "vu_le": now.isoformat()}}
        b = _books((f"{mid}Y", f"{yes - 0.01:.3f}", f"{yes + 0.01:.3f}"), (f"{mid}N", f"{1 - yes - 0.01:.3f}", f"{1 - yes + 0.01:.3f}"))
        for book in b.values():
            book.fetched_at = now
        ms.append(m)
        books.update(b)
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert {p.market_id for p in out.proposals} == {"a", "b"} and "déjà deux tranches de cet événement" in str(out.abstentions)


def test_dedup_rows_drops_the_other_network_copy_of_the_same_quake_only():
    # Cas réel du 20/10/2026 (Vanuatu) : pt26293000 (6,6 Mi) et us6000u3jl (6,3 mww) à la même minute ; 7,0 de Chine et 6,9 de Vanuatu seuls.
    t0 = datetime(2026, 10, 20, 4, 20, tzinfo=UTC)
    rows = [{"id": "pt26293000", "t": int(t0.timestamp()), "mag": 6.6}, {"id": "us6000u3jl", "t": int(t0.timestamp()) + 20, "mag": 6.3},
            {"id": "us6000u43g", "t": int((t0 + timedelta(days=2)).timestamp()), "mag": 7.0},
            {"id": "us6000u4j2", "t": int((t0 + timedelta(days=4)).timestamp()), "mag": 6.9},
            {"id": "pt99", "t": int((t0 + timedelta(days=3)).timestamp()), "mag": 6.7},                      # seul de son réseau, rien d'autre à côté : gardé
            {"id": "us6000u4j3", "t": int((t0 + timedelta(days=4)).timestamp()) + 1000, "mag": 6.6}]       # même réseau, 1 000 s plus tard : gardé
    kept = [r["id"] for r in sm.dedup_rows(rows)]
    assert "pt26293000" not in kept and {"us6000u3jl", "us6000u43g", "us6000u4j2", "pt99", "us6000u4j3"} <= set(kept)
    start, end = t0 - timedelta(hours=1), t0 + timedelta(days=5)
    now = t0 + timedelta(days=4, hours=12)
    p_all, n_all = sm.weekly_p(rows, 6.5, start, end, now, (4, 4))
    p_dedup, n_dedup = sm.weekly_p(sm.dedup_rows(rows), 6.5, start, end, now, (4, 4))
    assert (n_all, n_dedup) == (5, 4) and p_all == 0.0 and p_dedup > 0.2          # « exactement 4 » : perdue avec le doublon, probable sans


def test_strategy_abstains_when_the_duplicate_changes_the_count(tmp_path):
    s = _s(SeismesMarche, min_net_edge=0.05, uncertainty=0.0, min_price=0.04, max_price=0.96, max_stale_hours=1,
           max_extra_ticks=1, max_proposals_per_cycle=4, kelly_fraction=0.25, max_ecart_doublon=0.15)
    now = datetime(2026, 10, 14, 12, 0, tzinfo=UTC)
    ms, books = [], {}
    for mid, p, p_dedup in (("diverge", 0.0, 0.8), ("sur", 0.0, 0.0)):
        m = _daily_market(mid, "Will the biggest earthquake on October 22, 2026 be 6.1 or more?")
        m.references = {"seismes": {"p": p, "p_dedup": p_dedup, "titre": "test", "vu_le": now.isoformat()}}
        b = _books((f"{mid}Y", "0.390", "0.410"), (f"{mid}N", "0.590", "0.610"))
        for book in b.values():
            book.fetched_at = now
        ms.append(m)
        books.update(b)
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert [p.market_id for p in out.proposals] == ["sur"] and "doublon possible entre réseaux USGS" in str(out.abstentions)
