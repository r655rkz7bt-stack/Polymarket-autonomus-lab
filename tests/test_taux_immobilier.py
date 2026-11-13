"""Freddie Mac : barrière hebdomadaire du taux immobilier à 30 ans (13/11/2026, piste n° 46, experiments/taux_immobilier.md)."""
from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import references as refs
from polymarket_agent import taux_immobilier as ti
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import TauxImmobilierBarriere

UTC = timezone.utc
NUIT = datetime(2026, 11, 13, 1, 0, tzinfo=UTC)
CSV = (Path(__file__).parent / "data" / "pmms_2026-11-12.csv").read_text()


def _market(mid, question, created="2026-10-27T21:06:22Z"):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2027, 1, 15, 4, 59, tzinfo=UTC),
                                   question=question, createdAt=created, events=[{"id": "197683", "title": "30-year Mortgage Rate hit __ in 2026?"}]))


def test_csv_question_and_releases():
    rows = ti.parse_csv(CSV)
    assert rows[-1] == ("2026-11-12", 7.11) and rows[0] == ("1990-01-05", 9.83)
    assert ti.question("Will the U.S. 30-year Fixed-Rate Mortgage hit 8.00% (HIGH) by December 31, 2026?") == (8.0, True, date(2026, 12, 31))
    assert ti.question("Will the U.S. 30-year Fixed-Rate Mortgage hit 6.25% (LOW) by December 31, 2026?")[:2] == (6.25, False)
    assert ti.question("Will the 10-year Treasury yield hit 5.06% in November?") is None
    # relevés du 19/11 au 31/12 (jeudis) : 7
    assert ti.releves_restants(date(2026, 11, 12), date(2026, 12, 31)) == 7


def test_chance_uses_market_creation_and_past_releases_only():
    pm = [list(x) for x in ti.parse_csv(CSV)]
    loin = ti.chance(pm, 8.0, True, date(2026, 12, 31), NUIT, debut=date(2026, 10, 27))
    pres = ti.chance(pm, 7.5, True, date(2026, 12, 31), NUIT, debut=date(2026, 10, 27))
    assert loin < 0.04 < pres < 0.35
    # 7,40 % le 08/10 : « 7,25 % HIGH » créé en août est déjà touché, mais pas un marché créé après le 15/10
    assert ti.chance(pm, 7.25, True, date(2026, 12, 31), NUIT, debut=date(2026, 8, 3)) == 1.0
    assert ti.chance(pm, 7.25, True, date(2026, 12, 31), NUIT, debut=date(2026, 10, 27)) < 1.0
    # 5,98 % en février : « 6,25 % LOW » créé le 03/08 n'est PAS touché (la fenêtre commence à la création)
    assert ti.chance(pm, 6.25, False, date(2026, 12, 31), NUIT, debut=date(2026, 8, 3)) < 0.02
    # le 10 ans a monté depuis la semaine du dernier relevé (4,93 → 5,10) : la hausse devient plus probable
    dix = [["2026-11-09", 4.88], ["2026-11-10", 4.98], ["2026-11-12", 5.10]]
    assert ti.avance_dix_ans(dix, date(2026, 11, 12), NUIT.date()) == 0.7 * (5.10 - (4.88 + 4.98) / 2)
    assert ti.chance(pm, 7.5, True, date(2026, 12, 31), NUIT, dix, date(2026, 10, 27)) > pres
    # un relevé publié aujourd'hui ou après n'entre pas
    futur = pm + [["2026-11-13", 9.0]]
    assert ti.chance(futur, 8.0, True, date(2026, 12, 31), NUIT, debut=date(2026, 10, 27)) == loin


def test_collect_attach_at_night_and_buy_no_on_far_threshold(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    result = collect({"sources": {"taux_immobilier": {"enabled": True, "every_minutes": 60}}}, Http({ti.URL: CSV}), db, [], NUIT)
    assert result.status["taux_immobilier"].startswith("ok (1")
    huit = _market("6324662", "Will the U.S. 30-year Fixed-Rate Mortgage hit 8.00% (HIGH) by December 31, 2026?")
    sans_date = _market("9", huit.question, created=None)
    assert refs.attach_all([huit, sans_date], db, NUIT)["taux_immobilier"] == 1
    assert "taux_immobilier" not in (sans_date.references or {})
    assert refs.attach_all([_market("8", huit.question)], db, datetime(2026, 11, 13, 15, 0, tzinfo=UTC))["taux_immobilier"] == 0
    p = huit.references["taux_immobilier"]["p"]
    assert p < 0.04
    s = _s(TauxImmobilierBarriere, min_net_edge=0.04, uncertainty=0.02, min_price=0.05, max_price=0.95, max_stale_hours=30,
           max_extra_ticks=1, max_proposals_per_cycle=2, max_per_event=2, mise_max_pari=0.05, kelly_fraction=1.0, max_candidates=40)
    # carnet réel du 13/11 : OUI 0,10 / 0,11 → NON vendu 0,90
    b = _books(("6324662Y", "0.10", "0.11"), ("6324662N", "0.89", "0.90"))
    for x in b.values():
        x.fetched_at = NUIT
    out = s.propose([huit], b, _state(tmp_path), LIMITS, "b1")
    assert [x.token_id for x in out.proposals] == ["6324662N"]
