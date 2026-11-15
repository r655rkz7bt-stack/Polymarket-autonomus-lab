"""Tranches « <X> odds <a>-<b>% on <date>? » réglées sur l'indice de PredictionMarketOdds.com (15/11/2026, piste n° 65,
experiments/indice_cotes.md).

Polymarket ouvre des « dérivés » (étiquette `derivatives`) sur un INDICE de prix de marchés de prédiction : « Democratic 2028
presidential odds 66-68% on November 20? » se règle sur la valeur horaire publiée par PredictionMarketOdds.com (moyenne des
médianes horaires de Polymarket, Kalshi, Betfair, PredictIt…, pondérées par la liquidité) pour la fenêtre qui finit à 12 h (heure
de l'Est) le jour dit. La valeur est arrondie au millième (« round half up ») ; une valeur pile sur une borne va à la tranche du
dessus. Le flux `latest.json` (sans clé, pas de robots.txt) donne toutes les valeurs de l'heure, avec la valeur brute.

Chance : marche aléatoire du sous-jacent depuis la valeur brute du moment. Cœur : écart-type `SD_HEURE` × racine(heures restantes)
calé sur l'écart interquartile des variations sur 117 h de 180 jours de prix horaires du sous-jacent Polymarket (≈ 1 point, soit
0,75 point d'écart-type) ; queue épaisse (20 % des tirages à 2,5 fois : sauts de nouvelles, qui portent l'écart-type brut à 1,2
point). Le 15/11 : 66-68 % ≈ 0,65 et 64-66 % ≈ 0,05 (loi empirique : 0,58-0,69 et 0,00-0,05 selon la période). Rejeu (11 événements réglés, septembre → novembre 2026, vrais
échanges) : indice faible, voir l'expérience `indice_cotes`.
"""
from __future__ import annotations

import math
import re
from datetime import datetime

from polymarket_agent.http_client import HttpClient

LATEST = "https://predictionmarketodds.com/latest.json"
SD_HEURE = 0.0007
QUEUE = (0.20, 2.5)
# début de la question Polymarket -> (liste PredictionMarketOdds, option)
SOUS_JACENTS = {
    "democratic 2028 presidential": ("president_2028_party", "democratic_party"),
    "republican 2028 presidential": ("president_2028_party", "republican_party"),
    "democratic senate": ("senate_control_2026", "democratic_party"),
    "republican senate": ("senate_control_2026", "republican_party"),
    "democratic house": ("house_control_2026", "democratic_party"),
    "republican house": ("house_control_2026", "republican_party"),
}
_Q = re.compile(r"^(?P<nom>.+?) odds (?:(?P<inf><)\s*(?P<a1>[\d.]+)%|(?P<sup>>)\s*(?P<a2>[\d.]+)%|(?P<a3>[\d.]+)%\+|"
                r"(?P<lo>[\d.]+)\s*[-–]\s*(?P<hi>[\d.]+)%) on (?P<jour>\w+ \d{1,2})\?", re.IGNORECASE)


def lire(doc: dict, now: datetime) -> list[dict]:
    """Une ligne par option : liste, option, valeur publiée, valeur brute, heure de la fenêtre."""
    rows = []
    for p in (doc or {}).get("prints") or []:
        calc = p.get("calculation") or {}
        brut = (calc.get("final_math") or {}).get("raw_value")
        val = (p.get("print") or {}).get("value")
        if not p.get("market_set_id") or not p.get("candidate_id") or val is None:
            continue
        rows.append({"liste": p["market_set_id"], "option": p["candidate_id"], "valeur": float(val),
                     "brut": float(brut) if brut is not None else float(val), "fenetre": p.get("window_end"),
                     "genere": doc.get("generated_at"), "lu": now.isoformat()})
    return rows


def fetch_indice(http: HttpClient, now: datetime) -> list[dict]:
    return lire(http.get_json(LATEST), now)


def question(q: str) -> tuple[tuple[str, str], float, float] | None:
    """((liste, option), borne basse, borne haute) en fraction ; None si ce n'est pas une tranche « odds … on <date> »."""
    m = _Q.match((q or "").strip())
    if not m:
        return None
    cle = next((v for k, v in SOUS_JACENTS.items() if m["nom"].strip().lower() == k), None)
    if cle is None:
        return None
    if m["inf"]:
        lo, hi = 0.0, float(m["a1"]) / 100
    elif m["sup"]:
        lo, hi = float(m["a2"]) / 100, math.inf
    elif m["a3"]:
        lo, hi = float(m["a3"]) / 100, math.inf
    else:
        lo, hi = float(m["lo"]) / 100, float(m["hi"]) / 100
    return cle, lo, hi


def _cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def chance(brut: float, heures: float, lo: float, hi: float) -> float:
    """P(valeur publiée dans [lo ; hi[) dans `heures` heures. Publiée = brute arrondie au millième (moitié vers le haut) :
    publiée ≥ lo ⇔ brute ≥ lo − 0,0005."""
    a, b = lo - 0.0005, (hi - 0.0005 if hi != math.inf else math.inf)
    sd = max(0.0015, SD_HEURE * math.sqrt(max(heures, 0.0)))
    p = 0.0
    for poids, f in ((1 - QUEUE[0], 1.0), (QUEUE[0], QUEUE[1])):
        s = sd * f
        p += poids * ((_cdf((b - brut) / s) if b != math.inf else 1.0) - (_cdf((a - brut) / s) if lo > 0 else 0.0))
    return min(1.0, max(0.0, p))


def attach_indice(markets, db, now: datetime, max_age_hours: float = 3.0) -> int:
    if db is None:
        return 0
    from polymarket_agent.references import _load
    from polymarket_agent.sources._util import parse_date
    seen, rows = _load(db, "ref:indice_cotes")
    if seen is None or not rows:
        return 0
    lu = parse_date(rows[0].get("lu") or "")
    if lu is None or (now - lu).total_seconds() > max_age_hours * 3600:
        return 0
    par_cle = {(r["liste"], r["option"]): r for r in rows}
    n = 0
    for m in markets:
        q = question(m.question or "")
        fin = getattr(m, "end_date", None)
        if q is None or fin is None or [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        r = par_cle.get(q[0])
        heures = (fin - now).total_seconds() / 3600
        if r is None or heures <= 0:
            continue
        p = chance(r["brut"], heures, q[1], q[2])
        m.references = dict(m.references or {}, indice_cotes={
            "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "vu_le": seen.isoformat(),
            "titre": f"Indice {q[0][0]}/{q[0][1]} : brut {r['brut']:.4f} ({r.get('fenetre')}), {heures:.0f} h restantes, "
                     f"tranche {q[1]:g}-{q[2]:g} : {p:.3f}"})
        n += 1
    return n
