"""Convictions de Claude (labo v2, 07/11/2026) : prévisions écrites dans config/convictions.yaml, jouées sur les vrais carnets."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal as D

import yaml

from conftest import NOW, ROOT
from test_strategies_v3 import LIMITS, _books, _m, _state
from polymarket_agent.convictions import ConvictionsClaude, charger
from polymarket_agent.ledger import Position

PARAMS = {"min_net_edge": D("0.03"), "kelly_fraction": D("0.5"), "max_extra_ticks": D("2"), "max_proposals_per_cycle": D("5")}


def _write(tmp_path, convictions):
    path = tmp_path / "convictions.yaml"
    path.write_text(yaml.safe_dump({"convictions": convictions}, allow_unicode=True), encoding="utf-8")
    return ConvictionsClaude("2.0.0", "2026-11-07", PARAMS, path), path


def _conv(**kw):
    c = {"id": "c1", "marche": "7", "question": "Question 7", "issue": "No", "probabilite": 0.80, "probabilite_basse": 0.72,
         "expire": (NOW + timedelta(days=10)).date().isoformat(), "mise_max": 0.05, "raison": "lu la source officielle",
         "sources": ["https://exemple.org"], "ecrit_le": NOW.date().isoformat()}
    c.update(kw)
    return c


def test_buys_the_chosen_outcome_only_well_below_claude_s_cautious_bound(tmp_path):
    s, _ = _write(tmp_path, [_conv()])
    m, other = _m("7"), _m("8")
    assert s.candidates([m, other]) == [m]  # la stratégie demande ses marchés au scanner
    cheap = s.propose([m], _books(("7Y", 0.38, 0.40), ("7N", 0.58, 0.60)), _state(tmp_path), LIMITS, "b")
    assert [p.token_id for p in cheap.proposals] == ["7N"] and cheap.proposals[0].prob_low == D("0.72")
    assert float(cheap.proposals[0].shares * cheap.proposals[0].max_price) <= 50.0 + 1e-6  # mise_max : 5 % de 1 000
    dear = s.propose([m], _books(("7Y", 0.28, 0.30), ("7N", 0.70, 0.71)), _state(tmp_path), LIMITS, "b")
    assert not dear.proposals and dear.abstentions.get("avantage net insuffisant")  # 0,71 > 0,72 − 0,03


def test_expired_abandoned_mismatched_or_unknown_outcome_never_buy(tmp_path):
    books = _books(("7Y", 0.38, 0.40), ("7N", 0.58, 0.60))
    cases = {"conviction expirée": _conv(expire=(NOW - timedelta(days=1)).date().isoformat()),
             "conviction abandonnée": _conv(abandon=True),
             "question différente de la conviction (identifiant à vérifier)": _conv(question="Will something else"),
             "issue introuvable dans le marché": _conv(issue="Peut-être")}
    for i, (reason, conv) in enumerate(cases.items()):
        (tmp_path / str(i)).mkdir()
        s, _ = _write(tmp_path / str(i), [conv])
        out = s.propose([_m("7")], books, _state(tmp_path), LIMITS, "b")
        assert not out.proposals and out.abstentions.get(reason), reason


def test_malformed_lines_are_skipped_and_the_repository_file_loads():
    assert charger(ROOT / "config" / "convictions.yaml") == [] or all("marche" in c for c in charger(ROOT / "config" / "convictions.yaml"))
    raw = {"convictions": [{"marche": "1", "issue": "Yes", "probabilite": 1.2}, {"issue": "Yes"},
                           {"marche": "2", "issue": "Yes", "probabilite": 0.6, "probabilite_basse": 0.7}]}
    from pathlib import Path
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "c.yaml"
        p.write_text(yaml.safe_dump(raw), encoding="utf-8")
        assert charger(p) == []  # probabilité > 1, sans marché, borne basse au-dessus de l'estimation : ignorées


def test_sells_when_claude_changes_his_mind_or_the_market_pays_more_than_his_estimate(tmp_path):
    s, path = _write(tmp_path, [_conv()])
    m = _m("7")
    pos = {"7N": Position(token_id="7N", market_id="7", event_id="ev1", outcome="No", shares=D("50"), cost_basis=D("30"),
                          opened_at=NOW.isoformat(), strategy_id="convictions_claude", strategy_version="2.0.0")}
    calm = _books(("7Y", 0.30, 0.32), ("7N", 0.66, 0.68))
    assert s.exits(pos, {"7": m}, calm, "b", NOW) == []  # le marché paie 0,66 < 0,80 : on garde
    rich = _books(("7Y", 0.12, 0.14), ("7N", 0.84, 0.86))
    assert [p.side for p in s.exits(pos, {"7": m}, rich, "b", NOW)] == ["SELL"]  # 0,84 > 0,80 : vendre
    path.write_text(yaml.safe_dump({"convictions": [_conv(abandon=True)]}), encoding="utf-8")
    assert [p.token_id for p in s.exits(pos, {"7": m}, calm, "b", NOW)] == ["7N"]
