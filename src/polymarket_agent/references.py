"""Références externes : le prix de la MÊME question ailleurs (vingt nouvelles pistes, lot B, 20/10/2026).

Sources gratuites, sans clé (vérifiées en direct le 20/10/2026) :
- Kalshi : GET api.elections.kalshi.com/trade-api/v2/events?status=open&with_nested_markets=true
  (catégories hors sport : le sport a déjà été comparé, experiments/sport_kalshi.md) ;
- PredictIt : GET www.predictit.org/api/marketdata/all/ (politique américaine, contrats par candidat) ;
- Manifold : GET api.manifold.markets/v0/search-markets (monnaie fictive, mais souvent bien calibré) ;
- XTracker (le compteur de Polymarket pour les marchés « combien de tweets ») :
  GET xtracker.polymarket.com/api/users (périodes suivies) puis /api/users/{compte}/posts?startDate=…
  (chaque message compté ; le 20/10, le nombre de messages de chaque période égalait exactement le
  « Post Counter » qui tranche, sur les 8 comptes).
Chaque source écrit un INSTANTANÉ dans la petite mémoire de la base (clé « ref:<source> »),
remplacé à chaque passage (pas d'accumulation). `attach` relie ensuite chaque marché surveillé
à la question correspondante (texte proche, mêmes nombres, échéance proche) et pose
`market.references = {source: {"p", "vu_le", "titre", "similarite"}}` ; les stratégies
`*_reference` comparent ce prix au carnet de Polymarket. Prudence : un rattachement douteux
coûte cher ; seuils stricts et garde-fou d'écart maximal dans les stratégies.
"""

from __future__ import annotations

import json
import logging
import math
import re
from datetime import datetime, timedelta, timezone

from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.sources._util import parse_date

log = logging.getLogger(__name__)

STOP = set("""a an the of in on at by to for be will is are was were and or not no yes than more less
before after during this that which who what when how with as from it its x vs""".split())


GENERIC = set("who which what win wins winner election elections next become".split())  # mots de tournure


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", (text or "").lower()) if w not in STOP and len(w) > 1}


def numbers(text: str) -> set[str]:
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text or "")}


def similarity(a: str, b: str) -> float:
    """Indice de Jaccard sur les mots porteurs de sens (0 à 1)."""
    wa, wb = words(a), words(b)
    return len(wa & wb) / len(wa | wb) if wa and wb else 0.0


def _save(db, key: str, rows: list[dict], now: datetime) -> None:
    db.set_value(key, json.dumps({"vu_le": now.isoformat(timespec="seconds"), "rows": rows}))


def _load(db, key: str) -> tuple[datetime | None, list[dict]]:
    try:
        raw = json.loads(db.get_value(key) or "{}")
    except (ValueError, TypeError):
        return None, []
    return parse_date(raw.get("vu_le") or ""), list(raw.get("rows") or [])


# ------------------------------------------------------------------ sources


def fetch_kalshi(http: HttpClient, pages: int = 5, skip=("Sports",)) -> list[dict]:
    rows, cursor = [], None
    for _ in range(pages):
        params = {"status": "open", "with_nested_markets": "true", "limit": 200}
        if cursor:
            params["cursor"] = cursor
        data = http.get_json("https://api.elections.kalshi.com/trade-api/v2/events", params=params)
        for ev in (data or {}).get("events") or []:
            if ev.get("category") in skip:
                continue
            for m in ev.get("markets") or []:
                try:
                    bid, ask = float(m.get("yes_bid_dollars") or 0), float(m.get("yes_ask_dollars") or 0)
                except (TypeError, ValueError):
                    continue
                if ask <= 0 or bid <= 0 or ask - bid > 0.10:  # carnet vide ou trop large : prix peu fiable
                    continue
                rows.append({"titre": f"{m.get('title') or ev.get('title')} {m.get('yes_sub_title') or ''}".strip(),
                             "p": round((bid + ask) / 2, 4), "fin": m.get("close_time"),
                             "categorie": ev.get("category")})
        cursor = (data or {}).get("cursor")
        if not cursor:
            break
    return rows


