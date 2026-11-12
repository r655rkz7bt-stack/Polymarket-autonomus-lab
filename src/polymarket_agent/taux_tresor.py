"""Taux du Trésor américain : barrière sur les CLÔTURES quotidiennes publiées (12/11/2026, piste n° 43, experiments/taux_tresor.md).

« Will the 10-year Treasury yield hit 5.06% in November? » / « … dip below 4.82% in November? » / « … before 2027? » se règlent sur
la colonne de la durée dans « Daily Treasury Par Yield Curve Rates » (home.treasury.gov, une valeur par jour ouvré, au centième) :
« hit » = une clôture ≥ niveau, « dip below » = une clôture < niveau, entre deux dates écrites dans la description. Chance = marche
aléatoire sans dérive des clôtures restantes, écart-type = variations quotidiennes des 60 derniers jours ouvrés × K (K = 1,3 : sur
septembre-octobre 2026, K 1,2-1,4 bat le prix, K 1,0 l'égale). Le marché connaît les cours en séance : la chance n'est donnée que
la nuit (00-12 h UTC, marché américain fermé), comme dans le test (décision à 02 h UTC). Source : CSV de l'année (robots.txt :
tout permis), 1 appel par heure.
"""
from __future__ import annotations

import csv
import io
import math
import random
import re
from datetime import date, datetime, timedelta

from polymarket_agent.http_client import HttpClient

CSV = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{y}/all"
       "?type=daily_treasury_yield_curve&field_tdr_date_value={y}&page&_format=csv")
COLONNES = {2: "2 Yr", 5: "5 Yr", 10: "10 Yr", 30: "30 Yr"}
# Jours sans clôture publiée (marché obligataire fermé) d'ici début 2027 ; les autres jours ouvrés comptent.
FERIES = {date(2026, 11, 11), date(2026, 11, 26), date(2026, 12, 25), date(2027, 1, 1), date(2027, 1, 18), date(2027, 2, 15)}
_Q = re.compile(r"^Will the (\d+)-year Treasury yield (hit|dip below) (\d+(?:\.\d+)?)% (?:in \w+|before \d{4})\?", re.IGNORECASE)
_W = re.compile(r"between (\w+ \d{1,2}, \d{4}) and (\w+ \d{1,2}, \d{4})")


def parse_csv(text: str) -> dict[int, list[tuple[str, float]]]:
    """{durée: [(AAAA-MM-JJ, taux), …]} du plus ancien au plus récent."""
    out: dict[int, list[tuple[str, float]]] = {k: [] for k in COLONNES}
    for r in csv.DictReader(io.StringIO(text or "")):
        try:
            d = datetime.strptime(r["Date"], "%m/%d/%Y").date().isoformat()
        except (KeyError, ValueError):
            continue
        for k, col in COLONNES.items():
            try:
                out[k].append((d, float(r[col])))
            except (KeyError, TypeError, ValueError):
                continue
    return {k: sorted(v) for k, v in out.items() if v}


def fetch_taux(http: HttpClient, now: datetime) -> list[dict]:
    h = {"User-Agent": "Mozilla/5.0"}
    closes = parse_csv(http.get_text(CSV.format(y=now.year), headers=h))
    if not closes or min(len(v) for v in closes.values()) < 70:   # janvier : l'année d'avant complète la fenêtre de 60 jours
        old = parse_csv(http.get_text(CSV.format(y=now.year - 1), headers=h))
        closes = {k: sorted(set(old.get(k, [])) | set(closes.get(k, []))) for k in COLONNES if old.get(k) or closes.get(k)}
    if not closes:
        return []
    return [{"closes": {str(k): [list(x) for x in v[-90:]] for k, v in closes.items()}, "lu": now.isoformat()}]


def question(q: str, description: str = "") -> tuple[int, bool, float, date, date] | None:
    """(durée, hausse ?, niveau, début, fin) ; None si ce n'est pas un marché de barrière du Trésor."""
    g, w = _Q.match(q or ""), _W.search(description or "")
    if not g or not w:
        return None
    a, b = (datetime.strptime(x, "%B %d, %Y").date() for x in w.groups())
    return int(g.group(1)), g.group(2).lower() == "hit", float(g.group(3)), a, b


def jours_restants(debut: date, fin: date) -> list[date]:
    out, x = [], debut
    while x <= fin:
        if x.weekday() < 5 and x not in FERIES:
            out.append(x)
        x += timedelta(days=1)
    return out


def touche(v: float, niveau: float, hausse: bool) -> bool:
    """Valeur publiée au centième : « hit » = ≥ niveau, « dip below » = strictement sous le niveau."""
    v = round(v, 2)
    return v >= niveau - 1e-9 if hausse else v < niveau - 1e-9


def p_barriere(x0: float, sd: float, niveau: float, hausse: bool, n_jours: int, n: int = 4000, seed: int = 7) -> float:
    if n_jours <= 0:
        return 0.0
    rng, hit = random.Random(seed), 0
    for _ in range(n):
        x = x0
        for _j in range(n_jours):
            x += rng.gauss(0, sd)
            if touche(x, niveau, hausse):
                hit += 1
                break
    return (hit + 0.5) / (n + 1)


def chance(closes: list[list], niveau: float, hausse: bool, a: date, b: date, now: datetime, k: float = 1.3) -> float | None:
    """Chance qu'une clôture de [a, b] touche le niveau, d'après les clôtures publiées AVANT aujourd'hui."""
    today = now.date()
    pts = [(date.fromisoformat(d), float(v)) for d, v in closes if date.fromisoformat(d) < today]
    if len(pts) < 61 or today > b:
        return None
    if any(touche(v, niveau, hausse) for d, v in pts if a <= d <= b):
        return 1.0   # déjà touché : le marché se règle (rien à acheter)
    ch = [pts[i][1] - pts[i - 1][1] for i in range(len(pts) - 60, len(pts))]
    sd = k * math.sqrt(sum(c * c for c in ch) / len(ch))
    return p_barriere(pts[-1][1], sd, niveau, hausse, len(jours_restants(max(a, today), b)))


def attach_taux(markets, db, now: datetime, k: float = 1.3, heures: tuple[int, int] = (0, 12), max_age_hours: float = 3.0) -> int:
    if db is None or not heures[0] <= now.hour < heures[1]:
        return 0   # en séance américaine, le marché voit le cours du jour, pas nous
    from polymarket_agent.references import _load
    from polymarket_agent.sources._util import parse_date
    seen, rows = _load(db, "ref:taux_tresor")
    if seen is None or not rows:
        return 0
    lu = parse_date(rows[0].get("lu") or "")
    if lu is None or (now - lu).total_seconds() > max_age_hours * 3600:
        return 0
    n = 0
    for m in markets:
        q = question(m.question or "", getattr(m, "description", "") or "")
        if q is None or [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        ten, hausse, niveau, a, b = q
        closes = rows[0]["closes"].get(str(ten))
        p = chance(closes, niveau, hausse, a, b, now, k) if closes else None
        if p is None or p >= 1.0:
            continue
        m.references = dict(m.references or {}, taux_tresor={
            "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "vu_le": seen.isoformat(),
            "titre": f"{ten} ans, dernière clôture {closes[-1][1]:.2f} ({closes[-1][0]}), {'≥' if hausse else '<'} {niveau:.2f} d'ici le {b} : {p:.3f}"})
        n += 1
    return n
