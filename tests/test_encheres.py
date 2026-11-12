"""Prix de vente aux enchères contre l'estimation basse (12/11/2026, experiments/encheres.md, piste n° 45) : tranches, chances,
rattachement (arrêt le jour de la vente) et stratégie `encheres_estimation`. Cas réel : Klimt « Litzlbergkeller » (Christie's,
estimation 60-80 M$, garantie d'un tiers, vente du 17/11), carnets du 12/11 à 21 h UTC (« $60m-$75m » OUI vendu 0,25)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from conftest import raw_market
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import encheres as en
from polymarket_agent import references as refs
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import EncheresEstimation

UTC = timezone.utc
NOW = datetime(2026, 11, 12, 21, 0, tzinfo=UTC)
TRANCHES = [("6766298", "<$60m"), ("6766299", "$60m-$75m"), ("6766300", "$75m-$90m"), ("6766301", "$90m-$105m"), ("6766302", "$105m+")]


def _markets():
    return [parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2026, 11, 18, 4, 59, tzinfo=UTC),
                                    groupItemTitle=t, event_id="1328430",
                                    question=f"Will Gustav Klimt's “Litzlbergkeller” sell for {t} at auction?"))
            for mid, t in TRANCHES]


def _table(tmp_path, garanti="true"):
    p = tmp_path / "encheres.yaml"
    p.write_text(f"""lots:
  - {{evenement: "1328430", nom: "Klimt", estimation_basse: 60, garanti: {garanti}, vente: "2026-11-17"}}
""", encoding="utf-8")
    return p


def test_brackets_are_read():
    assert en.tranche("<$60m") == (0.0, 60.0)
    assert en.tranche("$60m-$75m") == (60.0, 75.0)
    assert en.tranche("$105m+") == (105.0, float("inf"))
    assert en.tranche("$3.5m–$4.5m") == (3.5, 4.5)
    assert en.tranche("<$3.5m") == (0.0, 3.5)
    assert en.tranche("Other") is None


@pytest.mark.parametrize("garanti", [True, False])
def test_bracket_chances_sum_to_one_and_follow_the_past_ratios(garanti):
    bornes = [(0, 60), (60, 75), (75, 90), (90, 105), (105, float("inf"))]
    p = [en.p_tranche(60, lo, hi, garanti, lo == 0) for lo, hi in bornes]
    assert sum(p) == pytest.approx(1.0)
    # 1,0-1,25 fois l'estimation basse : 36 rapports sur 66 (garanti : pas d'invendu ; sinon 4 invendus en plus)
    assert p[1] == pytest.approx(36 / 66 * 0.98 if garanti else 36 / 70 * 0.98)
    assert p[0] > (0.07 if garanti else 0.12)   # 4 rapports sous 1 + retrait (+ invendus)


def test_attach_stops_on_the_day_of_the_sale_and_the_strategy_buys_the_underpriced_bracket(tmp_path):
    table = _table(tmp_path)
    ms = _markets()
    assert en.attach_encheres(ms, None, NOW, table) == 5
    assert ms[1].references["encheres"]["p"] == pytest.approx(0.535, abs=0.002)
    late = _markets()
    assert en.attach_encheres(late, None, datetime(2026, 11, 17, 0, 1, tzinfo=UTC), table) == 0   # jour de la vente : rien
    s = _s(EncheresEstimation, min_net_edge=0.05, uncertainty=0.10, min_price=0.05, max_price=0.90, max_stale_hours=2,
           max_extra_ticks=1, max_proposals_per_cycle=4, max_per_event=2, kelly_fraction=1.0)
    books = _books(("6766298Y", "0.01", "0.20"), ("6766298N", "0.80", "0.99"),
                   ("6766299Y", "0.23", "0.25"), ("6766299N", "0.75", "0.77"),
                   ("6766300Y", "0.35", "0.36"), ("6766300N", "0.64", "0.65"),
                   ("6766301Y", "0.18", "0.29"), ("6766301N", "0.71", "0.82"),
                   ("6766302Y", "0.004", "0.102"), ("6766302N", "0.898", "0.996"))
    for b in books.values():
        b.fetched_at = NOW
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    toks = [p.token_id for p in out.proposals]
    # « $60m-$75m » à 0,25 pour 0,53 ; le NON de « $90m-$105m » (0,97 − 0,10 contre 0,82 + frais) et de « $75m-$90m » restent sous le seuil
    assert toks == ["6766299Y"]


def test_repository_table_and_attach_all(tmp_path):
    lots = en.lots()
    assert {"1328429", "1328430", "1328431", "1328432"} <= set(lots)
    assert all(l["vente"].isoformat() >= "2026-11-17" for l in lots.values())
    ms = _markets()
    assert refs.attach_all(ms, None, NOW)["encheres"] == 5
