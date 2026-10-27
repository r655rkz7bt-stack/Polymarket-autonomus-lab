"""App Store (27/10/2026, experiments/appstore_direct.md) : lecture des classements Apple, questions « #1 Free / Paid App … on <date> », heure du règlement
(12 h à New York), rattachement aux marchés, journal du classement, collecteur et stratégie `classement_appstore`."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from conftest import raw_market
from test_sources import FakeHttp
from test_strategies_v3 import LIMITS, _books, _s, _state
from polymarket_agent import appstore as ap
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources import appstore as src
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import ClassementAppStore

UTC = timezone.utc
NOW = datetime(2026, 10, 30, 12, 0, tzinfo=UTC)          # 8 h à New York (heure d'été) : midi est dans 4 h
FEED = {"feed": {"updated": "Tue, 27 Oct 2026 16:21:16 +0000", "results": [
    {"id": "1", "name": "TikTok Pro - Events"}, {"id": "2", "name": "Vinted: Pre-loved marketplace"}, {"id": "3", "name": ""}, {"id": "4", "name": "ChatGPT"}]}}


def _rows():
    return [{"kind": "free", "rang": 1, "id": "1", "nom": "TikTok Pro - Events"}, {"kind": "free", "rang": 2, "id": "2", "nom": "Vinted: Pre-loved marketplace"},
            {"kind": "paid", "rang": 1, "id": "9", "nom": "Minecraft: Play with Friends!"}]


def _market(mid, question):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", question=question, end=NOW + timedelta(days=1)))


def test_parse_chart_keeps_the_order_and_skips_nameless_rows():
    rows = src.parse_chart(FEED, "free")
    assert [(r["rang"], r["nom"]) for r in rows] == [(1, "TikTok Pro - Events"), (2, "Vinted: Pre-loved marketplace"), (3, "ChatGPT")]
    assert src.parse_chart(None, "free") == [] and src.parse_chart({"feed": {}}, "paid") == []


def test_fetch_appstore_reads_free_and_paid_and_refuses_an_empty_answer():
    http = FakeHttp({src.URL.format(kind="top-free", n=10): FEED, src.URL.format(kind="top-paid", n=10): FEED})
    rows = src.fetch_appstore(http, NOW)
    assert {r["kind"] for r in rows} == {"free", "paid"} and len(rows) == 6
    empty = FakeHttp({src.URL.format(kind="top-free", n=10): {}, src.URL.format(kind="top-paid", n=10): {}})
    try:
        src.fetch_appstore(empty, NOW)
    except ValueError:
        pass
    else:
        raise AssertionError("un classement vide doit lever une erreur (le cycle continue, la stratégie s'abstient)")


def test_parse_question_reads_app_kind_and_date():
    q = "Will Vinted: Pre-loved marketplace be #1 Free App in the US Apple App Store on October 30?"
    assert ap.parse_question(q) == {"app": "Vinted: Pre-loved marketplace", "kind": "free", "mois": 10, "jour": 30}
    assert ap.parse_question("Will Shadowrocket be #1 Paid App in the US Apple App Store on November 2?")["kind"] == "paid"
    assert ap.parse_question("Will another app be #1 Free App in the US Apple App Store on October 30?")["app"] == "another app"
    assert ap.parse_question("Will ChatGPT be #1 Free App in the US Apple App Store on Octobre 30?") is None
    assert ap.parse_question("Will it rain?") is None


def test_noon_eastern_follows_daylight_saving_time():
    assert ap.noon_eastern({"mois": 10, "jour": 30}, NOW) == datetime(2026, 10, 30, 16, 0, tzinfo=UTC)      # EDT = UTC-4
    assert ap.noon_eastern({"mois": 11, "jour": 5}, NOW) == datetime(2026, 11, 5, 17, 0, tzinfo=UTC)        # EST = UTC-5 (changement le 01/11)
    assert ap.noon_eastern({"mois": 2, "jour": 30}, NOW) is None                                             # date impossible
    assert ap.noon_eastern({"mois": 1, "jour": 2}, NOW) == datetime(2027, 1, 2, 17, 0, tzinfo=UTC)          # l'année suivante


def test_stay_chance_is_only_given_in_the_last_six_hours():
    assert ap.rester_n1(0.5) == 0.95 and ap.rester_n1(2) == 0.90 and ap.rester_n1(5) == 0.85
    assert ap.rester_n1(6.5) == 0.0 and ap.rester_n1(-1) == 0.0


def test_attach_gives_the_rank_of_each_app_and_the_chance_only_to_the_number_one(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    ms = [_market("a", "Will TikTok Pro - Events be #1 Free App in the US Apple App Store on October 30?"),
          _market("b", "Will Vinted: Pre-loved marketplace be #1 Free App in the US Apple App Store on October 30?"),
          _market("c", "Will Minecraft: Play with Friends! be #1 Paid App in the US Apple App Store on October 30?"),
          _market("d", "Will ChatGPT be #1 Free App in the US Apple App Store on October 30?"),
          _market("e", "Will it rain?")]
    assert ap.attach_appstore(ms, db, NOW) == 0                                       # pas de relevé : rien
    refs._save(db, "ref:appstore", _rows(), NOW)
    assert ap.attach_appstore(ms, db, NOW) == 4
    ref = lambda m: m.references["appstore"]
    assert (ref(ms[0])["rang"], ref(ms[0])["p"], ref(ms[0])["h"]) == (1, 0.85, 4.0)
    assert ref(ms[1])["rang"] == 2 and ref(ms[1])["p"] is None and ref(ms[1])["n1"] == "TikTok Pro - Events"
    assert ref(ms[2])["rang"] == 1 and ref(ms[3])["rang"] is None
    assert "appstore" not in (ms[4].references or {})


def test_history_is_written_every_thirty_minutes_and_kept_three_weeks(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    assert ap.record_history(db, _rows(), NOW) is True
    assert ap.record_history(db, _rows(), NOW + timedelta(minutes=10)) is False
    assert ap.record_history(db, _rows(), NOW + timedelta(minutes=31)) is True
    assert ap.record_history(db, _rows(), NOW + timedelta(days=22)) is True
    histo = json.loads(db.get_value(ap.HISTORY_KEY))
    assert len(histo) == 1 and histo[0]["free"][0] == "TikTok Pro - Events" and histo[0]["paid"] == ["Minecraft: Play with Friends!"]


def test_collector_saves_the_chart_and_survives_an_outage(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    cfg = {"sources": {"appstore": {"enabled": True, "every_minutes": 10, "n": 10}}}
    result = collect(cfg, None, db, [], NOW, {"appstore": lambda c: _rows()})
    assert result.status["appstore"] == "ok (3 prix relevés)"
    assert refs._load(db, "ref:appstore")[1] == _rows()
    http = FakeHttp({}, down=(src.URL.format(kind="top-free", n=10),))
    down = collect(cfg, None, db, [], NOW + timedelta(minutes=11), {"appstore": lambda c: src.fetch_appstore(http, NOW)})
    assert down.status["appstore"].startswith("indisponible") and refs._load(db, "ref:appstore")[1] == _rows()


def test_strategy_buys_only_the_number_one_in_the_last_hours_and_below_its_chance(tmp_path):
    s = _s(ClassementAppStore, min_net_edge=0.04, uncertainty=0.02, min_price=0.30, max_price=0.90, max_stale_hours=0.5, min_hours=0.25,
           max_extra_ticks=1, max_proposals_per_cycle=3, kelly_fraction=1)
    now = datetime(2026, 10, 14, 12, 0, tzinfo=UTC)   # NOW des carnets de test

    def mk(mid, rang, p, h, yes_mid, seen=now):
        m = _market(mid, "Will TikTok Pro - Events be #1 Free App in the US Apple App Store on October 30?")
        m.token_ids = [f"{mid}Y", f"{mid}N"]
        m.references = {"appstore": {"rang": rang, "n1": "TikTok Pro - Events", "h": h, "p": p, "vu_le": seen.isoformat()}}
        return m, _books((f"{mid}Y", f"{yes_mid - 0.01:.3f}", f"{yes_mid + 0.01:.3f}"), (f"{mid}N", f"{1 - yes_mid - 0.01:.3f}", f"{1 - yes_mid + 0.01:.3f}"))
    cases = [mk("bon", 1, 0.90, 2.0, 0.60), mk("cher", 1, 0.90, 2.0, 0.89), mk("second", 2, None, 2.0, 0.40), mk("loin", 1, 0.0, 9.0, 0.60),
             mk("fini", 1, 0.95, 0.1, 0.60), mk("vieux", 1, 0.90, 2.0, 0.60, seen=now - timedelta(hours=2)), mk("billet", 1, 0.90, 2.0, 0.20)]
    ms, books = [c[0] for c in cases], {}
    for _, b in cases:
        books.update(b)
        for book in b.values():
            book.fetched_at = now
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert [(p.market_id, p.outcome) for p in out.proposals] == [("bon", "Yes")]
    assert out.proposals[0].strategy_id == "classement_appstore" and out.abstentions
    assert {m.market_id for m in s.candidates(ms)} == {c[0].market_id for c in cases}
