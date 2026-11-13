"""Pluie du jour (13/11/2026, piste n° 55, experiments/pluie_du_jour.md) : vrais METAR de aviationweather.gov du 13/11/2026 vers
16 h 30 UTC (pluie à Los Angeles depuis le SPECI de 10 h 43 UTC, trace seulement à 10 h 09), lecture des marchés, journée climatique
en heure locale standard, collecteur, rattachement et stratégie `pluie_vue`."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from conftest import raw_market
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import pluie
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import PluieVue

UTC = timezone.utc
NOW = datetime(2026, 11, 13, 16, 30, tzinfo=UTC)
RAW = json.loads((Path(__file__).parent / "data" / "pluie_2026-11-13.json").read_text())


class _Http:
    def get_json(self, url, params=None, headers=None):
        assert url == pluie.URL and "KLAX" in params["ids"]
        return RAW


def _market(mid, ville, code, jour="November 13"):
    raw = raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2026, 11, 14, 19, 0, tzinfo=UTC),
                     question=f"Will it rain in {ville} on {jour}?",
                     resolutionSource=f"https://forecast.weather.gov/product.php?site=NWS&product=CLI&issuedby={code}",
                     events=[{"id": "1371256", "title": f"Where will it rain on {jour}?"}])
    return parse_market(raw)


def test_station_day_and_question():
    assert pluie.station_of("https://forecast.weather.gov/product.php?site=NWS&product=CLI&issuedby=LAX") == "LAX"
    assert pluie.station_of("https://www.weather.gov/wrh/timeseries?site=KLAX") is None
    assert pluie.jour_du_marche("Will it rain in Los Angeles, CA on November 13?", datetime(2026, 11, 14, 19, tzinfo=UTC)) == \
        datetime(2026, 11, 13, tzinfo=UTC)
    assert pluie.jour_du_marche("Will it rain on November 13?", datetime(2026, 11, 14, tzinfo=UTC)) is None
    # heure locale STANDARD : Los Angeles 08 h → 08 h UTC, même en été (règle du rapport CLI)
    assert pluie.journee("LAX", datetime(2026, 8, 20, tzinfo=UTC)) == (datetime(2026, 8, 20, 8, tzinfo=UTC), datetime(2026, 8, 21, 8, tzinfo=UTC))
    assert pluie.journee("NYC", datetime(2026, 11, 13, tzinfo=UTC))[0] == datetime(2026, 11, 13, 5, tzinfo=UTC)


def test_real_metar_first_measurable_rain_and_trace():
    rows = {r["station"]: r["obs"] for r in pluie.fetch_pluie(_Http(), NOW)}
    deb, fin = pluie.journee("LAX", datetime(2026, 11, 13, tzinfo=UTC))
    # 10 h 09 UTC : P0000 (trace, 0,005) ne compte pas ; 10 h 43 : 0,01 pouce → pluie mesurable
    assert pluie.premiere_pluie(rows["LAX"], deb, fin, NOW) == datetime(2026, 11, 13, 10, 43, tzinfo=UTC)
    # pas encore REÇU à 10 h 45 (réception 10 h 48) : rien
    assert pluie.premiere_pluie(rows["LAX"], deb, fin, datetime(2026, 11, 13, 10, 45, tzinfo=UTC)) is None
    deb, fin = pluie.journee("IAH", datetime(2026, 11, 13, tzinfo=UTC))
    assert pluie.premiere_pluie(rows.get("IAH", []), deb, fin, NOW) is None   # aucun groupe P : station sèche


def test_collect_attach_and_buy_only_the_cheap_yes(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    result = collect({"sources": {"pluie": {"enabled": True, "every_minutes": 5}}}, _Http(), db, [], NOW)
    assert result.status["pluie"].startswith("ok (")
    la, hou = _market("6800001", "Los Angeles, CA", "LAX"), _market("6800002", "Houston, TX", "IAH")
    demain = _market("6800003", "Los Angeles, CA", "LAX", jour="November 14")
    assert refs.attach_all([la, hou, demain], db, NOW)["pluie"] == 1
    assert la.references["pluie"]["cotes"] == [0] and "pluie" not in (hou.references or {}) and "pluie" not in (demain.references or {})
    s = _s(PluieVue, min_net_edge=0.02, uncertainty=0.0, min_price=0.10, max_price=0.95, max_stale_hours=0.5, max_extra_ticks=1,
           max_proposals_per_cycle=5, max_per_event=15, mise_max_pari=0.05, kelly_fraction=1.0, max_candidates=40)
    # carnet réel du 13/11 à 16 h 30 : OUI 0,952 / 0,999 → rien ; un vendeur oublié à 0,80 → achat du OUI, jamais du NON
    b = _books(("6800001Y", "0.952", "0.999"), ("6800001N", "0.001", "0.048"))
    for x in b.values():
        x.fetched_at = NOW
    assert s.propose([la], b, _state(tmp_path), LIMITS, "b1").proposals == []
    b = _books(("6800001Y", "0.75", "0.80"), ("6800001N", "0.20", "0.25"))
    for x in b.values():
        x.fetched_at = NOW
    out = s.propose([la], b, _state(tmp_path), LIMITS, "b2")
    assert [x.token_id for x in out.proposals] == ["6800001Y"]
    # relevé trop vieux (plus de 2 h) : plus de rattachement
    la2 = _market("6800001", "Los Angeles, CA", "LAX")
    assert refs.attach_all([la2], db, NOW + timedelta(hours=3))["pluie"] == 0
