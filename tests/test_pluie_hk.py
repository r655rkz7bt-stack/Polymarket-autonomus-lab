"""Pluie du mois à Hong Kong (14/11/2026, piste n° 32 suite, experiments/precipitations.md) : Daily Extract, bulletin RYES, pluie de
l'heure à la station de l'Observatoire et ensemble ECMWF réels du 14/11/2026 vers 05 h 50 UTC ; tranches, pluie du jour heure par
heure, chance, collecteur, journal et stratégie `pluie_hk`."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import pluie_hk as ph
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import PluieHk

UTC = timezone.utc
NOW = datetime(2026, 11, 14, 5, 50, tzinfo=UTC)          # 13 h 50 à Hong Kong
RAW = json.loads((Path(__file__).parent / "data" / "pluie_hk_2026-11-14.json").read_text())
BINS = [(0, 5), (5, 10), (10, 25), (25, 35), (35, 60), (60, 95), (95, float("inf"))]


def _extract_days(payload) -> dict[int, str]:
    """Jours du Daily Extract enregistré le 14/11 (jour → mm affichés) : sert à rejouer les bulletins RYES des mêmes jours."""
    return {int(r[0]): str(r[-1]) for r in payload["stn"]["data"][0]["dayData"] if r and str(r[0]).strip().isdigit()}


class _Http(Http):
    appels: list

    def get_json(self, url, params=None, headers=None):
        self.appels = getattr(self, "appels", []) + [(url, dict(params or {}))]
        assert "/cis/" not in url, "page interdite aux robots (www.weather.gov.hk/robots.txt : Disallow: /cis/)"
        if url == ph.OPENDATA:
            d = int(params["date"][-2:])
            if d == 13 and getattr(self, "pas_encore", False):
                from polymarket_agent.http_client import SourceUnavailable
                raise SourceUnavailable("réponse non JSON")   # bulletin de la veille pas encore publié
            jours = _extract_days(RAW["extract"])
            return RAW["ryes"] if d == 13 else ({"HKOReadingsRainfall": jours[d]} if d in jours else {})
        if url == ph.HORAIRE:
            return RAW["heure"]
        return RAW["ens"]


def _heures(nuit_mm: float):
    """Toutes les heures du 14/11 jusqu'à 13 h 45 (HKT), la pluie de la nuit répartie de 01 h à 06 h."""
    return [[f"2026-11-14T{h:02d}:45:00+08:00", nuit_mm / 6 if 1 <= h <= 6 else 0.0] for h in range(14)]


def _market(mid, question):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2027, 2, 8, 4, 59, tzinfo=UTC),
                                   question=question, description="Hong Kong Observatory Daily Extract",
                                   events=[{"id": "e1283556", "title": "Precipitation in Hong Kong in November?"}]))


def test_question_brackets():
    assert ph.question("Will Hong Kong have less than 5mm of precipitation in November?") == (0.0, 5.0, 11)
    assert ph.question("Will Hong Kong have between 35-60mm of precipitation in November?") == (35.0, 60.0, 11)
    assert ph.question("Will Hong Kong have 95mm or more of precipitation in November?")[::2] == (95.0, 11)
    assert ph.question("Will Hong Kong have between 20-40mm of precipitation in October?") == (20.0, 40.0, 10)
    assert ph.question("Will NYC have between 2-3 inches of precipitation in November?") is None


def test_real_14_11_days_from_ryes_bulletins_only():
    """Jours finis lus jour par jour au bulletin RYES (portail de données ouvertes) : 3,2 mm du 1er au 12/11, 7,9 mm le 13/11 ;
    jamais la page `/cis/` interdite aux robots (enquête du 14/11 après-midi)."""
    http = _Http({})
    r = ph.fetch_pluie_hk(http, NOW)[0]
    assert r["mois"] == "2026-11" and abs(sum(r["jours"][str(d)] for d in range(1, 13)) - 3.2) < 1e-9 and r["jours"]["13"] == 7.9
    assert r["heure"] == ["2026-11-14T13:45:00+08:00", 0.0] and len(r["ens"]["membres"]) == 51
    assert sum(u == ph.OPENDATA for u, _ in http.appels) == 13


def test_yesterday_bulletin_not_yet_published_does_not_break_the_source():
    http = _Http({})
    http.pas_encore = True
    r = ph.fetch_pluie_hk(http, NOW)[0]
    assert "13" not in r["jours"] and len(r["jours"]) == 12


