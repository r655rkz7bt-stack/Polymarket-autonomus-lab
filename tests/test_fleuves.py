"""Niveaux du Rhin et du Danube (11/11/2026, experiments/niveaux_eau.md, piste n° 25) : prévisions officielles (PegelOnline pour Kaub,
OVF pour Budapest), lecture des tranches de dates des marchés « return to normal levels », chance du premier passage, collecteur et
stratégie `fleuves_prevision`. Données : relevés réels du 11/11/2026 vers 16 h UTC."""

from __future__ import annotations

from datetime import datetime, timezone

from conftest import raw_market
from test_sources import FakeHttp
from test_strategies_v3 import LIMITS, _books, _s, _state
from polymarket_agent import fleuves as fl
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import FleuvesPrevision

UTC = timezone.utc
NOW = datetime(2026, 11, 11, 16, 0, tzinfo=UTC)

# Prévision WSV/BfG de Kaub émise le 11/11 à 07 h (heure de Berlin), un point sur deux du relevé réel.
KAUB_WV = [{"initialized": "2026-11-11T07:00:00+01:00", "timestamp": t, "value": v, "type": "forecast"} for t, v in (
    ("2026-11-11T07:00:00+01:00", 16.0), ("2026-11-11T15:00:00+01:00", 16.0), ("2026-11-11T23:00:00+01:00", 21.0),
    ("2026-11-12T07:00:00+01:00", 28.0), ("2026-11-12T15:00:00+01:00", 36.0), ("2026-11-12T23:00:00+01:00", 45.0),
    ("2026-11-13T07:00:00+01:00", 56.0), ("2026-11-13T15:00:00+01:00", 64.0), ("2026-11-13T23:00:00+01:00", 68.0),
    ("2026-11-14T07:00:00+01:00", 69.0), ("2026-11-14T23:00:00+01:00", 69.0), ("2026-11-15T07:00:00+01:00", 69.0))]
KAUB_W = [{"timestamp": "2026-11-11T16:30:00+01:00", "value": 16.0}, {"timestamp": "2026-11-11T16:45:00+01:00", "value": 17.0}]
CELL = '<td><font size="1"><b>{}</b></font></td>'
PM = '<td><table><tr><td><b>{}</b></td><td><font color="#808080"><b> &plusmn;  {}</b></font></td></tr></table></td>'
# Tableau de l'OVF (hydroinfo.hu, tables/ENG/dunelotH.html) réduit à l'en-tête, à Budapest et à une autre station.
OVF = ("<html><table><tr><td>River<br><b>Station</b><br><i>Issued at</i></td>" + CELL.format("Today <br>morning")
       + "".join(CELL.format(f"{d}.11. 07h") for d in range(12, 18)) + "</tr>"
       + "<tr><td>Danube<br><b>Vác</b><br><i>(11.11.2026 08:28)</i></td>" + CELL.format(-60)
       + "".join(PM.format(v, s) for v, s in ((-57, 5), (-48, 11), (-17, 16), (47, 22), (70, 27), (55, 32))) + "</tr>"
       + "<tr><td>Danube<br><b>Budapest</b><br><i>(11.11.2026 08:28)</i></td>" + CELL.format(36)
       + "".join(PM.format(v, s) for v, s in ((36, 2), (42, 7), (64, 13), (124, 17), (167, 22), (163, 26))) + "</tr></table></html>")
RHINE = ("This market will resolve according to the date (Berlin time) when the water level at the Kaub gauge (station 25700100) on the "
         "Rhine River first reaches or exceeds 77 centimeters, as reported by the German Federal Waterways and Shipping Administration.")
DANUBE = ("This market resolves based on when the water level at the Budapest gauge (station HU442027) first reaches or exceeds 93 "
          "centimeters ... A single reading at or above 93 centimeters is sufficient ... All dates and times in this market refer to "
          "Eastern Time (ET).")


