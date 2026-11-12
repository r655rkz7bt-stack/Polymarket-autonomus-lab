"""PIB mensuel canadien : l'estimation ANTICIPÉE de Statistique Canada contre les tranches du chiffre officiel (12/11/2026, piste
n° 36, experiments/pib_canada.md).

« Will Canada's GDP growth rate MoM in <Mois> <Année> be between -0.2% and -0.1% / less than -0.2% / at least 0.6%? » se règle
sur le communiqué officiel « Gross domestic product by industry » du mois ; le communiqué du mois d'AVANT donne déjà « Advance
information indicates that real GDP decreased 0.1% in <Mois> ». Officiel = anticipé + révision ; la révision (en dixièmes de
point) suit les fréquences de 33 paires 2022-2026 (communiqués du Quotidien) : elle est LARGE (−0,3 à +0,2), la tranche de
l'estimation n'est juste qu'environ 4 fois sur 10. Sources : page « Gross domestic product » du Quotidien (ind1-eng.htm, qui
pointe vers le dernier communiqué) puis le communiqué lui-même (robots.txt : permis, délai de 2 s ; 2 pages toutes les 3 h).
"""
from __future__ import annotations

import html
import re
from datetime import datetime

from polymarket_agent.http_client import HttpClient

INDEX = "https://www150.statcan.gc.ca/n1/dai-quo/ind1-eng.htm"
BASE = "https://www150.statcan.gc.ca/n1"
MOIS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
# officiel − anticipé, en dixièmes de point : 33 paires de décembre 2022 à août 2026 (experiments/pib_canada/releves/communiques.json)
REVISIONS = {-3: 2, -2: 6, -1: 5, 0: 8, 1: 8, 2: 4}
_VERB = (r"(rose|increased|grew|edged up|edged down|fell|declined|decreased|contracted|was essentially unchanged|was unchanged|"
         r"was flat|remained essentially unchanged)")
_NUM = r"(?:\s+(?:approximately |about |by |roughly )?(\d+(?:\.\d+)?)%)?"
_M = "(" + "|".join(MOIS) + ")"
_Q = re.compile(r"^Will Canada's GDP growth rate MoM in (\w+) (\d{4}) be (less than (-?\d+\.\d)%|between (-?\d+\.\d)% and (-?\d+\.\d)%|"
                r"at least (-?\d+\.\d)%)\?", re.IGNORECASE)


def _val(verb: str, x: str | None) -> float:
    if "unchanged" in verb or "flat" in verb:
        return 0.0
    v = float(x) if x else 0.0
    return -v if verb in ("edged down", "fell", "declined", "decreased", "contracted") else v


def _texte(page: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page or "")))


def dernier_communique(index_html: str) -> str | None:
    """Adresse du dernier communiqué « Gross domestic product by industry » (mensuel, pas « Provinces and territories »)."""
    for m in re.finditer(r'href="([^"]*daily-quotidien/\d{6}/dq\d{6}\w-eng\.htm)"[^>]*>(.*?)</a>', index_html or "", re.S):
        titre = _texte(m.group(2))
        if "Gross domestic product by industry" in titre and "Provinces" not in titre:
            u = m.group(1)
            return u if u.startswith("http") else BASE + u
    return None


def parse_communique(page: str) -> dict | None:
    x = _texte(page)
    a = re.search(r"Advance information indicates that real GDP(?: by industry)? " + _VERB + _NUM + r" in " + _M, x)
    o = re.search(r"Real gross domestic product \(\s*GDP\s*\) " + _VERB + _NUM + r" in " + _M, x)
    if not a:
        return None
    return {"anticipe_mois": a.group(3), "anticipe": _val(a.group(1), a.group(2)),
            "officiel_mois": o.group(3) if o else None, "officiel": _val(o.group(1), o.group(2)) if o else None}


def fetch_pib_canada(http: HttpClient, now: datetime) -> list[dict]:
    h = {"User-Agent": "Mozilla/5.0"}
    url = dernier_communique(http.get_text(INDEX, headers=h))
    if url is None:
        return []
    r = parse_communique(http.get_text(url, headers=h))
    return [dict(r, url=url, lu=now.isoformat())] if r else []


def tranche(question: str) -> tuple[float, float, str, int] | None:
    """(bas, haut inclus, mois, année) en % au dixième ; « less than -0.2% » = au plus −0,3."""
    g = _Q.match(question or "")
    if not g or g.group(1) not in MOIS:
        return None
    if g.group(4):
        return (-99.0, round(float(g.group(4)) - 0.1, 1), g.group(1), int(g.group(2)))
    if g.group(5):
        return (float(g.group(5)), float(g.group(6)), g.group(1), int(g.group(2)))
    return (float(g.group(7)), 99.0, g.group(1), int(g.group(2)))


def p_tranche(anticipe: float, bas: float, haut: float, lissage: float = 0.5) -> float:
    """Fréquences des révisions, lissées (+0,5 sur chaque dixième de −4 à +4 : jamais 0 ni 1)."""
    poids = {k: REVISIONS.get(k, 0) + lissage for k in range(-4, 5)}
    n = sum(poids.values())
    return sum(w for k, w in poids.items() if bas - 1e-9 <= round(anticipe + k / 10, 1) <= haut + 1e-9) / n


def attach_pib_canada(markets, db, now: datetime, max_age_hours: float = 8.0) -> int:
    if db is None:
        return 0
    from polymarket_agent.references import _load
    from polymarket_agent.sources._util import parse_date
    seen, rows = _load(db, "ref:pib_canada")
    if seen is None or not rows:
        return 0
    row = rows[0]
    lu = parse_date(row.get("lu") or "")
    if lu is None or (now - lu).total_seconds() > max_age_hours * 3600:
        return 0
    n = 0
    for m in markets:
        t = tranche(m.question or "")
        if t is None or [str(o).lower() for o in m.outcomes] != ["yes", "no"] or t[2] != row["anticipe_mois"]:
            continue
        if m.end_date is not None and abs(m.end_date.year - t[3]) > 1:
            continue
        p = p_tranche(float(row["anticipe"]), t[0], t[1])
        m.references = dict(m.references or {}, pib_canada={
            "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "vu_le": seen.isoformat(),
            "titre": f"estimation anticipée de {t[2]} {t[3]} = {row['anticipe']:+.1f} %, révisions 2022-2026 : {p:.3f}"})
        n += 1
    return n