def test_trace_in_lower_case_from_ryes():
    assert ph._mm("trace") == 0.0 and ph._mm("Trace") == 0.0 and ph._mm("7.9") == 7.9


def test_known_days_are_not_asked_again():
    http = _Http({})
    connus = {str(d): 0.0 for d in range(1, 13)}
    r = ph.fetch_pluie_hk(http, NOW, connus)[0]
    assert [p["date"] for u, p in http.appels if u == ph.OPENDATA] == ["20261113"] and r["jours"]["13"] == 7.9


def test_no_chance_without_every_hour_of_the_day():
    r = ph.fetch_pluie_hk(_Http({}), NOW)[0]
    assert ph.pluie_du_jour([r["heure"]], NOW.astimezone(ph.HKT).date(), NOW) is None      # une seule heure relevée
    assert ph.chance(r, [r["heure"]], NOW, 0, 5, 11) is None
    assert ph.pluie_du_jour(_heures(30), NOW.astimezone(ph.HKT).date(), NOW) == 30
    assert ph.chance(r, _heures(0), NOW, 0, 5, 10) is None                                  # pas le mois en cours


def test_chances_follow_the_rain_already_fallen():
    r = ph.fetch_pluie_hk(_Http({}), NOW)[0]
    for nuit in (0, 25, 60):
        p = [ph.chance(r, _heures(nuit), NOW, lo, hi, 11) for lo, hi in BINS]
        assert abs(sum(p) - 1) < 1e-9 and p[0] == 0.0 and p[1] == 0.0      # 11,1 mm déjà tombés au 13/11
    sec = [ph.chance(r, _heures(0), NOW, lo, hi, 11) for lo, hi in BINS]
    orage = [ph.chance(r, _heures(60), NOW, lo, hi, 11) for lo, hi in BINS]
    assert sec[2] > 0.3 and orage[2] == 0.0 and orage[4] == 0.0 and orage[6] > 0.3
    # valeur pile sur une borne → tranche du dessus
    pile = [["2026-11-14T00:45:00+08:00", 0.0]] + [[f"2026-11-14T{h:02d}:45:00+08:00", 0.0] for h in range(1, 14)]
    pile[1][1] = 95 - 11.1
    assert ph.chance(r, pile, NOW, 60, 95, 11) == 0.0


def test_collect_journal_attach_and_buy_a_cheap_bracket(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    result = collect({"sources": {"pluie_hk": {"enabled": True, "every_minutes": 20}}}, _Http({}), db, [], NOW)
    assert result.status["pluie_hk"].startswith("ok (1")
    assert refs._load(db, "pluie_hk:heures")[1] == [["2026-11-14T13:45:00+08:00", 0.0]]
    assert ph.journal(_heures(0)[:3], [{"heure": ["2026-11-14T01:45:00+08:00", 4.0]}])[1] == ["2026-11-14T01:45:00+08:00", 4.0]
    b25 = _market("6422680", "Will Hong Kong have between 25-35mm of precipitation in November?")
    rhin = _market("6433563", "Will the Rhine River return to normal levels before November 15, 2026?")
    # une seule heure du jour relevée : aucune chance, aucune référence
    assert refs.attach_all([b25, rhin], db, NOW)["pluie_hk"] == 0
    refs._save(db, "pluie_hk:heures", _heures(10), NOW)
    assert refs.attach_all([b25, rhin], db, NOW)["pluie_hk"] == 1 and "pluie_hk" not in (rhin.references or {})
    p = b25.references["pluie_hk"]["p"]
    assert 0.1 < p < 0.5
    s = _s(PluieHk, min_net_edge=0.08, uncertainty=0.05, min_price=0.05, max_price=0.95, max_stale_hours=1.5, max_extra_ticks=1,
           max_proposals_per_cycle=2, max_per_event=2, mise_max_pari=0.04, kelly_fraction=1.0, max_candidates=20)
    juste = f"{p:.3f}"
    b = _books(("6422680Y", juste, f"{min(p + 0.01, 0.99):.3f}"), ("6422680N", f"{1 - p - 0.01:.3f}", f"{1 - p:.3f}"))
    for x in b.values():
        x.fetched_at = NOW
    assert s.propose([b25], b, _state(tmp_path), LIMITS, "b1").proposals == []
    b = _books(("6422680Y", "0.04", "0.05"), ("6422680N", "0.95", "0.96"))
    for x in b.values():
        x.fetched_at = NOW
    out = s.propose([b25], b, _state(tmp_path), LIMITS, "b2")
    assert [x.token_id for x in out.proposals] == ["6422680Y"]
