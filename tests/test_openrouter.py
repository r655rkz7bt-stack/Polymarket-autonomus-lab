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
# 13/11 à 06 h : le graphique (134,43) n'avait que le début du jeudi ; jours finis 9-12/11 = 126,89 T (semaine réglée 211,28 moins
# 13, 14, 15/11 du journal de production) ; découpage lundi-mercredi fictif (seule leur somme, 94,26, est connue)
HISTO_13_11 = [{"jour": "2026-11-09", "total_jour": 31.42}, {"jour": "2026-11-10", "total_jour": 31.42},
               {"jour": "2026-11-11", "total_jour": 31.42}]
RAW_17 = json.loads((Path(__file__).parent / "data" / "openrouter_2026-11-17.json").read_text())
HISTO_17_11 = [{"jour": "2026-11-15", "total_jour": 25.4844}]   # journal de production (sauvegarde du 16/11 23 h 50)


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
    # 17/11 : sans le total des jours finis (journal), plus de projection (le graphique contient aussi le jour en cours)
    assert orr.projection(row) is None and "journal" in orr.detail(row)["refus"]
    lundi, total, k = orr.projection(row, HISTO_13_11)
    assert lundi == "2026-11-09" and k == 4 and 209.5 < total < 210.0
    p_bas, p_haut = orr.chance(total, k, 200, 210), orr.chance(total, k, 210, 220)
    assert 0.4 < p_bas < 0.6 and 0.4 < p_haut < 0.6
    assert orr.chance(total, k, 0, 200) + orr.chance(total, k, 200, 210) + orr.chance(total, k, 210, 220) + \
        orr.chance(total, k, 220, 230) + orr.chance(total, k, 230, math.inf) > 0.999
    # semaine finie : la tranche est connue
    assert orr.chance(209.75, 7, 200, 210) == 1.0 and orr.chance(210.0, 7, 200, 210) == 0.0
    # vues incohérentes (le jour lu n'est pas la fin des 7 jours) : pas de projection
    assert orr.projection(dict(row, sept_jours=["2026-11-11", row["sept_jours"][1]]), HISTO_13_11) is None


def test_17_11_current_day_in_chart_and_launch_refused():
    """Cas réel du 17/11 (enquête 2026-11-17_soir_openrouter_jour_en_cours.md) : graphique de la semaine du 16/11 = 69,71 T à 15 h 49
    pour un lundi fini de 32,13 T (vue « jour ») : le mardi en cours y est (37,6 T en 15,9 h, dont 15,7 T du nouveau tencent/hy4-flash).
    L'ancien calcul projetait 219 T (NON « 240 T ou plus » estimé 0,97, acheté 0,42 ; marché : OUI 0,84). Refus : rythme 1,8."""
    lu = datetime(2026, 11, 17, 15, 52, tzinfo=UTC)
    row = orr.lire(RAW_17["chart"], RAW_17["week"], RAW_17["day"], lu)[0]
    assert row["jour"] == ["2026-11-16", 32.1298] and row["semaines"][-1] == ["2026-11-16", 69.7066]
    d = orr.detail(row, HISTO_17_11)
    assert "refus" in d and "lancement" in d["refus"] and 1.7 < d["rythme"] < 1.9
    assert orr.projection(row, HISTO_17_11) is None
    # même graphique avec un jour en cours ordinaire (lundi + 20 T en 15,9 h, rythme 0,94) : jours finis = 32,13 seulement,
    # projection ≈ 32,13 × 211,28 / 29,61 ≈ 229 T, et jamais sous le graphique
    calme = dict(row, semaines=row["semaines"][:-1] + [["2026-11-16", 52.13]])
    d = orr.detail(calme, HISTO_17_11)
    assert "refus" not in d and d["jours_finis"] == 32.1298 and 228 < d["total"] < 231
    # tôt le matin (2 h) : trop tôt pour juger le rythme
    tot = dict(row, lu="2026-11-17T02:00:00+00:00", semaines=row["semaines"][:-1] + [["2026-11-16", 36.0]])
    assert "refus" not in orr.detail(tot, HISTO_17_11)


