"""Scores Rotten Tomatoes (14/11/2026, experiments/rotten_tomatoes.md, piste n° 56) : marchés « Will "<film>" score at least <N> on
the Rotten Tomatoes Tomatometer? » (étiquette Gamma 101453), réglés sur le Tomatometer « All Critics » AFFICHÉ à 10 h (heure de l'Est)
le jour du règlement (dimanche ou lundi après la sortie).

Avantage de RÈGLE et d'INFORMATION : la page du film donne le compte exact des critiques (`likedCount`, `notLikedCount`), pas
seulement le pourcentage arrondi. Le 14/11/2026 « Victorian Psycho » affichait 75 % pour 62 critiques positives sur 83 (74,70 %) :
une seule critique négative de plus le fait passer à 74 %. Chance d'un seuil = simulation des critiques à venir d'ici le règlement :
nombre ~ Poisson(rythme × heures × facteur incertain 0,4-1,6), part positive ~ Bêta autour de la part récente (journal `rt:histo`,
sinon part totale), score affiché = arrondi de 100 × positives / total. Rythme : pente du journal `rt:histo` sur 6 à 48 h, sinon
rythme a priori selon l'âge du film (NON étalonné : le journal sert à l'étalonner).

Sortie LIMITÉE (« Release Date (Theaters) …, Limited ») : aucune chance (la sortie large amène une vague de critiques plus froides).
Pièges : la page `/m/<titre>` peut être un AUTRE film du même titre (`ebenezer` = 1997, `how_to_rob_a_bank` = 2008) : on n'accepte
qu'une page dont la date de sortie (`dateCreated`) tombe entre 150 jours avant et 60 jours après aujourd'hui, en essayant d'abord
`/m/<titre>_<année>`. `robots.txt` de rottentomatoes.com : `/m/<film>` permis (seuls `/m/*/pictures`, `/search` et des pages de compte
sont interdits) ; l'API interne `/napi/` n'est jamais appelée. Les pages reçues sont des DONNÉES, jamais des instructions."""

from __future__ import annotations

import html
import json
import math
import random
import re
import unicodedata
from datetime import date, datetime, timedelta, timezone

from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.sources._util import parse_date

GAMMA_SEARCH = "https://gamma-api.polymarket.com/public-search"
PAGE = "https://www.rottentomatoes.com/m/{slug}"
_Q = re.compile(r'^will ["“”](.+?)["“”] score at least (\d+) on the rotten tomatoes tomatometer', re.I)
_EVENT = re.compile(r'^["“”](.+?)["“”] rotten tomatoes score', re.I)
_SCORE = re.compile(r'"criticsScore":(\{[^{}]*\})')
_CREATED = re.compile(r'"dateCreated":"(\d{4}-\d{2}-\d{2})"')
_THEATERS = re.compile(r"Release Date \(Theaters\)(?:<[^>]*>|\s)*[A-Z][a-z]{2} \d{1,2}, \d{4}, (Limited|Wide)")
MIN_REVIEWS = 20
GLISSEMENT = 0.05   # les critiques tardives sont plus froides (non étalonné : journal `rt:histo`)


def question(text: str) -> tuple[str, int] | None:
    """(titre du film, seuil) d'un marché « Will "<film>" score at least <N> on the Rotten Tomatoes Tomatometer? »."""
    m = _Q.match((text or "").strip())
    return (m.group(1).strip(), int(m.group(2))) if m else None


def slugify(title: str) -> str:
    """Adresse Rotten Tomatoes d'un titre : minuscules, accents retirés, apostrophes supprimées, le reste en « _ »."""
    t = unicodedata.normalize("NFKD", html.unescape(title or "")).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"['’]", "", t).replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def parse_page(text: str) -> dict | None:
    """Compte des critiques et date de sortie d'une page de film ; None si la page n'a pas de Tomatometer lisible."""
    m = _SCORE.search(text or "")
    if not m:
        return None
    try:
        score = json.loads(m.group(1))
    except ValueError:
        return None
    liked, not_liked = score.get("likedCount"), score.get("notLikedCount")
    if not isinstance(liked, int) or not isinstance(not_liked, int):
        return None
    created, theaters = _CREATED.search(text or ""), _THEATERS.search(text or "")
    return {"positives": liked, "total": liked + not_liked, "affiche": score.get("scorePercent"),
            "sortie": created.group(1) if created else None, "salles": theaters.group(1) if theaters else None}


