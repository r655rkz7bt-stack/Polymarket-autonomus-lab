"""Règle n°1 : à 0 € tu meurs. Séparation stricte des soldes. (FICHIER PROTÉGÉ)"""

from __future__ import annotations

import json
from decimal import Decimal

import pytest

from conftest import KEY, NOW, buy
from polymarket_agent.ledger import (Ledger, LedgerCorrupt, LedgerLocked, ResetRefused, canonical)

D = Decimal


def test_buy_separates_cash_immobilized_and_fees(ledger):
    buy(ledger, "op1", shares="100", price="0.5", fee="0.4")
    s = ledger.state
    assert s.cash == D("949.6")
    assert s.immobilized() == D("50.4")
    assert s.fees_paid == D("0.4")
    assert s.realized_pnl == 0
    assert s.total_estimated() == D("1000")  # sans prix de marque : valorisé au coût


def test_unrealized_gains_never_become_available_cash(ledger):
    buy(ledger, "op1", shares="100", price="0.5")
    marks = {"tokA": D("0.9")}
    assert ledger.state.unrealized_pnl(marks) == D("40")
    assert ledger.state.total_estimated(marks) == D("1040")
    assert ledger.state.cash == D("950")  # inchangé


def test_sell_books_realized_pnl_net_of_fees(ledger):
    buy(ledger, "op1", shares="100", price="0.5", fee="1")
    ledger.record_sell(op_id="op2", token_id="tokA", shares="50", price="0.7", fee="0.5", now=NOW)
    s = ledger.state
    assert s.cash == D("949") + D("35") - D("0.5")
    assert s.realized_pnl == D("34.5") - D("25.5")
    assert s.positions["tokA"].shares == D("50")
    assert s.positions["tokA"].cost_basis == D("25.5")
    assert s.fees_paid == D("1.5")


@pytest.mark.parametrize("payout,cash,pnl", [("1", "1050", "50"), ("0", "950", "-50"),
                                             ("0.5", "1000", "0")])
def test_settlement_win_loss_and_split(ledger, payout, cash, pnl):
    buy(ledger, "op1", shares="100", price="0.5")
    ledger.record_settlement(op_id="s1", token_id="tokA", payout_per_share=payout,
                             resolution="test", now=NOW)
    assert ledger.state.cash == D(cash)
    assert ledger.state.realized_pnl == D(pnl)
    assert not ledger.state.positions


def test_loss_cannot_create_artificial_positive_balance(ledger):
    buy(ledger, "op1", shares="100", price="0.5", fee="1")
    ledger.record_settlement(op_id="s1", token_id="tokA", payout_per_share="0",
                             resolution="perdu", now=NOW)
    assert ledger.state.cash == D("949")
    assert ledger.state.total_estimated() == D("949")
    assert ledger.state.realized_pnl == D("-51")
    with pytest.raises(Exception):
        ledger.record_settlement(op_id="s2", token_id="tokA", payout_per_share="1",
                                 resolution="encore", now=NOW)
    assert ledger.state.cash == D("949")


def _go_bankrupt(ledger):
    buy(ledger, "op1", shares="2000", price="0.5")  # tout le solde
    return ledger


def test_zero_balance_triggers_bankruptcy_and_lock(ledger, paths):
    _go_bankrupt(ledger)
    assert ledger.state.cash == 0
    assert ledger.state.bankrupt
    assert "<= 0" in ledger.state.bankrupt_reason
    assert paths[1].exists()
    last = json.loads(paths[0].read_text(encoding="utf-8").splitlines()[-1])
    assert last["type"] == "BANKRUPT"


def test_zero_balance_blocks_every_new_operation(ledger):
    _go_bankrupt(ledger)
    with pytest.raises(LedgerLocked):
        buy(ledger, "op2", token="tokB", shares="1", price="0.1")
    with pytest.raises(LedgerLocked):
        ledger.record_sell(op_id="op3", token_id="tokA", shares="1", price="0.5", fee="0")
    with pytest.raises(LedgerLocked):
        ledger.record_settlement(op_id="op4", token_id="tokA", payout_per_share="1", resolution="x")


def test_no_automatic_restart_after_bankruptcy(ledger, paths):
    _go_bankrupt(ledger)
    reopened = Ledger.open(paths[0], KEY, paths[1])
    assert reopened.state.bankrupt
    paths[1].unlink()  # supprimer le verrou ne suffit pas : l'écriture BANKRUPT reste
    assert Ledger.open(paths[0], KEY, paths[1]).state.bankrupt
    assert paths[1].exists()  # le verrou est réécrit
    with pytest.raises(LedgerLocked):
        Ledger.create(paths[0].with_name("nouveau.jsonl"), KEY, paths[1], "1000")


def test_truncating_bankruptcy_entry_is_detected(ledger, paths):
    _go_bankrupt(ledger)
    content = paths[0].read_text(encoding="utf-8").splitlines()
    paths[0].write_text("\n".join(content[:-1]) + "\n", encoding="utf-8")
    with pytest.raises(LedgerCorrupt):
        Ledger.open(paths[0], KEY, paths[1])  # verrou postérieur à la fin du journal


def test_zero_balance_without_bankrupt_entry_is_still_bankruptcy(ledger, paths):
    _go_bankrupt(ledger)
    content = paths[0].read_text(encoding="utf-8").splitlines()
    paths[0].write_text("\n".join(content[:-1]) + "\n", encoding="utf-8")
    paths[1].unlink()
    reopened = Ledger.open(paths[0], KEY, paths[1])
    assert reopened.state.bankrupt  # le solde recalculé est 0


def test_forged_lock_file_is_detected(ledger, paths):
    _go_bankrupt(ledger)
    lock = json.loads(paths[1].read_text(encoding="utf-8"))
    lock["reason"] = "autre"
    paths[1].write_text(canonical(lock), encoding="utf-8")
    with pytest.raises(LedgerCorrupt):
        Ledger.open(paths[0], KEY, paths[1])


def test_reset_requires_the_right_code(ledger, paths):
    _go_bankrupt(ledger)
    with pytest.raises(ResetRefused):
        ledger.reset(provided_code="faux-code", expected_code="le-bon-code-123", reason="test",
                     initial_capital="1000")
    with pytest.raises(ResetRefused):
        ledger.reset(provided_code="", expected_code="", reason="test", initial_capital="1000")
    with pytest.raises(ResetRefused):
        ledger.reset(provided_code="le-bon-code-123", expected_code="le-bon-code-123", reason=" ",
                     initial_capital="1000")
    assert ledger.state.bankrupt


def test_reset_with_code_restarts_documented(ledger, paths):
    _go_bankrupt(ledger)
    ledger.reset(provided_code="le-bon-code-123", expected_code="le-bon-code-123",
                 reason="Etienne : nouvelle expérience", initial_capital="1000")
    reopened = Ledger.open(paths[0], KEY, paths[1])
    assert not reopened.state.bankrupt
    assert reopened.state.cash == D("1000")
    assert reopened.state.epoch == 1
    assert not reopened.state.positions
    assert not paths[1].exists()
