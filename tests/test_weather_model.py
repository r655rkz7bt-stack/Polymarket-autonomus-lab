"""Modèle météo (marchés de température) : lecture des questions, probabilités des tranches."""

from __future__ import annotations

import pytest

from polymarket_agent import weather_model as wm


def test_questions_are_parsed_into_brackets():
    q = wm.parse_question("Will the highest temperature in Paris be 16°C on October 17?")
    assert (q.kind, q.low, q.high, q.unit, q.month, q.day) == ("max", 15.5, 16.5, "C", 10, 17)
    q = wm.parse_question("Will the lowest temperature in Miami be between 76-77°F on October 17?")
    assert (q.kind, q.low, q.high, q.unit) == ("min", 75.5, 77.5, "F")
    assert wm.parse_question("Will the highest temperature in Denver be 41°F or below on October 15?").high == 41.5
    assert wm.parse_question("Will the highest temperature in Seoul be 26°C or higher on October 17?").low == 25.5
    assert wm.parse_question("Will Bitcoin be above 80000 on October 17?") is None


def test_probabilities_sum_to_one_and_observations_rule_out_brackets():
    members = [15.8, 16.2, 16.4, 15.9]
    qs = [wm.parse_question(f"Will the highest temperature in Paris be {t}°C on October 17?") for t in range(5, 30)]
    total = sum(wm.probability(q, members, 1.0) for q in qs)
    assert total == pytest.approx(1.0, abs=1e-3)
    q16 = qs[11]
    assert wm.probability(q16, members, 1.0) > wm.probability(qs[14], members, 1.0)
    # Maximum déjà relevé à 18 °C : la tranche 16 °C est impossible.
    assert wm.probability(q16, members, 1.0, observed_c=18.0) == 0.0
    low, est, high = wm.band(q16, members, 1.0, 1.0, 1.6)
    assert low <= est <= high
    # °F : flou converti (1 °C = 1,8 °F).
    qf = wm.parse_question("Will the highest temperature in Dallas be between 60-61°F on October 17?")
    assert wm.probability(qf, [15.85], 0.5) > 0.5


def _setup_market(no_ask="0.45", question="Will the highest temperature in Paris be 16°C on October 17?",
                  members=(14.0, 14.4), offset=7200, observed=None, observed_day=None):
    from datetime import datetime, timedelta, timezone
    from decimal import Decimal
    from conftest import NOW, make_book, raw_market
    from polymarket_agent.sources.polymarket_gamma import parse_market
    m = parse_market(raw_market("w1", yes_token="Y", no_token="N", question=question,
                                resolutionSource="https://www.weather.gov/wrh/timeseries?site=lfpb",
                                bestBid=0.5, bestAsk=0.56))
    # NOW = 14/10 12:00 UTC ; jour du marché : 17/10 → trop loin. On décale la date du test.
    m.weather = {"prevision": {"station": "LFPB", "utc_offset": offset,
                               "jours": {"2026-10-17": {"max": list(members), "min": [8.0, 8.5]}}}}
    if observed is not None:
        m.weather.update(jour_local=observed_day, max_jour_c=observed)
    when = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)
    books = {"N": make_book("N", bids=((str(Decimal(no_ask) - Decimal("0.02")), "500"),), asks=((no_ask, "500"),),
                            ts=when, fetched=when),
             "Y": make_book("Y", bids=(("0.53", "500"),), asks=(("0.56", "500"),), ts=when, fetched=when)}
    return m, books


def _strategy(**over):
    from decimal import Decimal as D
    from polymarket_agent.strategies_v2 import MeteoForecast
    params = {"min_net_edge": D("0.05"), "margin": D("0.02"), "sigma_max": D("1.5"), "bias_max": D("0.5"),
              "sigma_min": D("1.8"), "bias_min": D("0"), "max_lead_hours": D("36"), "min_lead_hours": D("6"),
              "min_no_price": D("0.2"), "max_no_price": D("0.8"), "allow_yes": D("0"), "max_extra_ticks": D("1"),
              "max_proposals_per_cycle": D("8")}
    params.update(over)
    return MeteoForecast("1.0.0", "2026-10-16", params)


