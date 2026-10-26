"""27/10/2026 : Gamma refuse les décalages (`offset`) au-delà de ≈ 2 100 sur /events (« offset too large, use /events/keyset ») ; un script qui prenait cette
réponse pour la fin de la liste ne lisait que les ≈ 2 100 événements les plus récents d'une série (ATP : du 14/09 au 26/10 seulement ; MLB, NFL, tennis et CS2
manquaient presque entièrement de la fenêtre février-août de `totaux_sports.md`). Les nouveaux relevés d'événements doivent lire `/events/keyset`."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Relevés écrits avant le 27/10/2026 : ils paginent par `offset`. Ne pas en ajouter ; une analyse qui s'appuie sur l'un d'eux doit être refaite avec `keyset`.
ANCIENS = {
    "experiments/meteo_backtest/collect.py", "experiments/score_exact_poisson/sonde_compte.py", "experiments/score_exact_poisson/sonde_limites.py",
    "experiments/vague_volume_backtest/releve_marches.py", "experiments/vague_volume_backtest/releve_echanges.py", "experiments/score_exact/releve_evenements.py",
    "experiments/tennis_apres/scripts/releve_marches.py", "experiments/vague_opinion/vague_opinion.py", "experiments/tennis_oos/scripts/releve_marches.py",
    "experiments/saison_sport/scripts/releve_evenements.py", "experiments/nba/scripts/releve_marches.py", "experiments/vingt_pistes/scripts/mentions_releve_evenements.py",
    "experiments/vingt_pistes/scripts/nhl_releve_calendrier.py", "experiments/achat_echelonne/releve_univers.py", "experiments/tennis/scripts/releve_marches.py",
    "experiments/tennis/scripts/releve_sports.py", "experiments/tennis/scripts/releve_esport.py", "experiments/btts/scripts/releve_evenements.py",
    "experiments/totaux_sports/scripts/releve_avant.py", "experiments/totaux_sports/scripts/releve_evenements.py", "experiments/ecarts_sports/scripts/releve_evenements.py",
    "experiments/ensemble_meteo/releve.py", "experiments/ufc_coherence/scripts/releve.py", "experiments/prix_payes/mentions_releve_echanges.py",
    "experiments/elections_non/scripts/releve_evenements.py", "experiments/apres_fin_match/scripts/releve.py", "experiments/avant_match_50_50/scripts/releve.py",
    "experiments/courbe_de_risque/releve.py", "experiments/seismes/scripts/releve.py", "experiments/primaires/scripts/releve_evenements.py",
    "experiments/bo3_coherence/releve.py", "experiments/non_aux_drames/releve.py", "experiments/props_sport/scripts/releve_evenements.py",
    "experiments/queues_tranches/releve_evenements.py", "experiments/rallies_trump/scripts/prix_payes_mentions.py", "experiments/smart_money/collect.py",
    "experiments/sous_marches_football/scripts/inventaire.py", "experiments/sous_marches_football/scripts/releve_evenements.py",
    "experiments/tennis_sets_coherence/sonde_echanges.py", "experiments/tennis_sets_coherence/sonde_types.py", "experiments/toucher_avant_fin/releve.py",
    "experiments/void_5050/scripts/releve_void.py",
}


def _pagine_par_offset(texte: str) -> bool:
    return "gamma-api.polymarket.com/events" in texte and "keyset" not in texte and re.search(r"offset", texte) is not None


def test_nouveaux_releves_gamma_lisent_le_curseur():
    fautifs = []
    for chemin in sorted((ROOT / "experiments").rglob("*.py")):
        rel = chemin.relative_to(ROOT).as_posix()
        if rel in ANCIENS:
            continue
        if _pagine_par_offset(chemin.read_text(encoding="utf-8", errors="ignore")):
            fautifs.append(rel)
    assert not fautifs, f"relevé d'événements Gamma par `offset` (tronqué à ≈ 2 100) : utiliser /events/keyset et `after_cursor` — {fautifs}"


def test_le_detecteur_reconnait_le_defaut_reel():
    """Le script du 26/10 (releve_avant.py) est exactement le cas qui a tronqué les relevés."""
    assert _pagine_par_offset((ROOT / "experiments/totaux_sports/scripts/releve_avant.py").read_text(encoding="utf-8"))
    assert not _pagine_par_offset((ROOT / "experiments/totaux_sports/scripts/releve_complet.py").read_text(encoding="utf-8"))
