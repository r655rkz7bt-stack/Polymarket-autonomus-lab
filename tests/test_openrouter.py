"""OpenRouter : jetons de la semaine lus à la source (13/11/2026, piste n° 50, experiments/openrouter.md)."""
from __future__ import annotations

import json
import math
from datetime import date, datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import openrouter as orr
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import OpenrouterSemaine

UTC = timezone.utc
NOW = datetime(2026, 11, 13, 6, 10, tzinfo=UTC)
RAW = json.loads((Path(__file__).parent / "data" / "openrouter_2026-11-13.json").read_text())
FIN = datetime(2026, 11, 16, 4, 59, tzinfo=UTC)


def _http():
    return Http({orr.CHART: RAW["chart"], orr.WEEK: RAW["week"], orr.DAY: RAW["day"]})


def _market(mid, question):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=FIN, question=question,
                                   events=[{"id": "1308544", "title": "OpenRouter token usage week of November 9?"}]))


def test_question_brackets_and_week():
    assert orr.question("Will OpenRouter process between 200T and 210T tokens the week of November 9?", FIN) == (200.0, 210.0, date(2026, 11, 9))
    assert orr.question("Will OpenRouter process less than 200T tokens the week of November 9?", FIN) == (0.0, 200.0, date(2026, 11, 9))
    assert orr.question("Will OpenRouter process 230T or more tokens the week of November 9?", FIN) == (230.0, math.inf, date(2026, 11, 9))
    assert orr.question("Will Qwen have the highest OpenRouter market share in November?", FIN) is None


def test_projection_of_13_11_uses_last_weekend_shape():
    """Cas réel du 13/11 à 06 h UTC : lundi-jeudi 134,43 T, 7 derniers jours (6-12/11) 209,67, semaine du 2/11 209,52 :
    fin de semaine précédente 75,24, début 134,28 → 209,75 T (le marché payait 210-220 à 0,59 et 200-210 à 0,33)."""
    row = orr.lire(RAW["chart"], RAW["week"], RAW["day"], NOW)[0]
    assert row["jour"][0] == "2026-11-12" and row["semaines"][-1][0] == "2026-11-09"
    lundi, total, k = orr.projection(row)
    assert lundi == "2026-11-09" and k == 4 and 209.5 < total < 210.0
    p_bas, p_haut = orr.chance(total, k, 200, 210), orr.chance(total, k, 210, 220)
    assert 0.4 < p_bas < 0.6 and 0.4 < p_haut < 0.6
    assert orr.chance(total, k, 0, 200) + orr.chance(total, k, 200, 210) + orr.chance(total, k, 210, 220) + \
        orr.chance(total, k, 220, 230) + orr.chance(total, k, 230, math.inf) > 0.999
    # semaine finie : la tranche est connue
    assert orr.chance(209.75, 7, 200, 210) == 1.0 and orr.chance(210.0, 7, 200, 210) == 0.0
    # vues incohérentes (le jour lu n'est pas la fin des 7 jours) : pas de projection
    assert orr.projection(dict(row, sept_jours=["2026-11-11", row["sept_jours"][1]])) is None


def test_collect_attach_and_buy_cheap_lower_bracket(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    result = collect({"sources": {"openrouter": {"enabled": True, "every_minutes": 60}}}, _http(), db, [], NOW)
    assert result.status["openrouter"].startswith("ok (1")
    histo = refs._load(db, "openrouter:histo")[1]
    assert histo[-1]["jour"] == "2026-11-12" and histo[-1]["partiel"] == 134.4318
    bas = _market("6638953", "Will OpenRouter process between 200T and 210T tokens the week of November 9?")
    suivante = parse_market(raw_market("6942350", yes_token="aY", no_token="aN", end=datetime(2026, 11, 23, 4, 59, tzinfo=UTC),
                                       question="Will OpenRouter process between 210T and 220T tokens the week of November 16?"))
    assert refs.attach_all([bas, suivante], db, NOW)["openrouter"] == 1
    assert "openrouter" not in (suivante.references or {})   # semaine pas commencée : rien à projeter
    s = _s(OpenrouterSemaine, min_net_edge=0.06, uncertainty=0.04, min_price=0.08, max_price=0.92, max_stale_hours=3,
           max_extra_ticks=1, max_proposals_per_cycle=2, max_per_event=2, mise_max_pari=0.04, kelly_fraction=1.0, max_candidates=20)
    # carnet réel du 13/11 : 200-210 OUI 0,26 / 0,39 → pas assez d'écart (≈ 0,48 − 0,04 − 0,39 − frais) ; un vendeur à 0,30 → achat
    b = _books(("6638953Y", "0.26", "0.39"), ("6638953N", "0.61", "0.74"))
    for x in b.values():
        x.fetched_at = NOW
    assert s.propose([bas], b, _state(tmp_path), LIMITS, "b1").proposals == []
    b = _books(("6638953Y", "0.26", "0.30"), ("6638953N", "0.70", "0.74"))
    for x in b.values():
        x.fetched_at = NOW
    out = s.propose([bas], b, _state(tmp_path), LIMITS, "b2")
    assert [x.token_id for x in out.proposals] == ["6638953Y"]
