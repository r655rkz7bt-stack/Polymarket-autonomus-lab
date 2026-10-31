"""Sièges de la Chambre (31/10/2026, experiments/coherence_sieges.md) : lecture des districts, loi du nombre de sièges, rattachement aux tranches
des échelles d'État, collecteur et stratégie `sieges_coherence`."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from conftest import raw_market
from test_sources import FakeHttp
from test_strategies_v3 import LIMITS, _books, _s, _state
from polymarket_agent import references as refs
from polymarket_agent import sieges
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import SiegesCoherence

UTC = timezone.utc
NOW = datetime(2026, 10, 14, 12, 0, tzinfo=UTC)   # NOW des carnets de test


def _event(code: str, n: int, p: float) -> dict:
    return {"title": f"{code}-{n:02d} House Election Winner", "markets": [
        {"question": f"Will the Republican Party win the {code}-{n:02d} House seat?", "outcomePrices": json.dumps([str(1 - p), str(p)])},
        {"question": f"Will the Democratic Party win the {code}-{n:02d} House seat?", "outcomePrices": json.dumps([str(p), str(1 - p)]), "liquidityNum": 5000},
        {"question": f"Will A win the {code}-{n:02d} House seat?"}]}


def test_parse_districts_keeps_the_democratic_price_and_skips_other_events():
    rows = sieges.parse_districts([_event("OH", 9, 0.28), {"title": "Autre chose", "markets": []}, _event("NC", 1, 0.855)])
    assert [(r["district"], r["etat"], r["p"]) for r in rows] == [("OH-09", "OH", 0.28), ("NC-01", "NC", 0.855)]
    assert sieges.parse_districts(None) == [] and sieges.parse_districts([{"title": "OH-01 House Election Winner", "markets": [{"question": "Democratic", "outcomePrices": "x"}]}]) == []


def test_seat_distribution_is_a_law_whose_mean_is_the_sum_of_prices_without_shock():
    ps = [0.9, 0.5, 0.2, 0.05]
    for shock in (0.0, 0.7):
        dist = sieges.seat_distribution(ps, shock)
        assert len(dist) == 5 and sum(dist) == pytest.approx(1.0)
    dist = sieges.seat_distribution(ps, 0.0)
    assert sum(k * v for k, v in enumerate(dist)) == pytest.approx(sum(ps))
    assert dist[4] == pytest.approx(0.9 * 0.5 * 0.2 * 0.05)
    # un choc commun épaissit les queues (tout le monde gagne ou tout le monde perd ensemble)
    assert sieges.seat_distribution(ps, 1.0)[4] > dist[4] and sieges.seat_distribution(ps, 1.0)[0] > dist[0]
    assert sieges.seat_distribution([], 0.7) == pytest.approx([1.0])


def test_tranche_reads_the_three_bracket_forms():
    assert sieges.tranche("Will Democrats win fewer than 3 House seats in North Carolina in the 2026 midterm election?") == ("lt", 3)
    assert sieges.tranche("Will Democrats win exactly 5 House seats in North Carolina in the 2026 midterm elections?") == ("eq", 5)
    assert sieges.tranche("Will Democrats win 7 or more House seats in Ohio in the 2026 midterm elections?") == ("ge", 7)
    assert sieges.tranche("Will it rain?") is None
    dist = [0.1, 0.2, 0.3, 0.4]
    assert sieges.tranche_p(dist, "lt", 2) == pytest.approx(0.3) and sieges.tranche_p(dist, "eq", 3) == 0.4 and sieges.tranche_p(dist, "ge", 2) == pytest.approx(0.7)
    assert sieges.tranche_p(dist, "eq", 9) == 0.0


def _ladder_market(mid, question, state="Iowa"):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", question=question, end=NOW + timedelta(days=4),
                                   events=[{"id": f"e_{state}", "title": f"How many House seats will the Democrats win in {state}?"}]))


def _save_iowa(db, ps):
    refs._save(db, "ref:sieges", [{"district": f"IA-{i + 1:02d}", "etat": "IA", "p": p, "liq": 1} for i, p in enumerate(ps)], NOW)


def test_attach_marks_the_tranches_of_a_state_with_all_its_districts_only(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    markets = [_ladder_market("ge3", "Will Democrats win 3 or more House seats in Iowa in the 2026 midterm elections?"),
               _ladder_market("eq0", "Will Democrats win exactly 0 House seats in Iowa in the 2026 midterm elections?"),
               _ladder_market("autre_etat", "Will Democrats win 1 or more House seats in Atlantis?", state="Atlantis"),
               parse_market(raw_market("pluie", question="Will it rain?"))]
    assert sieges.attach_sieges(markets, db, NOW) == 0                      # pas de relevé : rien
    _save_iowa(db, [0.9, 0.9, 0.9])                                         # 3 districts sur 4 : État ignoré
    assert sieges.attach_sieges(markets, db, NOW) == 0
    _save_iowa(db, [0.95, 0.95, 0.9, 0.05])
    assert sieges.attach_sieges(markets, db, NOW) == 2
    ge3, eq0 = markets[0].references["sieges"], markets[1].references["sieges"]
    assert ge3["p"] > 0.7 and eq0["p"] < 0.05 and ge3["moyenne"] == 2.85 and "Iowa" in ge3["titre"]
    assert "sieges" not in (markets[2].references or {}) and "sieges" not in (markets[3].references or {})


def test_collector_saves_districts_and_survives_an_outage(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    cfg = {"sources": {"sieges": {"enabled": True, "every_minutes": 15}}}
    rows = sieges.parse_districts([_event("IA", 1, 0.6)])
    result = collect(cfg, None, db, [], NOW, {"sieges": lambda c: rows})
    assert result.status["sieges"] == "ok (1 prix relevés)"
    assert refs._load(db, "ref:sieges")[1] == rows
    http = FakeHttp({}, down=(sieges.GAMMA,))
    down = collect(cfg, None, db, [], NOW + timedelta(minutes=16), {"sieges": lambda c: sieges.fetch_sieges(http, NOW)})
    assert down.status["sieges"].startswith("indisponible") and refs._load(db, "ref:sieges")[1] == rows


def test_fetch_asks_every_district_slug_in_batches():
    http = FakeHttp({sieges.GAMMA: []})
    assert sieges.fetch_sieges(http, NOW, batch=50) == []
    total = sum(n for _, n in sieges.ETATS.values())
    assert sum(len(params["slug"]) for _, params, _ in http.calls) == total
    assert "nc-13-house-election-winner" in http.calls[0][1]["slug"] + http.calls[1][1]["slug"] + http.calls[2][1]["slug"] + http.calls[3][1]["slug"] + http.calls[4][1]["slug"] + http.calls[5][1]["slug"]


def test_strategy_buys_the_side_the_districts_call_cheap_and_skips_stale_prices(tmp_path):
    s = _s(SiegesCoherence, min_net_edge=0.10, retrait=0.3, min_price=0.05, max_price=0.92, max_stale_hours=0.5, max_extra_ticks=2,
           max_candidates=200, max_proposals_per_cycle=6, max_per_event=2, kelly_fraction=0.5)

    def mk(mid, p, yes_mid, seen=NOW, state="Iowa"):
        m = _ladder_market(mid, "Will Democrats win 3 or more House seats in Iowa in the 2026 midterm elections?", state)
        m.token_ids = [f"{mid}Y", f"{mid}N"]
        m.references = {"sieges": {"p": p, "titre": "test", "vu_le": seen.isoformat()}}
        return m, _books((f"{mid}Y", f"{yes_mid - 0.01:.3f}", f"{yes_mid + 0.01:.3f}"), (f"{mid}N", f"{1 - yes_mid - 0.01:.3f}", f"{1 - yes_mid + 0.01:.3f}"))
    cases = [mk("sous_cote", 0.80, 0.38, state="A"), mk("sur_cote", 0.05, 0.40, state="B"), mk("proche", 0.45, 0.40, state="C"),
             mk("vieux", 0.80, 0.38, seen=NOW - timedelta(hours=3), state="D")]
    ms, books = [c[0] for c in cases], {}
    for _, b in cases:
        books.update(b)
        for book in b.values():
            book.fetched_at = NOW
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert {p.market_id: p.outcome for p in out.proposals} == {"sous_cote": "Yes", "sur_cote": "No"}
    assert all(p.strategy_id == "sieges_coherence" for p in out.proposals) and out.abstentions
    assert {m.market_id for m in s.candidates(ms)} == {"sous_cote", "sur_cote", "proche", "vieux"}
