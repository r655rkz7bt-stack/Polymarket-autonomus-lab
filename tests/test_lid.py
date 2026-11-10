"""Lids de la Maison-Blanche (10/11/2026, experiments/lid_agenda.md) : questions « full lid by 6:30 PM on <date> », lecture du calendrier
Roll Call Factbase (lignes réelles des 08-10/11/2026), cases de l'agenda, rattachement, collecteur et stratégie `lid_agenda`."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from conftest import raw_market
from test_sources import FakeHttp
from test_strategies_v3 import LIMITS, _books, _s, _state
from polymarket_agent import lid
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import LidAgenda

UTC = timezone.utc
NOW = datetime(2026, 11, 10, 14, 0, tzinfo=UTC)   # 9 h à New York (heure d'hiver)


def _row(date, time, typ, details, location="The White House"):
    return {"date": date, "time": time, "type": typ, "details": details, "location": location}


# Lignes réelles du calendrier Factbase (lues le 10/11/2026 à 21 h UTC).
REAL = [
    _row("2026-11-08", "14:51:00", "Pool Report Schedule", "White House Press Office: Lunch lid until 4:50 PM", "Mar-a-Lago"),
    _row("2026-11-08", "21:18:00", "Pool Report Schedule", "White House Press Office: Travel/Photo lid called"),
    _row("2026-11-09", "12:13:00", "Pool Report Schedule", "White House Press Office: Lunch lid until 1:15 PM"),
    _row("2026-11-09", "18:00:00", "Pool Report Schedule", "White House Press Office: Travel/Photo lid called"),
    _row("2026-11-10", "08:00:00", "President Schedule", "The President participates in Executive Time"),
    _row("2026-11-10", "11:00:00", "President Schedule", "The President participates in a Policy Meeting", "Oval Office"),
    _row("2026-11-10", "12:03:00", "Pool Report Schedule", "White House Press Office: Lunch lid until 1:00 PM"),
    _row("2026-11-10", "17:00:00", "President Schedule", "The President participates in a Policy Meeting", "Oval Office"),
]


def _market(mid, question):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", question=question, end=NOW + timedelta(days=1)))


def test_parse_question_and_deadline_in_eastern_time():
    q = lid.parse_question("Will the White House call a full lid by 6:30 PM on November 13?")
    assert q == {"heure": "18:30:00", "mois": 11, "jour": 13}
    assert lid.parse_question("Will the White House call a full lid by 6:30PM on March 13?")["heure"] == "18:30:00"   # écriture de mars
    assert lid.parse_question("Will the White House call a full lid by 11:00 AM on July 4")["heure"] == "11:00:00"
    assert lid.parse_question("Will Tesla say \"Lidar\" during earnings call?") is None
    day = lid.target_day(q, NOW)
    assert day.isoformat() == "2026-11-13" and lid.deadline(q, day) == datetime(2026, 11, 13, 23, 30, tzinfo=UTC)   # EST = UTC-5


def test_first_lid_skips_lunch_lids_after_midnight_lids_and_foreign_times():
    rows = REAL + [_row("2026-11-11", "01:14:00", "Pool Report Schedule", "White House Press Office: Travel/Photo lid called"),
                   _row("2026-11-11", "15:00:00", "Pool Report Schedule", "White House Press Office: Travel/Photo lid called [4:00 PM Local]"),
                   _row("2026-11-11", "16:00:00", "Pool Report Schedule", "White House Press Office: Travel/Photo lid called for November 12, 2026")]
    assert lid.first_lid(rows, "2026-11-09") == "18:00:00" and lid.first_lid(rows, "2026-11-08") == "21:18:00"
    assert lid.first_lid(rows, "2026-11-10") is None and lid.first_lid(rows, "2026-11-11") is None


def test_assess_reads_the_two_stable_cases_and_stays_silent_otherwise():
    assert lid.assess(REAL, "2026-11-09", "18:30:00") == (lid.P_DEJA_APPELE, "lid déjà noté à 18:00")
    p, case = lid.assess(REAL, "2026-11-08", "18:30:00")
    assert p == 1 - lid.P_DEJA_APPELE and "après" in case
    # 10/11 : pas de voyage mais dernier rendez-vous à 17 h : case instable, pas d'avis
    assert lid.assess(REAL, "2026-11-10", "18:30:00")[0] is None
    calm = [_row("2026-11-12", "10:00:00", "President Schedule", "The President receives his Intelligence Briefing", "Oval Office"),
            _row("2026-11-12", "15:30:00", "President Schedule", "The President participates in Signing Time", "Oval Office")]
    assert lid.assess(calm, "2026-11-12", "18:30:00")[0] == lid.P_CALME
    busy = [_row("2026-11-13", "15:00:00", "President Schedule", "The President departs the White House en route to Joint Base Andrews"),
            _row("2026-11-13", "19:00:00", "President Schedule", "The President arrives Palm Beach International Airport", "West Palm Beach, FL")]
    assert lid.assess(busy, "2026-11-13", "18:30:00")[0] == lid.P_CHARGE
    assert lid.assess(REAL, "2026-11-14", "18:30:00") == (None, "agenda du jour pas encore publié")


def test_keep_rows_keeps_the_days_around_today_only():
    data = REAL + [_row("2025-03-01", "18:00:00", "Pool Report Schedule", "White House Press Office: Travel/Photo lid called"), "bruit", {"date": None}]
    kept = lid.keep_rows(data, NOW)
    assert {r["date"] for r in kept} == {"2026-11-09", "2026-11-10"}
    try:
        lid.fetch_lid(FakeHttp({lid.URL: []}), NOW)
    except ValueError:
        pass
    else:
        raise AssertionError("un calendrier vide doit lever une erreur (le cycle continue, la stratégie s'abstient)")


def test_attach_and_collector(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    ms = [_market("a", "Will the White House call a full lid by 6:30 PM on November 9?"),
          _market("b", "Will the White House call a full lid by 6:30 PM on November 10?"), _market("c", "Will it rain?")]
    assert lid.attach_lid(ms, db, NOW) == 0
    result = collect({"sources": {"factbase": {"enabled": True, "every_minutes": 15}}}, None, db, [], NOW, {"factbase": lambda c: REAL})
    assert result.status["factbase"] == f"ok ({len(REAL)} prix relevés)"
    assert lid.attach_lid(ms, db, NOW) == 2
    assert ms[0].references["lid"]["p"] == lid.P_DEJA_APPELE and ms[1].references["lid"]["p"] is None
    assert ms[1].references["lid"]["h"] == 9.5 and "lid" not in (ms[2].references or {})


def test_strategy_buys_the_side_the_agenda_favours_and_abstains_otherwise(tmp_path):
    s = _s(LidAgenda, min_net_edge=0.05, uncertainty=0.04, min_price=0.05, max_price=0.92, max_stale_hours=1, min_hours=0.5, max_hours=30,
           max_extra_ticks=1, max_proposals_per_cycle=5, kelly_fraction=0.5)
    now = datetime(2026, 10, 14, 12, 0, tzinfo=UTC)   # NOW des carnets de test

    def mk(mid, p, h, yes_mid, seen=now):
        m = _market(mid, "Will the White House call a full lid by 6:30 PM on November 13?")
        m.token_ids = [f"{mid}Y", f"{mid}N"]
        m.references = {"lid": {"p": p, "cas": "test", "h": h, "vu_le": seen.isoformat()}}
        return m, _books((f"{mid}Y", f"{yes_mid - 0.01:.3f}", f"{yes_mid + 0.01:.3f}"), (f"{mid}N", f"{1 - yes_mid - 0.01:.3f}", f"{1 - yes_mid + 0.01:.3f}"))
    cases = [mk("calme", 0.86, 10, 0.65), mk("charge", 0.14, 10, 0.40), mk("juste", 0.86, 10, 0.80), mk("muet", None, 10, 0.50),
             mk("tot", 0.86, 40, 0.50), mk("tard", 0.86, 0.2, 0.50), mk("vieux", 0.86, 10, 0.50, seen=now - timedelta(hours=3))]
    ms, books = [c[0] for c in cases], {}
    for _, b in cases:
        books.update(b)
        for book in b.values():
            book.fetched_at = now
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert sorted((p.market_id, p.outcome) for p in out.proposals) == [("calme", "Yes"), ("charge", "No")]
    assert out.proposals[0].strategy_id == "lid_agenda" and out.abstentions
