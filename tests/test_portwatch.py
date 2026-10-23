"""Lecteur PortWatch + AIS (23/10/2026) : réponses simulées, rattachement aux marchés qui citent PortWatch, mode dégradé."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from conftest import NOW, raw_market
from test_sources import FakeHttp
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.persistence import Database
from polymarket_agent.sources import portwatch as pw
from polymarket_agent.sources.polymarket_gamma import parse_market

BAB_RULES = ("This market will resolve according to the 7-day moving average of transit calls (“Arrivals of Ships”) for the "
             "Bab el-Mandeb Strait that IMF Portwatch reports for October 31, 2026.")
HZ_RULES = "This market will resolve according to the total number of transit calls that IMF Portwatch reports for the Strait of Hormuz"
PANAMA_RULES = "Yes if IMF PortWatch publishes a 7-day moving average of transit calls for the Panama Canal less than or equal to 10"


def _features(name, start, counts):
    return {"features": [{"attributes": {"date": (start + timedelta(days=i)).isoformat(), "n_total": c, "portname": name}}
                         for i, c in enumerate(counts)]}


def _routes(fail=()):
    start = date(2026, 8, 1)
    series = {"Bab el-Mandeb Strait": [26 + (i % 5) for i in range(79)], "Strait of Hormuz": [3 + (i % 4) for i in range(79)],
              "Panama Canal": [33] * 79}

    def arcgis(params):
        name = params["where"].split("'")[1]
        if name in fail:
            raise SourceUnavailable(f"{name} en panne (test)")
        return _features(name, start, series.get(name, []))
    return {
        pw.URL: arcgis,
        pw.AIS + "/api/crossings/daily": [{"day": "2026-10-22", "direction": "inbound", "count": 16},
                                          {"day": "2026-10-22", "direction": "outbound", "count": 9},
                                          {"day": "2026-10-22", "direction": "in_strait", "count": 142}],
        pw.AIS + "/api/bab/daily": {"days": [{"day": "2026-10-22", "northbound": 27, "southbound": 16, "in_strait": 9}]},
    }


def _markets():
    bab = parse_market(raw_market("b1", question="Will there be between 25 and 29 average daily transits of the Bab el-Mandeb Strait on October 31?",
                                  description=BAB_RULES))
    hz = parse_market(raw_market("h1", question="Will 20-24 ships transit the Strait of Hormuz between October 26-November 1?",
                                 description=HZ_RULES))
    pan = parse_market(raw_market("p1", question="Panama Canal effectively closed by October 31?", description=PANAMA_RULES))
    talk = parse_market(raw_market("t1", question="Will Iran close the Strait of Hormuz?", description="Resolves per credible reporting."))
    return [bab, hz, pan, talk]


def test_parsers_read_portwatch_and_both_ais_feeds():
    assert pw.parse_portwatch(_features("x", date(2026, 10, 17), [4, 0])) == [("2026-10-17", 4), ("2026-10-18", 0)]
    assert pw.parse_portwatch({"features": [{"attributes": {"date": "2026-10-18", "n_total": None}}]}) == []
    assert pw.parse_portwatch({"error": {"code": 400}}) == []
    routes = _routes()
    assert pw.parse_ais("Strait of Hormuz", routes[pw.AIS + "/api/crossings/daily"]) == [("2026-10-22", 25)]  # in_strait n'est pas un passage
    assert pw.parse_ais("Bab el-Mandeb Strait", routes[pw.AIS + "/api/bab/daily"]) == [("2026-10-22", 43)]
    assert pw.parse_ais("Suez Canal", routes[pw.AIS + "/api/bab/daily"]) == []


def test_markets_are_attached_only_when_they_cite_portwatch_and_name_the_strait():
    by = pw.markets_by_chokepoint(_markets())
    assert by == {"Bab el-Mandeb Strait": ["b1"], "Strait of Hormuz": ["h1"], "Panama Canal": ["p1"]}  # t1 ne cite pas PortWatch


def test_publication_rhythm_is_weekly_on_tuesday_up_to_the_previous_sunday():
    friday = datetime(2026, 10, 23, 18, tzinfo=timezone.utc)
    assert pw.last_update(friday.date()) == date(2026, 10, 18)
    assert pw.last_update(date(2026, 10, 26)) == date(2026, 10, 18)  # lundi : rien de neuf depuis mardi
    assert pw.last_update(date(2026, 10, 27)) == date(2026, 10, 25)  # mardi : la semaine précédente arrive


def test_source_gives_one_observation_per_strait_with_the_series_and_the_ais(tmp_path):
    http = FakeHttp(_routes())
    source = pw.PortWatchSource(http)
    obs = source.fetch(_markets(), NOW)
    by = {o.data["detroit"]: o for o in obs}
    assert set(by) == {"Bab el-Mandeb Strait", "Strait of Hormuz", "Panama Canal"}
    bab = by["Bab el-Mandeb Strait"]
    assert bab.market_ids == ["b1"] and bab.source == "portwatch" and bab.reliability >= 0.9
    assert bab.data["dernier_jour"] == "2026-10-18" and bab.data["somme7"] == sum(26 + (i % 5) for i in range(72, 79))
    assert bab.data["ais"] == [["2026-10-22", 43]] and "AIS" in bab.text
    assert by["Panama Canal"].data["ais"] == []  # pas de suivi AIS pour Panama : aucun appel
    assert not any(c[0].endswith("/api/panama/daily") for c in http.calls)
    assert {r["detroit"] for r in source.rows} == set(by) and len(source.rows[0]["jours"]) == 79


def test_degraded_mode_ais_down_or_one_strait_down_never_blocks_the_others():
    routes = _routes(fail=("Strait of Hormuz",))
    http = FakeHttp(routes, down=(pw.AIS,))
    source = pw.PortWatchSource(http)
    obs = source.fetch(_markets(), NOW)
    assert {o.data["detroit"] for o in obs} == {"Bab el-Mandeb Strait", "Panama Canal"}
    assert all(o.data["ais"] == [] for o in obs)
    assert "Strait of Hormuz" in source.failures and "AIS Bab el-Mandeb Strait" in source.failures
    with pytest.raises(SourceUnavailable):  # tout en panne : la source est « indisponible » (le collecteur continue)
        pw.PortWatchSource(FakeHttp({}, down=(pw.URL,))).fetch(_markets(), NOW)


def _settings(enabled=True):
    return {"sources": {"portwatch": {"enabled": enabled, "every_minutes": 120}}}


def test_collector_saves_the_series_for_attach_detroits_and_survives_a_failure(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    markets = _markets()
    result = collect(_settings(), None, db, markets, NOW, {"portwatch": lambda: pw.PortWatchSource(FakeHttp(_routes()))})
    assert result.status["portwatch"] == "ok (3 observations)"
    seen, rows = refs._load(db, "ref:portwatch")
    assert seen is not None and {r["detroit"] for r in rows} >= {"Bab el-Mandeb Strait", "Strait of Hormuz"}
    assert any(o.source == "portwatch" and o.market_ids == ["b1"] for o in result.observations)
    # Panne totale deux heures plus tard : source « indisponible », l'ancienne série reste en base, rien ne plante.
    later = NOW + timedelta(hours=2, minutes=1)
    down = collect(_settings(), None, db, markets, later, {"portwatch": lambda: pw.PortWatchSource(FakeHttp({}, down=(pw.URL,)))})
    assert down.status["portwatch"].startswith("indisponible")
    assert refs._load(db, "ref:portwatch")[1] == rows
    assert collect(_settings(False), None, db, markets, later, {}).status["portwatch"] == "désactivée"
