"""Tableau de bord : contenu, sécurité de l'affichage, fréquence de génération."""

from __future__ import annotations

import json
import re
from datetime import timedelta
from decimal import Decimal

import yaml

from conftest import KEY, NOW, ROOT, buy, make_book
from polymarket_agent import dashboard
from polymarket_agent.ledger import Ledger
from polymarket_agent.persistence import Database

EVIL = "</script><script>alert(1)</script><img src=x onerror=alert(2)>"
SETTINGS = {"paths": {"ledger": "ledger/ledger.jsonl", "bankruptcy_lock": "ledger/BANKRUPT.lock",
                      "shadow_dir": "ledger/fantome"},
            "dashboard": {"output_dir": "site", "every_minutes": 30}, "llm": {"max_calls_per_day": 200}}


def _setup(tmp_path):
    main = Ledger.create(tmp_path / "ledger" / "ledger.jsonl", KEY, tmp_path / "ledger" / "BANKRUPT.lock",
                         "1000", now=NOW)
    shadow_path = tmp_path / "ledger" / "fantome" / "test_v0.jsonl"
    shadow = Ledger.create(shadow_path, KEY, shadow_path.with_suffix(".BANKRUPT.lock"), "1000", now=NOW)
    buy(main, "b1", token="tA", shares="10", price="0.5")
    buy(shadow, "b2", token="tB", shares="100", price="0.8", event="ev2")
    shadow.record_settlement(op_id="s2", token_id="tB", payout_per_share="1", resolution="Yes", now=NOW)
    db = Database(tmp_path / "db.sqlite")
    db.conn.execute("INSERT INTO market_snapshots (cycle_id, collected_at, market_id, question, eligible) "
                    "VALUES ('c1', ?, 'm-tA', ?, 1)", (NOW.isoformat(), EVIL))
    db.save_books("c1", [make_book("tA", bids=(("0.6", "100"),), asks=(("0.61", "100"),))])
    for i, sources in enumerate([{"rss": "ok (3 observations)", "gdelt": "indisponible : 429"},
                                 {"rss": "pas encore (fréquence)", "gdelt": "pas encore (fréquence)"}]):
        db.start_cycle(f"c{i}", NOW + timedelta(minutes=5 * i))
        db.finish_cycle(f"c{i}", NOW + timedelta(minutes=5 * i, seconds=30), "OK", summary={"sources": sources})
    return main, {"test_v0": shadow}, db


def test_collect_reads_ledgers_and_db(tmp_path):
    main, shadows, db = _setup(tmp_path)
    data = dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW + timedelta(minutes=10))
    assert data["capital"]["palier_suivant"] == "1500.0"
    assert data["capital"]["solde_disponible"] == "995.0000"
    assert data["capital"]["gains_latents"] == "1.0000"  # 10 parts marquées au bid 0,6
    assert [s["nom"] for s in data["arene"]] == ["test_v0"]
    assert data["arene"][0]["operations"] == 1 and data["arene"][0]["capital"] == 1020.0
    main_pos = [p for p in data["positions"] if p["portefeuille"] == "principal"]
    assert main_pos[0]["marche"] == EVIL and main_pos[0]["latent"] == 1.0
    assert data["cloturees"][0]["resultat"] == 20.0
    assert data["surveilles"][0]["marche"] == EVIL
    db.close()


def test_regression_source_status_skips_not_due(tmp_path):
    """Le dernier cycle ne fait souvent que « pas encore (fréquence) » : on affiche le
    dernier résultat réel de chaque source, sinon la page ne dit jamais rien d'utile."""
    main, shadows, db = _setup(tmp_path)
    data = dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW + timedelta(minutes=10))
    assert data["sources"]["etat"] == {"rss": "ok (3 observations)", "gdelt": "indisponible : 429"}
    db.close()


def test_untrusted_text_cannot_close_the_script_tag(tmp_path):
    main, shadows, db = _setup(tmp_path)
    data = dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW)
    db.close()
    page = dashboard.render(data)
    blob = re.search(r'<script type="application/json" id="data">(.*?)</script>', page, re.S).group(1)
    assert "</script" not in blob
    assert json.loads(blob)["surveilles"][0]["marche"] == EVIL  # le texte reste intact une fois lu


def test_template_never_injects_html():
    """Les textes externes passent par textContent : aucune insertion de HTML brut."""
    template = (ROOT / "src" / "polymarket_agent" / "dashboard_template.html").read_text(encoding="utf-8")
    for forbidden in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
        assert forbidden not in template
    assert template.count("__DATA__") == 1
    assert "<script src" not in template  # aucune dépendance externe


def test_full_document_and_fragment(tmp_path):
    main, shadows, db = _setup(tmp_path)
    data = dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW)
    db.close()
    full, fragment = dashboard.render(data), dashboard.render(data, full_document=False)
    assert full.startswith("<!doctype html>") and '<html lang="fr">' in full
    assert "<html" not in fragment and "<!doctype" not in fragment
    assert fragment.startswith("<title>")


