"""Auditeurs mensuels Spotify (11/11/2026, experiments/spotify_auditeurs.md, piste n° 28) : lecture de kworb, journal, chance de
place, rattachement et stratégie `auditeurs_spotify`. Données : page kworb réelle du 11/11/2026 vers 21 h UTC (16 premiers)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state
from polymarket_agent import references as refs
from polymarket_agent import spotify_auditeurs as sp
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import AuditeursSpotify

UTC = timezone.utc
NOW = datetime(2026, 11, 11, 21, 0, tzinfo=UTC)
END = datetime(2026, 11, 30, 17, 0, tzinfo=UTC)          # 30/11 12 h, heure de l'Est
PAGE = (Path(__file__).parent / "data" / "kworb_listeners_2026-11-11.html").read_text()


def _market(mid, question, end=END):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=end, question=question,
                                   events=[{"id": "e2", "title": "#2 Spotify Artist in November?"}]))


def test_parse_kworb_reads_rank_name_listeners_and_daily_change():
    rows = sp.parse_kworb(PAGE)
    assert len(rows) == 16
    assert rows[0] == {"id": "Bruno Mars", "nom": "Bruno Mars", "rang": 1, "auditeurs": 124624825, "variation": -321978}
    assert (rows[1]["nom"], rows[1]["auditeurs"], rows[2]["nom"], rows[2]["auditeurs"]) == ("The Weeknd", 116993416, "Rihanna", 116778078)
    assert sp.parse_kworb("<html>maintenance</html>") == []


def test_market_target_reads_artist_and_place():
    assert sp.market_target("Will Rihanna have the second-greatest number of monthly Spotify listeners this month?") == ("Rihanna", 2)
    assert sp.market_target("Will Bruno Mars have the greatest number of monthly Spotify listeners this month?") == ("Bruno Mars", 1)
    assert sp.market_target("Will Bad Bunny be the top Spotify artist of 2026?") is None


def test_history_keeps_one_line_per_new_value_and_gives_the_drift():
    rows = sp.parse_kworb(PAGE)
    h = sp.keep_history([], rows, NOW - timedelta(days=2))
    moved = [dict(r, auditeurs=r["auditeurs"] - 300000) if r["nom"] == "The Weeknd" else r for r in rows]
    h = sp.keep_history(h, moved, NOW)
    h = sp.keep_history(h, moved, NOW + timedelta(hours=3))           # même valeur relue : pas de nouvelle ligne
    assert len([r for r in h if r["nom"] == "The Weeknd"]) == 2 and len([r for r in h if r["nom"] == "Rihanna"]) == 1
    assert sp.drift(h, "The Weeknd", NOW) == -150000.0
    assert sp.drift(h, "Rihanna", NOW) is None                         # une seule valeur : pas de pente


def test_close_race_is_near_a_coin_flip_and_a_far_artist_is_not():
    rows = sp.parse_kworb(PAGE)
    p_weeknd = sp.p_rang(rows, [], "The Weeknd", 2, NOW, END)
    p_rihanna = sp.p_rang(rows, [], "Rihanna", 2, NOW, END)
    assert 0.3 < p_rihanna < 0.6 and 0.3 < p_weeknd < 0.7 and p_rihanna + p_weeknd <= 1.0
    assert sp.p_rang(rows, [], "Bruno Mars", 1, NOW, END) > 0.95
    assert sp.p_rang(rows, [], "Nobody Famous", 2, NOW, END) is None
    # la veille du règlement, l'écart de 215 000 auditeurs tranche presque
    assert sp.p_rang(rows, [], "The Weeknd", 2, END - timedelta(hours=1), END, retrait=0.0) > 0.9


def test_collector_attach_and_strategy_buy_the_underpriced_challenger(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    http = Http({sp.KWORB: PAGE})
    result = collect({"sources": {"spotify": {"enabled": True, "every_minutes": 180}}}, http, db, [], NOW)
    assert result.status["spotify"].startswith("ok (")
    assert len(refs._load(db, "spotify:histo")[1]) == 16
    rihanna = _market("r2", "Will Rihanna have the second-greatest number of monthly Spotify listeners this month?")
    year = _market("y1", "Will Rihanna have the second-greatest number of monthly Spotify listeners this month?",
                   end=datetime(2027, 2, 1, tzinfo=UTC))
    assert refs.attach_all([rihanna, year], db, NOW)["spotify"] == 1
    assert "spotify" not in (year.references or {})
    s = _s(AuditeursSpotify, min_net_edge=0.05, uncertainty=0.10, min_price=0.10, max_price=0.90, max_stale_hours=6,
           max_extra_ticks=1, max_proposals_per_cycle=2, max_per_event=1, kelly_fraction=0.5)
    books = _books(("r2Y", "0.16", "0.19"), ("r2N", "0.81", "0.84"))     # carnet réel du 11/11 21 h
    for b in books.values():
        b.fetched_at = NOW
    out = s.propose([rihanna], books, _state(tmp_path), LIMITS, "b1")
    assert [p.token_id for p in out.proposals] == ["r2Y"]
