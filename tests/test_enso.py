"""El Niño : chances chiffrées du CPC contre les marchés « peak RONI » (12/11/2026, experiments/el_nino.md, piste n° 39) : lecture
de la discussion ENSO, bornes par marché, fraîcheur de la discussion, rattachement et stratégie `el_nino_cpc`.
Données : discussion réelle du 08/10/2026 (lue le 12/11/2026) et RONI.ascii.txt du 12/11/2026 (ASO 2026 = 1,97) ; questions réelles
des événements 867162 et 1023298."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import enso
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import ElNinoCpc

UTC = timezone.utc
DATA = Path(__file__).parent / "data"
PAGE = (DATA / "cpc_ensodisc_2026-10-08.html").read_text(encoding="utf-8", errors="replace")
RONI = (DATA / "cpc_roni_2026-11-12.txt").read_text()
Q = {"bas": "Will the peak RONI for the 2026–27 El Niño be below 1.5?",
     "225": "Will the peak RONI for the 2026–27 El Niño be at least 2.25 but below 2.5?",
     "25": "Will the peak RONI for the 2026–27 El Niño be 2.5 or above?",
     "record": "Will the 2026–27 El Niño be the strongest on record?"}
DESC_RECORD = "This market will resolve to \"Yes\" if the peak RONI for the 2026–27 El Niño is above 2.40°C, the highest RONI value on record."


def _market(mid, question, description=""):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2027, 4, 1, tzinfo=UTC),
                                   question=question, description=description, events=[{"id": "867162", "title": "peak RONI"}]))


def test_discussion_and_roni_are_read():
    d = enso.parse_discussion(PAGE)
    assert d == {"emis": "2026-10-08", "seuils": {"2.5": {"Sep-Nov": 0.54, "Oct-Dec": 0.83, "Nov-Jan": 0.70}}}
    assert enso.parse_discussion("<html>maintenance</html>") is None
    assert enso.parse_roni(RONI)[-1] == ("ASO", 2026, 1.97)
    # autre tournure (13/08/2026) : « During the October-December 2026 season, there is a 69% chance of a historic event … (+2.5°C … »
    aout = (DATA / "cpc_ensodisc_2026-08-13.html").read_text(encoding="utf-8", errors="replace")
    assert enso.parse_discussion(aout) == {"emis": "2026-08-13", "seuils": {"2.5": {"Oct-Dec": 0.69}}}
    # tournure libre, fourchette « 75-85% » : la borne basse ; une chance sur le Niño-3.4 classique (2023) ne compte pas
    libre = "<p>8 October 2026</p><p>Text. There is a 75-85% chance of a historic event (+2.5°C or more for a 3-month RONI value) for the November-January season. Next.</p>"
    assert enso.parse_discussion(libre)["seuils"] == {"2.5": {"Nov-Jan": 0.75}}
    assert enso.parse_discussion(libre.replace("3-month RONI value", "Niño-3.4 seasonal average"))["seuils"] == {}


def test_bounds_follow_the_inequality_only():
    s = {"2.5": {"Sep-Nov": 0.54, "Oct-Dec": 0.83, "Nov-Jan": 0.70}}
    assert enso.intervalle(Q["25"]) == (2.5, 1e9) and enso.borne((2.5, 1e9), s) == (0, 0.83)
    assert enso.intervalle(Q["record"], DESC_RECORD) == (2.40, 1e9) and enso.borne((2.40, 1e9), s) == (0, 0.83)
    assert enso.borne(enso.intervalle(Q["225"]), s) == (1, 0.83)      # tranche sous 2,5 : son NON vaut au moins 0,83
    assert enso.borne(enso.intervalle(Q["bas"]), s) == (1, 0.83)
    assert enso.borne((2.25, 2.75), s) is None                          # chevauche le seuil : rien de prouvé
    assert enso.borne((3.0, 1e9), s) is None                            # seuil plus haut que ceux du CPC : rien de prouvé
    assert enso.intervalle("Will the Fed cut rates in December?") is None


def test_stale_discussion_buys_nothing_and_fresh_one_buys_the_bounded_side(tmp_path):
    http = Http({enso.PAGE: PAGE, enso.RONI: RONI})
    # 12/11 au matin : la discussion du 08/10 a 35 jours, elle est ignorée (cas réel : le marché était à 0,61-0,64)
    late = datetime(2026, 11, 12, 11, 0, tzinfo=UTC)
    db = Database(tmp_path / "db.sqlite")
    assert collect({"sources": {"enso": {"enabled": True, "every_minutes": 180}}}, http, db, [], late).status["enso"].startswith("ok (1")
    assert refs._load(db, "enso:histo")[1][0]["emis"] == "2026-10-08"
    ms = [_market("3680999", Q["25"]), _market("3680998", Q["225"]), _market("4557459", Q["record"], DESC_RECORD)]
    assert refs.attach_all(ms, db, late)["enso"] == 0
    # le lendemain de la discussion : rattachée, et la stratégie n'achète que le côté borné
    fresh = datetime(2026, 10, 9, 12, 0, tzinfo=UTC)
    db2 = Database(tmp_path / "db2.sqlite")
    collect({"sources": {"enso": {"enabled": True, "every_minutes": 180}}}, http, db2, [], fresh)
    ms = [_market("3680999", Q["25"]), _market("3680998", Q["225"]), _market("4557459", Q["record"], DESC_RECORD)]
    assert refs.attach_all(ms, db2, fresh)["enso"] == 3
    assert ms[0].references["enso"]["cotes"] == [0] and ms[1].references["enso"]["cotes"] == [1]
    s = _s(ElNinoCpc, min_net_edge=0.05, uncertainty=0.05, min_price=0.05, max_price=0.95, max_stale_hours=8,
           max_extra_ticks=1, max_proposals_per_cycle=2, max_per_event=2, kelly_fraction=1.0)
    books = _books(("3680999Y", "0.58", "0.64"), ("3680999N", "0.36", "0.42"),
                   ("3680998Y", "0.29", "0.35"), ("3680998N", "0.65", "0.71"),
                   ("4557459Y", "0.61", "0.65"), ("4557459N", "0.35", "0.39"))
    for b in books.values():
        b.fetched_at = fresh
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    toks = sorted(p.token_id for p in out.proposals)
    assert toks and set(toks) <= {"3680999Y", "4557459Y", "3680998N"}   # jamais le NON des tranches hautes
    assert "3680999N" not in toks and "4557459N" not in toks
