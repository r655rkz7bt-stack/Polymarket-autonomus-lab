"""Marges des districts californiens (17/11/2026, piste n° 66, experiments/comptage_tardif.md) : vraies réponses de api.sos.ca.gov
(CA-26 au 14/11 17 h 16 et au 16/11 16 h 34, relevés `comptage_tardif/releves/`), libellés des marchés, loi de la marge finale,
collecteur, journal, scanner par liste d'identifiants et stratégie `marges_californie`."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from conftest import raw_market
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import marges_californie as mc
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import MargesCalifornie

UTC = timezone.utc
NOW = datetime(2026, 11, 17, 1, 0, tzinfo=UTC)
END = datetime(2026, 11, 3, 12, 0, tzinfo=UTC)     # date de fin Gamma : le jour du vote


def _api(heure, irwin, gallucci):
    return {"raceTitle": "U.S. House of Representatives District 26 - Districtwide Results",
            "Reporting": "100% (1,087 of 1,087) precincts reporting", "ReportingTime": heure,
            "candidates": [{"Name": "Jacqui Irwin", "Party": "Dem", "Votes": f"{irwin:,}", "Percent": "63.5", "incumbent": False},
                           {"Name": "Sam Gallucci", "Party": "Rep", "Votes": f"{gallucci:,}", "Percent": "36.5", "incumbent": False}]}


AVANT = _api("November 14, 2026, 5:16 p.m.", 164_433, 96_929)    # 261 362 voix, marge 25,83
APRES = _api("November 16, 2026, 4:34 p.m.", 178_048, 102_533)   # 280 581 voix, marge 26,91


class _Http:
    def __init__(self, page):
        self.page, self.calls = page, []

    def get_json(self, url, params=None, headers=None):
        self.calls.append(url)
        if url == mc.API.format(n=26):
            return self.page
        raise SourceUnavailable(f"{url} : HTTP 404")


def _market(mid, question, event="ev26"):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=END, question=question,
                                   events=[{"id": event, "title": "CA-26 House Election Margin of Victory"}]))


def test_questions_of_the_three_shapes():
    assert mc.question("Will a Democratic Party candidate win the 2026 CA-26 House election by 25%-30%?") == (26, "D", 25.0, 30.0)
    assert mc.question("Will a Democratic Party candidate win the 2026 CA-13 House election by 25% or more?") == (13, "D", 25.0, math.inf)
    assert mc.question("Will a Republican Party candidate win the 2026 CA-01 House election?") == (1, "R", 0.0, math.inf)
    assert mc.question("Will Person A win the 2026 CA-26 House election?") is None
    assert mc.question("Will a Democratic Party candidate win the 2026 TX-28 House election by 0%-5%?") is None


def test_read_the_official_count_and_the_margin_of_the_late_ballots():
    a, b = mc.lire(AVANT), mc.lire(APRES)
    assert b == {"heure": "November 16, 2026, 4:34 p.m.", "d": 178_048, "r": 102_533, "total": 280_581, "meme_parti": False,
                 "autre_en_tete": False, "ecart_api": 27.0}
    h = mc.journal([], [dict(a, district=26, lu="2026-11-16T11:01:00+00:00")])
    h = mc.journal(h, [dict(b, district=26, lu="2026-11-17T00:57:00+00:00")])
    assert mc.journal(h, [dict(b, district=26, lu="2026-11-17T01:57:00+00:00")]) == h   # même heure officielle : pas de nouvelle ligne
    m, ajout = mc.marge_tardive(h, 26)
    assert ajout == 19_219 and abs(m - 41.68) < 0.01   # les tardifs penchent D +41,7 contre 25,8 cumulés
    same = dict(APRES, candidates=[dict(c, Party="Dem") for c in APRES["candidates"]])
    assert mc.lire(same)["meme_parti"]


CA06 = {"raceTitle": "U.S. House of Representatives District 6 - Districtwide Results",   # vraie réponse du 17/11 (7 h 12 p.m.)
        "Reporting": "100% (309 of 309) precincts reporting", "ReportingTime": "November 16, 2026, 7:12 p.m.",
        "candidates": [{"Name": "Richard Pan", "Party": "Dem", "Votes": "158,804", "Percent": "58.9", "incumbent": False},
                       {"Name": "Kevin Kiley", "Party": "NPP", "Votes": "110,899", "Percent": "41.1", "incumbent": False}]}


def test_margin_is_against_the_second_candidate_even_without_party_17_11():
    """Enquête du 17/11 (6 h) : CA-06 oppose un démocrate à un candidat sans parti (NPP). `lire` prenait les voix du premier républicain
    (0) : marge 58,9 points au lieu de 17,76, et le fantôme a acheté « Democrat 25%+ » à 0,91 estimé 0,99 (marché 4166518)."""
    x = mc.lire(CA06)
    s0 = 100.0 * (x["d"] - x["r"]) / x["total"]
    assert abs(s0 - 17.76) < 0.01 and not x["meme_parti"]
    assert mc.chance(s0, s0, 25, math.inf) < 0.001       # « Democrat 25%+ » : presque impossible
    assert mc.chance(s0, s0, 15, 20) > 0.97              # la tranche courante est « Democrat 15-20% »
    # un sans-parti EN TÊTE : ni les tranches démocrates ni les républicaines ne peuvent gagner, pas de chance donnée
    tete = dict(CA06, candidates=[dict(CA06["candidates"][1], Votes="160,000"), CA06["candidates"][0]])
    assert mc.lire(tete)["autre_en_tete"]
    # journal de production écrit avec l'ancien calcul (r = 0) puis le nouveau : pas de « marge tardive » de −40 000 points
    vieux = {"district": 6, "heure": "November 16, 2026, 4:34 p.m.", "d": 158_100, "r": 0, "total": 269_703, "lu": "2026-11-17T00:57:00+00:00"}
    neuf = dict({k: x[k] for k in ("heure", "d", "r", "total")}, district=6, total=269_703 + 1_000, lu="2026-11-17T06:57:00+00:00")
    assert mc.marge_tardive([vieux, neuf], 6) is None


def test_law_of_the_final_margin_on_the_real_cases_of_17_11():
    assert mc.chance(26.91, 41.7, 25, 30) > 0.97          # CA-26 : vendue 0,89
    assert mc.chance(17.56, 17.56, 15, 20) > 0.97         # CA-3 : vendue 0,898
    assert 0.1 < mc.chance(24.93, 42.7, 20, 25) < 0.4     # CA-13 à 0,07 point de la borne, tardifs D +42,7 : sortira sans doute
    assert 0.5 < mc.chance(59.90, 59.90, 55, 60) < 0.8    # CA-15 à 0,10 point de la borne 60
    total = sum(mc.chance(26.91, 41.7, a, b) for a, b in ((-math.inf, 0), (1e-9, 25), (25, 30), (30, math.inf)))
    assert abs(total - 1) < 1e-9


def test_collect_attach_and_buy_the_current_bracket_only_when_sold_cheap(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    cfg = {"sources": {"marges_ca": {"enabled": True, "every_minutes": 60}}}
    first = collect(cfg, _Http(AVANT), db, [], NOW - timedelta(hours=14))
    assert first.status["marges_ca"].startswith("ok (1")
    collect(cfg, _Http(APRES), db, [], NOW)
    assert len(refs._load(db, "marges_ca:histo")[1]) == 2
    cur = _market("4166861", "Will a Democratic Party candidate win the 2026 CA-26 House election by 25%-30%?")
    up = _market("4166860", "Will a Democratic Party candidate win the 2026 CA-26 House election by 30%-35%?")
    rep = _market("4166867", "Will a Republican Party candidate win the 2026 CA-26 House election?")
    assert refs.attach_all([cur, up, rep], db, NOW)["marges_ca"] == 3
    assert cur.references["marges_ca"]["p"] > 0.97 and "+41.7 sur 19219" in cur.references["marges_ca"]["titre"]
    assert up.references["marges_ca"]["p"] < 0.02 and rep.references["marges_ca"]["p"] < 0.001
    s = _s(MargesCalifornie, min_net_edge=0.04, uncertainty=0.02, min_price=0.30, max_price=0.95, max_stale_hours=3,
           max_extra_ticks=1, max_candidates=400, max_proposals_per_cycle=4, max_per_event=1, mise_max_pari=0.04, kelly_fraction=1.0)
    assert s.candidates([cur, up, rep]) and len(s.candidates([cur, up, rep])) == 3

    def books(ask):
        b = _books(("4166861Y", "0.39", ask), ("4166861N", "0.02", "0.61"), ("4166860Y", "0.04", "0.93"), ("4166860N", "0.05", "0.97"),
                   ("4166867Y", "0.003", "0.87"), ("4166867N", "0.12", "0.997"))
        for x in b.values():
            x.fetched_at = NOW
        return b
    out = s.propose([cur, up, rep], books("0.89"), _state(tmp_path), LIMITS, "b1")   # le carnet réel du 17/11
    assert [p.token_id for p in out.proposals] == ["4166861Y"]
    assert s.propose([cur, up, rep], books("0.96"), _state(tmp_path), LIMITS, "b2").proposals == []   # au prix juste : rien


def test_scanner_reads_the_fixed_list_past_its_gamma_end_date(tmp_path):
    """Les 386 tranches ont une date de fin Gamma au 03/11 : sans `min_horizon_minutes` négatif, toutes « hors horizon »."""
    from test_market_scanner import CFG, FakeGamma, NOW as SNOW
    from polymarket_agent.market_scanner import scan
    liste = tmp_path / "marches.yaml"
    liste.write_text('marches:\n  - "4166861"\n  - "4166406"\n', encoding="utf-8")

    class IdGamma(FakeGamma):
        asked = []

        def markets_by_ids(self, ids, *, closed):
            IdGamma.asked.append(list(ids))
            return [raw_market(i, end=SNOW - timedelta(days=14), spread=0.49, liquidityNum=70, volume24hr=0) for i in ids]

    spec = {"fichier": str(liste), "min_horizon_minutes": -86400, "max_horizon_hours": 4400, "min_liquidity": 0, "min_volume_24h": 0,
            "max_spread": 1.0, "max_favorite_price": 0.9999}
    result = scan(IdGamma([raw_market("1")]), SNOW, dict(CFG, listes_marches={"marges_californie": spec}))
    by_id = {m.market_id: m for m in result.markets}
    assert IdGamma.asked == [["4166861", "4166406"]]
    assert by_id["4166861"].eligible and by_id["4166861"].extra_only and by_id["4166406"].eligible
    assert {"4166861", "4166406"}.isdisjoint(m.market_id for m in result.watchlist)


def test_repository_list_and_source_are_configured():
    import yaml
    from conftest import ROOT
    settings = yaml.safe_load((ROOT / "config" / "settings.yaml").read_text(encoding="utf-8"))
    spec = settings["scanner"]["listes_marches"]["marges_californie"]
    ids = yaml.safe_load((ROOT / spec["fichier"]).read_text(encoding="utf-8"))["marches"]
    assert len(ids) == 386 and "4166861" in ids and spec["min_horizon_minutes"] < 0
    assert settings["sources"]["marges_ca"]["enabled"]


def test_ca06_no_longer_gets_a_chance_for_democrat_25_plus(tmp_path):
    """Cas réel du 17/11 : avec la vraie réponse de CA-06, « Democrat 25%+ » reçoit ≈ 0 et « Democrat 15-20% » la tranche courante ;
    une ligne qui ne redonne pas l'écart des pourcentages officiels (ancien calcul) ne reçoit aucune chance."""
    class Http(_Http):
        def get_json(self, url, params=None, headers=None):
            if url == mc.API.format(n=6):
                return self.page
            raise SourceUnavailable(f"{url} : HTTP 404")
    db = Database(tmp_path / "db.sqlite")
    cfg = {"sources": {"marges_ca": {"enabled": True, "every_minutes": 60}}}
    collect(cfg, Http(CA06), db, [], NOW)
    plus = _market("4166518", "Will a Democratic Party candidate win the 2026 CA-06 House election by 25% or more?", "ev6")
    cour = _market("4166517", "Will a Democratic Party candidate win the 2026 CA-06 House election by 15%-20%?", "ev6")
    assert refs.attach_all([plus, cour], db, NOW)["marges_ca"] == 2
    assert plus.references["marges_ca"]["p"] < 0.001 and cour.references["marges_ca"]["p"] > 0.97
    faux = [dict(mc.lire(CA06), d=158_804, r=0, district=6, lu=NOW.isoformat())]   # ce que lisait l'ancien code
    db2 = Database(tmp_path / "db2.sqlite")
    refs._save(db2, "ref:marges_ca", faux, NOW)
    assert mc.attach_marges([_market("1", plus.question, "ev6")], db2, NOW) == 0