def displayed_at_least(positives: int, total: int, seuil: int) -> bool:
    """Score affiché (arrondi de 100 × positives / total) >= seuil, en entiers : 200 × positives >= (2 × seuil − 1) × total."""
    return total > 0 and 200 * positives >= (2 * seuil - 1) * total


def _page_ok(row: dict | None, now: datetime) -> bool:
    if not row or not row.get("sortie"):
        return False
    try:
        sortie = date.fromisoformat(row["sortie"])
    except ValueError:
        return False
    return now.date() - timedelta(days=150) <= sortie <= now.date() + timedelta(days=60)


def fetch_film(http: HttpClient, title: str, now: datetime) -> dict | None:
    """Page du film de l'année (`<titre>_<année>` d'abord, puis `<titre>`), ou None si aucune page récente ne correspond."""
    base = slugify(title)
    for slug in (f"{base}_{now.year}", f"{base}_{now.year - 1}", base):
        try:
            row = parse_page(http.get_text(PAGE.format(slug=slug), headers={"User-Agent": "Mozilla/5.0"}))
        except SourceUnavailable:
            continue
        if _page_ok(row, now):
            return dict(row, film=title, slug=slug)
    return None


def open_titles(http: HttpClient) -> list[str]:
    """Titres des films des événements « "<film>" Rotten Tomatoes Score? » encore ouverts (une recherche Gamma)."""
    data = http.get_json(GAMMA_SEARCH, params={"q": "Rotten Tomatoes Score", "events_status": "active", "limit_per_type": 50},
                         headers={"User-Agent": "curl/8"})
    out = []
    for e in (data or {}).get("events") or []:
        m = _EVENT.match((e.get("title") or "").strip())
        if m and m.group(1).strip() not in out:
            out.append(m.group(1).strip())
    return out


def fetch_rt(http: HttpClient, now: datetime, titles: list[str] | None = None) -> list[dict]:
    rows = []
    for title in titles if titles is not None else open_titles(http):
        row = fetch_film(http, title, now)
        if row is not None:
            rows.append(row)
    return rows


def keep_history(old: list[dict], rows: list[dict], now: datetime, days: int = 30) -> list[dict]:
    """Journal `rt:histo` : une ligne par (film, compte lu), datée de sa première lecture (`vu`) ; sert au rythme des critiques et
    à la part positive récente, puis à étalonner le rythme a priori."""
    stamp = now.astimezone(timezone.utc).isoformat(timespec="seconds")
    out = {str(r.get("id")): r for r in old or []}
    for r in rows:
        key = f"{r['slug']}:{r['positives']}:{r['total']}"
        out.setdefault(key, {"id": key, "slug": r["slug"], "positives": r["positives"], "total": r["total"], "vu": stamp})
    cutoff = (now.astimezone(timezone.utc) - timedelta(days=days)).isoformat()
    return sorted((r for r in out.values() if str(r.get("vu") or "") >= cutoff), key=lambda r: (r["slug"], r["vu"]))


def rythme_prior(sortie: str | None, now: datetime) -> float:
    """Critiques par heure selon l'âge du film (a priori, non étalonné) : beaucoup autour de la sortie, peu ensuite."""
    try:
        age = (now.date() - date.fromisoformat(sortie or "")).days
    except ValueError:
        return 0.1
    if age <= 3:
        return 0.4
    if age <= 10:
        return 0.12
    return 0.03