def fetch_predictit(http: HttpClient) -> list[dict]:
    rows = []
    for m in (http.get_json("https://www.predictit.org/api/marketdata/all/") or {}).get("markets") or []:
        for c in m.get("contracts") or []:
            yes, no = c.get("bestBuyYesCost"), c.get("bestBuyNoCost")
            if not yes or not no or c.get("status") != "Open":
                continue
            rows.append({"marche": m.get("name") or "", "contrat": c.get("name") or "",
                         "p": round((float(yes) + 1 - float(no)) / 2, 4),
                         "fin": None if c.get("dateEnd") in (None, "NA") else c.get("dateEnd")})
    return rows


def fetch_tweet_trackings(http: HttpClient, handles=None, now: datetime | None = None) -> list[dict]:
    """Périodes suivies par XTracker : messages déjà comptés, et les 14 derniers jours heure par heure
    (heures complètes seulement, la plus récente en dernier) pour le rythme. Un appel par compte."""
    now = (now or now_utc()).astimezone(timezone.utc)
    hour = now.replace(minute=0, second=0, microsecond=0)
    rows = []
    for user in (http.get_json("https://xtracker.polymarket.com/api/users") or {}).get("data") or []:
        active = [t for t in user.get("trackings") or [] if t.get("isActive") and parse_date(t.get("startDate") or "")]
        if (handles and user.get("handle") not in handles) or not active:
            continue
        since = min([hour - timedelta(days=14)] + [parse_date(t["startDate"]) for t in active])
        posts = (http.get_json(f"https://xtracker.polymarket.com/api/users/{user['handle']}/posts",
                               params={"startDate": since.isoformat().replace("+00:00", "Z"),
                                       "endDate": now.isoformat().replace("+00:00", "Z")}) or {}).get("data") or []
        times = [t for t in (parse_date(p.get("createdAt") or "") for p in posts) if t is not None]
        hourly = [0] * (24 * 14)
        for t in times:
            k = int((hour - t).total_seconds() // 3600)  # 0 = heure qui vient de finir
            if 0 <= k < len(hourly) and t < hour:
                hourly[-1 - k] += 1
        for t in active:
            start, end = parse_date(t["startDate"]), parse_date(t.get("endDate") or "")
            rows.append({"compte": user.get("handle"), "titre": t.get("title"),
                         "slug": str(t.get("marketLink") or "").rstrip("/").rsplit("/", 1)[-1],
                         "debut": t.get("startDate"), "fin": t.get("endDate"),
                         "total": sum(1 for x in times if start <= x and (end is None or x <= end)),
                         "vu_le": now.isoformat(timespec="seconds"), "heures": hourly})
    return rows


class ManifoldMatcher:
    """Recherche la question Polymarket sur Manifold (une recherche par marché, gardée 24 h)."""

    URL = "https://api.manifold.markets/v0"

    def __init__(self, http: HttpClient, db, min_similarity: float = 0.6):
        self.http, self.db, self.min_sim = http, db, min_similarity

    def run(self, markets, now: datetime, searches: int = 15, refresh: int = 30) -> int:
        done, found = 0, 0
        for m in markets:
            key = f"manifold:{m.market_id}"
            try:
                cached = json.loads(self.db.get_value(key) or "{}")
            except (ValueError, TypeError):
                cached = {}
            seen = parse_date(cached.get("vu_le") or "")
            if seen and now - seen < timedelta(hours=24 if not cached.get("id") else 1):
                found += bool(cached.get("id"))
                continue
            if cached.get("id") and refresh > 0:  # rattachement connu : seulement le prix du jour
                refresh -= 1
                try:
                    d = self.http.get_json(f"{self.URL}/market/{cached['id']}")
                    cached.update(p=round(float(d.get("probability")), 4), vu_le=now.isoformat(timespec="seconds"))
                    self.db.set_value(key, json.dumps(cached))
                    found += 1
                except (SourceUnavailable, TypeError, ValueError):
                    pass
                continue
            if done >= searches:
                continue
            done += 1
            try:
                hits = self.http.get_json(f"{self.URL}/search-markets", params={
                    "term": m.question[:120], "limit": 5, "filter": "open", "contractType": "BINARY"}) or []
            except SourceUnavailable:
                continue
            best = max(hits, key=lambda h: similarity(h.get("question", ""), m.question), default=None)
            entry = {"vu_le": now.isoformat(timespec="seconds")}
            if best is not None and similarity(best.get("question", ""), m.question) >= self.min_sim \
                    and numbers(best.get("question", "")) == numbers(m.question) and best.get("probability") is not None:
                entry.update(id=best.get("id"), titre=best.get("question"), p=round(float(best["probability"]), 4),
                             similarite=round(similarity(best["question"], m.question), 3),
                             parieurs=best.get("uniqueBettorCount"))
                found += 1
            self.db.set_value(key, json.dumps(entry))
        return found


# ------------------------------------------------------------------ rattachement


def _close_dates(a: datetime | None, b: str | None, days: float) -> bool:
    when = parse_date(b) if b else None
    return a is None or when is None or abs((a - when).total_seconds()) <= days * 86400


def match_kalshi(market, rows: list[dict], min_sim: float = 0.55) -> dict | None:
    if [str(o).lower() for o in market.outcomes] != ["yes", "no"]:
        return None
    text = f"{market.question} {market.group_title}"
    best, best_sim = None, 0.0
    for r in rows:
        sim = similarity(text, r["titre"])
        # Mêmes nombres, échéance proche, et aucun mot distinctif de Kalshi absent de Polymarket
        # (au plus un : les titres de Kalshi ajoutent souvent « be the … »).
        if (sim > best_sim and numbers(text) == numbers(r["titre"]) and _close_dates(market.end_date, r.get("fin"), 7)
                and len(words(r["titre"]) - GENERIC - words(text)) <= 1):
            best, best_sim = r, sim
    return dict(best, similarite=round(best_sim, 3)) if best is not None and best_sim >= min_sim else None


def match_predictit(market, rows: list[dict], min_sim: float = 0.4) -> dict | None:
    """Règles strictes (essai en direct du 20/10/2026 : « Which 2026 Senate race will be the
    closest? » rattaché à « Will the Democrats win the Texas Senate race? », la vice-présidence à
    la présidence, des tranches d'écart au vainqueur) :
    - le contrat (candidat, parti) figure dans la question ou dans l'intitulé de l'issue ;
    - chaque mot distinctif du marché PredictIt figure dans la question Polymarket ;
    - mêmes nombres des deux côtés (années, districts) et aucun nombre dans l'intitulé de l'issue
      qui ne soit pas dans le contrat (tranches « 8-1 », « 25-30% »)."""
    if [str(o).lower() for o in market.outcomes] != ["yes", "no"]:
        return None
    q = market.question or ""
    text = f"{q} {market.group_title}"
    best, best_sim = None, 0.0
    for r in rows:
        name = words(r["contrat"])
        if not name or not (name <= words(text)) or numbers(market.group_title) - numbers(r["contrat"]):
            continue
        if not (words(r["marche"]) - GENERIC - name) <= words(text):
            continue
        if numbers(q) != numbers(r["marche"]) | numbers(r["contrat"]):
            continue
        sim = similarity(q, f"{r['marche']} {r['contrat']}")
        if sim > best_sim:
            best, best_sim = r, sim
    return dict(best, titre=f"{best['marche']} — {best['contrat']}", similarite=round(best_sim, 3)) \
        if best is not None and best_sim >= min_sim else None


def attach(markets, db, now: datetime) -> dict[str, int]:
    """Pose `market.references` (et `market.tweets`) sur les marchés surveillés ; renvoie le nombre
    de rattachements par source."""
    counts = {"kalshi": 0, "predictit": 0, "manifold": 0, "tweets": 0}
    if db is None:
        return counts
    k_seen, kalshi = _load(db, "ref:kalshi")
    p_seen, predictit = _load(db, "ref:predictit")
    _, tweets = _load(db, "ref:tweets")
    by_slug = {t["slug"]: t for t in tweets if t.get("slug")}
    for m in markets:
        refs = {}
        hit = match_kalshi(m, kalshi) if kalshi else None
        if hit:
            refs["kalshi"] = dict(hit, vu_le=k_seen.isoformat() if k_seen else None)
        hit = match_predictit(m, predictit) if predictit else None
        if hit:
            refs["predictit"] = dict(hit, vu_le=p_seen.isoformat() if p_seen else None)
        try:
            man = json.loads(db.get_value(f"manifold:{m.market_id}") or "{}")
        except (ValueError, TypeError):
            man = {}
        if man.get("id") and man.get("p") is not None:
            refs["manifold"] = man
        m.references = {**(getattr(m, "references", None) or {}), **refs}
        m.tweets = by_slug.get(getattr(m, "event_slug", "")) if by_slug else None
        for k in ("kalshi", "predictit", "manifold"):
            counts[k] += k in refs
        counts["tweets"] += m.tweets is not None
    return counts


# ------------------------------------------------------------------ loi du nombre de tweets


def negbin_interval(lo: int, hi: int, mean: float, dispersion: float) -> float:
    """P(lo ≤ X ≤ hi) pour X binomiale négative de moyenne `mean` et variance mean + mean²/dispersion
    (dispersion grande → Poisson). lo, hi ≥ 0 ; hi = 10**9 pour « et plus »."""
    if mean <= 0:
        return 1.0 if lo <= 0 <= hi else 0.0
    r = max(dispersion, 1e-6)
    q = r / (r + mean)  # probabilité de « succès »
    total, k, upper = 0.0, max(lo, 0), min(hi, int(mean + 12 * math.sqrt(mean + mean * mean / r)) + 50)
    log_q, log_1q = math.log(q), math.log(1 - q)
    while k <= upper:
        total += math.exp(math.lgamma(k + r) - math.lgamma(r) - math.lgamma(k + 1) + r * log_q + k * log_1q)
        k += 1
    return min(max(total, 0.0), 1.0)


def bucket_of(title: str) -> tuple[int, int] | None:
    """« 200-219 » → (200, 219) ; « <100 », « less than 100 » → (0, 99) ; « 400+ », « 400 or more » →
    (400, 10**9)."""
    t = (title or "").lower().replace(",", "")
    if m := re.match(r"^\s*(\d+)\s*[-–]\s*(\d+)\s*$", t):
        return int(m.group(1)), int(m.group(2))
    if m := re.match(r"^\s*(?:<|less than|under|fewer than)\s*(\d+)\s*$", t):
        return 0, int(m.group(1)) - 1
    if m := re.match(r"^\s*(\d+)\s*(?:\+|or more|and above|or higher)\s*$", t):
        return int(m.group(1)), 10 ** 9
    return None


def tweet_bucket_probability(tracking: dict, bucket: tuple[int, int], now: datetime, dispersion: float,
                             recent_hours: int = 168, long_hours: int = 336, recent_weight: float = 0.5) -> float | None:
    """Chance que le total final tombe dans la tranche : déjà compté + rythme horaire × heures
    restantes depuis le relevé (loi binomiale négative : les rafales de messages sont fréquentes).
    Rythme = mélange du rythme récent (`recent_hours`) et du rythme long (`long_hours`). Réglages
    choisis sur le passé (experiments/vingt_pistes.md, 7 comptes, 6 058 prévisions)."""
    end = parse_date(tracking.get("fin") or "")
    start = parse_date(tracking.get("debut") or "")
    seen = parse_date(tracking.get("vu_le") or "") or now
    count = tracking.get("total")
    hourly = tracking.get("heures") or []
    if end is None or count is None or not hourly:
        return None
    remaining = max((end - max(seen, start or seen)).total_seconds() / 3600, 0)
    recent = sum(hourly[-recent_hours:]) / max(len(hourly[-recent_hours:]), 1)
    long = sum(hourly[-long_hours:]) / max(len(hourly[-long_hours:]), 1)
    rate = recent_weight * recent + (1 - recent_weight) * long
    lo, hi = bucket
    return negbin_interval(lo - int(count), hi - int(count), rate * remaining, dispersion)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


# ------------------------------------------------------------------ bookmakers : champions et football à 3 issues

CHAMPION = {"basketball_nba_championship_winner": r"nba (?:finals|champion)",
            "americanfootball_nfl_super_bowl_winner": r"super bowl",
            "baseball_mlb_world_series_winner": r"world series",
            "icehockey_nhl_championship_winner": r"stanley cup|nhl (?:champion|finals)"}
WILL_WIN = re.compile(r"^will (?:the )?(.+?) win\b", re.IGNORECASE)
WIN_ON = re.compile(r"^will (.+?) win on (\d{4}-\d{2}-\d{2})\??$", re.IGNORECASE)
DRAW = re.compile(r"^will (.+?) vs\.? (.+?) end in a draw\??$", re.IGNORECASE)


def attach_outrights(markets, db) -> int:
    """Marchés « Will the X win the 2027 NBA Finals? » ↔ cote de champion de l'équipe X."""
    from polymarket_agent.sports_link import same_team
    seen, rows = _load(db, "ref:outrights") if db is not None else (None, [])
    n = 0
    for m in markets:
        if not rows or [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        q = (m.question or "").lower()
        sport = next((s for s, pat in CHAMPION.items() if re.search(pat, q)), None)
        team = WILL_WIN.match(m.question or "")
        if sport is None or team is None:
            continue
        hits = [r for r in rows if r["sport"] == sport and same_team(team.group(1), r["equipe"])]
        if len(hits) == 1:
            m.references = {**(getattr(m, "references", None) or {}),
                            "outright": {"p": hits[0]["p"], "vu_le": hits[0]["vu_le"],
                                         "titre": f"{hits[0]['titre']} — {hits[0]['equipe']} ({hits[0]['reference']})"}}
            n += 1
    return n


def attach_football(markets, observations) -> int:
    """Football (victoire / nul / victoire) : « Will Arsenal FC win on 2026-10-25? » et « Will A vs.
    B end in a draw? » ↔ cotes à 3 issues des bookmakers (odds_api, Pinnacle préféré)."""
    from polymarket_agent.sports_link import same_team
    odds = [o for o in observations if o.source == "odds_api"
            and "Draw" in ((o.data or {}).get("reference") or (o.data or {}).get("probabilites") or {})]
    n = 0
    for m in markets:
        if not odds or [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        q = (m.question or "").strip()
        win, draw = WIN_ON.match(q), DRAW.match(q)
        if not win and not draw:
            continue
        best = None
        for o in odds:
            d = o.data
            teams = (d.get("domicile", ""), d.get("exterieur", ""))
            start = parse_date(d.get("debut") or "")
            if win:
                team = next((t for t in teams if same_team(win.group(1), t)), None)
                day_ok = start is not None and abs((start.date() - datetime.fromisoformat(win.group(2)).date()).days) <= 1
                if team is None or not day_ok:
                    continue
                key = team
            else:
                if not (any(same_team(draw.group(1), t) for t in teams) and any(same_team(draw.group(2), t) for t in teams)):
                    continue
                if start is not None and m.end_date is not None and abs((start - m.end_date).days) > 2:
                    continue
                key = "Draw"
            probs = d.get("reference") or d.get("probabilites") or {}
            if key in probs and (best is None or o.collected_at > best[0].collected_at):
                best = (o, float(probs[key]))
        if best is not None:
            m.references = {**(getattr(m, "references", None) or {}),
                            "bookmakers_3": {"p": round(best[1], 4), "vu_le": best[0].collected_at.isoformat(timespec="seconds"),
                                             "titre": best[0].title}}
            n += 1
    return n


# ------------------------------------------------------------------ NHL : qui a joué la veille ?

NHL_SCHEDULE = "https://api-web.nhle.com/v1/schedule/{day}"


def _team_names(team: dict) -> list[str]:
    return [n for n in ((team.get("commonName") or {}).get("default"), (team.get("placeName") or {}).get("default"),
                        team.get("abbrev")) if n]


def fetch_nhl_rest(http: HttpClient, now: datetime | None = None) -> list[dict]:
    """Matchs NHL des 6 prochains jours, avec pour chaque équipe « a joué la veille » (un seul appel :
    le calendrier part d'hier et couvre 7 jours ; dates de la NHL, heure de l'Est)."""
    now = now or now_utc()
    yesterday = (now - timedelta(hours=4) - timedelta(days=1)).date()  # heure de l'Est, à peu près
    raw = http.get_json(NHL_SCHEDULE.format(day=yesterday.isoformat())) or {}
    played: dict[str, set[str]] = {}
    days = raw.get("gameWeek") or []
    for day in days:
        for g in day.get("games") or []:
            for side in ("awayTeam", "homeTeam"):
                played.setdefault(day["date"], set()).add((g.get(side) or {}).get("abbrev"))
    rows = []
    for day in days[1:]:  # hier ne sert qu'à savoir qui a joué
        before = (datetime.fromisoformat(day["date"]) - timedelta(days=1)).date().isoformat()
        for g in day.get("games") or []:
            away, home = g.get("awayTeam") or {}, g.get("homeTeam") or {}
            rows.append({"debut": g.get("startTimeUTC"), "date": day["date"],
                         "exterieur": _team_names(away), "domicile": _team_names(home),
                         "fatigue_exterieur": away.get("abbrev") in played.get(before, set()),
                         "fatigue_domicile": home.get("abbrev") in played.get(before, set())})
    return rows


def attach_nhl_rest(markets, db) -> int:
    """`market.references["repos_nhl"] = {"fatigue": [issue 0 a joué la veille, issue 1 …], "vu_le"}`
    pour les marchés « vainqueur » NHL (deux équipes, même coup d'envoi à 3 h près)."""
    if db is None:
        return 0
    seen, rows = _load(db, "ref:nhl_repos")
    n = 0
    for m in markets:
        if len(m.outcomes) != 2 or m.game_start is None or {o.lower() for o in m.outcomes} == {"yes", "no"}:
            continue
        for r in rows:
            start = parse_date(r.get("debut") or "")
            if start is None or abs((start - m.game_start).total_seconds()) > 3 * 3600:
                continue
            teams = {"e": [x.lower() for x in r["exterieur"]], "d": [x.lower() for x in r["domicile"]]}

            def side(outcome: str) -> str | None:
                o = outcome.lower()
                hits = [k for k, names in teams.items() if any(x == o or (len(x) > 3 and x in o) or o in x for x in names)]
                return hits[0] if len(hits) == 1 else None
            sides = [side(str(o)) for o in m.outcomes]
            if sorted(s or "" for s in sides) != ["d", "e"]:
                continue
            tired = {"e": bool(r["fatigue_exterieur"]), "d": bool(r["fatigue_domicile"])}
            m.references = dict(m.references or {}, repos_nhl={
                "fatigue": [tired[s] for s in sides], "domicile": [s == "d" for s in sides],
                "vu_le": seen.isoformat() if seen else None,
                "titre": f"{r['exterieur'][0]} à {r['domicile'][0]}, {r['date']}"})
            n += 1
            break
    return n


# ------------------------------------------------------------------ « dira-t-il ce mot ? » : taux historique

MENTION = re.compile(r"^will (.+?) (?:say|mention|be said)\b", re.IGNORECASE)


def mention_key(question: str, word: str) -> tuple[str, str] | None:
    """(orateur, mot) : « Will Trump say "crypto" or "Bitcoin" this week? », tranche « Crypto / Bitcoin »
    → ("trump", "crypto/bitcoin"). Les questions « Will "X" be said … » (sans orateur) sont écartées."""
    m = MENTION.match((question or "").strip())
    speaker = m.group(1).strip().lower() if m else ""
    w = re.sub(r"\s*/\s*", "/", (word or "").strip().lower())
    if not speaker or not w or speaker[0] in "\"'“”":
        return None
    return speaker, w


def fetch_mention_history(http: HttpClient, pages: int = 20) -> list[dict]:
    """Marchés « mentions » réglés (les plus récents d'abord) → par orateur et par mot : nombre de
    OUI et de marchés ; une ligne « * » par orateur (son taux de OUI tous mots confondus)."""
    counts: dict[tuple[str, str], list[int]] = {}
    for page in range(pages):
        events = http.get_json("https://gamma-api.polymarket.com/events", params={
            "tag_slug": "mention-markets", "closed": "true", "limit": 100, "offset": 100 * page,
            "order": "endDate", "ascending": "false"})
        if not isinstance(events, list) or not events:
            break
        for e in events:
            for mk in e.get("markets") or []:
                try:
                    res = json.loads(mk.get("outcomePrices") or "[]")
                except (ValueError, TypeError):
                    continue
                key = mention_key(mk.get("question") or "", mk.get("groupItemTitle") or "")
                if key is None or res not in (["1", "0"], ["0", "1"]):
                    continue
                for k in (key, (key[0], "*")):
                    c = counts.setdefault(k, [0, 0])
                    c[0] += res == ["1", "0"]
                    c[1] += 1
    return [{"orateur": s, "mot": w, "oui": c[0], "n": c[1]} for (s, w), c in counts.items()]


def attach_mentions(markets, db, prior: float = 2.0, new_word_min: int = 10) -> int:
    """`market.references["mentions"] = {"p", "n", "vu_le", "titre"}` : taux de OUI passé du même mot
    chez le même orateur, rapproché de son taux tous mots confondus (`prior` marchés fictifs).
    Mot jamais proposé chez un orateur qui a au moins `new_word_min` marchés passés :
    `market.references["mot_nouveau"] = {"n_orateur", "vu_le", "titre"}`."""
    if db is None:
        return 0
    seen, rows = _load(db, "ref:mentions")
    table = {(r["orateur"], r["mot"]): r for r in rows}
    n = 0
    for m in markets:
        if [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        key = mention_key(m.question, m.group_title)
        hit = table.get(key) if key else None
        base = table.get((key[0], "*"), {"oui": 1, "n": 2}) if key else None
        if key and not hit and base["n"] >= new_word_min:
            m.references = dict(m.references or {}, mot_nouveau={
                "n_orateur": base["n"], "vu_le": seen.isoformat() if seen else None,
                "titre": f"« {key[1]} » jamais proposé en {base['n']} marchés de {key[0]}"})
            n += 1
        if not hit:
            continue
        g = (base["oui"] + 1) / (base["n"] + 2)
        p = (hit["oui"] + prior * g) / (hit["n"] + prior)
        m.references = dict(m.references or {}, mentions={
            "p": round(p, 4), "n": hit["n"], "vu_le": seen.isoformat() if seen else None,
            "titre": f"{key[0]} a dit « {key[1]} » {hit['oui']} fois sur {hit['n']}"})
        n += 1
    return n
