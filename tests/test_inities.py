"""Comptes suspects qui parient avant une annonce (27/10/2026, affaire du Ballon d'Or, experiments/inities.md) : familles « à
initiés », grappes de comptes neufs et concentrés, profils gardés en base, articles et commentaires, rattachement aux marchés,
collecteur et stratégie `suivre_inities`."""

from __future__ import annotations

import json
from datetime import timedelta

import pytest

from conftest import NOW, raw_market
from test_sources import FakeHttp
from test_strategies_v3 import LIMITS, _books, _s, _state
from polymarket_agent import inities
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import SuivreInities

T = int(NOW.timestamp())
FRESH, OLD = {"premiere": T - 86400, "marches": 3}, {"premiere": T - 200 * 86400, "marches": 400}


def _trade(wallet, token, usd, price=0.70, hours_ago=2, side="BUY", name=""):
    return {"proxyWallet": wallet, "asset": token, "conditionId": "c" + token, "side": side, "price": price,
            "size": usd / price, "timestamp": T - int(hours_ago * 3600), "name": name}


def test_insider_families_are_recognised_and_live_counters_are_not():
    assert inities.famille("Ballon d'Or 2026: 3rd Place") == "prix"
    assert inities.famille("#1 Searched Person on Google this year?") == "donnees_entreprise"
    assert inities.famille("Who will be evicted from Big Brother? (Week 5)") == "emission"
    assert inities.famille("Who will Trump nominate as Fed Chair?") == "decision"
    for live in ("# of views of next MrBeast video on day 1?", "What will Trump say during Cabinet meeting?",
                 "NJ-12 Democratic Primary Winner", "#2 Free App in the US Apple App Store on June 12?"):
        assert inities.famille(live) is None, live


def test_fresh_concentrated_accounts_form_a_cluster_and_old_or_scattered_ones_do_not():
    """Ballon d'Or 2026 : `Aggravating-Lettuce-Local`, créé 16 minutes avant son premier achat, 15 766 $ sur « Yamal 3e »."""
    trades = [_trade("A", "T", 3000), _trade("A", "T", 2000, price=0.72, hours_ago=1),
              _trade("B", "T", 9000),                                   # vieux compte : pas suspect
              _trade("C", "T", 3000),                                   # neuf mais 80 marchés : pas concentré
              _trade("D", "U", 50),                                     # sous la mise minimale
              _trade("A", "T", 4000, side="SELL"),                      # une vente ne compte pas
              _trade("A", "T", 9000, hours_ago=100)]                    # hors de la fenêtre de 72 h
    profils = {"A": FRESH, "B": OLD, "C": {"premiere": T - 86400, "marches": 80}, "D": FRESH}
    out = inities.grappes(trades, profils, NOW)
    assert len(out) == 1 and out[0]["jeton"] == "T" and out[0]["comptes"] == 1 and out[0]["adresses"] == ["A"]
    assert out[0]["dollars"] == 5000.0 and 0.70 < out[0]["prix_moyen"] < 0.72
    assert inities.gros_acheteurs(trades, NOW, 72, 300) == ["B", "A", "C"]


def test_a_never_renamed_profile_gives_its_creation_date():
    """Un profil jamais renommé s'appelle « <adresse>-<création en ms> » : son âge se lit sans appel."""
    nom = "0x" + "a" * 40 + f"-{(T - 2 * 86400) * 1000}"
    assert inities.creation_par_nom(nom) == T - 2 * 86400 and inities.creation_par_nom("kraben006") is None
    assert inities.suspect({"marches": 2}, T, 7, 15, nom) and not inities.suspect({"marches": 2}, T, 1, 15, nom)
    assert not inities.suspect(None, T, 7, 15, nom)  # nombre de marchés inconnu : on ne conclut pas


def _ballon(mid="m3", event_title="Ballon d'Or 2026: 3rd Place"):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", question="Will Lamine Yamal finish 3rd?",
                                   end=NOW + timedelta(days=12), events=[{"id": "e1", "title": event_title}]))


