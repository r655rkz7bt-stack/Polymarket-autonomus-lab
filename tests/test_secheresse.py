"""Sécheresse D4 par État (11/11/2026, experiments/secheresse.md, piste n° 24) : source USDM, loi de transition, rattachement aux
marchés « Exceptional drought (D4) by state — week of … », collecteur et stratégie `secheresse_d4`."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from conftest import raw_market
from test_sources import FakeHttp
from test_strategies_v3 import LIMITS, _books, _s, _state
from polymarket_agent import references as refs
from polymarket_agent import secheresse as sh
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources import usdm
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import SecheresseD4

UTC = timezone.utc
NOW = datetime(2026, 11, 11, 11, 0, tzinfo=UTC)
# Cartes réelles du 03/11/2026 (API USDM, statistiques catégorielles)
API = [{"mapDate": "2026-11-03T00:00:00", "stateAbbreviation": "AR", "none": 0.0, "d0": 0.0, "d1": 3.0, "d2": 14.9, "d3": 42.38, "d4": 39.72},
       {"mapDate": "2026-11-03T00:00:00", "stateAbbreviation": "AZ", "none": 62.94, "d0": 25.14, "d1": 10.18, "d2": 1.75, "d3": 0.0, "d4": 0.0},
       {"mapDate": "2026-11-03T00:00:00", "stateAbbreviation": "NV", "none": 50.0, "d0": 20.0, "d1": 15.0, "d2": 11.23, "d3": 3.76, "d4": 0.01},
       {"mapDate": "2026-10-27T00:00:00", "stateAbbreviation": "AR", "none": 0.0, "d0": 0.0, "d1": 3.0, "d2": 15.0, "d3": 42.0, "d4": 40.0},
       "bruit", {"mapDate": "2026-11-03T00:00:00"}]


def _market(mid, state, week="November 10, 2026"):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2026, 11, 12, 14, tzinfo=UTC),
                                   question=f"Will {state} have D4 (Exceptional Drought) this week?",
                                   events=[{"id": "d1", "title": f"Exceptional drought (D4) by state — week of {week}"}]))


def test_parse_usdm_keeps_state_date_and_d2_d4_and_skips_broken_rows():
    rows = usdm.parse_usdm(API)
    assert [r["id"] for r in rows] == ["AR:2026-10-27", "AR:2026-11-03", "AZ:2026-11-03", "NV:2026-11-03"]
    assert rows[1] == {"id": "AR:2026-11-03", "etat": "AR", "date": "2026-11-03", "d2": 14.9, "d3": 42.38, "d4": 39.72}


def test_fetch_usdm_asks_all_states_with_their_fips_codes():
    http = FakeHttp({usdm.URL: API})
    assert len(usdm.fetch_usdm(http, NOW)) == 4
    _, params, _ = http.calls[0]
    assert params["statisticsType"] == 2 and params["startdate"] == "10/21/2026" and params["enddate"] == "11/12/2026"
    assert len(params["aoi"].split(",")) == 48 and "05" in params["aoi"]


def test_week_and_state_are_read_from_the_event_and_the_question():
    assert sh.week_of("Exceptional drought (D4) by state — week of November 10, 2026") == date(2026, 11, 10)
    assert sh.week_of("How many states will be in D4 (Exceptional Drought) — week of November 10, 2026?") is None
    assert sh.state_of("Will New Mexico have D4 (Exceptional Drought) this week?") == "NM"
    assert sh.state_of("Will Atlantis have D4 (Exceptional Drought) this week?") is None


def test_p_yes_uses_the_transition_law_then_the_published_map():
    rows = usdm.parse_usdm(API)
    ar, _ = sh.p_yes(rows, "AR", date(2026, 11, 10))
    az, _ = sh.p_yes(rows, "AZ", date(2026, 11, 10))
    nv, _ = sh.p_yes(rows, "NV", date(2026, 11, 10))
    assert ar > 0.97 and az < 0.001 and 0.05 < nv < 0.3          # D4 39,7 % ; aucun D3 ; D4 0,01 % (sous le seuil, bruit de frontière)
    assert sh.p_yes(rows, "AR", date(2026, 11, 3))[0] == 1.0       # carte de la semaine publiée : réponse connue
    assert sh.p_yes(rows, "AZ", date(2026, 11, 3))[0] == 0.0
    assert sh.p_yes(rows, "AR", date(2026, 11, 24)) is None        # carte trop vieille de trois semaines : pas d'avis
    assert sh.p_yes(rows, "TX", date(2026, 11, 10)) is None


def test_collector_saves_the_maps_and_attach_and_strategy_buy_the_cheap_near_certain_side(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    cfg = {"sources": {"usdm": {"enabled": True, "every_minutes": 60, "days": 21}}}
    result = collect(cfg, None, db, [], NOW, {"usdm": lambda c: usdm.parse_usdm(API)})
    assert result.status["usdm"] == "ok (4 prix relevés)"
    ar, az, nv = _market("ar", "Arkansas"), _market("az", "Arizona"), _market("nv", "Nevada")
    other = _market("old", "Arkansas", week="October 27, 2026")     # carte de la semaine publiée : réponse connue
    assert refs.attach_all([ar, az, nv, other], db, NOW)["secheresse"] == 4
    assert ar.references["secheresse"]["p"] > 0.97 and other.references["secheresse"]["p"] == 1.0
    s = _s(SecheresseD4, min_net_edge=0.05, uncertainty=0.02, min_price=0.10, max_price=0.95, max_stale_hours=2, max_extra_ticks=1,
           max_proposals_per_cycle=6, max_per_event=10, kelly_fraction=1.0)
    books = {}
    books.update(_books(("arY", "0.20", "0.30"), ("arN", "0.70", "0.80")))     # OUI d'un État en D4 vendu 0,30 : à acheter
    books.update(_books(("azY", "0.01", "0.99"), ("azN", "0.01", "0.99")))     # cotes de façade : rien
    books.update(_books(("nvY", "0.10", "0.15"), ("nvN", "0.85", "0.90")))     # loi ≈ 0,14 : prix juste, rien
    for b in books.values():
        b.fetched_at = NOW
    out = s.propose([ar, az, nv], books, _state(tmp_path), LIMITS, "b1")
    assert [(p.market_id, p.token_id) for p in out.proposals] == [("ar", "arY")]
