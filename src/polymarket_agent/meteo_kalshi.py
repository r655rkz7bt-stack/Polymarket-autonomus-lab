"""Températures maximales du jour : loi de Kalshi (maximum CLI du NWS) décalée vers la valeur des marchés Polymarket (maximum
des METAR horaires), pour le fantôme `meteo_sous_cli` (15/11/2026, experiments/meteo_kalshi.md, piste n° 62).

Mêmes stations (KAUS, KMIA, KDEN, KLAX), valeur différente : le maximum horaire manque les pointes entre deux relevés.
Sur 104 jours de la règle METAR (octobre-novembre 2026), CLI − valeur Polymarket = 0 °F (0,36), 1 °F (0,565), 2 °F (0,075)
(EM sur les tranches gagnantes). Aux vrais échanges, la tranche Polymarket JUSTE SOUS la médiane CLI de Kalshi gagne plus que
son prix (frais compris, queues Kalshi ≤ 0,15 : règle METAR 23 gagnés pour 19,5 payés à ≥ 100 parts, 28 pour 24,0 à ≥ 20 ;
weather.gov ≈ 0 ; la tranche du dessus perd 33 à 36 % ; hypothèse posée avant le calcul, indice faible, z ≈ 1,4) ; les autres tranches gagnent comme leur prix. On ne chiffre donc que cette tranche (`k = −1`).

Kalshi : `GET /trade-api/v2/events?series_ticker=<série>&status=open&with_nested_markets=true` (API publique sans clé,
robots.txt permis le 15/11/2026), un appel par ville."""
from __future__ import annotations

import re
from datetime import date, datetime, timezone

SERIES = {"KXHIGHAUS": "Austin", "KXHIGHMIA": "Miami", "KXHIGHDEN": "Denver", "KXHIGHLAX": "Los Angeles"}
ECART = (0.36, 0.565, 0.075)   # P(CLI − METAR = 0, 1, 2 °F), règle METAR (experiments/meteo_kalshi.md)
MOIS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
MONTHS = {m: i + 1 for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                          "september", "october", "november", "december"])}
QUESTION = re.compile(r"^will the highest temperature in (austin|miami|denver|los angeles) be (?:between )?(.+?) on (\w+) (\d+)\??$",
                      re.IGNORECASE)


def jour_kalshi(event_ticker: str) -> date | None:
    m = re.search(r"-(\d\d)([A-Z]{3})(\d\d)$", event_ticker or "")
    if not m or m.group(2) not in MOIS:
        return None
    return date(2000 + int(m.group(1)), MOIS.index(m.group(2)) + 1, int(m.group(3)))


def fetch_kalshi_meteo(http, now: datetime) -> list[dict]:
    """Une ligne par (ville, jour) ouvert : milieu acheteur/vendeur de chaque marché Kalshi (en dollars)."""
    rows = []
    for serie, ville in SERIES.items():
        data = http.get_json("https://api.elections.kalshi.com/trade-api/v2/events",
                             params={"series_ticker": serie, "status": "open", "with_nested_markets": "true", "limit": 20}) or {}
        for ev in data.get("events") or []:
            jour = jour_kalshi(ev.get("event_ticker") or "")
            if jour is None:
                continue
            marches = []
            for m in ev.get("markets") or []:
                bid, ask = m.get("yes_bid_dollars"), m.get("yes_ask_dollars")
                if bid is None or ask is None or m.get("strike_type") not in ("between", "less", "greater"):
                    continue
                marches.append({"type": m["strike_type"], "floor": m.get("floor_strike"), "cap": m.get("cap_strike"),
                                "bid": float(bid), "ask": float(ask)})
            if marches:
                rows.append({"ville": ville, "jour": jour.isoformat(), "marches": marches, "vu_le": now.isoformat(timespec="seconds")})
    return rows