def test_attach_links_the_cluster_and_the_press_to_the_market(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    row = {"jeton": "m3Y", "evenement": "e1", "titre": "Ballon d'Or 2026: 3rd Place", "comptes": 2, "dollars": 12000.0,
           "prix_moyen": 0.70, "dernier": T - 3600, "commentaires": []}
    refs._save(db, "ref:inities", [row], NOW)
    refs._save(db, "ref:soupcons", [{"titre": "Ballon d’Or 2026 : les paris suspects sur Polymarket interrogent"},
                                    {"titre": "Nobel Peace Prize leak: suspicious bets"}], NOW)
    m, other = _ballon(), _ballon("m9", "Oscars 2026: Best Picture Winner")
    assert inities.attach_inities([m, other], db, NOW) == 1
    ref = m.references["inities"]
    assert ref["issue"] == 0 and ref["dollars"] == 12000.0 and ref["presse"] == ["Ballon d’Or 2026 : les paris suspects sur Polymarket interrogent"]
    assert not (other.references or {}).get("inities")
    late = _ballon("m3")
    assert inities.attach_inities([late], db, NOW + timedelta(hours=7)) == 0  # relevé trop vieux : rien
    # L'affaire du Ballon d'Or 2026 (terminée) ne rend pas suspect le marché de 2027.
    assert not inities._meme_sujet("Ballon d’Or 2026 : les paris suspects", "Ballon d'Or 2027 Winner")
    assert inities._meme_sujet("Ballon d’Or 2026 : les paris suspects", "Ballon d'Or 2026: 3rd Place")


def test_fetch_inities_reads_trades_profiles_and_comments_and_keeps_profiles_in_the_base(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    event = {"id": "e1", "title": "Ballon d'Or 2026: 3rd Place", "volume24hr": 5000}
    http = FakeHttp({inities.GAMMA + "/events": [event, {"id": "e2", "title": "# of views of next MrBeast video?"}],
                     inities.DATA + "/trades": [_trade("A", "m3Y", 6000), _trade("B", "m3N", 400)],
                     inities.DATA + "/activity": [{"timestamp": T - 3600}],
                     inities.DATA + "/traded": {"traded": 2},
                     inities.GAMMA + "/comments": [{"body": "someone has inside info, Yamal 3rd", "createdAt": "2026-10-14T10:00:00Z"},
                                                   {"body": "insider? no, old news", "createdAt": "2026-09-01T10:00:00Z"},
                                                   {"body": "go Mbappé", "createdAt": "2026-10-14T11:00:00Z"}]})
    cfg = {"etiquettes": [18], "pages": 1}
    rows = inities.fetch_inities(http, db, NOW, cfg)
    assert [r["jeton"] for r in rows] == ["m3Y", "m3N"] and rows[0]["evenement"] == "e1"
    assert rows[0]["commentaires"] == ["someone has inside info, Yamal 3rd"]
    assert json.loads(db.get_value("inities:profil:A"))["marches"] == 2
    asked = sum(1 for url, *_ in http.calls if url.endswith("/activity"))
    inities.fetch_inities(http, db, NOW + timedelta(hours=1), cfg)
    assert sum(1 for url, *_ in http.calls if url.endswith("/activity")) == asked  # profils gardés 12 h : pas redemandés


def test_fetch_soupcons_keeps_only_titles_about_suspicious_bets():
    rss = b"""<?xml version="1.0"?><rss><channel>
<item><title>Ballon d'Or 2026 : des paris suspects font scandale - Foot01</title><link>https://a</link>
<pubDate>Sat, 24 Oct 2026 12:00:00 GMT</pubDate><source url="https://foot01.com">Foot01</source></item>
<item><title>Who will win the Ballon d'Or? - Yahoo</title><link>https://b</link><source url="https://yahoo.com">Yahoo</source></item>
</channel></rss>"""

    class Session:
        def get(self, url, timeout=10):
            return type("R", (), {"status_code": 200, "content": rss})()
    rows = inities.fetch_soupcons(Session(), NOW, {"requetes": ["Polymarket insider"]})
    assert [r["titre"] for r in rows] == ["Ballon d'Or 2026 : des paris suspects font scandale"] and rows[0]["media"] == "Foot01"


def test_fetch_soupcons_also_reads_mastodon_and_hacker_news_and_fails_only_if_everything_fails():
    """Réseaux ouverts sans compte : #polymarket sur Mastodon, Hacker News (X payant ; Bluesky et Reddit : 403)."""
    import requests
    recent, old = (NOW - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z"), (NOW - timedelta(days=9)).strftime("%Y-%m-%dT%H:%M:%SZ")
    answers = {inities.MASTODON: [{"created_at": recent, "url": "https://m/1", "content": "<p>Fresh wallets loading Yamal 3rd at the <b>Ballon d'Or</b> #polymarket</p>"},
                                  {"created_at": recent, "url": "https://m/2", "content": "<p>Kane to win, easy money #polymarket</p>"},
                                  {"created_at": old, "url": "https://m/3", "content": "<p>insider on the Nobel</p>"}],
               inities.HACKER_NEWS: {"hits": [{"created_at": recent, "objectID": "9", "story_title": "Ballon d'Or odds",
                                               "comment_text": "Someone knows: 12 new accounts bet the exact ranking"},
                                              {"created_at": recent, "objectID": "8", "title": "Polymarket raises money"}]}}

    class Session:
        def __init__(self, down=()):
            self.down = down

        def get(self, url, timeout=10):
            base = url.split("?")[0]
            if base in self.down or (base == inities.NEWS and inities.NEWS in self.down):
                raise requests.ConnectionError("injoignable")
            body = json.dumps(answers[base]).encode() if base in answers else b"<rss><channel></channel></rss>"
            return type("R", (), {"status_code": 200, "content": body})()
    rows = inities.fetch_soupcons(Session(), NOW, {"requetes": ["Polymarket insider"]})
    assert [(r["media"], r["lien"]) for r in rows] == [("Mastodon", "https://m/1"), ("Hacker News", "https://news.ycombinator.com/item?id=9")]
    assert rows[0]["titre"] == "Fresh wallets loading Yamal 3rd at the Ballon d'Or #polymarket"
    assert rows[1]["titre"] == "Ballon d'Or odds — Someone knows: 12 new accounts bet the exact ranking"
    # Un réseau injoignable est sauté ; tout injoignable : la source le dit.
    assert len(inities.fetch_soupcons(Session(down=(inities.MASTODON,)), NOW, {"requetes": ["q"]})) == 1
    assert inities.fetch_soupcons(Session(), NOW, {"requetes": ["q"], "reseaux": False}) == []
    with pytest.raises(SourceUnavailable):
        inities.fetch_soupcons(Session(down=(inities.NEWS, inities.MASTODON, inities.HACKER_NEWS)), NOW, {"requetes": ["q"]})


def test_collector_saves_both_insider_snapshots(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    cfg = {"sources": {"inities": {"enabled": True, "every_minutes": 20}, "soupcons": {"enabled": True, "every_minutes": 60}}}
    result = collect(cfg, None, db, [], NOW, {"inities": lambda c: [{"jeton": "t", "comptes": 1}],
                                             "soupcons": lambda c: [{"titre": "paris suspects"}]})
    assert result.status["inities"].startswith("ok") and result.status["soupcons"].startswith("ok")
    assert refs._load(db, "ref:inities")[1] == [{"jeton": "t", "comptes": 1}]
    assert refs._load(db, "ref:soupcons")[1] == [{"titre": "paris suspects"}]


PARAMS = dict(presse_requise=1, min_comptes=1, min_dollars=2000, prix_min=0.30, max_age_hours=72, max_price=0.90,
              max_rattrapage=0.15, edge_prior=0.10, uncertainty=0.03, stake_fraction=0.03, min_net_edge=0.0,
              max_extra_ticks=2, max_proposals_per_cycle=3)


def _with_ref(**ref):
    m = _ballon()
    base = {"issue": 0, "comptes": 2, "dollars": 12000.0, "prix_moyen": 0.70, "dernier": T - 3600,
            "presse": ["Ballon d'Or 2026 : paris suspects"], "commentaires": []}
    m.references = {"inities": dict(base, **ref)}
    return m


def test_follow_insiders_buys_with_public_suspicion_before_the_price_catches_up(tmp_path):
    """Ballon d'Or 2026 : article d'Upside le 23/10, « Yamal 3e » encore à 0,70-0,72, réponse le 26/10."""
    s = _s(SuivreInities, **PARAMS)
    books = _books(("m3Y", 0.71, 0.72), ("m3N", 0.28, 0.29))
    state = _state(tmp_path)
    out = s.propose([_with_ref()], books, state, LIMITS, "b")
    assert [p.token_id for p in out.proposals] == ["m3Y"]
    assert 25 <= float(out.proposals[0].shares * out.proposals[0].max_price) <= 31  # 3 % de 1 000 €
    cases = {"personne ne parle de paris suspects sur cet événement": _with_ref(presse=[], commentaires=[]),
             "comptes suspects sur un outsider (joueurs, pas initiés)": _with_ref(prix_moyen=0.08),
             "grappe trop ancienne": _with_ref(dernier=T - 100 * 3600),
             "grappe trop petite": _with_ref(dollars=900.0)}
    for reason, m in cases.items():
        out = s.propose([m], books, state, LIMITS, "b")
        assert not out.proposals and out.abstentions.get(reason), reason
    late = s.propose([_with_ref()], _books(("m3Y", 0.89, 0.90), ("m3N", 0.10, 0.11)), state, LIMITS, "b")
    assert not late.proposals and late.abstentions.get("le prix a déjà rattrapé les comptes suspects")
    # Les commentaires Polymarket valent la presse.
    talk = s.propose([_with_ref(presse=[], commentaires=["insider bought Yamal 3rd"])], books, state, LIMITS, "b")
    assert [p.token_id for p in talk.proposals] == ["m3Y"]
    assert s.candidates([_with_ref(), _ballon("m8")])[0].market_id == "m3"
