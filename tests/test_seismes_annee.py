"""Séismes de l'année (12/11/2026, experiments/seismes_annee.md, piste n° 40) : compte des >= 7,0, magnitude maximale, Californie ;
rattachement et stratégie `seismes_annee`. Données : catalogue USGS réel du 01/01 au 12/11/2026 11 h UTC (séismes >= 6,8 : 13 de
magnitude >= 7,0, maximum 7,8) ; questions réelles des événements 134977, 870991 et 744604 ; carnets du 12/11."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import references as refs
from polymarket_agent import seismes_annee as sa
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.sources.usgs import URL, parse_usgs
from polymarket_agent.strategies_v3 import SeismesAnnee

UTC = timezone.utc
NOW = datetime(2026, 11, 12, 11, 0, tzinfo=UTC)
DATA = json.loads((Path(__file__).parent / "data" / "usgs_annee_2026-11-12.json").read_text())
ROWS = parse_usgs(DATA)
Q = {"11": "Will there be between 11 and 13 earthquakes of magnitude 7.0 or higher worldwide in 2026?",
     "17": "Will there be between 17 and 19 earthquakes of magnitude 7.0 or higher worldwide in 2026?",
     "20": "Will there be 20 or more earthquakes of magnitude 7.0 or higher worldwide in 2026?",
     "5": "Will there be fewer than 5 earthquakes of magnitude 7.0 or higher worldwide in 2026?",
     "79": "Will the highest-magnitude earthquake in 2026 be 7.9 or below?",
     "80": "Will the highest-magnitude earthquake in 2026 be 8.0 – 8.1?",
     "90": "Will the highest-magnitude earthquake in 2026 be 9.0 or above?",
     "ca": "Will California experience a 7.0 or above magnitude earthquake in 2026?"}


def _p(k):
    return sa.chance(Q[k], ROWS, NOW)[0]


def test_counts_and_chances_on_the_real_catalogue():
    assert sum(1 for r in ROWS if r["mag"] >= 7.0) == 13 and max(r["mag"] for r in ROWS) == 7.8
    assert 0.12 < _p("11") < 0.15 and 0.12 < _p("17") < 0.16 and _p("20") < 0.01   # Poisson(2,0) sur 49 jours
    assert _p("5") == 0.0                                                            # déjà 13 : « moins de 5 » impossible
    assert abs(_p("11") + sa.chance("Will there be between 14 and 16 earthquakes of magnitude 7.0 or higher worldwide in 2026?",
                                    ROWS, NOW)[0] + _p("17") + _p("20") - 1) < 0.01
    assert 0.85 < _p("79") < 0.92 and 0.03 < _p("80") < 0.08 and _p("90") < 0.02     # marché : 0,845 / 0,07 / 0,046
    assert 0.005 < _p("ca") < 0.03                                                   # marché : 0,093
    assert sa.chance("Will the Fed cut rates in December?", ROWS, NOW) is None


def test_an_earthquake_in_california_already_counts():
    ca = ROWS + [{"id": "nc1", "t": int(datetime(2026, 11, 1, tzinfo=UTC).timestamp()), "mag": 7.1, "lieu": "10 km N of Ridgecrest, CA"}]
    assert sa.chance(Q["ca"], ca, NOW)[0] == 0.97
    after = ROWS + [{"id": "us9", "t": int(datetime(2026, 11, 10, tzinfo=UTC).timestamp()), "mag": 8.0, "lieu": "Kuril Islands"}]
    assert sa.chance(Q["79"], after, NOW)[0] == 0.0 and sa.chance(Q["80"], after, NOW)[0] > 0.9


def test_collect_attach_and_buy_the_mispriced_side(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    result = collect({"sources": {"usgs_annee": {"enabled": True, "every_minutes": 30}}}, Http({URL: DATA}), db, [], NOW)
    assert result.status["usgs_annee"].startswith("ok (")
    mk = lambda mid, k: parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2027, 1, 8, tzinfo=UTC),
                                                question=Q[k], events=[{"id": "134977", "title": "How many 7.0 or above earthquakes in 2026?"}]))
    ms = [mk("1073793", "17"), mk("1073791", "11"), mk("3088911", "ca")]
    assert refs.attach_all(ms, db, NOW)["seismes_annee"] == 3
    s = _s(SeismesAnnee, min_net_edge=0.04, uncertainty=0.02, min_price=0.05, max_price=0.95, max_stale_hours=2, max_extra_ticks=1,
           max_proposals_per_cycle=3, max_per_event=2, kelly_fraction=1.0)
    books = _books(("1073793Y", "0.18", "0.32"), ("1073793N", "0.68", "0.82"),
                   ("1073791Y", "0.004", "0.088"), ("1073791N", "0.912", "0.996"),
                   ("3088911Y", "0.081", "0.105"), ("3088911N", "0.895", "0.919"))
    for b in books.values():
        b.fetched_at = NOW
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    toks = {p.token_id for p in out.proposals}
    assert "3088911N" in toks                       # NON Californie : 0,986 calculé pour 0,919 demandé
    assert "1073793Y" not in toks and "3088911Y" not in toks
    big = next(p for p in out.proposals if p.token_id == "3088911N")
    assert big.shares * big.max_price > 200                 # Kelly entier : ≈ 25 % du fantôme sur un pari (plafond général)
    capped = _s(SeismesAnnee, min_net_edge=0.04, uncertainty=0.02, min_price=0.05, max_price=0.95, max_stale_hours=2,
                max_extra_ticks=1, max_proposals_per_cycle=3, max_per_event=2, kelly_fraction=1.0, mise_max_pari=0.05)
    small = next(p for p in capped.propose(ms, books, _state(tmp_path), LIMITS, "b2").proposals if p.token_id == "3088911N")
    assert small.shares * small.max_price <= 50.01          # `mise_max_pari` : au plus 5 % de 1 000
