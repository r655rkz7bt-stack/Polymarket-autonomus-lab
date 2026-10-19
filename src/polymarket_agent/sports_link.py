"""Relier un marché sportif « Équipe A vs. Équipe B » à son match (scores officiels des ligues) et
aux cotes des bookmakers (AMELIORATION n°2 et 5, 17/10/2026).

Sources (observations déjà collectées, sources/sports.py et sources/odds_api.py) :
- scores : mlb_stats, nhl_stats, football_data → data {domicile, exterieur, score_domicile,
  score_exterieur, etat (« terminé », « en cours », « à venir »), debut} ;
- cotes : odds_api → data {domicile, exterieur, probabilites {équipe: probabilité}, debut}.

Rattachement prudent : les DEUX issues du marché doivent correspondre aux deux équipes (mots du
nom de l'issue tous présents dans le nom officiel, ex. « Dodgers » ⊂ « Los Angeles Dodgers »),
et le coup d'envoi du marché (Gamma gameStartTime), s'il est connu, à moins de 12 h de celui du
match. Au moindre doute : pas de rattachement (une erreur d'équipe coûterait toute la mise).
Résultat posé sur `market.sport` : {"etat", "gagnant" (indice de l'issue ou None), "score",
"ligue", "vu_le", "cotes" ([proba issue 0, proba issue 1] ou None), "cotes_le"}.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timedelta

from polymarket_agent.sources._util import parse_date

GAME_SOURCES = ("mlb_stats", "nhl_stats", "football_data")
ODDS_SOURCE = "odds_api"
FINISHED = "terminé"
MAX_START_GAP = timedelta(hours=12)


def _words(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode().lower()
    return [w for w in re.split(r"[^a-z0-9]+", text) if w and w not in ("fc", "cf", "sc", "the", "afc")]


def same_team(outcome: str, team: str) -> bool:
    """Tous les mots de l'issue sont dans le nom officiel de l'équipe (ou l'inverse)."""
    a, b = _words(outcome), _words(team)
    return bool(a) and bool(b) and (set(a) <= set(b) or set(b) <= set(a))


def _order(outcomes: list[str], home: str, away: str) -> tuple[str, str] | None:
    """(équipe de l'issue 0, équipe de l'issue 1), ou None si le rattachement n'est pas sûr."""
    if len(outcomes) != 2:
        return None
    o0, o1 = outcomes
    if same_team(o0, home) and same_team(o1, away) and not same_team(o0, away):
        return home, away
    if same_team(o0, away) and same_team(o1, home) and not same_team(o0, home):
        return away, home
    return None


def _close(market, start: str | None) -> bool:
    game_start = getattr(market, "game_start", None)
    when = parse_date(start) if start else None
    return game_start is None or when is None or abs(game_start - when) <= MAX_START_GAP


# Paris qui ne portent PAS sur le vainqueur du match (19/10/2026) : leurs deux issues sont aussi des
# noms d'équipes (« Spread: Titans (-3.5) » → Titans / Colts), mais le score officiel et les cotes
# des bookmakers (vainqueur) ne s'y appliquent pas. cotes_bookmakers les prenait pour le vainqueur :
# Patriots estimés à 75 % vendus 28 %, Colts achetés dans 3 paris du même match (−287 sur 14 paris).
NOT_WINNER = re.compile(r"spread|handicap|o/u|over/under|total|1h|2h|half|quarter|period|inning|"
                        r"map \d|game \d|set \d|round \d|exact score|both teams|first|player", re.IGNORECASE)


def winner_market(market) -> bool:
    """Le marché porte-t-il sur le vainqueur du match ? Type donné par Gamma s'il existe, sinon le
    libellé (« A vs. B » sans précision)."""
    kind = getattr(market, "sports_market_type", None)
    if kind:
        return kind == "moneyline"
    return not NOT_WINNER.search(str(market.question or ""))


def link(market, observations: list) -> dict | None:
    """Le match et les cotes du marché, d'après les observations les plus récentes."""
    outcomes = [str(o) for o in (market.outcomes or [])]
    if len(outcomes) != 2 or {o.lower() for o in outcomes} == {"yes", "no"} or not winner_market(market):
        return None
    game, odds = None, None
    for o in observations:
        d = o.data or {}
        if o.source not in GAME_SOURCES and o.source != ODDS_SOURCE:
            continue
        order = _order(outcomes, d.get("domicile", ""), d.get("exterieur", ""))
        if order is None or not _close(market, d.get("debut")):
            continue
        if o.source == ODDS_SOURCE:
            if odds is None or o.collected_at > odds[0].collected_at:
                odds = (o, order)
        elif game is None or o.collected_at > game[0].collected_at:
            game = (o, order)
    if game is None and odds is None:
        return None
    out: dict = {"etat": None, "gagnant": None, "score": None, "ligue": None, "vu_le": None,
                 "cotes": None, "cotes_le": None}
    if game is not None:
        o, (t0, t1) = game
        d = o.data
        out.update(etat=d.get("etat"), ligue=d.get("ligue"), vu_le=o.collected_at.isoformat(timespec="seconds"))
        try:
            score = {d["domicile"]: int(d["score_domicile"]), d["exterieur"]: int(d["score_exterieur"])}
        except (KeyError, TypeError, ValueError):
            score = None
        if score is not None:
            out["score"] = [score[t0], score[t1]]
            if d.get("etat") == FINISHED and score[t0] != score[t1]:
                out["gagnant"] = 0 if score[t0] > score[t1] else 1
    if odds is not None:
        o, (t0, t1) = odds
        probs = o.data.get("probabilites") or {}
        p0 = next((float(v) for k, v in probs.items() if same_team(k, t0)), None)
        p1 = next((float(v) for k, v in probs.items() if same_team(k, t1)), None)
        if p0 is not None and p1 is not None and p0 + p1 > 0:
            # Match nul possible (football) : les deux probabilités ne somment pas à 1 ; on les garde telles quelles.
            out.update(cotes=[round(p0, 4), round(p1, 4)], cotes_le=o.collected_at.isoformat(timespec="seconds"))
    return out


def attach(markets: list, observations: list) -> int:
    """Pose `market.sport` sur chaque marché sportif rattaché ; renvoie le nombre de rattachements."""
    pool = [o for o in observations if o.source in GAME_SOURCES or o.source == ODDS_SOURCE]
    n = 0
    for m in markets:
        info = link(m, pool) if pool else None
        m.sport = info
        n += info is not None
    return n


def age_minutes(iso: str | None, now: datetime) -> float | None:
    when = parse_date(iso) if iso else None
    return (now - when).total_seconds() / 60 if when else None
