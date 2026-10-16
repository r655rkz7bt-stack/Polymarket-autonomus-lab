"""Météo : biais et flou par station appris sur les jours précédents (valeur réelle = tranche gagnante)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from polymarket_agent import weather_calibration as wc
from polymarket_agent.observations import Observation
from polymarket_agent.persistence import Database

SRC = "https://www.weather.gov/wrh/timeseries?site=lfpb"


def _event(question: str, won: bool = True, end: str = "2026-10-14T12:00:00Z", eid: str = "e1") -> dict:
    return {"id": eid, "slug": "highest-temperature-in-paris-on-october-14-2026", "endDate": end,
            "markets": [{"question": "Will the highest temperature in Paris be 30°C on October 14?",
                         "outcomePrices": '["0", "1"]', "resolutionSource": SRC},
                        {"question": question, "outcomePrices": '["1", "0"]' if won else '["0", "1"]',
                         "resolutionSource": SRC, "endDate": end}]}


def test_true_value_is_read_from_the_winning_bracket():
    assert wc.truth_from_event(_event("Will the highest temperature in Paris be 16°C on October 14?")) == (
        "LFPB", "2026-10-14", "max", 16.0)
    # Tranche « X ou plus » : un demi-degré au-dessus de la borne ; °F converti en °C.
    assert wc.truth_from_event(_event("Will the highest temperature in Paris be 20°C or higher on October 14?"))[3] == 20.0
    st, day, kind, v = wc.truth_from_event(_event("Will the lowest temperature in Paris be between 50-51°F on October 14?"))
    assert (kind, round(v, 2)) == ("min", round((50.5 - 32) / 1.8, 2))
    assert wc.truth_from_event(_event("Will the highest temperature in Paris be 16°C on October 14?", won=False)) is None


def _forecast(day: str, mx: list[float], offset: int = 7200) -> Observation:
    return Observation(source="meteo_prevision", external_id=f"p-{day}", published_at=None, collected_at=None, url="", title="", text="",
                       data={"station": "LFPB", "utc_offset": offset, "jours": {day: {"max": mx, "min": [5.0, 6.0]}}})


def test_only_forecasts_made_before_the_local_day_are_kept_and_errors_are_joined(tmp_path):
    db = Database(tmp_path / "m.sqlite")
    before = datetime(2026, 10, 13, 20, 0, tzinfo=timezone.utc)  # 13/10 22 h à Paris : la veille
    assert wc.record_forecasts(db, [_forecast("2026-10-14", [14.0, 15.0])], before) == 2
    # Le jour a commencé (14/10 02 h à Paris) : cette prévision ne remplace pas celle de la veille.
    during = datetime(2026, 10, 14, 0, 0, tzinfo=timezone.utc)
    assert wc.record_forecasts(db, [_forecast("2026-10-14", [30.0, 30.0])], during) == 0
    db.conn.execute("INSERT INTO meteo_reel VALUES ('LFPB','2026-10-14','max',16.0,'e1')")
    assert wc.errors(db, "LFPB", "max", "2026-10-15") == [pytest.approx(1.5)]
    assert wc.errors(db, "LFPB", "max", "2026-10-14") == []  # jamais le jour même ni après


def test_update_truth_reads_closed_weather_events(tmp_path):
    from test_sources import FakeHttp
    db = Database(tmp_path / "m.sqlite")
    http = FakeHttp({wc.GAMMA_EVENTS: [_event("Will the highest temperature in Paris be 16°C on October 14?"),
                                       {"id": "x", "slug": "bitcoin-above", "markets": []}]})
    assert wc.update_truth(db, http, datetime(2026, 10, 16, tzinfo=timezone.utc)) == 1
    assert [tuple(r) for r in db.conn.execute("SELECT station, jour, type, valeur FROM meteo_reel")] == [
        ("LFPB", "2026-10-14", "max", 16.0)]


def test_station_parameters_shrink_towards_the_global_setting():
    assert wc.station_params([2.0, 2.0], 1.5, 0.5) == (1.5, 0.5, 2)  # trop peu de jours : réglage global
    sigma, bias, n = wc.station_params([2.0, 2.0, 2.0], 1.5, 0.5)
    assert n == 3 and bias == pytest.approx(1.25)  # (6 + 3 × 0,5) / 6
    assert sigma == pytest.approx((3 * 1.5 ** 2 / 6) ** 0.5, abs=1e-3)  # erreurs identiques : flou réduit
    assert wc.station_params([0.0, 0.0, 0.0, 0.0], 1.0, 0.0, shrink=0)[0] == 0.8  # plancher


def test_strategy_uses_the_station_errors_when_enabled(tmp_path):
    from conftest import KEY, NOW, ROOT
    from test_weather_model import _setup_market, _strategy
    from polymarket_agent.ledger import Ledger
    from polymarket_agent.safety_controller import RiskLimits
    ledger = Ledger.create(tmp_path / "l.jsonl", KEY, tmp_path / "l.lock", "1000", now=NOW)
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    # Modèles à 14-14,4 °C ; la station est d'habitude 2 °C plus chaude : la tranche 16 °C devient probable.
    m, books = _setup_market(no_ask="0.60")
    m.weather["prevision"]["erreurs"] = {"max": [2.0, 2.1, 1.9, 2.0, 2.0], "min": []}
    plain = _strategy().propose([m], books, ledger.state, limits, "b1")
    assert plain.proposals  # réglage global : NON sur 16 °C
    calibrated = _strategy(station_calibration=Decimal("1")).propose([m], books, ledger.state, limits, "b1")
    assert not calibrated.proposals  # étalonnée : 16 °C n'est plus surcotée
    m.weather["prevision"]["erreurs"] = {"max": [0.0, 0.1, -0.1, 0.0, 0.0], "min": []}
    out = _strategy(station_calibration=Decimal("1")).propose([m], books, ledger.state, limits, "b1")
    assert out.proposals and "(station, 5 j)" in out.proposals[0].uncertainty


def test_collector_records_forecasts_and_attaches_past_errors(tmp_path):
    from conftest import NOW, raw_market
    from test_sources import FakeHttp
    from polymarket_agent.data_collector import collect
    from polymarket_agent.sources.polymarket_gamma import parse_market
    from polymarket_agent.sources.weather import FORECAST_URL
    times = [f"2026-10-15T{h:02d}:00" for h in range(24)]
    hourly = {"time": times, "temperature_2m_gfs_seamless": [10.0] * 24, "temperature_2m_ecmwf_ifs025": [12.0] * 24}
    m = parse_market(raw_market("w1", question="Will the highest temperature in Paris be 16°C on October 15?",
                                resolutionSource=SRC))
    db = Database(tmp_path / "m.sqlite")
    db.set_value("station:LFPB", "[48.97, 2.44]")
    db.conn.executescript(wc.SCHEMA)
    db.conn.execute("INSERT INTO meteo_previsions VALUES ('LFPB','2026-10-13','max',15.0,'x')")
    db.conn.execute("INSERT INTO meteo_reel VALUES ('LFPB','2026-10-13','max',16.0,'e1')")
    http = FakeHttp({FORECAST_URL: [{"utc_offset_seconds": 7200, "hourly": hourly}], wc.GAMMA_EVENTS: []})
    settings = {"sources": {"meteo_prevision": {"enabled": True, "every_minutes": 60},
                            "meteo_reel": {"enabled": True, "every_minutes": 180}}}
    result = collect(settings, http, db, [m], NOW)  # NOW = 14/10 : le 15/10 n'a pas commencé
    fc = next(o for o in result.observations if o.source == "meteo_prevision")
    assert fc.data["erreurs"] == {"max": [1.0], "min": []}
    assert db.conn.execute("SELECT moyenne FROM meteo_previsions WHERE jour='2026-10-15' AND type='max'"
                           ).fetchone()[0] == 11.0
    assert result.status["meteo_reel"] == "ok (0 valeurs réelles)"


def test_backfill_reads_the_forecast_archive_once_per_station_without_overwriting(tmp_path):
    from test_sources import FakeHttp
    db = Database(tmp_path / "m.sqlite")
    db.conn.executescript(wc.SCHEMA)
    db.conn.execute("INSERT INTO meteo_previsions VALUES ('LFPB','2026-10-13','max',99.0,'direct')")
    times = [f"2026-10-{d}T{h:02d}:00" for d in (13, 14) for h in range(24)]
    hourly = {"time": times, "temperature_2m_previous_day1_gfs_seamless": [10.0] * 47 + [20.0],
              "temperature_2m_previous_day1_ecmwf_ifs025": [12.0] * 48}
    http = FakeHttp({wc.PREVIOUS_RUNS: [{"hourly": hourly}]})
    now = datetime(2026, 10, 14, 6, 0, tzinfo=timezone.utc)
    assert wc.backfill_forecasts(db, http, {"LFPB": (48.97, 2.44)}, now) == 1  # 13/10 min seulement
    rows = {(r[0], r[1]): r[2] for r in db.conn.execute("SELECT jour, type, moyenne FROM meteo_previsions")}
    assert rows == {("2026-10-13", "max"): 99.0, ("2026-10-13", "min"): 11.0}  # le 14/10 n'est pas passé
    assert wc.backfill_forecasts(db, http, {"LFPB": (48.97, 2.44)}, now) == 0 and len(http.calls) == 1