def test_17_11_strategy_says_why(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    lu = datetime(2026, 11, 17, 15, 52, tzinfo=UTC)
    rows = orr.lire(RAW_17["chart"], RAW_17["week"], RAW_17["day"], lu)
    refs._save(db, "ref:openrouter", rows, lu)
    refs._save(db, "openrouter:histo", orr.journal(HISTO_17_11, rows), lu)
    m = parse_market(raw_market("6942353", yes_token="hY", no_token="hN", end=datetime(2026, 11, 23, 4, 59, tzinfo=UTC),
                                question="Will OpenRouter process 240T or more tokens the week of November 16?"))
    assert refs.attach_all([m], db, lu)["openrouter"] == 1 and "refus" in m.references["openrouter"]
    s = _s(OpenrouterSemaine, min_net_edge=0.06, uncertainty=0.04, min_price=0.08, max_price=0.92, max_stale_hours=3,
           max_extra_ticks=1, max_proposals_per_cycle=2, max_per_event=2, mise_max_pari=0.04, kelly_fraction=1.0, max_candidates=20)
    b = _books(("hY", "0.55", "0.58"), ("hN", "0.42", "0.45"))
    for x in b.values():
        x.fetched_at = lu
    out = s.propose([m], b, _state(tmp_path), LIMITS, "b1")
    assert out.proposals == [] and any("lancement" in k for k in out.abstentions)


def test_collect_attach_and_buy_cheap_lower_bracket(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    refs._save(db, "openrouter:histo", HISTO_13_11, NOW)
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


RAW_21 = json.loads((Path(__file__).parent / "data" / "openrouter_2026-11-21.json").read_text())
# journal de production (sauvegarde du 21/11) : jours 15-19/11 lus AVANT la révision, sauf le 19 (relu à 23 h 55 le 20/11)
HISTO_21_11 = [
    {"jour": "2026-11-15", "total_jour": 25.4844, "semaine": "2026-11-16", "precedente": 211.2801},
    {"jour": "2026-11-16", "total_jour": 32.1298, "semaine": "2026-11-16", "precedente": 211.2801},
    {"jour": "2026-11-17", "total_jour": 53.5561, "semaine": "2026-11-16", "precedente": 211.2801},
    {"jour": "2026-11-18", "total_jour": 56.2461, "semaine": "2026-11-16", "precedente": 211.2801},
    {"jour": "2026-11-19", "total_jour": 29.9085, "semaine": "2026-11-16", "precedente": 171.2123}]


def test_21_11_history_revised_by_source_is_named():
    """Cas réel du 21/11 (enquête 2026-11-21_matin_openrouter_historique_revise.md) : OpenRouter a récrit tout son historique le
    20/11 vers 23 h UTC (semaine du 9/11 : 211,28 → 171,21 T). Le journal (jours lus avant) ne s'additionne plus au graphique :
    l'ancien code refusait par « forme incohérente » (raison fausse) ; il doit dire « historique révisé »."""
    lu = datetime(2026, 11, 21, 5, 55, tzinfo=UTC)
    row = orr.lire(RAW_21["chart"], RAW_21["week"], RAW_21["day"], lu)[0]
    assert row["semaines"][-2] == ["2026-11-09", 171.2123] and row["jour"][0] == "2026-11-20"
    d = orr.detail(row, HISTO_21_11)
    assert "refus" in d and "révisé" in d["refus"] and "211.3 → 171.2" in d["refus"] and -0.20 < d["revision"] < -0.18
    # journal cohérent avec le graphique (petite dérive < 3 %) : pas de refus « révisé »
    propre = [dict(o, precedente=171.2123 * (1.01 if i % 2 else 1.0)) for i, o in enumerate(HISTO_21_11)]
    assert "révisé" not in orr.detail(row, propre).get("refus", "")
