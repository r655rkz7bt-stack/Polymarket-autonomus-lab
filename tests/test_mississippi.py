"""Plus bas niveau du Mississippi (13/11/2026, piste n° 52, experiments/mississippi.md) : relevés USGS et prévisions NWPS réels du
13/11/2026 vers 11 h UTC, lecture des tranches, chance par simulation, collecteur, journal et stratégie `mississippi_plus_bas`."""
from __future__ import annotations

import json
import math
from datetime import date, datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import mississippi as mi
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import MississippiPlusBas

UTC = timezone.utc
NOW = datetime(2026, 11, 13, 11, 15, tzinfo=UTC)
FIN = datetime(2026, 12, 2, 4, 59, tzinfo=UTC)
RAW = json.loads((Path(__file__).parent / "data" / "mississippi_2026-11-13.json").read_text())
BR_DESC = ("This market will resolve according to the lowest daily mean gage height ... The resolution source is the USGS Daily Values "
           "service for site 07374000 ... https://waterservices.usgs.gov/nwis/dv/?sites=07374000&parameterCd=00065&statCd=00003"
           "&startDT=2026-09-21&endDT=2026-11-30&format=rdb")
STL_DESC = "... lowest gage height ... St. Louis, MO streamgage (USGS site 07010000) between market creation and November 30, 2026 ..."


class _Http(Http):
    def get_json(self, url, params=None, headers=None):
        if url == mi.USGS:
            return RAW["stl_usgs"] if params["sites"] == "07010000" else RAW["btr_usgs"]
        return RAW["stl_nwps"] if "EADM7" in url else RAW["btr_nwps"]


def _rows():
    return mi.fetch_mississippi(_Http({}), NOW)


def _market(mid, question, description, created="2026-09-22T19:15:40Z"):
    raw = raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=FIN, question=question, description=description,
                     events=[{"id": "e" + mid[:3], "title": "Lowest Mississippi level by November 30?"}])
    raw["createdAt"] = created
    return parse_market(raw)


def test_question_brackets_and_window():
    assert mi.question("Will the lowest St. Louis river level be 1.00 to 2.99 ft by November 30?", FIN) == \
        ("st. louis", 1.0, 3.0, date(2026, 11, 30))
    assert mi.question("Will the lowest St. Louis river level be below -3.00 ft by November 30?", FIN)[1:3] == (-math.inf, -3.0)
    assert mi.question("Will the lowest Baton Rouge river level be 6.00 ft or more by November 30?", FIN)[:3] == \
        ("baton rouge", 6.0, math.inf)
    q = mi.question("Will the lowest St. Louis river level be -3.00 to -1.01 ft by November 30?", FIN)
    assert q[1] == -3.0 and abs(q[2] - (-1.0)) < 1e-9          # -1.00 tombe dans la tranche du dessus (bornes au centième)
    assert mi.question("Will the Rhine River return to normal levels before November 15?", FIN) is None
    assert mi.debut_fenetre(BR_DESC, None) == date(2026, 9, 21)
    assert mi.debut_fenetre(STL_DESC, datetime(2026, 9, 22, 19, 15, tzinfo=UTC)) == date(2026, 9, 22)


def test_real_13_11_readings_and_forecasts_give_market_like_chances():
    """Cas réel du 13/11 : Saint-Louis plus bas 2,77 (01/11), 11,38 le 12/11, prévision NWS 2,6 pi le 27/11 (fin de l'horizon) ;
    Baton Rouge plus bas 6,38 (09/11), prévision ≥ 7,1 jusqu'au 30/11. Marché : Saint-Louis « 1-2,99 » 0,812, « -1 à 0,99 » 0,11 ;
    Baton Rouge « 6 ft ou plus » 0,834, « 5-5,99 » 0,165."""
    stl, br = sorted(_rows(), key=lambda r: r["jauge"], reverse=True)
    assert stl["jauge"] == "st. louis" and stl["obs"][-1] == ["2026-11-12", 11.38] and stl["prevision"][-1][1] == 2.6
    assert br["jauge"] == "baton rouge" and br["emis"] == "2026-11-12T16:09:00+00:00"
    deb_s, deb_b, fin = date(2026, 9, 22), date(2026, 9, 21), date(2026, 11, 30)
    p = {k: mi.chance(stl, NOW, deb_s, fin, lo, hi) for k, lo, hi in (("bas", -math.inf, -3), ("m3", -3, -0.99), ("m1", -1, 1.0),
                                                                       ("1-3", 1, 3.0), ("3+", 3, math.inf))}
    assert p["3+"] == 0.0                       # 2,77 déjà publié le 01/11 : « 3 ft ou plus » est mort
    assert 0.72 < p["1-3"] < 0.9 and 0.1 < p["m1"] < 0.27 and abs(sum(p.values()) - 1) < 1e-9
    p6 = mi.chance(br, NOW, deb_b, fin, 6, math.inf)
    assert 0.85 < p6 < 0.95 and mi.chance(br, NOW, deb_b, fin, -math.inf, 3) == 0.0
    # fenêtre finie : le plus bas publié décide seul
    assert mi.chance(stl, NOW, deb_s, date(2026, 11, 12), 1, 3.0) == 1.0


def test_collect_journal_attach_and_no_buy_inside_the_margin(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    result = collect({"sources": {"mississippi": {"enabled": True, "every_minutes": 60}}}, _Http({}), db, [], NOW)
    assert result.status["mississippi"].startswith("ok (2")
    histo = refs._load(db, "mississippi:histo")[1]
    assert {h["jauge"] for h in histo} == {"st. louis", "baton rouge"}
    assert mi.journal(histo, _rows()) == histo      # même prévision relue : rien de nouveau
    six = _market("4852059", "Will the lowest Baton Rouge river level be 6.00 ft or more by November 30?", BR_DESC)
    rhin = _market("6433563", "Will the Rhine River return to normal levels before November 15, 2026?", "Kaub gauge")
    assert refs.attach_all([six, rhin], db, NOW)["mississippi"] == 1
    assert "mississippi" not in (rhin.references or {})
    s = _s(MississippiPlusBas, min_net_edge=0.04, uncertainty=0.06, min_price=0.08, max_price=0.95, max_stale_hours=3,
           max_extra_ticks=1, max_proposals_per_cycle=2, max_per_event=1, mise_max_pari=0.05, kelly_fraction=1.0, max_candidates=20)
    # carnet réel du 13/11 : OUI 0,831 / 0,837 → chance ≈ 0,90 − 0,06 d'incertitude : pas assez d'écart ; un vendeur à 0,78 → achat
    b = _books(("4852059Y", "0.831", "0.837"), ("4852059N", "0.163", "0.169"))
    for x in b.values():
        x.fetched_at = NOW
    assert s.propose([six], b, _state(tmp_path), LIMITS, "b1").proposals == []
    b = _books(("4852059Y", "0.77", "0.78"), ("4852059N", "0.22", "0.23"))
    for x in b.values():
        x.fetched_at = NOW
    out = s.propose([six], b, _state(tmp_path), LIMITS, "b2")
    assert [x.token_id for x in out.proposals] == ["4852059Y"]
