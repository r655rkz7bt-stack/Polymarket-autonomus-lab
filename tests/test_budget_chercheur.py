"""Budget de temps du chercheur (décisions d'Etienne du 21/10/2026 : ~70 % du quota du jour,
de la marge sur la limite de la semaine)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import yaml

from conftest import ROOT
from polymarket_agent import budget_chercheur as bc

UTC = timezone.utc
CFG = {"demarrage": "2026-10-24T00:00:00+00:00", "remise_a_zero": {"jour": "samedi", "heure_utc": 0},
       "budget_semaine_minutes": 3500, "duree_min_minutes": 30, "duree_max_minutes": 135,
       "avant_demarrage_minutes": [45, 90], "passages_paris": ["01:54", "06:54", "11:54", "16:54", "21:54"]}


def test_week_starts_at_the_saturday_reset():
    assert bc.week_start(datetime(2026, 10, 24, 0, 0, tzinfo=UTC), CFG) == datetime(2026, 10, 24, tzinfo=UTC)
    assert bc.week_start(datetime(2026, 10, 23, 23, 59, tzinfo=UTC), CFG) == datetime(2026, 10, 17, tzinfo=UTC)
    assert bc.week_start(datetime(2026, 10, 29, 12, 0, tzinfo=UTC), CFG) == datetime(2026, 10, 24, tzinfo=UTC)


def test_remaining_passes_count_the_one_starting_and_follow_paris_time():
    # Samedi 24/10 00:00 UTC : le passage de 01:54 (Paris, heure d'été) a eu lieu vendredi à 23:54 UTC ;
    # celui du dimanche 25/10 à 01:54 est encore en heure d'été (23:54 UTC samedi) ; celui du samedi 31/10
    # à 01:54 (heure d'hiver, 00:54 UTC) appartient à la semaine suivante : 4 + 5 + 5 × 5 = 34.
    assert bc.remaining_passes(datetime(2026, 10, 24, 0, 0, tzinfo=UTC), CFG) == 34
    # Le passage de 16:54 (Paris, heure d'hiver = 15:54 UTC) a démarré il y a 5 minutes : il compte.
    late = datetime(2026, 10, 30, 15, 59, tzinfo=UTC)
    assert bc.remaining_passes(late, CFG) == 2  # 16:54 et 21:54 ; 01:54 samedi (00:54 UTC) : semaine suivante


def test_target_spreads_what_is_left_and_never_spends_beyond_the_budget():
    now = datetime(2026, 10, 24, 4, 56, tzinfo=UTC)  # passage de 06:54 à Paris (heure d'été)
    first = bc.target(now, CFG, [])
    assert not first["avant_demarrage"] and first["minutes"] == round(3500 / first["restants"])
    # Passages précédents trop longs : celui-ci raccourcit ; budget épuisé : durée minimale et alerte.
    rows = [{"debut_utc": "2026-10-24T00:00:00+00:00", "minutes": "3000"}]
    assert bc.target(now, CFG, rows)["minutes"] < first["minutes"]
    spent = bc.target(now, CFG, [{"debut_utc": "2026-10-24T00:00:00+00:00", "minutes": "4000"}])
    assert spent["minutes"] == 30 and spent["epuise"] and "ÉPUISÉ" in spent["texte"]
    # Passages de la semaine d'avant : ne comptent pas.
    old = [{"debut_utc": "2026-10-23T10:00:00+00:00", "minutes": "4000"}]
    assert bc.target(now, CFG, old)["minutes"] == first["minutes"]
    # Avant le démarrage : 45 à 90 minutes, comme avant.
    before = bc.target(datetime(2026, 10, 22, 10, 0, tzinfo=UTC), CFG, [])
    assert before["avant_demarrage"] and (before["min"], before["minutes"]) == (45, 90)


def test_rows_are_appended_and_read_back(tmp_path):
    path = tmp_path / "budget.csv"
    start = datetime(2026, 10, 24, 4, 55, tzinfo=UTC)
    assert bc.append_row(path, start, start + timedelta(minutes=104, seconds=30)) == 104.5
    bc.append_row(path, start + timedelta(hours=5), start + timedelta(hours=6))
    rows = bc.read_rows(path)
    assert len(rows) == 2 and bc.used_minutes(rows, datetime(2026, 10, 24, tzinfo=UTC)) == 164.5


def test_repository_config_is_valid_and_leaves_a_margin():
    cfg = yaml.safe_load((ROOT / "config" / "chercheur.yaml").read_text(encoding="utf-8"))
    assert len(cfg["passages_paris"]) == 5 and cfg["duree_min_minutes"] < cfg["duree_max_minutes"]
    # Au plus 2 h 15 par passage et un budget de la semaine sous 35 passages de 2 h (marge sur la limite).
    assert cfg["duree_max_minutes"] <= 135 and cfg["budget_semaine_minutes"] <= 35 * 120
    bc.target(datetime(2026, 10, 25, 12, 0, tzinfo=UTC), cfg, [])
