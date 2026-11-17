"""Marges du Maryland (17/11/2026, piste n° 68) : vraies pages du State Board of Elections du 16/11 23 h 06 (gouverneur, MD-08 dont les
provisoires de Montgomery ne sont pas publiés), libellés des marchés, collecteur, rattachement sous `marges_ca` et achat par
`marges_californie` de la tranche courante seulement quand elle est vendue sous sa chance (cas réel : MD-05 « 40-45 % » à 0,94 :
juste sous le seuil ; MD-08 « 65-70 % » avec les provisoires non publiés et le gouverneur « 30-35 % » à 0,779, sur le fil : rien)."""
from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import marges_maryland as mm
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import MargesCalifornie

UTC = timezone.utc
NOW = datetime(2026, 11, 17, 11, 0, tzinfo=UTC)
END = datetime(2026, 11, 4, 4, 59, tzinfo=UTC)
FIX = Path(__file__).parent / "fixtures"
GOUV = (FIX / "maryland_gouverneur_20261116.html").read_text(encoding="utf-8", errors="ignore")
MD08 = (FIX / "maryland_md08_20261116.html").read_text(encoding="utf-8", errors="ignore")
MD05 = (FIX / "maryland_md05_20261116.html").read_text(encoding="utf-8", errors="ignore")


class _Http:
    def __init__(self, pages):
        self.pages = pages

    def get_text(self, url, params=None, headers=None):
        for course, page in mm.PAGES.items():
            if url == mm.BASE + page and course in self.pages:
                return self.pages[course]
        raise SourceUnavailable(f"{url} : HTTP 404")


def _market(mid, question, event):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=END, question=question,
                                   events=[{"id": event, "title": "Margin of Victory"}]))


def test_questions_of_maryland():
    assert mm.question("Will the Democratic Party candidate win the 2026 MD-05 House election by 40%-45%?") == ("MD-05", "D", 40.0, 45.0)
    assert mm.question("Will the Democratic Party candidate win the 2026 Maryland gubernatorial election by 35%-40%?") == \
        ("MD-GOV", "D", 35.0, 40.0)
    assert mm.question("Will the Democratic Party candidate win the 2026 MD-02 House election by 40% or more?") == ("MD-02", "D", 40.0, math.inf)
    assert mm.question("Will the Republican Party candidate win the 2026 MD-01 House election by 3%-6%?") == ("MD-01", "R", 3.0, 6.0)
    assert mm.question("Will the Republican Party candidate win the 2026 MD-05 House election?") == ("MD-05", "R", 0.0, math.inf)
    assert mm.question("Will Person A win the 2026 MD-02 House election?") is None
    assert mm.question("Will a Democratic Party candidate win the 2026 CA-26 House election by 25%-30%?") is None


def test_read_the_real_pages_of_16_11():
    g = mm.lire(GOUV)
    assert (g["d"], g["r"], g["total"]) == (1_452_074, 681_194, 2_230_537)
    assert abs(100 * (g["d"] - g["r"]) / g["total"] - 34.56) < 0.01 and g["ecart_api"] == 34.56
    assert g["tard_total"] == 482_985 + 67_784 and g["provisoires_publies"]
    assert 60 < 100 * (g["tard_d"] - g["tard_r"]) / g["tard_total"] < 61       # correspondance et provisoires : ≈ +60,5
    h = mm.lire(MD08)
    assert (h["d"], h["r"], h["total"]) == (235_491, 41_426, 282_239) and not h["provisoires_publies"]   # Montgomery : 0 provisoire
    assert mm.lire("<html>Page Not Found</html>") is None


def test_collect_attach_and_buy_only_the_safe_current_bracket(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    cfg = {"sources": {"marges_md": {"enabled": True, "every_minutes": 60}}}
    res = collect(cfg, _Http({"MD-GOV": GOUV, "MD-05": MD05, "MD-08": MD08}), db, [], NOW)
    assert res.status["marges_md"].startswith("ok (3")
    q = "Will the Democratic Party candidate win the 2026 {} election by {}?"
    cinq = _market("3490850", q.format("MD-05 House", "40%-45%"), "828263")
    cinq_haut = _market("3490841", q.format("MD-05 House", "55% or more"), "828263")
    huit = _market("3490921", q.format("MD-08 House", "65%-70%"), "828266")
    gouv_bas = _market("3365749", q.format("Maryland gubernatorial", "30%-35%"), "802343")
    gouv_haut = _market("3365750", q.format("Maryland gubernatorial", "35%-40%"), "802343")
    rep = _market("3490881", "Will the Republican Party candidate win the 2026 MD-05 House election?", "828263")
    ms = [cinq, cinq_haut, huit, gouv_bas, gouv_haut, rep]
    counts = refs.attach_all(ms, db, NOW)
    assert counts["marges_md"] == 6
    p = {m.market_id: m.references["marges_ca"]["p"] for m in ms}
    assert p["3490850"] > 0.99 and p["3490841"] < 0.001 and p["3490881"] < 0.001
    assert 0.85 < p["3490921"] < 0.95   # MD-08 : provisoires de Montgomery non publiés, restants doublés (prudence) : pas d'achat à 0,94
    assert 0.3 < p["3365749"] < 0.8 and 0.2 < p["3365750"] < 0.7 and abs(p["3365749"] + p["3365750"] - 1) < 0.02   # sur le fil
    assert "provisoires non publiés" in huit.references["marges_ca"]["titre"]
    s = _s(MargesCalifornie, min_net_edge=0.04, uncertainty=0.02, min_price=0.30, max_price=0.95, max_stale_hours=3,
           max_extra_ticks=1, max_candidates=400, max_proposals_per_cycle=4, max_per_event=1, mise_max_pari=0.04, kelly_fraction=1.0)
    def books(ask_md05):
        b = _books(("3490850Y", "0.26", ask_md05), ("3490850N", "0.06", "0.74"), ("3490841Y", "0.001", "0.01"),
                   ("3490841N", "0.99", "0.999"), ("3490921Y", "0.60", "0.94"), ("3490921N", "0.06", "0.40"),
                   ("3365749Y", "0.024", "0.779"), ("3365749N", "0.221", "0.976"), ("3365750Y", "0.06", "0.81"),
                   ("3365750N", "0.19", "0.94"), ("3490881Y", "0.001", "0.005"), ("3490881N", "0.995", "0.999"))
        for x in b.values():
            x.fetched_at = NOW
        return b
    # Carnet réel du 17/11 (MD-05 à 0,94) : 0,9957 − 0,02 − 0,94 − frais = 0,033 < 0,04 : rien ; un vendeur à 0,92 (comme en
    # Californie, 0,89-0,92) : MD-05 seulement (MD-08 trop incertain, le gouverneur sur le fil).
    assert s.propose(ms, books("0.94"), _state(tmp_path), LIMITS, "b1").proposals == []
    out = s.propose(ms, books("0.92"), _state(tmp_path), LIMITS, "b2")
    assert [x.token_id for x in out.proposals] == ["3490850Y"]


def test_source_and_list_are_configured():
    import yaml
    from conftest import ROOT
    settings = yaml.safe_load((ROOT / "config" / "settings.yaml").read_text(encoding="utf-8"))
    spec = settings["scanner"]["listes_marches"]["marges_maryland"]
    ids = yaml.safe_load((ROOT / spec["fichier"]).read_text(encoding="utf-8"))["marches"]
    assert len(ids) == 87 and "3490850" in ids and "3365750" in ids and spec["min_horizon_minutes"] < 0
    assert settings["sources"]["marges_md"]["enabled"]
