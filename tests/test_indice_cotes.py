"""Tranches de l'indice PredictionMarketOdds (15/11/2026, experiments/indice_cotes.md, piste n° 65).
Données : `latest.json` réel du 15/11/2026 à 20 h UTC, réduit à la liste « 2028 Presidential Winner by Party » (démocrates 0,675,
brut 0,67453) ; marché réel « Democratic 2028 presidential odds … on November 20? » (événement 1375284, fin 17 h UTC)."""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import indice_cotes as ic
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import IndiceCotes

UTC = timezone.utc
NOW = datetime(2026, 11, 15, 20, 30, tzinfo=UTC)
FIN = datetime(2026, 11, 20, 17, 0, tzinfo=UTC)
DOC = json.loads((Path(__file__).parent / "data" / "predictionmarketodds_2026-11-15.json").read_text())


def _market(mid, tranche):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=FIN,
                                   question=f"Democratic 2028 presidential odds {tranche} on November 20?",
                                   events=[{"id": "1375284", "title": "Democratic 2028 presidential odds on November 20?"}]))


def test_lecture_et_questions():
    rows = ic.lire(DOC, NOW)
    dem = next(r for r in rows if r["option"] == "democratic_party")
    assert dem["liste"] == "president_2028_party" and dem["valeur"] == 0.675 and abs(dem["brut"] - 0.67453) < 1e-4
    cle = ("president_2028_party", "democratic_party")
    assert ic.question("Democratic 2028 presidential odds 64-66% on November 20?") == (cle, 0.64, 0.66)
    assert ic.question("Democratic 2028 presidential odds <62% on November 20?") == (cle, 0.0, 0.62)
    assert ic.question("Democratic 2028 presidential odds >70% on November 20?") == (cle, 0.70, math.inf)
    assert ic.question("Democratic Senate odds 64%+ on October 2?")[1:] == (0.64, math.inf)
    # barrières et « leader » : autre règle (4 valeurs consécutives, classement), pas jouées
    assert ic.question("Democratic 2028 presidential odds hit 70% by December 31?") is None
    assert ic.question("Ossoff's Democratic nomination odds 30-32% on November 20?") is None


def test_chance_arrondi_et_somme():
    tr = [(0, 0.62), (0.62, 0.64), (0.64, 0.66), (0.66, 0.68), (0.68, 0.70), (0.70, math.inf)]
    ps = [ic.chance(0.67453, 116.5, a, b) for a, b in tr]
    assert abs(sum(ps) - 1) < 1e-9
    assert ps[3] > 0.55 and ps[2] < 0.12 and ps[0] < 0.01
    # à l'échéance : la valeur publiée est l'arrondi au millième (0,6795 publié 0,680 va à « 68-70 ») : la borne est à 0,6795
    assert ic.chance(0.6796, 0.0, 0.68, 0.70) > 0.5 > ic.chance(0.6794, 0.0, 0.68, 0.70)
    assert ic.chance(0.6770, 0.0, 0.66, 0.68) > 0.9


def test_collecte_rattachement_et_achat(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    result = collect({"sources": {"indice_cotes": {"enabled": True, "every_minutes": 60}}}, Http({ic.LATEST: DOC}), db, [], NOW)
    assert result.status["indice_cotes"].startswith("ok (2")
    m64, m66 = _market("7000219", "64-66%"), _market("7000220", "66-68%")
    autre = parse_market(raw_market("9", yes_token="9Y", no_token="9N", end=FIN, question="Democratic 2028 presidential odds hit 70% by December 31?"))
    assert refs.attach_all([m64, m66, autre], db, NOW)["indice_cotes"] == 2
    assert "indice_cotes" not in (autre.references or {})
    p64 = m64.references["indice_cotes"]["p"]
    # le 15/11 à 20 h : « 64-66 % » coté 0,14/0,15 pour une chance ≈ 0,06 : achat du NON à 0,86
    b = _books(("7000219Y", "0.14", "0.15"), ("7000219N", "0.85", "0.86"),
               ("7000220Y", str(round(m66.references["indice_cotes"]["p"] - 0.01, 2)), str(round(m66.references["indice_cotes"]["p"], 2))),
               ("7000220N", "0.3", "0.4"))
    for x in b.values():
        x.fetched_at = NOW
    s = _s(IndiceCotes, min_net_edge=0.05, uncertainty=0.02, min_price=0.08, max_price=0.92, max_stale_hours=3,
           max_extra_ticks=1, max_proposals_per_cycle=2, max_per_event=2, kelly_fraction=1.0, max_candidates=30)
    assert p64 < 0.08
    out = s.propose([m64, m66], b, _state(tmp_path), LIMITS, "b1")
    assert [p.token_id for p in out.proposals] == ["7000219N"]
    # source vieille de plus de 3 h : plus de chance donnée
    assert refs.attach_all([_market("7000221", "68-70%")], db, datetime(2026, 11, 16, 0, 0, tzinfo=UTC))["indice_cotes"] == 0
