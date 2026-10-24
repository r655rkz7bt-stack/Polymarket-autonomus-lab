"""Observatoire de Hong Kong (23/10/2026) : lecteur `meteo_hko`, rattachement aux marchés de Hong Kong,
règlement par troncature. Réponses simulées reprises des vraies réponses du 23-24/10/2026."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from conftest import NOW, make_book, raw_market
from polymarket_agent import weather_model as wm
from polymarket_agent.data_collector import collect
from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.intel_pipeline import latest_weather, weather_station
from polymarket_agent.persistence import Database
from polymarket_agent.sources import hko
from polymarket_agent.sources.polymarket_gamma import parse_market

D = Decimal
CSV = """Date time,Automatic Weather Station,Maximum Air Temperature Since Midnight(degree Celsius),Minimum Air Temperature Since Midnight(degree Celsius)
202610241410,Chek Lap Kok,29.5,27.2
202610241410,HK Observatory,31.6,27.1
202610241410,HK Park,30.9,26.4
"""
RYES = {"BulletinDate": "20261024", "ReportTimeInfoDate": "20261023", "HKOReadingsMaxTemp": "30.7",
        "HKOReadingsMinTemp": "25.9", "ChekLapKokMaxTemp": "30.1"}
DESC = ("This market will resolve to the temperature range that contains the highest temperature recorded by the Hong Kong "
        "Observatory in degrees Celsius on 24 Oct '26.\n\nThe resolution source for this market will be information from the "
        "Hong Kong Observatory, specifically the \"Absolute Daily Max (deg. C)\" ... https://www.weather.gov.hk/en/cis/climat.htm")
WHEN = datetime(2026, 10, 24, 6, 15, tzinfo=timezone.utc)  # 14 h 15 à Hong Kong


class FakeHko:
    def __init__(self, csv=CSV, ryes=RYES, down=False):
        self.csv, self.ryes, self.down, self.calls = csv, ryes, down, []

    def get_text(self, url, params=None, headers=None):
        self.calls.append(url)
        if self.down:
            raise SourceUnavailable("HKO en panne (test)")
        return self.csv

    def get_json(self, url, params=None, headers=None):
        self.calls.append(url)
        if self.ryes is None:
            raise SourceUnavailable("bulletin absent (test)")
        return self.ryes


def hk_market(mid="51", bucket="31°C", kind="highest", yes="HY", no="HN"):
    return parse_market(raw_market(market_id=mid, yes_token=yes, no_token=no, event_id="hk24", description=DESC,
                                   question=f"Will the {kind} temperature in Hong Kong be {bucket} on October 24?",
                                   resolutionSource="", end=NOW + timedelta(hours=6)))


def test_parse_maxmin_reads_the_observatory_row_in_hong_kong_time():
    when, mx, mn = hko.parse_maxmin(CSV)
    assert (when, mx, mn) == (WHEN - timedelta(minutes=5), 31.6, 27.1)  # 14 h 10 HKT = 06 h 10 UTC
    assert hko.parse_maxmin("Date time,Automatic Weather Station\n202610241410,Chek Lap Kok,29.5,27.2\n") is None
    assert hko.parse_maxmin("") is None


def test_hko_readings_are_attached_only_to_hong_kong_markets():
    other = parse_market(raw_market("52", question="Will the highest temperature in London be 16°C on October 24?",
                                    resolutionSource="https://aviationweather.gov/api/data/metar?ids=EGLC&format=raw"))
    http = FakeHko()
    obs = hko.HkoSource(http).fetch([hk_market(), other], WHEN)
    assert len(obs) == 1 and obs[0].market_ids == ["51"] and obs[0].source == "meteo_hko"
    d = obs[0].data
    assert (d["station"], d["jour_local"], d["max_jour_c"], d["min_jour_c"], d["regle"]) == ("HKO", "2026-10-24", 31.6, 27.1, "troncature")
    assert d["veille"] == {"jour": "2026-10-23", "max_c": 30.7, "min_c": 25.9}
    assert hko.HkoSource(FakeHko()).fetch([other], WHEN) == []  # aucun marché de Hong Kong : aucun appel
    # Bulletin de la veille indisponible : le relevé du jour reste servi.
    assert "veille" not in hko.HkoSource(FakeHko(ryes=None)).fetch([hk_market()], WHEN)[0].data
    assert weather_station(hk_market()) == "HKO" and weather_station(other) == "EGLC"


def test_hko_failure_is_a_degraded_source_not_a_crash(tmp_path):
    settings = {"sources": {"meteo_hko": {"enabled": True, "every_minutes": 15}}}
    result = collect(settings, FakeHko(down=True), Database(tmp_path / "m.sqlite"), [hk_market()], WHEN,
                     factories={"meteo_hko": lambda: hko.HkoSource(FakeHko(down=True))})
    assert result.status["meteo_hko"].startswith("indisponible") and result.observations == []
    garbled = collect(settings, FakeHko(), Database(tmp_path / "n.sqlite"), [hk_market()], WHEN,
                      factories={"meteo_hko": lambda: hko.HkoSource(FakeHko(csv="<html>maintenance</html>"))})
    assert garbled.status["meteo_hko"].startswith("indisponible")
    off = collect({"sources": {"meteo_hko": {"enabled": False}}}, FakeHko(), None, [hk_market()], WHEN)
    assert off.status["meteo_hko"] == "désactivée"
    # Aucun marché de Hong Kong surveillé (cycle local du 23/10) : ce n'est pas une source vide pour l'enquête.
    from polymarket_agent.enquete import sources_vides
    quiet = collect(settings, FakeHko(), Database(tmp_path / "o.sqlite"), [], WHEN)
    assert quiet.status["meteo_hko"].startswith("ok (aucun marché de Hong Kong") and not sources_vides(quiet.status)


def test_latest_weather_serves_hko_like_metar_so_lost_buckets_are_seen(ledger, limits):
    """La logique « tranche déjà dépassée » (temperature_floor) voit les marchés de Hong Kong."""
    from polymarket_agent.strategies_v2 import TemperatureFloor
    obs = hko.HkoSource(FakeHko()).fetch([hk_market()], WHEN)
    weather = latest_weather(obs, WHEN)
    assert weather["HKO"]["max_jour_c"] == 31.6 and weather["HKO"]["jour_local"] == "2026-10-24"
    lost = hk_market("53", "30°C", yes="Y30", no="N30")   # [30,0 ; 31,0[ : déjà dépassée par 31,6
    alive = hk_market("54", "31°C", yes="Y31", no="N31")  # [31,0 ; 32,0[ : 31,6 dedans
    for m in (lost, alive):
        m.weather = weather[weather_station(m)]
    strat = TemperatureFloor("1.0.0", "2026-10-24", {
        "margin_c": D("0.5"), "margin_f": D("2"), "certainty": D("0.96"), "min_net_edge": D("0.01"),
        "max_extra_ticks": D("2"), "max_proposals_per_cycle": D("3"), "kelly_fraction": D("0.5")})
    books = {t: make_book(t, bids=((b, "1000"),), asks=((a, "1000"),), ts=WHEN)
             for t, b, a in (("Y30", "0.08", "0.10"), ("N30", "0.90", "0.92"), ("Y31", "0.50", "0.52"), ("N31", "0.48", "0.50"))}
    out = strat.propose([lost, alive], books, ledger.state, limits, "B1")
    assert [p.token_id for p in out.proposals] == ["N30"]


def test_truncated_buckets_for_hong_kong_settlement():
    """122/122 marchés réglés d'août-septembre : « 27°C » contient 27,0 à 27,9 (pas 26,5 à 27,4)."""
    q = wm.parse_question("Will the highest temperature in Hong Kong be 27°C on October 24?")
    t = wm.truncated(q)
    assert (t.low, t.high) == (27.0, 28.0) and (q.low, q.high) == (26.5, 27.5)
    assert wm.truncated(wm.parse_question("Will the lowest temperature in Hong Kong be 19°C or below on October 24?")).high == 20.0
    # Tous les membres à 27,7 °C : tranche 27 sûre par troncature, alors que l'arrondi la donnait perdue.
    assert wm.probability(t, [27.7] * 10, 0.05) > 0.99 and wm.probability(q, [27.7] * 10, 0.05) < 0.01
    # « Tranche déjà dépassée » : 27,7 °C n'a pas dépassé la tranche 27 °C de Hong Kong, 28,0 °C si.
    b = wm.parse_bucket("Will the highest temperature in Hong Kong be 27°C on October 24?")
    assert wm.certain_side(b, 27.7, margin_c=0.5) == 1                      # lecture « arrondi » : faux pour Hong Kong
    assert wm.certain_side(b, 27.7, margin_c=0.5, truncation=True) is None
    assert wm.certain_side(b, 28.0, margin_c=0.5, truncation=True) == 1
    up = wm.parse_bucket("Will the highest temperature in Hong Kong be 33°C or higher on October 24?")
    assert wm.certain_side(up, 33.4, margin_c=0.5, truncation=True) is None and wm.certain_side(up, 34.0, 0.5, truncation=True) == 0


def test_get_text_returns_the_raw_body():
    class Resp:
        status_code, text, headers = 200, CSV, {}

    class Session:
        headers = {}

        def __init__(self):
            self.seen = []

        def request(self, method, url, **kw):
            self.seen.append(kw.get("headers"))
            return Resp()
    s = Session()
    http = HttpClient(session=s, sleep=lambda _: None)
    assert http.get_text(hko.MAXMIN_URL) == CSV and s.seen[0]["Accept"] == "*/*"
