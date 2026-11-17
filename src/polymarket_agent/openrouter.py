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
    return lire(http.get_json(CHART), http.get_json(WEEK), http.get_json(DAY), now)


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


RUPTURE = 1.5            # jour en cours > 1,5 fois le rythme du dernier jour fini : lancement ou panne, la forme passée ne vaut plus
RUPTURE_HEURES_MIN = 3.0  # avant 3 h UTC le jour en cours est trop petit (et creux) pour juger


def detail(row: dict, histo: list[dict] | None = None) -> dict:
    """Projection de la semaine en cours, avec la raison d'un refus.

    17/11/2026 (16 h, experiments/enquetes/2026-11-17_soir_openrouter_jour_en_cours.md) : la semaine en cours du graphique contient
    AUSSI le jour en cours, mis à jour en direct (0,15 T le lundi 16/11 à 00 h 40, 69,71 T le mardi 17/11 à 15 h 49 pour un lundi fini
    de 32,13 T). L'ancien calcul prenait ce total pour « k jours finis » : le mardi 17/11 à 12 h 57 il projetait ≈ 219 T et achetait
    le NON « 240 T ou plus » à 0,42 estimé 0,973, alors que le nouveau modèle gratuit tencent/hy4-flash (lancé le 16/11) traitait déjà
    15,7 T dans la journée (le marché : OUI à 0,84). Désormais : jours finis = somme des totaux quotidiens du journal
    `openrouter:histo` (ou la vue « jour » quand seul lundi est fini) ; total ≥ graphique ; refus quand le jour en cours tourne à plus
    de `RUPTURE` fois le rythme du dernier jour fini."""
    sem = {date.fromisoformat(x): float(v) for x, v in row.get("semaines") or []}
    if len(sem) < 2 or not (row.get("jour") or [None])[0] or not (row.get("sept_jours") or [None])[0]:
        return {"refus": "OpenRouter : vues incomplètes"}
    lundi = max(sem)
    jour = date.fromisoformat(row["jour"][0])
    if date.fromisoformat(row["sept_jours"][0]) != jour:
        return {"refus": "OpenRouter : vue « jour » et vue « 7 jours » décalées"}
    k = (jour - lundi).days + 1
    prec = sem.get(lundi - timedelta(days=7))
    if not 1 <= k <= 7 or prec is None:
        return {"refus": "OpenRouter : aucun jour fini de la semaine"}
    graphique = sem[lundi]
    if k == 7:
        return {"lundi": lundi.isoformat(), "total": graphique, "k": 7}
    par_jour = {str(o.get("jour")): float(o["total_jour"]) for o in histo or [] if o.get("total_jour") is not None}
    par_jour[jour.isoformat()] = float(row["jour"][1])
    jours = [(lundi + timedelta(days=i)).isoformat() for i in range(k)]
    if not all(j in par_jour for j in jours):
        return {"refus": "OpenRouter : total d'un jour fini de la semaine absent du journal (graphique = jours finis + jour en cours)"}
    p = sum(par_jour[j] for j in jours)
    en_cours = max(0.0, graphique - p)
    lu = row.get("lu")
    try:
        heures = (datetime.fromisoformat(lu) - datetime.combine(jour + timedelta(days=1), datetime.min.time(),
                                                                   tzinfo=datetime.fromisoformat(lu).tzinfo)).total_seconds() / 3600
    except (TypeError, ValueError):
        heures = 0.0
    rythme = en_cours / heures * 24 / float(row["jour"][1]) if heures >= RUPTURE_HEURES_MIN and float(row["jour"][1]) > 0 else None
    if rythme is not None and rythme > RUPTURE:
        return {"refus": f"OpenRouter : jour en cours à {rythme:.1f} fois le rythme d'hier ({en_cours:.1f} T en {heures:.1f} h) : "
                         f"lancement ou panne, la fin de semaine passée ne dit plus rien", "rythme": round(rythme, 2)}
    fin = float(row["sept_jours"][1]) - p
    debut = prec - fin
    attendu = (7 - k) / k   # fin / début d'une semaine plate (l'ancienne borne fixe 0,1-3 refusait tout lundi seul : 6 jours / 1)
    if fin <= 0 or debut <= 0 or not 0.3 * attendu <= fin / debut <= 3.0 * attendu:
        return {"refus": "OpenRouter : forme de la semaine précédente incohérente"}
    return {"lundi": lundi.isoformat(), "total": max(p * (1 + fin / debut), graphique), "k": k, "jours_finis": round(p, 4),
            "en_cours": round(en_cours, 4), "rythme": None if rythme is None else round(rythme, 2)}


def projection(row: dict, histo: list[dict] | None = None) -> tuple[str, float, int] | None:
    """(lundi de la semaine en cours, total projeté en T, jours finis) ; None si refus (voir `detail`)."""
    d = detail(row, histo)
    return None if "refus" in d else (d["lundi"], d["total"], d["k"])


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
    d = detail(rows[0], _load(db, "openrouter:histo")[1] or [])
    n = 0
    if "refus" in d:
        # la stratégie DIT pourquoi elle s'abstient (marchés de la semaine en cours seulement : lundi = semaine du graphique)
        lundi = max(x for x, _ in rows[0].get("semaines") or [["", 0]])
        for m in markets:
            q = question(m.question or "", getattr(m, "end_date", None))
            if q is not None and q[2].isoformat() == lundi and [str(o).lower() for o in m.outcomes] == ["yes", "no"]:
                m.references = dict(m.references or {}, openrouter={"refus": d["refus"], "vu_le": seen.isoformat()})
                n += 1
        return n
    lundi, total, k = d["lundi"], d["total"], d["k"]
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
