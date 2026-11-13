"""Jetons traités par OpenRouter dans la semaine (13/11/2026, piste n° 50, experiments/openrouter.md).

« Will OpenRouter process between 200T and 210T tokens the week of November 9? » se règle sur le total hebdomadaire du graphique
« Top Models » de openrouter.ai/rankings (semaine du lundi 00 h au dimanche 23 h 59 UTC, total affiché quand la semaine suivante
apparaît). Ce graphique est servi sans clé par `api/frontend/v1/rankings/model-rankings-chart` (un an de semaines, la semaine en
cours = jours FINIS depuis lundi) ; la même API donne le total des 7 derniers jours finis (`models?view=week`) et du dernier jour
fini (`models?view=day`). robots.txt : « Allow: / ».

Projection : semaine en cours = lundi → jour D (k jours finis, total P). Les 7 derniers jours (R) = P + la fin de la semaine
précédente (jours D−6 → dimanche, 7 − k jours) : fin = R − P ; début de la semaine précédente (k jours) = total de la semaine
précédente − fin. La semaine en cours finit comme la précédente : total ≈ P × (1 + fin / début). Le 13/11 (k = 4, jeudi fini) :
P 134,43, R 209,67, semaine du 2/11 209,52 → fin 75,24, début 134,28 → 209,75 T, pile sur la borne 210 (le marché paie 210-220
à 0,59). Incertitude : écart-type relatif `SD_JOUR` × racine(jours restants), queue épaisse (15 % à 3 fois l'écart-type).
Aucun historique quotidien public : le journal `openrouter:histo` garde chaque jour lu pour étalonner plus tard.
"""
from __future__ import annotations

import math
import re
from datetime import date, datetime, timedelta

from polymarket_agent.http_client import HttpClient

BASE = "https://openrouter.ai/api/frontend/v1/rankings/"
CHART = BASE + "model-rankings-chart"
WEEK = BASE + "models?view=week"
DAY = BASE + "models?view=day"
UA = {"User-Agent": "Mozilla/5.0"}
SD_JOUR = 0.0125          # écart-type relatif par jour restant (≈ 2,2 % à 3 jours ; cinq estimations du 13/11 : 200,8-210,3)
QUEUE = (0.15, 3.0)       # 15 % des tirages à 3 fois l'écart-type (lancement d'un modèle gratuit, panne)
_Q = re.compile(r"OpenRouter process (?:(less than) ([\d.]+)T|between ([\d.]+)T and ([\d.]+)T|([\d.]+)T or more) tokens the week of "
                r"(\w+ \d{1,2})", re.IGNORECASE)


def _total(rows) -> float:
    return sum(float(r.get("total_prompt_tokens") or 0) + float(r.get("total_completion_tokens") or 0) for r in rows or [])


def _jour(rows) -> str | None:
    dates = sorted({str(r.get("date") or "")[:10] for r in rows or [] if r.get("date")})
    return dates[-1] if dates else None


def lire(chart: dict, week: dict, day: dict, now: datetime) -> list[dict]:
    pts = ((chart or {}).get("data") or {}).get("data") or []
    semaines = [[p["x"], round(sum(float(v) for v in (p.get("ys") or {}).values()) / 1e12, 4)] for p in pts if p.get("x")]
    d_rows = (day or {}).get("data") or []
    w_rows = (week or {}).get("data") or []
    if not semaines or not d_rows or not w_rows:
        return []
    return [{"semaines": semaines, "jour": [_jour(d_rows), round(_total(d_rows) / 1e12, 4)],
             "sept_jours": [_jour(w_rows), round(_total(w_rows) / 1e12, 4)], "lu": now.isoformat()}]


def fetch_openrouter(http: HttpClient, now: datetime) -> list[dict]:
    return lire(http.get_json(CHART, headers=UA), http.get_json(WEEK, headers=UA), http.get_json(DAY, headers=UA), now)


def question(q: str, fin: datetime | None = None) -> tuple[float, float, date] | None:
    """(borne basse, borne haute, lundi de la semaine) en T ; None si ce n'est pas un marché de jetons OpenRouter."""
    g = _Q.search(q or "")
    if not g:
        return None
    lo, hi = (0.0, float(g.group(2))) if g.group(1) else (float(g.group(3)), float(g.group(4))) if g.group(3) else (float(g.group(5)), math.inf)
    annee = (fin or datetime.now()).year
    lundi = datetime.strptime(f"{g.group(6)} {annee}", "%B %d %Y").date()
    if fin is not None and lundi > fin.date():
        lundi = lundi.replace(year=annee - 1)   # semaine de fin décembre réglée en janvier
    return lo, hi, lundi


