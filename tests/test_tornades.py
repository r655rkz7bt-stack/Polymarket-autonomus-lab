"""Tornades du mois (11/11/2026, experiments/tornades.md) : lecture des marchés réels, loi du compte, source SPC/NCEI, stratégie."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from conftest import raw_market
from polymarket_agent import references as refs
from polymarket_agent import tornades as tn
from polymarket_agent.persistence import Database
from polymarket_agent.sources import tornades as src
from polymarket_agent.sources.polymarket_gamma import parse_market

UTC = timezone.utc
NOW = datetime(2026, 11, 11, 14, 0, tzinfo=UTC)


def _m(mid, question, end=datetime(2026, 12, 9, 16, tzinfo=UTC)):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", question=question, end=end,
                                   events=[{"id": "t11", "title": "US Tornadoes in November 2026"}]))


def test_reads_both_real_wordings_of_the_markets():
    q1 = "Will there be between 10 and 24 tornadoes in the US in November 2026?"
    q2 = "Will fewer than 40 tornadoes occur in the United States in August 2026?"
    q3 = "Will 40 to 59 tornadoes occur in the United States in August 2026?"
    assert tn.target_month(q1, None) == (2026, 11) and tn.bracket(q1) == (10, 24)
    assert tn.target_month(q2, None) == (2026, 8) and tn.bracket(q2) == (0, 39)
    assert tn.bracket(q3) == (40, 59)
    assert tn.bracket("Will there be 60 or more tornadoes in the US in November 2026?") == (60, 10 ** 6)
    assert tn.bracket("Will there be under 10 tornadoes in the US in November 2026?") == (0, 9)
    assert tn.target_month("Will it rain in Paris?", None) is None


def test_published_ncei_value_decides_and_month_so_far_plus_climatology_otherwise():
    # octobre 2026 : NCEI 53 publiée → la tranche 35-59 est sûre
    assert tn.p_bracket({}, {"2026-10": 53}, 2026, 10, (35, 59), NOW)[0] == 1.0
    assert tn.p_bracket({}, {"2026-10": 53}, 2026, 10, (60, 89), NOW)[0] == 0.0
    # novembre 2026 : 7 tornades du 1er au 10 (à 14 h UTC le 11, le jour SPC du 10 — 12 h UTC le 10 → 12 h UTC le 11 — est complet)
    counts = {date(2026, 11, d).isoformat(): (7 if d == 1 else 0) for d in range(1, 11)}
    p_small, so_far = tn.p_bracket(counts, {}, 2026, 11, (0, 9), NOW)
    p_mid, _ = tn.p_bracket(counts, {}, 2026, 11, (10, 24), NOW)
    p_big, _ = tn.p_bracket(counts, {}, 2026, 11, (60, 10 ** 6), NOW)
    assert so_far == 7 and 0.05 < p_small < 0.3 and 0.3 < p_mid < 0.6 and 0.05 < p_big < 0.3
    del counts["2026-11-05"]
    assert tn.p_bracket(counts, {}, 2026, 11, (0, 9), NOW) is None        # un jour manque au relevé : pas d'avis


def test_finished_month_waiting_for_ncei_keeps_room_for_late_reports():
    counts = {date(2026, 10, d).isoformat(): (2 if d <= 27 else 0) for d in range(1, 32)}   # 54 au SPC (octobre 2026)
    p, so_far = tn.p_bracket(counts, {}, 2026, 10, (35, 59), datetime(2026, 11, 3, 14, tzinfo=UTC))
    assert so_far == 54 and 0.5 < p < 1.0                                  # 54 × 1,08 = 58 : toujours dans 35-59
    assert tn.p_bracket(counts, {}, 2026, 10, (60, 89), datetime(2026, 11, 3, 14, tzinfo=UTC))[0] < 0.2


class _Http:
    def __init__(self, text, ncei):
        self.text, self.ncei, self.urls = text, ncei, []

    def get_text(self, url, params=None, headers=None):
        self.urls.append(url)
        return self.text

    def get_json(self, url, params=None, headers=None):
        self.urls.append(url)
        return self.ncei


def test_source_counts_filtered_reports_reads_ncei_and_keeps_the_first_count():
    csv = "Time,F_Scale,Location,County,State,Lat,Lon,Comments\n2010,UNK,3 N X,Y,KY,37.1,-88.1,(PAH)\n2015,UNK,2 S Z,W,TN,36,-89,(MEG)\n"
    http = _Http(csv, {"tornadoes": {"202610": "53*", "202611": None}})
    rows = src.fetch_tornades(http, NOW)
    days = [r for r in rows if "n" in r]
    assert days[0]["id"] == "2026-10-01" and days[-1]["id"] == "2026-11-10" and all(r["n"] == 2 for r in days)   # le 11 : octobre encore ouvert
    assert {"id": "ncei:2026-10", "ncei": 53} in rows and not any(r["id"] == "ncei:2026-11" for r in rows)
    assert "250925_rpts" not in " ".join(http.urls) and "261110_rpts_filtered_torn.csv" in " ".join(http.urls)
    first = src.keep_first([], days[-1:], NOW)
    later = src.keep_first(first, [dict(days[-1], n=5)], NOW + timedelta(hours=3))
    assert later[0]["n"] == 5 and later[0]["n0"] == 2 and later[0]["vu"] == "2026-11-11T14:00:00+00:00"


def test_attach_and_strategy_see_the_november_markets(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    rows = [{"id": date(2026, 11, d).isoformat(), "n": (7 if d == 1 else 0)} for d in range(1, 11)]
    refs._save(db, "ref:tornades", rows, NOW)
    ms = [_m("a", "Will there be under 10 tornadoes in the US in November 2026?"),
          _m("b", "Will there be between 10 and 24 tornadoes in the US in November 2026?"),
          _m("c", "Will there be 60 or more tornadoes in the US in November 2026?")]
    assert tn.attach_tornades(ms, db, NOW) == 3
    assert abs(sum(m.references["tornades"]["p"] for m in ms) - 1) < 0.5 and "7 déjà comptées" in ms[1].references["tornades"]["titre"]
