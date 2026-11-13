"""Taux immobilier à 30 ans de Freddie Mac : barrière sur les relevés hebdomadaires (13/11/2026, piste n° 46,
experiments/taux_immobilier.md).

« Will the U.S. 30-year Fixed-Rate Mortgage hit 8.00% (HIGH) / 6.25% (LOW) by December 31, 2026? » se règle sur l'enquête
hebdomadaire de Freddie Mac (PMMS, publiée le jeudi, au centième) : OUI dès qu'un relevé d'une semaine finie au plus tard à la date
limite est ≥ (HIGH) ou ≤ (LOW) au niveau. Chance = part des fenêtres historiques de n relevés (depuis 1990 et depuis 2019, moyenne des
deux) où le relevé, décalé au niveau d'aujourd'hui, touche le niveau : les vraies trajectoires gardent les tendances et les queues
épaisses que la marche aléatoire perd (+0,89 en 7 relevés : 1,3-3 % des fenêtres réelles, 0,3 % au hasard). Le relevé suivant est
avancé de 0,7 × la variation du 10 ans du Trésor depuis la semaine du dernier relevé (bêta 0,6-0,77, résidu 0,05-0,07 sur 2019-2026).
Source : https://www.freddiemac.com/pmms/docs/PMMS_history.csv (robots.txt : /pmms/docs/ permis), sans clé.
"""
from __future__ import annotations

import csv
import io
import re
from datetime import date, datetime, timedelta

from polymarket_agent.http_client import HttpClient

URL = "https://www.freddiemac.com/pmms/docs/PMMS_history.csv"
BETA = 0.7
DEPUIS = (date(1990, 1, 1), date(2019, 1, 1))
_Q = re.compile(r"30-year Fixed-Rate Mortgage hit (\d+(?:\.\d+)?)% \((HIGH|LOW)\) by (\w+ \d{1,2}, \d{4})", re.IGNORECASE)


def parse_csv(text: str) -> list[tuple[str, float]]:
    out = []
    for r in csv.reader(io.StringIO(text or "")):
        try:
            out.append((datetime.strptime(r[0], "%m/%d/%Y").date().isoformat(), float(r[1])))
        except (IndexError, ValueError):
            continue
    return sorted(out)


def fetch_pmms(http: HttpClient, now: datetime) -> list[dict]:
    rows = [x for x in parse_csv(http.get_text(URL, headers={"User-Agent": "Mozilla/5.0"})) if x[0] >= DEPUIS[0].isoformat()]
    return [{"pmms": [list(x) for x in rows], "lu": now.isoformat()}] if rows else []


def question(q: str) -> tuple[float, bool, date] | None:
    """(niveau, hausse ?, date limite) ; None si ce n'est pas un marché de barrière Freddie Mac."""
    g = _Q.search(q or "")
    if not g:
        return None
    return float(g.group(1)), g.group(2).upper() == "HIGH", datetime.strptime(g.group(3), "%B %d, %Y").date()


def releves_restants(dernier: date, limite: date) -> int:
    """Jeudis (semaines) après le dernier relevé publié et au plus tard à la date limite."""
    n, d = 0, dernier + timedelta(days=7)
    while d <= limite:
        n, d = n + 1, d + timedelta(days=7)
    return n


def avance_dix_ans(dix_ans: list[list], dernier: date, today: date) -> float:
    """0,7 × (dernière clôture du 10 ans publiée avant aujourd'hui − moyenne lundi-mercredi de la semaine du dernier relevé)."""
    pts = {date.fromisoformat(d): float(v) for d, v in dix_ans or [] if date.fromisoformat(d) < today}
    semaine = [pts[dernier - timedelta(days=k)] for k in (1, 2, 3) if dernier - timedelta(days=k) in pts]
    apres = [d for d in pts if d >= dernier]   # l'enquête se ferme le mercredi : la clôture du jeudi de publication vient après
    if not semaine or not apres:
        return 0.0
    return BETA * (pts[max(apres)] - sum(semaine) / len(semaine))


def chance(pmms: list[list], niveau: float, hausse: bool, limite: date, now: datetime, dix_ans: list[list] | None = None,
           debut: date | None = None) -> float | None:
    """`debut` : création du marché (« any week ending after market creation ») ; sans elle, le 1er janvier de l'année limite."""
    today = now.date()
    pts = [(date.fromisoformat(d), float(v)) for d, v in pmms if date.fromisoformat(d) < today]
    if len(pts) < 400:
        return None
    debut = debut or date(limite.year, 1, 1)
    annee = [v for d, v in pts if debut < d <= limite]
    if any((v >= niveau - 1e-9) if hausse else (v <= niveau + 1e-9) for v in annee):
        return 1.0   # déjà touché : le marché se règle
    n = releves_restants(pts[-1][0], limite)
    if n <= 0:
        return 0.0
    cur = pts[-1][1] + avance_dix_ans(dix_ans or [], pts[-1][0], today)
    parts = []
    for depuis in DEPUIS:
        serie = [v for d, v in pts if d >= depuis]
        hit = tot = 0
        for i in range(len(serie) - n):
            moves = [round(cur + v - serie[i], 2) for v in serie[i + 1:i + n + 1]]
            hit += any((m >= niveau - 1e-9) if hausse else (m <= niveau + 1e-9) for m in moves)
            tot += 1
        if tot:
            parts.append((hit + 0.5) / (tot + 1))
    return sum(parts) / len(parts) if parts else None


def attach_immobilier(markets, db, now: datetime, heures: tuple[int, int] = (0, 12), max_age_hours: float = 30.0) -> int:
    if db is None or not heures[0] <= now.hour < heures[1]:
        return 0   # en séance américaine, le marché voit le 10 ans du jour, pas nous
    from polymarket_agent.references import _load
    from polymarket_agent.sources._util import parse_date
    seen, rows = _load(db, "ref:taux_immobilier")
    if seen is None or not rows:
        return 0
    lu = parse_date(rows[0].get("lu") or "")
    if lu is None or (now - lu).total_seconds() > max_age_hours * 3600:
        return 0
    _, taux = _load(db, "ref:taux_tresor")
    dix = ((taux or [{}])[0].get("closes") or {}).get("10") if taux else None
    n = 0
    for m in markets:
        q = question(m.question or "")
        if q is None or [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        niveau, hausse, limite = q
        cree = getattr(m, "created_at", None)
        if cree is None:
            continue   # la fenêtre commence à la création du marché : sans elle, on ne sait pas ce qui est déjà touché
        p = chance(rows[0]["pmms"], niveau, hausse, limite, now, dix, cree.date())
        if p is None or p >= 1.0:
            continue
        dernier = rows[0]["pmms"][-1]
        m.references = dict(m.references or {}, taux_immobilier={
            "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "vu_le": seen.isoformat(),
            "titre": f"Freddie Mac {dernier[1]:.2f} ({dernier[0]}), {'≥' if hausse else '≤'} {niveau:.2f} d'ici le {limite} : {p:.3f}"})
        n += 1
    return n