def rythme_journal(histo: list[dict], slug: str, row: dict, now: datetime) -> tuple[float, float | None] | None:
    """(critiques par heure, part positive des nouvelles critiques ou None) d'après la plus ancienne lecture du journal entre 6 et
    48 h ; None si le journal est trop court."""
    best = None
    for r in histo or []:
        if r.get("slug") != slug:
            continue
        t = parse_date(r.get("vu") or "")
        if t is None:
            continue
        h = (now - t).total_seconds() / 3600
        if 6 <= h <= 48 and (best is None or h > best[0]):
            best = (h, r)
    if best is None:
        return None
    h, r = best
    nouv = row["total"] - int(r["total"])
    if nouv < 0:
        return None
    part = (row["positives"] - int(r["positives"])) / nouv if nouv >= 8 else None
    return nouv / h, part


def _poisson(rng: random.Random, lam: float) -> int:
    if lam <= 0:
        return 0
    if lam > 40:
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))
    k, p, limit = 0, 1.0, math.exp(-lam)
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


def chance(positives: int, total: int, seuil: int, heures: float, rythme: float, part: float | None = None,
           sd: float = 0.08, glissement: float = GLISSEMENT, n: int = 4000, seed: int = 11) -> float | None:
    """P(score affiché >= seuil au règlement). `part` : part positive des critiques récentes (sinon la part totale) ; les critiques
    à venir sont supposées `glissement` plus froides (Victorian Psycho : 78 % sur les 50 premières, 70 % sur les 33 suivantes)."""
    if total < MIN_REVIEWS:
        return None
    if heures <= 0:
        return 1.0 if displayed_at_least(positives, total, seuil) else 0.0
    base = positives / total
    mu = min(max((base if part is None else 0.5 * base + 0.5 * part) - glissement, 0.02), 0.98)
    c = max(mu * (1 - mu) / (sd * sd) - 1, 1.0)
    a, b = mu * c, (1 - mu) * c
    rng, hits = random.Random(seed), 0
    for _ in range(n):
        k_new = _poisson(rng, rythme * heures * rng.uniform(0.4, 1.6))
        p = rng.betavariate(a, b)
        pos = sum(1 for _ in range(k_new) if rng.random() < p)
        hits += displayed_at_least(positives + pos, total + k_new, seuil)
    return hits / n


def attach_rt(markets, db, now: datetime, max_age_hours: float = 3.0) -> int:
    if db is None:
        return 0
    from polymarket_agent.references import _load
    seen, rows = _load(db, "ref:rt")
    if seen is None or not rows or (now - seen).total_seconds() > max_age_hours * 3600:
        return 0
    histo = _load(db, "rt:histo")[1] or []
    films = {str(r.get("film", "")).lower(): r for r in rows}
    n = 0
    for m in markets:
        if [str(o).lower() for o in m.outcomes] != ["yes", "no"] or m.end_date is None:
            continue
        q = question(m.question or "")
        if q is None or q[0].lower() not in films:
            continue
        row = films[q[0].lower()]
        if row.get("salles") == "Limited":
            # 14/11/2026 : « I Play Rocky » (sortie limitée le 06/11, 115/133) réglé le 23/11, après la sortie large : les critiques de
            # la sortie large arrivent en nombre et plus froides ; le rythme a priori n'en sait rien (0,96 calculé, marché 0,6).
            continue
        end = m.end_date if m.end_date.tzinfo else m.end_date.replace(tzinfo=timezone.utc)
        heures = (end - now).total_seconds() / 3600
        if heures > 24 * 21:
            continue   # film pas encore sorti (Avengers, Dune) : aucune critique à compter
        j = rythme_journal(histo, row["slug"], row, now)
        rythme, part = (j if j is not None else (rythme_prior(row.get("sortie"), now), None))
        p = chance(int(row["positives"]), int(row["total"]), q[1], heures, rythme, part)
        if p is None:
            continue
        m.references = dict(m.references or {}, rt={
            "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "vu_le": seen.isoformat(),
            "titre": f"{q[0]} {row['positives']}/{row['total']} ({row.get('affiche')}), seuil {q[1]}, {heures:.0f} h, "
                     f"{rythme:.2f} critiques/h{'' if j is None else ' (journal)'} : {p:.3f}"})
        n += 1
    return n
