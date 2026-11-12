"""Préliminaire du Michigan contre les tranches du final (12/11/2026, experiments/michigan_preliminaire.md, piste n° 35) : lecture
de la page d'accueil des Surveys of Consumers, tranches des questions, chance, rattachement et stratégie `michigan_preliminaire`.
Données : page réelle lue le 12/11/2026 vers 06 h 30 UTC (« Preliminary Results for November 2026 … 51.0 ») et carnet réel du
« 55.0+ » (NON vendu 0,897)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import michigan as mi
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import MichiganPreliminaire

UTC = timezone.utc
NOW = datetime(2026, 11, 12, 6, 30, tzinfo=UTC)
PAGE = (Path(__file__).parent / "data" / "sca_umich_2026-11-12.html").read_text()


def _market(mid, question):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2026, 11, 20, 15, tzinfo=UTC),
                                   question=question, events=[{"id": "1242771", "title": "University of Michigan Consumer Sentiment - November 2026"}]))


def test_page_and_questions_are_read():
    assert mi.parse_page(PAGE) == {"etat": "preliminaire", "mois": "2026-11", "ics": 51.0}
    assert mi.parse_page(PAGE.replace("Preliminary Results", "Final Results"))["etat"] == "final"
    assert mi.parse_page("<html>maintenance</html>") is None
    assert mi.tranche("Will UMich Consumer Sentiment be between 49.0 and 51.9 in November?") == (49.0, 52.0, "November")
    assert mi.tranche("Will UMich Consumer Sentiment be at least 55.0 in November?") == (55.0, 1e9, "November")
    assert mi.tranche("Will UMich Consumer Sentiment be below 40.0 in November?") == (-1e9, 40.0, "November")
    assert mi.tranche("Will the Fed cut rates in November?") is None


def test_chances_around_the_preliminary_of_november():
    p = {k: mi.p_tranche(51.0, a, b) for k, (a, b) in {"46": (46.0, 49.0), "49": (49.0, 52.0), "52": (52.0, 55.0), "55": (55.0, 1e9)}.items()}
    assert 0.55 < p["49"] < 0.62 and 0.25 < p["52"] < 0.32 and 0.10 < p["46"] < 0.15
    assert p["55"] < 0.02                                   # le marché le cotait 0,10-0,13
    assert abs(sum(p.values()) - 1) < 0.01


def test_collect_attach_and_buy_the_no_of_an_excluded_bracket(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    result = collect({"sources": {"michigan": {"enabled": True, "every_minutes": 60}}}, Http({mi.PAGE: PAGE}), db, [], NOW)
    assert result.status["michigan"].startswith("ok (1")
    m55 = _market("6096682", "Will UMich Consumer Sentiment be at least 55.0 in November?")
    m49 = _market("6096680", "Will UMich Consumer Sentiment be between 49.0 and 51.9 in November?")
    other = _market("9", "Will UMich Consumer Sentiment be at least 55.0 in December?")
    assert refs.attach_all([m55, m49, other], db, NOW)["michigan"] == 2
    assert "michigan" not in (other.references or {})
    s = _s(MichiganPreliminaire, min_net_edge=0.05, uncertainty=0.02, min_price=0.05, max_price=0.97, max_stale_hours=3,
           max_extra_ticks=1, max_proposals_per_cycle=3, max_per_event=3, kelly_fraction=1.0)
    books = _books(("6096682Y", "0.103", "0.128"), ("6096682N", "0.872", "0.897"),
                   ("6096680Y", "0.499", "0.500"), ("6096680N", "0.500", "0.501"))
    for b in books.values():
        b.fetched_at = NOW
    out = s.propose([m55, m49], books, _state(tmp_path), LIMITS, "b1")
    assert [p.token_id for p in out.proposals] == ["6096682N"]   # « 49-51,9 » à 0,50 pour 0,58 : sous le seuil après frais et marge
    # le final publié : plus de rattachement
    db2 = Database(tmp_path / "db2.sqlite")
    collect({"sources": {"michigan": {"enabled": True, "every_minutes": 60}}},
            Http({mi.PAGE: PAGE.replace("Preliminary Results", "Final Results")}), db2, [], NOW)
    fresh = _market("6096682", "Will UMich Consumer Sentiment be at least 55.0 in November?")
    assert refs.attach_all([fresh], db2, NOW)["michigan"] == 0

