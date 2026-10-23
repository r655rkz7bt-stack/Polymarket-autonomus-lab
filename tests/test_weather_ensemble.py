"""Ensembles Open-Meteo (23/10/2026) : membres par jour local, probabilité par tranche (°C / °F, arrondi /
troncature), relevé en base à côté des prix, mode dégradé. Réponses simulées au format réel du 23/10/2026."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from conftest import raw_market
from polymarket_agent import weather_model as wm
from polymarket_agent import weather_ensemble as we
from polymarket_agent.data_collector import collect
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.intel_pipeline import latest_weather
from polymarket_agent.persistence import Database
from polymarket_agent.sources import hko
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.sources.weather import ENSEMBLE_URL, EnsembleSource, station_for_market
from test_sources import FakeHttp

NOW = datetime(2026, 10, 23, 18, 0, tzinfo=timezone.utc)
HK_DESC = "the highest temperature recorded by the Hong Kong Observatory ... https://www.weather.gov.hk/en/cis/climat.htm"


def hourly(days=("2026-10-24", "2026-10-25"), gefs=(16.0, 17.2, 15.4), ecmwf=(16.4, 18.0), partial_last=False):
    """Format Open-Meteo : témoin sans « memberNN », puis les membres ; une valeur par heure locale."""
    times = [f"{d}T{h:02d}:00" for d in days for h in range(24)]
    out = {"time": times}

    def series(peak):
        vals = [peak - 6 + 6 * (1 - abs(h - 14) / 14) for d in days for h in range(24)]
        if partial_last:
            vals[-10:] = [None] * 10
        return vals
    for i, peak in enumerate(gefs):
        out["temperature_2m_ncep_gefs025" if i == 0 else f"temperature_2m_member{i:02d}_ncep_gefs025"] = series(peak)
    for i, peak in enumerate(ecmwf):
        out["temperature_2m_ecmwf_ifs025_ensemble" if i == 0 else f"temperature_2m_member{i:02d}_ecmwf_ifs025_ensemble"] = series(peak)
    out["temperature_2m_member01_ukmo_global_ensemble_20km"] = series(40.0)  # modèle non demandé : ignoré
    return out


def london(mid="61", bucket="16°C", yes="LY", no="LN", bid=0.40, ask=0.42):
    return parse_market(raw_market(mid, yes_token=yes, no_token=no, event_id="lon24", best_bid=bid, best_ask=ask,
                                   question=f"Will the highest temperature in London be {bucket} on October 24?",
                                   resolutionSource="https://aviationweather.gov/api/data/metar?ids=EGLC&format=raw"))


def hong_kong(mid="62", bucket="27°C"):
    return parse_market(raw_market(mid, event_id="hk24", description=HK_DESC, resolutionSource="",
                                   question=f"Will the highest temperature in Hong Kong be {bucket} on October 24?"))


def test_daily_keeps_each_member_max_and_min_per_local_day():
    days = EnsembleSource(None).daily(hourly())
    assert sorted(days) == ["2026-10-24", "2026-10-25"]
    assert days["2026-10-24"]["max"]["gefs"] == [16.0, 17.2, 15.4] and days["2026-10-24"]["max"]["ecmwf"] == [16.4, 18.0]
    assert days["2026-10-24"]["min"]["gefs"] == [10.0, 11.2, 9.4]
    assert "ukmo" not in json.dumps(days)  # seuls les modèles demandés
    # Jour incomplet (moins de 20 heures) : écarté.
    assert sorted(EnsembleSource(None).daily(hourly(partial_last=True))) == ["2026-10-24"]
    only_gefs = EnsembleSource(None, models=("gfs025",)).daily(hourly())
    assert set(only_gefs["2026-10-24"]["max"]) == {"gefs"}


def test_bucket_probability_is_the_share_of_members_with_unit_and_settlement_rule():
    q = wm.parse_question("Will the highest temperature in London be 16°C on October 24?")      # [15,5 ; 16,5[
    assert we.share(q, [16.0, 17.2, 15.4, 16.4, 18.0]) == 2 / 5
    assert we.share(q, [16.0, 17.2, 15.4, 16.4, 18.0], shift_c=1.0) == 1 / 5  # biais de station : +1 °C
    f = wm.parse_question("Will the highest temperature in Dallas be between 76-77°F on October 24?")  # [75,5 ; 77,5[
    assert we.share(f, [24.5, 25.0, 25.3, 26.0]) == 2 / 4   # 76,1 / 77,0 dedans ; 77,54 et 78,8 °F : tranche suivante
    hk = wm.parse_question("Will the highest temperature in Hong Kong be 27°C on October 24?")
    assert we.share(hk, [27.7, 27.2, 26.8], truncation=True) == 2 / 3 and we.share(hk, [27.7, 27.2, 26.8]) == 2 / 3
    assert we.share(hk, [27.7, 27.6], truncation=True) == 1.0 and we.share(hk, [27.7, 27.6]) == 0.0
    assert we.share(q, []) is None
    assert we.market_day(q, NOW) == "2026-10-24"
    jan = wm.parse_question("Will the highest temperature in London be 5°C on January 1?")
    assert we.market_day(jan, datetime(2026, 12, 31, tzinfo=timezone.utc)) == "2027-01-01"


def test_ensemble_is_fetched_for_cited_stations_and_recorded_next_to_prices(tmp_path):
    db = Database(tmp_path / "m.sqlite")
    db.set_value("station:EGLC", json.dumps([51.505, 0.055]))
    payload = [dict(utc_offset_seconds=3600, hourly=hourly()), dict(utc_offset_seconds=28800, hourly=hourly(gefs=(27.7, 27.2, 26.8), ecmwf=(27.5,)))]
    http = FakeHttp({ENSEMBLE_URL: payload})
    markets = [london(), london("63", "17°C", "L7", "N7"), hong_kong(), hong_kong("64", "26°C"),
               parse_market(raw_market("65", question="Will Bitcoin be above 80k on October 24?"))]
    settings = {"sources": {"meteo_ensemble": {"enabled": True, "every_minutes": 360, "per_request": 10}}}
    result = collect(settings, http, db, markets, NOW)
    assert result.status["meteo_ensemble"] == "ok (2 observations, 4 tranches relevées)"
    params = http.calls[0][1]
    assert params["models"] == "gfs025,ecmwf_ifs025" and params["latitude"] == "51.505,22.302"  # EGLC puis HKO (ordre alphabétique)
    rows = {r[0]: r for r in db.conn.execute(
        "SELECT marche, station, regle, p_gefs, p_ecmwf, p_ensemble, membres, meilleur_acheteur, meilleur_vendeur, avance_h "
        "FROM meteo_ensemble_releves")}
    assert rows["61"][1:7] == ("EGLC", "arrondi", 1 / 3, 1 / 2, 2 / 5, 5)
    assert rows["61"][7:9] == (0.40, 0.42)
    assert rows["61"][9] == 5.0   # minuit à Londres (UTC+1) le 24/10 = 23 h UTC le 23/10, 5 h après 18 h
    assert rows["62"][1:3] == ("HKO", "troncature") and rows["62"][5] == 0.75    # 27,7 / 27,2 / 27,5 dans [27 ; 28[
    assert rows["64"][5] == 0.25                                                   # 26,8 dans [26 ; 27[
    members = db.conn.execute("SELECT station, type, gefs, ecmwf FROM meteo_ensemble_membres ORDER BY station").fetchall()
    assert [(s, k) for s, k, *_ in members] == [("EGLC", "max"), ("HKO", "max")]
    assert json.loads(members[0][2]) == [16.0, 17.2, 15.4]
    # Les marchés reçoivent l'ensemble de leur station (clé « ensemble »), comme la prévision.
    weather = latest_weather(result.observations, NOW)
    assert weather[station_for_market(markets[2])]["ensemble"]["jours"]["2026-10-24"]["max"]["ecmwf"] == [27.5]


def test_ensemble_outage_or_no_station_is_degraded_not_fatal(tmp_path):
    db = Database(tmp_path / "m.sqlite")
    db.set_value("station:EGLC", json.dumps([51.505, 0.055]))
    settings = {"sources": {"meteo_ensemble": {"enabled": True}}}
    down = collect(settings, FakeHttp({}, down=(ENSEMBLE_URL,)), db, [london()], NOW)
    assert down.status["meteo_ensemble"].startswith("indisponible")
    nothing = collect(settings, FakeHttp({}), Database(tmp_path / "n.sqlite"), [london()], NOW)  # coordonnées inconnues
    assert nothing.status["meteo_ensemble"] == "ok (0 observations)"
    assert we.record(db, [london()], [], NOW) == 0
    assert hko.is_hko_market(hong_kong()) and not hko.is_hko_market(london())
