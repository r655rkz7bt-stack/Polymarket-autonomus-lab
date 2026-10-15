"""Learning Engine : verdicts honnêtes, analyses par opération (cahier des charges §4.I)."""

from __future__ import annotations

from datetime import timedelta

from conftest import NOW, buy
from polymarket_agent.learning_engine import analyze


def close(ledger, i, won, price="0.5", est="0.9", hours=2, event=None):
    ledger.record_buy(op_id=f"b{i}", token_id=f"t{i}", market_id=f"m{i}", event_id=event or f"e{i}",
                      outcome="Yes", shares="10", price=price, fee="0.05", strategy_id="s",
                      strategy_version="1", now=NOW + timedelta(hours=i),
                      extra={"est_probability": est})
    ledger.record_settlement(op_id=f"s{i}", token_id=f"t{i}", payout_per_share="1" if won else "0",
                             resolution="x", now=NOW + timedelta(hours=i + hours))


def test_too_few_trades_is_insufficient_data(ledger):
    for i in range(5):
        close(ledger, i, won=True)
    report = analyze({"p": ledger})["p"]["strategies"]["s v1"]
    assert report["verdict"] == "données insuffisantes"
    assert report["operations"] == 5 and report["taux_reussite"] == 1.0


def test_losing_strategy_is_recognized_and_lessons_are_kept(ledger):
    for i in range(30):
        close(ledger, i, won=(i % 5 == 0), est="0.9")  # 20 % de réussite avec 90 % annoncés
    out = analyze({"p": ledger}, {"m0": "sports"})["p"]
    report = out["strategies"]["s v1"]
    assert report["verdict"] == "ne fonctionne pas"
    assert report["probabilite_hasard"] > 0.9
    assert report["lecons_frequentes"]["surconfiance : probabilité >= 0,8 et perte"] == 24
    assert report["calibration"][0]["prevu"] == 0.9 and report["calibration"][0]["observe"] == 0.2
    assert len(out["operations"]) == 30  # perdantes ET gagnantes conservées
    assert out["operations"][0]["categorie"] == "sports"
    assert report["par_duree"]["1–6 h"]["n"] == 30


def test_winning_strategy_is_promising_not_proven(ledger):
    for i in range(40):
        close(ledger, i, won=(i % 10 != 0), est="0.85")  # 90 % de réussite à 0,50 : gros gain
    report = analyze({"p": ledger})["p"]["strategies"]["s v1"]
    assert report["verdict"] == "prometteuse"
    assert report["probabilite_hasard"] < 0.05
    assert report["ic90_rendement"][0] > 0


def test_noisy_strategy_is_undetermined(ledger):
    for i in range(24):
        close(ledger, i, won=(i % 2 == 0), price="0.5", est="0.5")
    report = analyze({"p": ledger})["p"]["strategies"]["s v1"]
    assert report["verdict"].startswith("indéterminée")