def test_build_writes_site_and_is_due(tmp_path):
    main, shadows, db = _setup(tmp_path)
    out = tmp_path / "site"
    assert dashboard.is_due(out, NOW, 30)
    page = dashboard.build(SETTINGS, tmp_path, KEY, db, now=NOW)
    db.close()
    assert page == out / "index.html" and page.exists()
    assert json.loads((out / "data.json").read_text(encoding="utf-8"))["genere_le"] == NOW.isoformat()
    assert not dashboard.is_due(out, NOW + timedelta(minutes=20), 30)
    assert dashboard.is_due(out, NOW + timedelta(minutes=30), 30)


def test_downsample_keeps_last_point():
    curve = [(f"t{i}", Decimal(i)) for i in range(1000)]
    out = dashboard._downsample(curve, 50)
    assert len(out) == 50 and out[-1] == ["t999", 999.0] and out[0] == ["t0", 0.0]


def test_page_refreshes_itself_from_its_own_data_file():
    """Actualisation automatique : la page relit data.json (même site, sans cache) et se recharge
    seulement si le cycle a publié de nouvelles données."""
    template = (ROOT / "src" / "polymarket_agent" / "dashboard_template.html").read_text(encoding="utf-8")
    assert 'fetch("data.json?t="' in template and 'cache: "no-store"' in template
    assert "fresh.genere_le !== D.genere_le" in template and "document.hidden" in template
    settings = yaml.safe_load((ROOT / "config" / "settings.yaml").read_text(encoding="utf-8"))
    assert 6 <= settings["dashboard"]["every_minutes"] <= 30  # GitHub Pages : ~10 publications par heure au plus


def test_pulse_and_system_vitals_feed_the_beating_heart(tmp_path):
    """Organisme vivant : le pouls (derniers cycles, durée, erreurs) et les constantes du système
    nourrissent le cœur et le journal vital de la page ; la règle n°1 l'arrête (aucun battement)."""
    main, shadows, db = _setup(tmp_path)
    data = dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW + timedelta(minutes=10))
    db.close()
    pulse = data["sante"]["pouls"]
    assert [c["date"] for c in pulse] == sorted(c["date"] for c in pulse) and len(pulse) == 2
    assert pulse[0]["duree"] == 30.0 and pulse[0]["statut"] == "OK" and pulse[0]["erreur"] is False
    assert data["systeme"]["strategies_actives"] == 1 and data["systeme"]["ordres_poses"] == 0
    template = (ROOT / "src" / "polymarket_agent" / "dashboard_template.html").read_text(encoding="utf-8")
    assert 'id="heart"' in template and "C.faillite ? 0" in template  # faillite : le cœur s'arrête
    assert "prefers-reduced-motion" in template
    # Cœur anatomique : les constantes sont des légendes posées autour, hors de portée du battement.
    for part in ("aorte", "veine cave", "nœud sinusal", "ventricule gauche", "ventricule droit", "apex"):
        assert part in template
    assert "placeLabels" in template and "jamais\n      // d'expansion" not in template


def test_independent_audit_is_shown(tmp_path):
    """Le résultat de l'audit indépendant (branche data, audit/etat.json) apparaît sur la page."""
    main, shadows, db = _setup(tmp_path)
    (tmp_path / "_data" / "audit").mkdir(parents=True)
    (tmp_path / "_data" / "audit" / "etat.json").write_text(json.dumps(
        {"verifiees": 80, "non_verifiables": 2, "anomalies": [{"portefeuille": "principal", "detail": "achat à 0.1"}],
         "derniere_execution": "2026-10-15T19:30:00+00:00"}), encoding="utf-8")
    data = dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW)
    db.close()
    assert data["audit"]["verifiees"] == 80 and data["audit"]["anomalies"] == 1
    assert data["audit"]["dernieres_anomalies"][0]["detail"] == "achat à 0.1"


def test_today_tells_the_last_24_hours_in_plain_french(tmp_path):
    main, shadows, db = _setup(tmp_path)
    data = dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW + timedelta(minutes=10))
    texts = {t["sujet"]: [] for t in data["aujourdhui"]}
    for t in data["aujourdhui"]:
        texts[t["sujet"]].append(t["texte"])
    assert set(texts) == {"capital", "arene", "operations", "machine"}
    assert any("Aucune stratégie n'a encore prouvé" in t for t in texts["arene"])
    assert any(t.startswith("2 achats et 1 vente ou règlement") for t in texts["operations"])
    assert any("1 opération clôturée : 1 gagnante(s), 0 perdante(s), résultat net +20,00 €" in t
               for t in texts["operations"])
    assert any("Meilleure stratégie qui a tradé : test_v0, 1 020,00 € réalisés (+20,00 €)" in t for t in texts["arene"])
    assert "1 sur 1 stratégie(s) ayant tradé gagnent de l'argent." in texts["arene"]
    assert any(t.startswith("2 cycles en 24 h") and "aucun en erreur" in t for t in texts["machine"])
    assert any("en panne au dernier essai : gdelt" in t for t in texts["machine"])
    # Le texte venu de l'extérieur (question du marché) reste une donnée : la page l'insère en texte.
    assert "textContent" in (ROOT / "src/polymarket_agent/dashboard_template.html").read_text(encoding="utf-8")
    db.close()


