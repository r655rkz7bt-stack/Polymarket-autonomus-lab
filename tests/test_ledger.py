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


def test_group_and_heartbeat_total_survive_restart(ledger, paths):
    ledger.record_buy(op_id="g1", token_id="tokA", market_id="m", event_id="e", outcome="Yes",
                      shares="10", price="0.5", fee="0", strategy_id="t", strategy_version="0",
                      now=NOW, group="crypto:btc")
    ledger.heartbeat("c1", "OK", NOW, total_estimated=Decimal("1001.5"))
    reopened = Ledger.open(paths[0], KEY, paths[1])
    assert reopened.state.positions["tokA"].group == "crypto:btc"
    last = json.loads(paths[0].read_text(encoding="utf-8").splitlines()[-1])
    assert last["data"]["total_estimated"] == "1001.5"
    buy(ledger, "g2", token="tokB", event="e9")
    assert Ledger.open(paths[0], KEY, paths[1]).state.positions["tokB"].group == "e9"


def test_state_clone_is_equivalent_to_deepcopy_and_independent(ledger):
    import copy
    import dataclasses
    buy(ledger, "op1", token="tokA", shares="10", price="0.5")
    ledger.record_settlement(op_id="s", token_id="tokA", payout_per_share="1", resolution="x", now=NOW)
    buy(ledger, "op2", token="tokB", shares="10", price="0.5")
    state = ledger.state
    clone, deep = state.clone(), copy.deepcopy(state)
    assert clone == deep
    # Tous les champs mutables sont bien recopiés (garde-fou si on en ajoute un).
    for f in dataclasses.fields(state):
        value = getattr(state, f.name)
        if isinstance(value, (dict, set, list)):
            assert getattr(clone, f.name) is not value, f.name
    clone.positions["tokB"].shares += 5
    clone.op_ids.add("x")
    clone.realized_by_day["2000-01-01"] = Decimal("1")
    assert state.positions["tokB"].shares == Decimal("10")
    assert "x" not in state.op_ids and "2000-01-01" not in state.realized_by_day


def test_reward_of_a_finished_day_is_credited_once_and_survives_restart(ledger, paths):
    """AMELIORATION n°7 (21/10/2026) : récompense estimée d'une journée TERMINÉE créditée au solde,
    une fois par source et par jour, rejouée à l'identique au rechargement."""
    from datetime import timedelta
    day, later = NOW.date().isoformat(), NOW + timedelta(days=1)  # journal ouvert le jour NOW
    ledger.record_reward(day=day, amount="3.5", source="liquidite", method="estimation × 0,5",
                         details=[{"market_id": "m1", "montant": 7.0, "cagnotte": 50.0}], now=later)
    ledger.record_reward(day=day, amount="0.25", source="detention", now=later)
    assert ledger.state.cash == Decimal("1003.75") and ledger.state.realized_pnl == Decimal("3.75")
    assert ledger.state.summary()["recompenses_recues"] == "3.7500"
    with pytest.raises(DuplicateOperation):
        ledger.record_reward(day=day, amount="1", source="liquidite", now=later)
    reopened = Ledger.open(paths[0], KEY, paths[1])
    assert reopened.state.summary() == ledger.state.summary()
    assert reopened.state.rewards_by_source == {"liquidite": Decimal("3.5"), "detention": Decimal("0.25")}


@pytest.mark.parametrize("day_offset, amount, source", [
    (0, "1", "liquidite"),      # journée pas terminée
    (-1, "0", "liquidite"),     # montant nul
    (-1, "-2", "liquidite"),    # montant négatif
    (-1, "50.01", "liquidite"), # plus de 5 % du capital réalisé (1 000)
    (-1, "1", "cadeau"),        # source inconnue
    (-2, "1", "liquidite"),     # journée antérieure au capital actuel (journal ouvert le jour NOW)
])
def test_invalid_reward_is_refused_and_changes_nothing(ledger, paths, day_offset, amount, source):
    from datetime import timedelta
    size, cash = paths[0].stat().st_size, ledger.state.cash
    later = NOW + timedelta(days=1)
    with pytest.raises(InvalidEntry):
        ledger.record_reward(day=(later + timedelta(days=day_offset)).date().isoformat(), amount=amount,
                             source=source, now=later)
    assert ledger.state.cash == cash and paths[0].stat().st_size == size


def test_reward_with_forged_identifier_or_after_bankruptcy_is_refused(ledger):
    from datetime import timedelta
    from polymarket_agent.ledger import LedgerLocked, apply_entry
    later = NOW + timedelta(days=1)
    day = NOW.date().isoformat()
    with pytest.raises(InvalidEntry):  # un autre identifiant permettrait de créditer deux fois le même jour
        apply_entry(ledger.state.clone(), "REWARD", {"op_id": "REWARD-x", "day": day, "amount": "1",
                                                     "source": "liquidite"}, later)
    ledger.declare_bankruptcy("test", now=NOW)
    with pytest.raises(LedgerLocked):
        ledger.record_reward(day=day, amount="1", source="liquidite", now=later)
