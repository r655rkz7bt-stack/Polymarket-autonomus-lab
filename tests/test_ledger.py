"""Journal signé : intégrité, idempotence, reprise après redémarrage. (FICHIER PROTÉGÉ)"""

from __future__ import annotations

import json
from decimal import Decimal

import pytest

from conftest import KEY, NOW, buy
from polymarket_agent.ledger import (DuplicateOperation, InsufficientFunds, InvalidEntry, Ledger,
                                     LedgerCorrupt, LedgerError, NotInitialized, canonical,
                                     entry_hash, sign)


def lines(path):
    return path.read_text(encoding="utf-8").splitlines()


def test_genesis_and_replay(ledger, paths):
    reopened = Ledger.open(paths[0], KEY, paths[1])
    assert reopened.state.cash == Decimal("1000")
    assert reopened.state.last_seq == 0
    assert reopened.hash_at(0) == ledger.state.last_hash


def test_restart_recovers_positions_and_capital(ledger, paths):
    buy(ledger, "op1", shares="100", price="0.5", fee="0.25")
    ledger.record_sell(op_id="op2", token_id="tokA", shares="40", price="0.6", fee="0.1", now=NOW)
    before = ledger.state.summary()
    reopened = Ledger.open(paths[0], KEY, paths[1])
    assert reopened.state.summary() == before
    assert reopened.state.positions["tokA"].shares == Decimal("60")
    assert reopened.state.op_ids == {"op1", "op2"}


def test_open_missing_ledger_never_creates_capital(paths):
    with pytest.raises(NotInitialized):
        Ledger.open(paths[0], KEY, paths[1])
    assert not paths[0].exists()


def test_create_refuses_existing_ledger(ledger, paths):
    with pytest.raises(LedgerError):
        Ledger.create(paths[0], KEY, paths[1], "1000")


def test_duplicate_operation_is_not_booked_twice(ledger, paths):
    buy(ledger, "op1")
    size, cash = paths[0].stat().st_size, ledger.state.cash
    with pytest.raises(DuplicateOperation):
        buy(ledger, "op1")
    assert ledger.state.cash == cash
    assert paths[0].stat().st_size == size


def test_buy_beyond_cash_is_refused(ledger):
    with pytest.raises(InsufficientFunds):
        buy(ledger, "op1", shares="3000", price="0.5")
    assert ledger.state.cash == Decimal("1000")
    assert not ledger.state.positions


@pytest.mark.parametrize("bad", [{"shares": "-1"}, {"price": "1.2"}, {"fee": "-0.1"},
                                 {"price": "NaN"}, {"shares": "0"}])
def test_invalid_buy_is_refused(ledger, bad):
    params = {"shares": "10", "price": "0.5", "fee": "0"} | bad
    with pytest.raises(InvalidEntry):
        buy(ledger, "op1", **params)
    assert ledger.state.cash == Decimal("1000")


def test_tampered_amount_is_detected(ledger, paths):
    buy(ledger, "op1")
    content = lines(paths[0])
    record = json.loads(content[1])
    record["data"]["price"] = "0.01"  # tentative de payer moins cher
    content[1] = canonical(record)
    paths[0].write_text("\n".join(content) + "\n", encoding="utf-8")
    with pytest.raises(LedgerCorrupt):
        Ledger.open(paths[0], KEY, paths[1])


def test_deleted_middle_line_is_detected(ledger, paths):
    buy(ledger, "op1")
    buy(ledger, "op2", token="tokB")
    content = lines(paths[0])
    del content[1]
    paths[0].write_text("\n".join(content) + "\n", encoding="utf-8")
    with pytest.raises(LedgerCorrupt):
        Ledger.open(paths[0], KEY, paths[1])


def test_wrong_key_is_detected(ledger, paths):
    with pytest.raises(LedgerCorrupt):
        Ledger.open(paths[0], b"x" * 40, paths[1])


def test_forged_line_without_key_is_detected(ledger, paths):
    """Ajouter une ligne qui crée du capital sans connaître la clé est impossible."""
    state = ledger.state
    data = {"reason": "triche", "initial_capital": "1000000"}
    ts = "2026-10-14T13:00:00.000000+00:00"
    digest = entry_hash(state.last_seq + 1, ts, "RESET", data, state.last_hash)
    forged = {"seq": state.last_seq + 1, "ts": ts, "type": "RESET", "data": data,
              "prev": state.last_hash, "hash": digest, "sig": sign(b"z" * 40, digest)}
    with paths[0].open("a", encoding="utf-8") as handle:
        handle.write(canonical(forged) + "\n")
    with pytest.raises(LedgerCorrupt):
        Ledger.open(paths[0], KEY, paths[1])


def test_partial_last_line_is_detected(ledger, paths):
    buy(ledger, "op1")
    text = paths[0].read_text(encoding="utf-8")
    paths[0].write_text(text[:-20], encoding="utf-8")
    with pytest.raises(LedgerCorrupt):
        Ledger.open(paths[0], KEY, paths[1])


def test_timestamp_going_backwards_is_detected(ledger, paths):
    """Même signée avec la bonne clé, une écriture antidatée est refusée."""
    state = ledger.state
    data = {"cycle_id": "x", "status": "OK", "cash": "1000"}
    ts = "2020-01-01T00:00:00.000000+00:00"
    digest = entry_hash(1, ts, "HEARTBEAT", data, state.last_hash)
    record = {"seq": 1, "ts": ts, "type": "HEARTBEAT", "data": data, "prev": state.last_hash,
              "hash": digest, "sig": sign(KEY, digest)}
    with paths[0].open("a", encoding="utf-8") as handle:
        handle.write(canonical(record) + "\n")
    with pytest.raises(LedgerCorrupt):
        Ledger.open(paths[0], KEY, paths[1])


def test_sell_more_than_held_is_refused(ledger):
    buy(ledger, "op1", shares="10")
    with pytest.raises(InvalidEntry):
        ledger.record_sell(op_id="op2", token_id="tokA", shares="11", price="0.5", fee="0")


def test_key_is_never_in_repr_or_file(ledger, paths):
    assert KEY.decode() not in repr(ledger)
    assert KEY.decode() not in paths[0].read_text(encoding="utf-8")