def test_arena_ranking_history_one_photo_per_hour(tmp_path):
    from polymarket_agent import arena_history
    main, shadows, db = _setup(tmp_path)
    dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW)
    dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW + timedelta(minutes=10))  # trop tôt
    rows = [{"nom": "a", "capital": 1010, "operations": 3, "eliminee": False},
            {"nom": "test_v0", "capital": 1000, "operations": 1, "eliminee": False}]
    assert arena_history.record(db, rows, NOW + timedelta(hours=1))
    assert not arena_history.record(db, rows, NOW + timedelta(hours=1, minutes=20))
    h = arena_history.series(db, NOW + timedelta(hours=2))
    assert len(h["dates"]) == 2 and h["strategies"]["test_v0"] == [1, 2] and h["strategies"]["a"] == [None, 1]
    assert arena_history.rank_at(db, NOW + timedelta(minutes=30)) == {"test_v0": 1}
    # « Aujourd'hui » compare à la photo d'il y a 24 h (a 1re, test_v0 2e) : test_v0 repasse devant.
    from polymarket_agent import today
    data = dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW + timedelta(hours=25))
    data["arene"] = [dict(r, sante=None) for r in reversed(rows)]
    entries = {n: [] for n in ("principal",)}
    texts = [t["texte"] for t in today.build(data, entries, {}, db, NOW + timedelta(hours=25))]
    assert "Plus forte remontée : test_v0, +1 place depuis hier." in texts
    assert "Plus forte chute : a, −1 place depuis hier." in texts
    db.close()


def test_last_research_actions_are_read_from_the_journal(tmp_path):
    journal = tmp_path / "experiments" / "journal_recherche.md"
    journal.parent.mkdir()
    journal.write_text("""# Journal de recherche

## 2026-10-16 (passage chercheur, ~10 h UTC)

- **Lu** : CLAUDE.md.
- **Fait** : deux variantes « patientes » `meteo_prevision_patiente`
  et `news_momentum_patiente` dans l'arène.
- **Pas fait** : chantier sport.

## 2026-10-16 (session avec Etienne, ~6 h UTC) — météo

- **Fait** : stratégie meteo_prevision.

## 2026-10-15 (passage chercheur, ~20 h UTC)

- **Fait** : variante market_structure_patiente.
""", encoding="utf-8")
    log = dashboard.research_log(tmp_path)
    assert [r["date"] for r in log] == ["2026-10-16", "2026-10-15"]  # sessions avec Etienne exclues
    assert log[0]["quand"] == "~10 h UTC"
    assert log[0]["fait"] == "deux variantes « patientes » meteo_prevision_patiente et news_momentum_patiente dans l'arène."
    assert log[0]["details"] == [{"titre": "Pas fait", "texte": "chantier sport."}]
    assert dashboard.research_log(tmp_path / "absent") == []
    main, shadows, db = _setup(tmp_path)
    data = dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW)
    assert data["chercheur"][0]["date"] == "2026-10-16"
    db.close()


def test_layout_is_set_by_the_researcher_with_guardrails(tmp_path):
    """17/10/2026 : le chercheur règle la mise en page (config/dashboard.yaml) ; le résumé et le
    capital (règle n°1) ne peuvent jamais être cachés ; « À la une » est borné."""
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "dashboard.yaml").write_text(yaml.safe_dump({
        "ordre": ["arene", "inconnu", "resume", "arene"], "masquer": ["capital", "resume", "systeme", "x"],
        "a_la_une": {"date": "2026-10-17", "points": [EVIL] + [f"point {i}" for i in range(9)] + ["y" * 400]}}),
        encoding="utf-8")
    lay = dashboard.layout(tmp_path)
    assert lay["ordre"] == ["arene", "resume"] and lay["masquer"] == ["systeme"]
    assert len(lay["a_la_une"]["points"]) == 5 and lay["a_la_une"]["points"][0] == EVIL
    assert dashboard.layout(tmp_path / "absent") == {"ordre": [], "masquer": [], "a_la_une": {"date": "", "points": []}}
    main, shadows, db = _setup(tmp_path)
    data = dashboard.collect(main, shadows, db, SETTINGS, tmp_path, now=NOW)
    page = dashboard.render(data)
    assert data["mise_en_page"] == lay and EVIL not in page  # texte du chercheur échappé comme le reste
    repo = dashboard.layout(ROOT)  # la configuration du dépôt est valide
    assert repo["ordre"][0] in ("organisme", "resume") and not set(repo["masquer"]) & {"organisme", "resume", "capital"}
