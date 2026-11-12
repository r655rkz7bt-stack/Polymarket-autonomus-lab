"""Sentiment des consommateurs de l'université du Michigan : le PRÉLIMINAIRE contre les tranches du FINAL (12/11/2026, piste n° 35,
experiments/michigan_preliminaire.md).

« Will UMich Consumer Sentiment be between 49.0 and 51.9 / at least 55.0 / below 40.0 in <mois>? » se règle sur le chiffre FINAL
(publié deux semaines après le préliminaire). La page d'accueil des Surveys of Consumers (sca.isr.umich.edu, sans clé, pas de
robots.txt) affiche « Preliminary Results for <Mois> <Année> … Index of Consumer Sentiment <x> ». Final = préliminaire + révision ;
révision ~ N(0 ; SD), SD = 1,8 par défaut (2026 : +0,6, +0,8, +0,3, +1,7 ; 2024-2025 de mémoire : −3,1 à +2,9). Sur 4 mois réglés
aux vrais échanges : 18 paris, 13 gagnés pour 9,6 attendus, +35 % par mise (4 mois sur 4 positifs).
"""
from __future__ import annotations

import html
import re
from datetime import datetime
from statistics import NormalDist

from polymarket_agent.http_client import HttpClient

PAGE = "https://www.sca.isr.umich.edu/"
MOIS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
_RES = re.compile(r"(Preliminary|Final) Results for (\w+) (\d{4})")
_ICS = re.compile(r"Index of Consumer Sentiment\s+(\d{2,3}\.\d)")
_Q = re.compile(r"^Will UMich Consumer Sentiment be (below (\d+\.\d)|between (\d+\.\d) and (\d+\.\d)|at least (\d+\.\d)) in (\w+)\?",
                re.IGNORECASE)


def parse_page(text: str) -> dict | None:
    x = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text or "")))
    r, v = _RES.search(x), _ICS.search(x)
    if not r or not v or r.group(2) not in MOIS:
        return None
    return {"etat": "preliminaire" if r.group(1) == "Preliminary" else "final", "mois": f"{r.group(3)}-{MOIS.index(r.group(2)) + 1:02d}",
            "ics": float(v.group(1))}


def fetch_michigan(http: HttpClient, now: datetime) -> list[dict]:
    row = parse_page(http.get_text(PAGE, headers={"User-Agent": "Mozilla/5.0"}))
    return [dict(row, lu=now.isoformat())] if row else []


def tranche(question: str) -> tuple[float, float, str] | None:
    """(bas, haut exclu, nom du mois) ; valeurs publiées au dixième : « 49.0 à 51.9 » = [49,0 ; 52,0)."""
    g = _Q.match(question or "")
    if not g:
        return None
    if g.group(2):
        return (-1e9, float(g.group(2)), g.group(6))
    if g.group(3):
        return (float(g.group(3)), round(float(g.group(4)) + 0.1, 1), g.group(6))
    return (float(g.group(5)), 1e9, g.group(6))


def p_tranche(prelim: float, bas: float, haut: float, sd: float = 1.8) -> float:
    n = NormalDist(prelim, sd)
    return n.cdf(haut - 0.05) - n.cdf(bas - 0.05)


def attach_michigan(markets, db, now: datetime, sd: float = 1.8, max_age_hours: float = 6.0) -> int:
    if db is None:
        return 0
    from polymarket_agent.references import _load
    from polymarket_agent.sources._util import parse_date
    seen, rows = _load(db, "ref:michigan")
    if seen is None or not rows:
        return 0
    row = rows[0]
    lu = parse_date(row.get("lu") or "")
    if lu is None or (now - lu).total_seconds() > max_age_hours * 3600 or row.get("etat") != "preliminaire":
        return 0  # final publié : le marché est réglé, plus rien à prévoir
    annee, mois = int(row["mois"][:4]), int(row["mois"][5:])
    n = 0
    for m in markets:
        t = tranche(m.question or "")
        if t is None or [str(o).lower() for o in m.outcomes] != ["yes", "no"] or t[2] != MOIS[mois - 1]:
            continue
        if m.end_date is not None and (m.end_date.year, m.end_date.month) != (annee, mois) and m.end_date.month != mois % 12 + 1:
            continue  # même nom de mois, autre année
        p = p_tranche(float(row["ics"]), t[0], t[1], sd)
        m.references = dict(m.references or {}, michigan={
            "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "vu_le": seen.isoformat(),
            "titre": f"préliminaire {MOIS[mois - 1]} {annee} = {row['ics']:.1f}, révision ±{sd} : {p:.3f}"})
        n += 1
    return n
