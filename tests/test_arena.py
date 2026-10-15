"""Arène : cliquet des paliers, champion, élimination hebdomadaire."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest

from conftest import KEY, NOW, buy
from polymarket_agent.arena import Standing, choose_champion, choose_elimination, run_arena
from polymarket_agent.ledger import InvalidEntry, Ledger

D = Decimal


def st(name, trades, growth, days=10, eliminated=False):
    return Standing(name, trades, 1000.0, 1000.0, growth, NOW - timedelta(days=days), eliminated)


def test_champion_needs_enough_trades_and_must_beat_doing_nothing():
    assert choose_champion([st("a", 19, 0.5)], "", 20)[0] == ""          # pas assez d'opérations
    assert choose_champion([st("a", 20, -0.1)], "", 20)[0] == ""         # pire que ne rien faire
    assert choose_champion([st("a", 20, 0.1), st("b", 30, 0.3)], "", 20)[0] == "b"


def test_champion_keeps_title_until_beaten_and_new_champion_gets_time():
    standings = [st("a", 40, 0.2), st("b", 40, 0.15)]
    assert choose_champion(standings, "a", 20)[0] == "a"
    assert choose_champion([st("a", 40, 0.2), st("b", 40, 0.25)], "a", 20)[0] == "b"
    assert choose_champion([st("new", 3, -0.05)], "new", 20)[0] == "new"  # pas encore jugé
    assert choose_champion([st("a", 25, -0.01)], "a", 20)[0] == ""        # déchu
    assert choose_champion([st("a", 25, 0.3, eliminated=True)], "a", 20)[0] == ""


def test_weekly_elimination_of_the_worst_never_the_champion():
    standings = [st("champ", 50, -0.5), st("x", 30, 0.1), st("y", 30, -0.2)]
    assert choose_elimination(standings, "champ", None, NOW, 20, 7, 7).name == "y"
    assert choose_elimination(standings, "champ", NOW - timedelta(days=3), NOW, 20, 7, 7) is None
    young = [st("x", 30, 0.1, days=2), st("y", 30, -0.2, days=2)]
    assert choose_elimination(young, "", None, NOW, 20, 7, 7) is None
    assert choose_elimination([st("x", 30, 0.1)], "", None, NOW, 20, 7, 7) is None


def test_run_arena_writes_signed_promotion(ledger, paths, tmp_path):
    shadow = Ledger.create(tmp_path / "s.jsonl", KEY, tmp_path / "s.lock", "1000", now=NOW)
    for i in range(20):
        buy(shadow, f"b{i}", token=f"t{i}", shares="10", price="0.5", event=f"e{i}")
        shadow.record_settlement(op_id=f"s{i}", token_id=f"t{i}", payout_per_share="1",
                                 resolution="Yes", now=NOW)
    summary = run_arena(ledger, {"star_v1": shadow}, {"min_closed_trades": 20}, NOW)
    assert summary["champion"] == "star_v1" and summary["events"]
    assert Ledger.open(paths[0], KEY, paths[1]).state.champion == "star_v1"


def test_ratchet_milestones_use_realized_capital_only(ledger, paths):
    assert ledger.state.next_target == D("1500")
    buy(ledger, "b1", token="tA", shares="1000", price="0.5")
    # Gain latent énorme : ne compte pas.
    assert ledger.state.total_estimated({"tA": D("0.99")}) > D("1450")
    assert ledger.record_milestones(NOW) == []
    ledger.record_settlement(op_id="s1", token_id="tA", payout_per_share="1", resolution="Yes", now=NOW)
    assert ledger.state.realized_capital() == D("1500")
    reached = ledger.record_milestones(NOW + timedelta(hours=2))
    assert [m["target"] for m in reached] == ["1500.0"] or [D(m["target"]) for m in reached] == [D("1500")]
    assert ledger.state.next_target == D("2250")
    assert Ledger.open(paths[0], KEY, paths[1]).state.next_target == D("2250")


def test_several_milestones_at_once_and_no_fake_milestone(ledger):
    buy(ledger, "b1", token="tA", shares="1990", price="0.5")
    ledger.record_settlement(op_id="s1", token_id="tA", payout_per_share="1", resolution="Yes", now=NOW)
    # 2 000 + 5 = 2 005 de capital réalisé → paliers 1 500 puis… 2 250 non atteint.
    assert [D(m["target"]) for m in ledger.record_milestones(NOW)] == [D("1500")]
    with pytest.raises(InvalidEntry):
        ledger._append("MILESTONE", {"target": "2250"}, NOW)  # pas atteint : refusé


def test_champion_cannot_be_eliminated(ledger):
    ledger.record_promotion("a_v1", "test", now=NOW)
    with pytest.raises(InvalidEntry):
        ledger.record_elimination("a_v1", "test", now=NOW)
    ledger.record_elimination("b_v1", "test", now=NOW)
    with pytest.raises(InvalidEntry):
        ledger.record_promotion("b_v1", "retour interdit", now=NOW)


def test_brief_lists_innovation_obligations(ledger, tmp_path):
    from polymarket_agent.brief import build_brief, render_brief
    cfg = {"min_strategies_in_test": 3, "radical_idea_after_days_without_record": 7}
    brief = build_brief(ledger, {}, ["a_v1"], cfg, now=NOW + timedelta(days=8))
    text = " ".join(brief["obligations"])
    assert "Ajouter 2 nouvelle(s)" in text and "RADICALEMENT" in text
    assert brief["palier_suivant"] == "1500.0" or D(brief["palier_suivant"]) == D("1500")
    assert "Feuille de mission" in render_brief(brief)
    calm = build_brief(ledger, {}, ["a_v1", "b_v1", "c_v1"], cfg, now=NOW + timedelta(days=1))
    assert calm["obligations"] == []