def test_meteo_strategy_buys_no_on_an_overpriced_favourite_bracket(tmp_path):
    from conftest import KEY, NOW
    from polymarket_agent.ledger import Ledger
    from polymarket_agent.safety_controller import RiskLimits
    from conftest import ROOT
    ledger = Ledger.create(tmp_path / "l.jsonl", KEY, tmp_path / "l.lock", "1000", now=NOW)
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    # Modèles à 14-14,4 °C : la tranche 16 °C est peu probable, le marché la cote ≈ 0,55 → NON à 0,45.
    m, books = _setup_market()
    s = _strategy()
    assert s.candidates([m]) == [m]
    out = s.propose([m], books, ledger.state, limits, "b1")
    assert len(out.proposals) == 1 and out.proposals[0].token_id == "N" and out.proposals[0].outcome == "No"
    assert float(out.proposals[0].est_probability) > 0.8
    # Tranche la plus probable selon le modèle (≈ 25 %), cotée à son juste prix (NON à 0,76) : aucun pari.
    m2, books2 = _setup_market(no_ask="0.76", question="Will the highest temperature in Paris be 15°C on October 17?")
    assert not _strategy().propose([m2], books2, ledger.state, limits, "b1").proposals
    # Hors de la zone testée (NON à 0,9) ou hors fenêtre (jour trop lointain) : abstention.
    m3, books3 = _setup_market(no_ask="0.90")
    assert not s.propose([m3], books3, ledger.state, limits, "b1").proposals
    s_close = _strategy(max_lead_hours=__import__("decimal").Decimal("1"))
    assert not s_close.propose([m], books, ledger.state, limits, "b1").proposals
    # Sans prévision : abstention.
    m.weather = None
    assert not s.propose([m], books, ledger.state, limits, "b1").proposals


def test_forecast_source_summarises_the_local_day_and_is_attached_to_markets(tmp_path):
    from datetime import timedelta
    from conftest import NOW, raw_market
    from test_sources import FakeHttp
    from polymarket_agent.data_collector import collect
    from polymarket_agent.intel_pipeline import latest_weather
    from polymarket_agent.persistence import Database
    from polymarket_agent.sources.polymarket_gamma import parse_market
    from polymarket_agent.sources.weather import FORECAST_URL
    times = [f"2026-10-17T{h:02d}:00" for h in range(24)]
    hourly = {"time": times, "temperature_2m_gfs_seamless": [10 + h * 0.3 for h in range(24)],
              "temperature_2m_ecmwf_ifs025": [11 + h * 0.2 for h in range(24)]}
    m = parse_market(raw_market("w1", question="Will the highest temperature in Paris be 16°C on October 17?",
                                resolutionSource="https://www.weather.gov/wrh/timeseries?site=lfpb"))
    metar = [{"icaoId": "LFPB", "obsTime": int(NOW.timestamp()) - 600, "temp": 12.0, "lat": 48.97, "lon": 2.44,
              "name": "Paris Le Bourget"}]
    http = FakeHttp({"https://aviationweather.gov/api/data/metar": metar,
                     FORECAST_URL: [{"utc_offset_seconds": 7200, "hourly": hourly}]})
    db = Database(tmp_path / "m.sqlite")
    settings = {"sources": {"meteo_metar": {"enabled": True, "every_minutes": 15},
                            "meteo_prevision": {"enabled": True, "every_minutes": 60}}}
    result = collect(settings, http, db, [m], NOW)
    assert result.status["meteo_prevision"] == "ok (1 observations)"
    fc = next(o for o in result.observations if o.source == "meteo_prevision")
    day = fc.data["jours"]["2026-10-17"]
    assert day["max"] == [round(10 + 23 * 0.3, 6), round(11 + 23 * 0.2, 6)] or day["max"][0] > 16.8
    assert day["min"] == [10.0, 11.0] and fc.market_ids == ["w1"] and fc.data["utc_offset"] == 7200
    weather = latest_weather(result.observations, NOW + timedelta(minutes=1))
    assert "prevision" in weather["LFPB"] and weather["LFPB"]["station"] == "LFPB"
    assert weather["LFPB"]["max_jour_c"] is not None or "jour_local" in weather["LFPB"]
    # Sans coordonnées connues (station jamais relevée) : rien n'est demandé.
    db2 = Database(tmp_path / "m2.sqlite")
    r2 = collect({"sources": {"meteo_prevision": {"enabled": True, "every_minutes": 60}}}, FakeHttp({}), db2, [m], NOW)
    assert r2.status["meteo_prevision"] == "ok (0 observations)"