class Http(FakeHttp):
    def get_text(self, url, params=None, headers=None):
        return self.get_json(url, params, headers)


def _http():
    return Http({fl.KAUB_WV: KAUB_WV, fl.KAUB_W: KAUB_W, fl.OVF: OVF})


def _market(mid, question, description):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2027, 1, 1, tzinfo=UTC),
                                   question=question, description=description,
                                   events=[{"id": f"e{mid[0]}", "title": "When will the river return to normal levels?"}]))


def test_parse_pegelonline_and_ovf_keep_issue_time_last_reading_and_forecast_points():
    rows = fl.fetch_fleuves(_http(), NOW)
    kaub, bud = rows
    assert kaub["station"] == "KAUB" and kaub["obs"] == 17.0 and kaub["emis"] == "2026-11-11T06:00:00+00:00"
    assert kaub["points"][-1] == ["2026-11-15T06:00:00+00:00", 69.0, None]
    assert bud["station"] == "BUDAPEST" and bud["obs"] == 36.0 and bud["emis"] == "2026-11-11T07:28:00+00:00"   # 08 h 28 à Budapest
    assert bud["points"][3] == ["2026-11-15T06:00:00+00:00", 124.0, 17.0] and len(bud["points"]) == 6           # pas la ligne de Vác


def test_a_station_down_does_not_hide_the_other():
    rows = fl.fetch_fleuves(Http({fl.OVF: OVF}, down=(fl.KAUB_W,)), NOW)
    assert [r["station"] for r in rows] == ["BUDAPEST"]
    assert fl.parse_ovf("<html>maintenance</html>") is None


def test_market_window_reads_river_threshold_bucket_and_timezone():
    st, start, end, seuil = fl.market_window("Will the Rhine River return to normal levels before November 15, 2026?", RHINE)
    assert (st, seuil, end) == ("KAUB", 77.0, datetime(2026, 11, 14, 23, tzinfo=UTC))           # minuit à Berlin
    st, start, end, seuil = fl.market_window(
        "Will the Danube River return to normal levels between November 15 and November 30, 2026?", DANUBE)
    assert (st, seuil, start, end) == ("BUDAPEST", 93.0, datetime(2026, 11, 15, 5, tzinfo=UTC), datetime(2026, 12, 1, 5, tzinfo=UTC))
    assert fl.market_window("Will the Danube River return to normal levels by January 1, 2027?", DANUBE) is None
    assert fl.market_window("Will the Rhine River return to normal levels before November 15, 2026?", "no gauge named") is None


def test_first_crossing_follows_the_official_forecast():
    kaub, bud = fl.fetch_fleuves(_http(), NOW)
    p_kaub = fl.p_first_crossing(kaub, NOW, datetime(2000, 1, 1, tzinfo=UTC), datetime(2026, 11, 14, 23, tzinfo=UTC), 77.0)
    p_bud = fl.p_first_crossing(bud, NOW, datetime(2000, 1, 1, tzinfo=UTC), datetime(2026, 11, 15, 5, tzinfo=UTC), 93.0)
    assert 0.2 < p_kaub < 0.55          # pic prévu 69 cm pour un seuil de 77
    assert 0.6 < p_bud < 0.9            # 124 ± 17 le 15/11 à 07 h : passage prévu le 14 au soir
    # tranche qui commence plus tard : passage avant elle exclu ; tranche au-delà de la prévision : pas d'avis
    later = fl.p_first_crossing(bud, NOW, datetime(2026, 11, 15, 5, tzinfo=UTC), datetime(2026, 11, 16, 5, tzinfo=UTC), 93.0)
    assert 0.05 < later < 0.4 and later + p_bud <= 1.0
    assert fl.p_first_crossing(bud, NOW, datetime(2026, 11, 15, 5, tzinfo=UTC), datetime(2026, 12, 1, 5, tzinfo=UTC), 93.0) is None


