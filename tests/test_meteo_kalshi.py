"""Températures du jour, Kalshi (maximum CLI) décalé vers la règle METAR de Polymarket (15/11/2026, experiments/meteo_kalshi.md,
piste n° 62) : lecture des événements Kalshi, loi, garde des queues, tranche visée, rattachement et fantôme `meteo_sous_cli`.
Données : réponses réelles de Kalshi du 15/11/2026 vers 06 h 20 UTC (Austin : « < 61 » à 0,93/0,95 ; Miami : 78-79 à 0,32/0,33,
80-81 à 0,59/0,62)."""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import meteo_kalshi as mk
from polymarket_agent import references as refs
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import MeteoSousCli

UTC = timezone.utc
NOW = datetime(2026, 11, 15, 6, 20, tzinfo=UTC)
KALSHI = json.loads((Path(__file__).parent / "data" / "kalshi_meteo_2026-11-15.json").read_text())


class Http:
    def __init__(self):
        self.calls = []

    def get_json(self, url, params=None, headers=None):
        self.calls.append((url, params))
        return KALSHI.get((params or {}).get("series_ticker"), {"events": []})


def _market(mid, ville, tranche, jour=15):
    q = (f"Will the highest temperature in {ville} be between {tranche} on November {jour}?" if "-" in tranche
         else f"Will the highest temperature in {ville} be {tranche} on November {jour}?")
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2026, 11, jour, 12, tzinfo=UTC),
                                   question=q, events=[{"id": f"e{ville}{jour}", "title": f"Highest temperature in {ville} on November {jour}?"}]))


def test_kalshi_events_are_read_and_the_heavy_tail_is_refused():
    rows = mk.fetch_kalshi_meteo(Http(), NOW)
    assert {(r["ville"], r["jour"]) for r in rows} == {("Austin", "2026-11-14"), ("Austin", "2026-11-15"), ("Miami", "2026-11-15")}
    by = {(r["ville"], r["jour"]): r for r in rows}
    assert mk.jour_kalshi("KXHIGHMIA-26NOV15") == date(2026, 11, 15)
    # Austin 15/11 : « < 61 » porte 0,94 de la loi, sa forme est inconnue : pas de loi (sinon la « médiane » tomberait à 60).
    assert mk.loi_cli(by[("Austin", "2026-11-15")]["marches"]) is None
    loi = mk.loi_cli(by[("Miami", "2026-11-15")]["marches"])
    assert abs(sum(loi.values()) - 1) < 1e-9 and mk.mediane(loi) == 80
    assert mk.tranche_visee(loi) == (78, 79)                   # tranche Polymarket juste sous celle de la médiane CLI (80-81)
    p = mk.chance_tranche(loi, 78, 79)
    assert 0.40 < p < 0.45                                     # Kalshi brut donnerait ≈ 0,33 à « 78-79 »
    assert mk.tranche("78-79°F") == (78, 79) and mk.tranche("74°F or higher") is None


def test_collect_attach_only_the_target_bracket_and_buy_its_yes(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    result = collect({"sources": {"meteo_kalshi": {"enabled": True, "every_minutes": 30}}}, Http(), db, [], NOW)
    assert result.status["meteo_kalshi"].startswith("ok (3")
    cible = _market("701", "Miami", "78-79°F")
    dessus = _market("702", "Miami", "80-81°F")
    queue = _market("703", "Miami", "69°F or below")
    austin = _market("704", "Austin", "58-59°F")
    autre_jour = _market("705", "Miami", "78-79°F", jour=16)
    assert refs.attach_all([cible, dessus, queue, austin, autre_jour], db, NOW)["meteo_kalshi"] == 1
    assert "meteo_kalshi" in cible.references and all("meteo_kalshi" not in (m.references or {}) for m in (dessus, queue, austin, autre_jour))
    s = _s(MeteoSousCli, min_net_edge=0.03, uncertainty=0.03, min_price=0.10, max_price=0.60, max_stale_hours=2,
           max_extra_ticks=1, max_proposals_per_cycle=4, max_per_event=1, kelly_fraction=1.0)
    books = _books(("701Y", "0.29", "0.31"), ("701N", "0.69", "0.71"))
    for b in books.values():
        b.fetched_at = NOW
    out = s.propose([cible], books, _state(tmp_path), LIMITS, "b1")
    assert [p.token_id for p in out.proposals] == ["701Y"]     # OUI seulement (`cotes`), jamais le NON de la tranche
    cher = _books(("701Y", "0.38", "0.40"), ("701N", "0.60", "0.62"))
    for b in cher.values():
        b.fetched_at = NOW
    assert s.propose([cible], cher, _state(tmp_path), LIMITS, "b1").proposals == []   # 0,40 : sous l'avantage net après frais