def projection(row: dict) -> tuple[str, float, int] | None:
    """(lundi de la semaine en cours, total projeté en T, jours finis) ; None si les trois vues ne sont pas cohérentes."""
    sem = {date.fromisoformat(x): float(v) for x, v in row.get("semaines") or []}
    if len(sem) < 2 or not (row.get("jour") or [None])[0] or not (row.get("sept_jours") or [None])[0]:
        return None
    lundi = max(sem)
    jour = date.fromisoformat(row["jour"][0])
    if date.fromisoformat(row["sept_jours"][0]) != jour:
        return None
    k = (jour - lundi).days + 1
    prec = sem.get(lundi - timedelta(days=7))
    if not 1 <= k <= 7 or prec is None:
        return None
    p = sem[lundi]
    if k == 7:
        return lundi.isoformat(), p, 7
    fin = float(row["sept_jours"][1]) - p
    debut = prec - fin
    if fin <= 0 or debut <= 0 or not 0.1 <= fin / debut <= 3.0:
        return None
    return lundi.isoformat(), p * (1 + fin / debut), k


def _cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def chance(total: float, k: int, lo: float, hi: float) -> float:
    """P(lo ≤ total final < hi) (une valeur pile sur une borne va à la tranche du dessus)."""
    if k >= 7:
        return 1.0 if lo <= total < hi else 0.0
    sd = max(1e-9, SD_JOUR * math.sqrt(7 - k) * total)
    p = 0.0
    for poids, f in ((1 - QUEUE[0], 1.0), (QUEUE[0], QUEUE[1])):
        s = sd * f
        p += poids * (_cdf((hi - total) / s) if hi != math.inf else 1.0) - poids * _cdf((lo - total) / s)
    return min(1.0, max(0.0, p))


def attach_openrouter(markets, db, now: datetime, max_age_hours: float = 3.0) -> int:
    if db is None:
        return 0
    from polymarket_agent.references import _load
    from polymarket_agent.sources._util import parse_date
    seen, rows = _load(db, "ref:openrouter")
    if seen is None or not rows:
        return 0
    lu = parse_date(rows[0].get("lu") or "")
    if lu is None or (now - lu).total_seconds() > max_age_hours * 3600:
        return 0
    proj = projection(rows[0])
    if proj is None:
        return 0
    lundi, total, k = proj
    n = 0
    for m in markets:
        q = question(m.question or "", getattr(m, "end_date", None))
        if q is None or q[2].isoformat() != lundi or [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        p = chance(total, k, q[0], q[1])
        m.references = dict(m.references or {}, openrouter={
            "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "vu_le": seen.isoformat(),
            "titre": f"OpenRouter semaine du {lundi} : {k} jours finis, projection {total:.1f} T, tranche {q[0]:g}-{q[1]:g} : {p:.3f}"})
        n += 1
    return n


def journal(old: list[dict], rows: list[dict]) -> list[dict]:
    """Journal `openrouter:histo` : un point par jour fini lu (total du jour, 7 jours, semaine en cours) ; sert à étalonner."""
    if not rows:
        return old
    r = rows[0]
    point = {"jour": r["jour"][0], "total_jour": r["jour"][1], "sept_jours": r["sept_jours"][1],
             "semaine": r["semaines"][-1][0], "partiel": r["semaines"][-1][1],
             "precedente": r["semaines"][-2][1] if len(r["semaines"]) > 1 else None, "lu": r["lu"]}
    avant = next((o for o in old if o.get("jour") == point["jour"]), None)
    if avant is not None:   # première lecture du jour gardée : un total qui bouge ensuite = révision (à mesurer)
        point.update(premier_lu=avant.get("premier_lu", avant["lu"]), premier_partiel=avant.get("premier_partiel", avant["partiel"]),
                     premier_sept_jours=avant.get("premier_sept_jours", avant["sept_jours"]))
    garde = [o for o in old if o.get("jour") != point["jour"]]
    return (garde + [point])[-400:]
