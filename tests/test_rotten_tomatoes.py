"""Scores Rotten Tomatoes (14/11/2026, piste n° 56, experiments/rotten_tomatoes.md) : vraies pages du 14/11/2026 vers 11 h UTC
(extraits : `criticsScore` et `dateCreated`) ; libellés, bonne page du film (pas l'homonyme de 1997 ou 2008), score affiché
arrondi, chance, collecteur, journal et stratégie `rt_compte_critiques`."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from conftest import raw_market
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import references as refs
from polymarket_agent import rotten_tomatoes as rt
from polymarket_agent.data_collector import collect
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import RtCompteCritiques

UTC = timezone.utc
NOW = datetime(2026, 11, 14, 11, 0, tzinfo=UTC)
END = datetime(2026, 11, 16, 15, 0, tzinfo=UTC)           # 10 h (heure de l'Est) le lundi 16/11
PAGES = json.loads((Path(__file__).parent / "data" / "rt_2026-11-14.json").read_text())
SEARCH = {"events": [{"title": '"Victorian Psycho" Rotten Tomatoes Score?'}, {"title": '"Ebenezer" Rotten Tomatoes Score?'},
                     {"title": '"How to Rob a Bank" Rotten Tomatoes Score?'}, {"title": '"I Play Rocky" Rotten Tomatoes Score?'},
                     {"title": "Something else"}]}


class _Http:
    """Réponses EXACTES par adresse (une adresse inconnue = 404)."""

    def __init__(self):
        self.calls = []

    def get_json(self, url, params=None, headers=None):
        self.calls.append(url)
        if url == rt.GAMMA_SEARCH:
            return SEARCH
        raise SourceUnavailable(url)

    def get_text(self, url, params=None, headers=None):
        self.calls.append(url)
        slug = url.rsplit("/m/", 1)[-1]
        if slug in PAGES:
            return "<html>" + PAGES[slug] + "</html>"
        raise SourceUnavailable(f"{url} : HTTP 404")


def _market(mid, question):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=END, question=question,
                                   description="Rotten Tomatoes Tomatometer", events=[{"id": "e1353401", "title": "RT"}]))


def test_question_slug_and_rounded_display():
    assert rt.question('Will "Victorian Psycho" score at least 75 on the Rotten Tomatoes Tomatometer?') == ("Victorian Psycho", 75)
    assert rt.question("Will “Ghost Soldier” score at least 30 on the Rotten Tomatoes Tomatometer?") == ("Ghost Soldier", 30)
    assert rt.question("Will Hong Kong have less than 5mm of precipitation in November?") is None
    assert rt.slugify("The Hunger Games: Sunrise on the Reaping") == "the_hunger_games_sunrise_on_the_reaping"
    assert rt.slugify("Ocean's Eleven") == "oceans_eleven"
    # 62/83 = 74,70 % : affiché 75 % (comme la page) ; une critique négative de plus : 74,0 % → 74
    assert rt.displayed_at_least(62, 83, 75) and not rt.displayed_at_least(62, 84, 75)
    assert rt.displayed_at_least(149, 200, 75) and not rt.displayed_at_least(148, 200, 75)   # 74,5 % → 75 (arrondi au-dessus, supposé)
    assert rt.displayed_at_least(3, 4, 75) and not rt.displayed_at_least(0, 0, 1)


def test_real_pages_skip_the_namesakes_of_1997_and_2008():
    http = _Http()
    rows = rt.fetch_rt(http, NOW)
    by = {r["film"]: r for r in rows}
    assert set(by) == {"Victorian Psycho", "How to Rob a Bank", "Ebenezer", "I Play Rocky"}
    assert by["Victorian Psycho"] == {"positives": 62, "total": 83, "affiche": "75%", "sortie": "2026-11-13", "salles": "Wide",
                                      "film": "Victorian Psycho", "slug": "victorian_psycho"}
    assert by["How to Rob a Bank"]["slug"] == "how_to_rob_a_bank_2026" and by["How to Rob a Bank"]["total"] == 85   # pas 2008
    assert by["Ebenezer"]["slug"] == "ebenezer_2026" and by["Ebenezer"]["total"] == 117                            # pas 1997
    assert by["I Play Rocky"]["salles"] == "Limited"
    # sans la page de l'année, l'homonyme de 1997 n'est jamais pris pour le film
    PAGES_SANS = {k: v for k, v in PAGES.items() if k != "ebenezer_2026"}
    http2 = _Http()
    http2.get_text = lambda url, params=None, headers=None: ("<html>" + PAGES_SANS[url.rsplit("/m/", 1)[-1]] + "</html>"
                                                             if url.rsplit("/m/", 1)[-1] in PAGES_SANS else (_ for _ in ()).throw(SourceUnavailable(url)))
    assert rt.fetch_film(http2, "Ebenezer", NOW) is None
    assert not any("/napi/" in c for c in http.calls)


def test_chance_moves_with_counts_rate_and_time():
    p75 = rt.chance(62, 83, 75, 52, 0.12)
    assert 0.3 < p75 < 0.6                                   # pile sur le seuil : ni sûr ni perdu
    assert rt.chance(62, 83, 73, 52, 0.12) > 0.8 > p75        # 1,7 point de marge
    assert rt.chance(62, 83, 75, 52, 0.12, part=0.55) < p75   # critiques récentes plus froides
    assert rt.chance(62, 83, 75, 52, 0.12, glissement=0.0) > p75   # sans glissement des critiques tardives : plus haut
    assert rt.chance(62, 83, 75, 0, 0.12) == 1.0 and rt.chance(61, 83, 75, 0, 0.12) == 0.0
    assert rt.chance(5, 14, 30, 52, 0.12) is None             # moins de 20 critiques : pas de chance


def test_journal_rate_and_recent_share():
    row = {"slug": "victorian_psycho", "positives": 62, "total": 83}
    old = [{"slug": "victorian_psycho", "positives": 39, "total": 50, "vu": (NOW - timedelta(hours=40)).isoformat()},
           {"slug": "victorian_psycho", "positives": 60, "total": 80, "vu": (NOW - timedelta(hours=2)).isoformat()}]
    r, part = rt.rythme_journal(old, "victorian_psycho", row, NOW)
    assert abs(r - 33 / 40) < 1e-9 and abs(part - 23 / 33) < 1e-9
    assert rt.rythme_journal(old[1:], "victorian_psycho", row, NOW) is None   # 2 h seulement
    h = rt.keep_history([], [dict(row, film="Victorian Psycho")], NOW)
    assert h == [{"id": "victorian_psycho:62:83", "slug": "victorian_psycho", "positives": 62, "total": 83,
                  "vu": "2026-11-14T11:00:00+00:00"}]
    assert rt.keep_history(h, [dict(row, film="x")], NOW + timedelta(hours=1)) == h   # même compte : pas de nouvelle ligne


def test_collect_attach_and_buy_only_a_cheap_side(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    result = collect({"sources": {"rotten_tomatoes": {"enabled": True, "every_minutes": 60}}}, _Http(), db, [], NOW)
    assert result.status["rotten_tomatoes"].startswith("ok (4")
    assert len(refs._load(db, "rt:histo")[1]) == 4
    s75 = _market("6920131", 'Will "Victorian Psycho" score at least 75 on the Rotten Tomatoes Tomatometer?')
    s73 = _market("6991673", 'Will "Victorian Psycho" score at least 73 on the Rotten Tomatoes Tomatometer?')
    eb = _market("6279938", 'Will "Ebenezer" score at least 50 on the Rotten Tomatoes Tomatometer?')
    # « I Play Rocky » 115/133 (86 %) : sortie LIMITÉE le 06/11, règlement après la sortie large : aucune chance (le 14/11 : 0,96
    # calculé sans ce garde-fou, marché ≈ 0,6)
    rocky = _market("6279945", 'Will "I Play Rocky" score at least 85 on the Rotten Tomatoes Tomatometer?')
    assert refs.attach_all([s75, s73, eb, rocky], db, NOW)["rt"] == 3 and "rt" not in (rocky.references or {})
    assert eb.references["rt"]["p"] > 0.85                   # 62/117 = 53 %, seuil 50
    p = s73.references["rt"]["p"]
    assert 0.6 < p < 0.97 and "62/83" in s73.references["rt"]["titre"]
    s = _s(RtCompteCritiques, min_net_edge=0.06, uncertainty=0.04, min_price=0.05, max_price=0.95, max_stale_hours=2,
           max_extra_ticks=1, max_proposals_per_cycle=2, max_per_event=2, mise_max_pari=0.04, kelly_fraction=1.0, max_candidates=40)
    b = _books(("6991673Y", f"{p - 0.01:.3f}", f"{p:.3f}"), ("6991673N", f"{1 - p - 0.01:.3f}", f"{1 - p:.3f}"))
    for x in b.values():
        x.fetched_at = NOW
    assert s.propose([s73], b, _state(tmp_path), LIMITS, "b1").proposals == []          # au prix juste : rien
    b = _books(("6991673Y", "0.39", "0.45"), ("6991673N", "0.55", "0.61"))             # vendeur pressé du OUI
    for x in b.values():
        x.fetched_at = NOW
    out = s.propose([s73], b, _state(tmp_path), LIMITS, "b2")
    assert [x.token_id for x in out.proposals] == ["6991673Y"]