def loi_cli(marches: list[dict], max_spread: float = 0.15, queue_max: float = 0.15) -> dict[int, float] | None:
    """{degré entier : chance} de la valeur CLI ; tranche 75-76 partagée moitié-moitié, queues sur 2 degrés. None si un carnet
    est trop large (prix Kalshi peu fiable), si la somme des milieux est trop loin de 1, ou si une queue (« < 61 ») porte plus de
    `queue_max` de la loi (15/11/2026 : Austin, « < 61 » à 0,94 en fin de journée, la forme de la queue est inconnue et la médiane
    n'a plus de sens ; sur le passé, la tranche visée garde son avantage avec 0,15 comme avec 0,30)."""
    loi: dict[int, float] = {}
    tot, queue = 0.0, 0.0
    for m in marches:
        if m["ask"] - m["bid"] > max_spread:
            return None
        p = (m["bid"] + m["ask"]) / 2
        if m["type"] == "between":
            cells = [int(m["floor"]), int(m["cap"])]
        elif m["type"] == "less":
            cells = [int(m["cap"]) - 1, int(m["cap"]) - 2]
        else:
            cells = [int(m["floor"]) + 1, int(m["floor"]) + 2]
        for v in cells:
            loi[v] = loi.get(v, 0.0) + p / 2
        tot += p
        if m["type"] != "between":
            queue = max(queue, p)
    if not 0.8 <= tot <= 1.2 or queue / tot > queue_max:
        return None
    return {v: q / tot for v, q in loi.items()}


def mediane(loi: dict[int, float]) -> int:
    acc = 0.0
    for v in sorted(loi):
        acc += loi[v]
        if acc >= 0.5:
            return v
    return max(loi)


def tranche(texte: str) -> tuple[int, int] | None:
    t = (texte or "").replace("°F", "").replace("°", "").strip().lower()
    if m := re.match(r"^(-?\d+)\s*-\s*(-?\d+)$", t):
        return int(m.group(1)), int(m.group(2))
    return None   # queues (« or below », « or higher ») : jamais la tranche visée


def chance_tranche(loi: dict[int, float], lo: int, hi: int, ecart=ECART) -> float:
    return sum(p * w for v, p in loi.items() for s, w in enumerate(ecart) if lo <= v - s <= hi)


def tranche_visee(loi: dict[int, float]) -> tuple[int, int]:
    """Tranche Polymarket (paire, ex. 60-61) juste sous celle qui contient la médiane CLI."""
    med = mediane(loi)
    debut = med if med % 2 == 0 else med - 1
    return debut - 2, debut - 1


def attach_meteo_kalshi(markets, db, now: datetime, max_age_hours: float = 2.0) -> int:
    """Référence `meteo_kalshi` sur la seule tranche visée de chaque (ville, jour) : chance décalée, OUI seulement (`cotes`)."""
    if db is None:
        return 0
    from polymarket_agent.references import _load
    seen, rows = _load(db, "ref:meteo_kalshi")
    if seen is None or not rows or (now - seen).total_seconds() > max_age_hours * 3600:
        return 0
    lois = {}
    for r in rows:
        loi = loi_cli(r["marches"])
        if loi:
            lois[(r["ville"].lower(), r["jour"])] = loi
    n = 0
    for m in markets:
        q = QUESTION.match((m.question or "").strip())
        if q is None or [str(o).lower() for o in m.outcomes] != ["yes", "no"] or q.group(3).lower() not in MONTHS:
            continue
        b = tranche(q.group(2))
        if b is None:
            continue
        mois, jour_m = MONTHS[q.group(3).lower()], int(q.group(4))
        annee = (m.end_date or now).year
        try:
            jour = date(annee, mois, jour_m)
        except ValueError:
            continue
        loi = lois.get((q.group(1).lower(), jour.isoformat()))
        if loi is None or tranche_visee(loi) != b:
            continue
        p = chance_tranche(loi, *b)
        m.references = dict(m.references or {}, meteo_kalshi={
            "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "cotes": [0], "vu_le": seen.isoformat(),
            "titre": f"Kalshi {q.group(1)} {jour.isoformat()} : médiane CLI {mediane(loi)} °F, tranche {b[0]}-{b[1]} décalée {p:.3f}"})
        n += 1
    return n


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
