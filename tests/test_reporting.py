"""Rapports : opérations clôturées, performances, drawdown."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from conftest import NOW, buy
from polymarket_agent.persistence import Database
from polymarket_agent.reporting import (build_report, closed_trades, equity_curve, max_drawdown,
                                        read_entries, render_markdown, strategy_metrics)

D = Decimal


def test_closed_trades_keep_winners_and_losers(ledger):
    buy(ledger, "b1", token="tA", shares="100", price="0.9", fee="0.36")
    buy(ledger, "b2", token="tB", shares="50", price="0.8", fee="0.32", event="ev2")
    buy(ledger, "b3", token="tC", shares="10", price="0.5", event="ev3")  # reste ouverte
    ledger.record_settlement(op_id="s1", token_id="tA", payout_per_share="1", resolution="Yes", now=NOW)
    ledger.record_settlement(op_id="s2", token_id="tB", payout_per_share="0", resolution="No", now=NOW)
    trades = closed_trades(read_entries(ledger))
    assert [t["token_id"] for t in trades] == ["tA", "tB"]
    assert trades[0]["pnl"] == D("100") - D("90.36")
    assert trades[1]["pnl"] == D("-40.32")
    metrics = strategy_metrics(trades)["test v0"]
    assert metrics["operations"] == 2 and metrics["gagnantes"] == 1
    assert metrics["assez_de_donnees"] is False


def test_partial_sell_then_close(ledger):
    buy(ledger, "b1", token="tA", shares="100", price="0.5")
    ledger.record_sell(op_id="v1", token_id="tA", shares="40", price="0.6", fee="0", now=NOW)
    assert closed_trades(read_entries(ledger)) == []
    ledger.record_sell(op_id="v2", token_id="tA", shares="60", price="0.4", fee="0", now=NOW)
    trades = closed_trades(read_entries(ledger))
    assert trades[0]["pnl"] == D("24") + D("24") - D("50")


def test_drawdown_from_heartbeats(ledger):
    for i, total in enumerate(["1000", "1100", "880", "990"]):
        ledger.heartbeat(f"c{i}", "OK", NOW + timedelta(minutes=i), total_estimated=D(total))
    curve = equity_curve(read_entries(ledger))
    assert abs(max_drawdown(curve) - 0.2) < 1e-9


def test_full_report_renders(ledger, tmp_path):
    buy(ledger, "b1", token="tA", shares="10", price="0.5")
    db = Database(tmp_path / "db.sqlite")
    report = build_report(ledger, db, {"tA": D("0.6")}, now=NOW)
    text = render_markdown(report)
    assert "Solde disponible" in text and "995" in text
    assert report["positions_ouvertes"][0]["latent"] == "1.00"
    db.close()


def test_regression_cash_only_heartbeat_is_not_a_drawdown(ledger):
    """Défaut du 14/10/2026 : un battement sans total estimé (solde seul) faisait croire
    à une perte de 18 % alors que l'argent était simplement immobilisé en positions."""
    buy(ledger, "b1", token="tA", shares="400", price="0.5")
    ledger.heartbeat("c0", "OK", NOW)  # ancien format : solde seul (800)
    ledger.heartbeat("c1", "OK", NOW, total_estimated=D("1000"))
    assert max_drawdown(equity_curve(read_entries(ledger))) == 0.0
