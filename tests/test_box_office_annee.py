"""Film le plus rentable de l'année (12/11/2026, experiments/box_office_annee.md, piste n° 33) : tranches du marché du premier
week-end, loi ajustée, chance de dépasser le meneur, rattachement et stratégie `box_office_annee`.
Données : prix réels Gamma du 12/11/2026 vers 06 h UTC (« "Avengers: Doomsday" Opening Weekend Box Office », événement 1285841)."""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import box_office as bo
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import BoxOfficeAnnee

UTC = timezone.utc
NOW = datetime(2026, 11, 12, 6, 0, tzinfo=UTC)
PRIX_12_11 = [("<260m", 0.009), ("260m-300m", 0.0165), ("300m-340m", 0.07), ("340m-360m", 0.145), ("360m-400m", 0.265), ("400m+", 0.475)]
COURSE = {"film": "Avengers: Doomsday", "annee": 2026, "ow_event": 1285841, "meneur": 959.5, "ratio": 2.35, "ratio_sigma": 0.08,
          "jusqu_au": "2026-12-22T12:00:00+00:00"}


def _event(prix, reglee=None):
    ms = []
    for titre, p in prix:
        closed = reglee is not None
        pp = (1.0 if titre == reglee else 0.0) if closed else p
        ms.append({"groupItemTitle": titre, "outcomePrices": json.dumps([str(pp), str(1 - pp)]), "closed": closed})
    return {"id": "1285841", "markets": ms}


def _market(mid, question):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2027, 1, 8, 4, 59, tzinfo=UTC),
                                   question=question, events=[{"id": "79831", "title": "Highest grossing movie in 2026?"}]))


def test_tranches_are_read_in_millions_with_open_ends():
    assert bo.parse_tranche("<260m") == (1.0, 260.0)
    assert bo.parse_tranche("260m-300m") == (260.0, 300.0)
    assert bo.parse_tranche("400m+") == (400.0, math.inf)
    assert bo.parse_tranche("Spider-Man: Brand New Day") is None


def test_lognormal_fit_and_chance_on_the_real_prices_of_12_11():
    tr = bo.tranches_of_event(_event(PRIX_12_11))
    med, s = bo.fit_lognormal(tr)
    assert 390 <= med <= 410 and 0.10 <= s <= 0.17          # médiane ≈ 399 M$, écart log ≈ 0,135
    r = bo.p_depasse(tr, 959.5, 2.35, 0.08)
    assert 0.38 <= r["p"] <= 0.48 and r["mode"] == "prix du premier week-end"
    # Multiplicateur de Spider-Man NWH (2,15) : bien moins, mais toujours au-dessus du prix de l'année (0,077)
    assert 0.15 <= bo.p_depasse(tr, 959.5, 2.15, 0.08)["p"] < r["p"]


def test_settled_tranche_replaces_the_price_fit():
    haut = bo.p_depasse(bo.tranches_of_event(_event(PRIX_12_11, reglee="400m+")), 959.5, 2.35, 0.08)
    bas = bo.p_depasse(bo.tranches_of_event(_event(PRIX_12_11, reglee="300m-340m")), 959.5, 2.35, 0.08)
    assert haut["mode"] == "tranche réglée" and haut["p"] > 0.5
    assert bas["p"] < 0.01


def test_collect_attach_and_buy_only_above_the_ticket_floor(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    http = Http({bo.GAMMA_EVENT.format(id=1285841): _event(PRIX_12_11)})
    result = collect({"sources": {"box_office": {"enabled": True, "every_minutes": 60, "courses": [COURSE]}}}, http, db, [], NOW)
    assert result.status["box_office"].startswith("ok (1")
    doom = _market("678416", "Will Avengers: Doomsday be the top grossing movie of 2026?")
    spidey = _market("678414", "Will Spider-Man: Brand New Day be the top grossing movie of 2026?")
    assert refs.attach_all([doom, spidey], db, NOW)["box_office"] == 1
    assert "box_office" not in (spidey.references or {})
    s = _s(BoxOfficeAnnee, min_net_edge=0.05, uncertainty=0.15, min_price=0.10, max_price=0.90, max_stale_hours=3,
           max_extra_ticks=1, max_proposals_per_cycle=1, max_per_event=1, kelly_fraction=0.5)

    def books(bid, ask):
        b = _books(("678416Y", str(bid), str(ask)), ("678416N", str(round(1 - ask, 3)), str(round(1 - bid, 3))))
        for x in b.values():
            x.fetched_at = NOW
        return b
    # carnet réel du 12/11 (0,076/0,077) : billet sous 0,10, pas d'achat
    out = s.propose([doom], books(0.076, 0.077), _state(tmp_path), LIMITS, "b1")
    assert out.proposals == [] and out.abstentions.get("issue hors de la plage de prix ou carnet vide")
    # si le prix monte à 0,12 sans que le marché du week-end bouge : achat du OUI
    out = s.propose([doom], books(0.11, 0.12), _state(tmp_path), LIMITS, "b1")
    assert [p.token_id for p in out.proposals] == ["678416Y"]
    # après la date d'arrêt (recettes réelles publiées), plus de rattachement
    dec23 = datetime(2026, 12, 23, tzinfo=UTC)
    collect({"sources": {"box_office": {"enabled": True, "every_minutes": 60, "courses": [COURSE]}}}, http, db, [], dec23)
    late = _market("678416", "Will Avengers: Doomsday be the top grossing movie of 2026?")
    assert refs.attach_all([late], db, dec23)["box_office"] == 0
