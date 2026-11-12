"""Compteur de la rougeole du CDC (12/11/2026, experiments/rougeole_compteur.md, piste n° 8) : lecture de la page, journal, rythme,
mises à jour restantes (Thanksgiving), chance d'un seuil, rattachement et stratégie `rougeole_compteur`.
Données : extrait réel de la page du CDC lu le 12/11/2026 vers 01 h UTC (« As of November 5, 2026, 5,182 confirmed* measles cases »)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state
from polymarket_agent import references as refs
from polymarket_agent import rougeole as rg
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import RougeoleCompteur

UTC = timezone.utc
NOW = datetime(2026, 11, 12, 1, 0, tzinfo=UTC)
END = datetime(2026, 12, 1, 4, 59, tzinfo=UTC)          # 30/11 23 h 59, heure de l'Est
PAGE = (Path(__file__).parent / "data" / "cdc_rougeole_2026-11-12.html").read_text()


def _market(mid, question, end=END):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=end, question=question,
                                   events=[{"id": "e9", "title": "Measles cases in U.S. by November 30?"}]))


def test_parse_reads_the_real_counter_and_refuses_a_changed_page():
    assert rg.parse_compteur(PAGE) == {"date": "2026-11-05", "total": 5182}
    assert rg.parse_compteur("<html>maintenance</html>") is None


def test_market_target_reads_threshold_and_date_but_not_the_whole_year():
    assert rg.market_target("Will there be at least 6000 measles cases in the U.S. by November 30, 2026?") == (6000, date(2026, 11, 30))
    assert rg.market_target("Will there be at least 7,500 measles cases in the U.S. in 2026?") is None


def test_updates_left_and_thanksgiving():
    # « As of » le jeudi : 12, 19 et 26/11 (Thanksgiving) avant le 30/11
    assert rg.mises_a_jour(date(2026, 11, 5), date(2026, 11, 30)) == [date(2026, 11, 12), date(2026, 11, 19), date(2026, 11, 26)]
    assert date(2026, 11, 26) in rg._feries(2026)


def test_history_and_rhythm_from_the_three_known_updates():
    h = rg.keep_history([], [{"date": "2026-11-05", "total": 5182}], NOW)
    h = rg.keep_history(h, [{"date": "2026-11-05", "total": 5182}], NOW + timedelta(hours=2))   # relue : pas de nouvelle ligne
    assert len(h) == 1
    assert rg.rythme(h) == (rg.MU, rg.SD)                                   # trop court : valeurs de départ
    mu, sd = rg.rythme(rg.CONNU + [{"date": "2026-11-12", "total": 5450}])
    assert round(mu) == round((264 + 330 + 268) / 3) and sd >= 30


def test_threshold_chances_are_ordered_and_the_holiday_matters():
    p = {s: rg.p_seuil(5182, date(2026, 11, 5), s, date(2026, 11, 30)) for s in (5600, 5800, 6000, 6200)}
    assert p[5600] > 0.85 and p[5600] > p[5800] > p[6000] > p[6200]
    assert 0.3 < p[6000] < 0.55                                             # marché du 12/11 : 0,36 au milieu
    ferie_saute = rg.p_seuil(5182, date(2026, 11, 5), 6000, date(2026, 11, 30), q_ferie=0.3)
    assert ferie_saute < p[6000] - 0.08                                     # une mise à jour de Thanksgiving sautée retire une semaine
    assert rg.p_seuil(6100, date(2026, 11, 5), 6000, date(2026, 11, 30)) == 1.0
    assert rg.p_seuil(5182, date(2026, 11, 26), 6000, date(2026, 11, 30)) == 0.0   # plus aucune mise à jour


def test_collector_attach_and_strategy_trade_against_a_wrong_price(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    http = Http({rg.PAGE: PAGE})
    result = collect({"sources": {"rougeole": {"enabled": True, "every_minutes": 120}}}, http, db, [], NOW)
    assert result.status["rougeole"].startswith("ok (")
    assert refs._load(db, "rougeole:histo")[1][0]["total"] == 5182
    m6 = _market("m6", "Will there be at least 6000 measles cases in the U.S. by November 30, 2026?")
    m56 = _market("m56", "Will there be at least 5600 measles cases in the U.S. by November 30, 2026?")
    year = _market("y7", "Will there be at least 7000 measles cases in the U.S. in 2026?", end=datetime(2027, 1, 1, 4, 59, tzinfo=UTC))
    assert refs.attach_all([m6, m56, year], db, NOW)["rougeole"] == 2
    assert "rougeole" not in (year.references or {})
    assert m56.references["rougeole"]["p"] > 0.85
    s = _s(RougeoleCompteur, min_net_edge=0.05, uncertainty=0.10, min_price=0.10, max_price=0.90, max_stale_hours=6,
           max_extra_ticks=1, max_proposals_per_cycle=2, max_per_event=1, kelly_fraction=1.0)
    # un OUI « 6 000+ » vendu 0,70 (le modèle dit ≈ 0,3) : la stratégie achète le NON
    books = _books(("m6Y", "0.66", "0.70"), ("m6N", "0.30", "0.34"))
    for b in books.values():
        b.fetched_at = NOW
    out = s.propose([m6], books, _state(tmp_path), LIMITS, "b1")
    assert [p.token_id for p in out.proposals] == ["m6N"]
    # au carnet réel du 12/11 (0,15/0,57) : rien d'assez bon
    books = _books(("m6Y", "0.15", "0.57"), ("m6N", "0.43", "0.85"))
    for b in books.values():
        b.fetched_at = NOW
    assert s.propose([m6], books, _state(tmp_path), LIMITS, "b1").proposals == []
