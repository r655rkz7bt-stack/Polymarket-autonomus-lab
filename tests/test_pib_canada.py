"""PIB mensuel canadien : estimation anticipée contre tranches de l'officiel (12/11/2026, experiments/pib_canada.md, piste n° 36).
Données : page réelle « Gross domestic product » du Quotidien lue le 12/11/2026 et communiqué du 30/10/2026 (« Advance information
indicates that real GDP decreased 0.1% in September »)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import pib_canada as pc
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import PibCanadaAnticipe

UTC = timezone.utc
NOW = datetime(2026, 11, 12, 7, 0, tzinfo=UTC)
DATA = Path(__file__).parent / "data"
INDEX = (DATA / "statcan_ind1_2026-11-12.html").read_text()
COMM = (DATA / "statcan_pib_2026-10-30.html").read_text()
URL = "https://www150.statcan.gc.ca/n1/daily-quotidien/261030/dq261030a-eng.htm"


def _market(mid, question):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2026, 11, 30, 12, 30, tzinfo=UTC),
                                   question=question, events=[{"id": "1310284", "title": "Canada GDP: September 2026 (MoM)"}]))


def test_index_release_and_questions_are_read():
    assert pc.dernier_communique(INDEX) == URL
    r = pc.parse_communique(COMM)
    assert (r["anticipe_mois"], r["anticipe"], r["officiel_mois"], r["officiel"]) == ("September", -0.1, "August", 0.0)
    assert pc.parse_communique("<html>rien</html>") is None
    q = "Will Canada's GDP growth rate MoM in September 2026 be "
    assert pc.tranche(q + "less than -0.2%?") == (-99.0, -0.3, "September", 2026)
    assert pc.tranche(q + "between -0.2% and -0.1%?") == (-0.2, -0.1, "September", 2026)
    assert pc.tranche(q + "at least 0.6%?") == (0.6, 99.0, "September", 2026)
    assert pc.tranche("Will the UK GDP grow?") is None


def test_revision_frequencies_spread_the_chance_around_the_estimate():
    p = {k: pc.p_tranche(-0.1, a, b) for k, (a, b) in {"bas": (-99, -0.3), "est": (-0.2, -0.1), "haut": (0.0, 0.1), "0.2": (0.2, 0.3)}.items()}
    assert 0.35 < p["est"] < 0.42            # marché du 12/11 : 0,485
    assert 0.30 < p["haut"] < 0.38           # marché : 0,245
    assert 0.20 < p["bas"] < 0.28            # marché : 0,135
    assert 0.0 < p["0.2"] < 0.05


def test_collect_attach_and_buy(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    result = collect({"sources": {"pib_canada": {"enabled": True, "every_minutes": 180}}}, Http({pc.INDEX: INDEX, URL: COMM}), db, [], NOW)
    assert result.status["pib_canada"].startswith("ok (1")
    q = "Will Canada's GDP growth rate MoM in September 2026 be "
    est, haut = _market("6", q + "between -0.2% and -0.1%?"), _market("7", q + "between 0.0% and 0.1%?")
    autre = _market("8", "Will Canada's GDP growth rate MoM in October 2026 be between 0.0% and 0.1%?")
    assert refs.attach_all([est, haut, autre], db, NOW)["pib_canada"] == 2
    s = _s(PibCanadaAnticipe, min_net_edge=0.05, uncertainty=0.05, min_price=0.05, max_price=0.95, max_stale_hours=8,
           max_extra_ticks=1, max_proposals_per_cycle=3, max_per_event=3, kelly_fraction=1.0)
    # carnets réels du 12/11 : « 0,0 à 0,1 » OUI vendu 0,25 (chance 0,35) ; « −0,2 à −0,1 » NON vendu 0,52 (chance 0,63) :
    # après la marge de 0,05 et les frais, juste sous le seuil
    def books(y6, y7):
        b = _books(("6Y", str(y6 - 0.01), str(y6)), ("6N", str(round(1 - y6, 2)), str(round(1.01 - y6, 2))),
                   ("7Y", str(y7 - 0.01), str(y7)), ("7N", str(round(1 - y7, 2)), str(round(1.01 - y7, 2))))
        for x in b.values():
            x.fetched_at = NOW
        return b
    out = s.propose([est, haut], books(0.49, 0.25), _state(tmp_path), LIMITS, "b1")
    assert out.proposals == [] and out.abstentions.get("avantage net insuffisant") == 2
    # un vendeur à 0,20 sur « 0,0 à 0,1 » et un acheteur à 0,56 sur la tranche de l'estimation : les deux achats
    out = s.propose([est, haut], books(0.57, 0.20), _state(tmp_path), LIMITS, "b1")
    assert sorted(p.token_id for p in out.proposals) == ["6N", "7Y"]