def test_collector_attach_and_strategy_buy_the_side_the_forecast_favours(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    cfg = {"sources": {"fleuves": {"enabled": True, "every_minutes": 60}}}
    result = collect(cfg, _http(), db, [], NOW)
    assert result.status["fleuves"].startswith("ok (2")
    rhin = _market("r15", "Will the Rhine River return to normal levels before November 15, 2026?", RHINE)
    danube = _market("d15", "Will the Danube River return to normal levels before November 15, 2026?", DANUBE)
    plus_tard = _market("d30", "Will the Danube River return to normal levels between November 15 and November 30, 2026?", DANUBE)
    assert refs.attach_all([rhin, danube, plus_tard], db, NOW)["fleuves"] == 2
    assert "fleuves" not in (plus_tard.references or {})
    s = _s(FleuvesPrevision, min_net_edge=0.05, uncertainty=0.10, min_price=0.10, max_price=0.90, max_stale_hours=2,
           max_extra_ticks=1, max_proposals_per_cycle=4, max_per_event=1, kelly_fraction=0.5)
    books = {}
    books.update(_books(("r15Y", "0.63", "0.66"), ("r15N", "0.34", "0.37")))     # prix du 11/11 : le NON du Rhin
    books.update(_books(("d15Y", "0.23", "0.29"), ("d15N", "0.71", "0.77")))     # et le OUI du Danube
    for b in books.values():
        b.fetched_at = NOW
    out = s.propose([rhin, danube], books, _state(tmp_path), LIMITS, "b1")
    assert sorted(p.token_id for p in out.proposals) == ["d15Y", "r15N"]


def test_old_forecast_or_threshold_already_reached_gives_no_reference(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    collect({"sources": {"fleuves": {"enabled": True, "every_minutes": 60}}}, _http(), db, [], NOW)
    danube = _market("d15", "Will the Danube River return to normal levels before November 15, 2026?", DANUBE)
    assert refs.attach_all([danube], db, datetime(2026, 11, 13, 0, tzinfo=UTC))["fleuves"] == 0    # prévision vieille de 40 h


def test_history_keeps_every_issued_forecast_while_the_reference_is_replaced(tmp_path):
    """11/11/2026 : `ref:fleuves` est remplacé à chaque relevé ; sans `fleuves:histo`, le test « prévision contre niveau réel »
    prévu dans 1-2 mois aurait été impossible (même défaut que `lid:histo` le 11/11 à 1 h)."""
    db = Database(tmp_path / "db.sqlite")
    cfg = {"sources": {"fleuves": {"enabled": True, "every_minutes": 60}}}
    collect(cfg, _http(), db, [], NOW)
    later = [dict(e, initialized="2026-11-12T07:00:00+01:00") for e in KAUB_WV]          # prévision du lendemain
    w2 = KAUB_W + [{"timestamp": "2026-11-12T08:00:00+01:00", "value": 30.0}]
    collect(cfg, Http({fl.KAUB_WV: later, fl.KAUB_W: w2, fl.OVF: OVF}), db, [], datetime(2026, 11, 12, 7, 5, tzinfo=UTC))
    _, ref = refs._load(db, "ref:fleuves")
    _, histo = refs._load(db, "fleuves:histo")
    assert [r["emis"] for r in ref if r["station"] == "KAUB"] == ["2026-11-12T06:00:00+00:00"]
    kaub = [r for r in histo if r["id"].startswith("prev:KAUB")]
    assert [r["emis"] for r in kaub] == ["2026-11-11T06:00:00+00:00", "2026-11-12T06:00:00+00:00"]
    assert kaub[0]["vu"] == "2026-11-11T16:00:00+00:00" and kaub[0]["points"][-1][1] == 69.0
    assert len([r for r in histo if r["id"].startswith("prev:BUDAPEST")]) == 1       # même prévision OVF relue : une seule ligne
    assert {r["cm"] for r in histo if r["id"].startswith("obs:KAUB")} == {17.0, 30.0}
