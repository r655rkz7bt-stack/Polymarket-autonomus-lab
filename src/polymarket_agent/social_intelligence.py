"""News & Social Intelligence : relier les observations aux marchés et les résumer.

Règles du cahier des charges, appliquées ici par construction :
  - la viralité (likes, reposts, réactions) n'entre dans AUCUN calcul de signal ;
  - un message isolé n'est jamais un signal : il faut >= 2 sources indépendantes
    (domaines distincts, copies exclues) ;
  - l'absence d'information n'est pas un signal (signal = False, direction = 0) ;
  - si une source active est indisponible, l'analyse est marquée PARTIELLE ;
  - X étant payant et désactivé, l'analyse sociale est toujours partielle sur ce point.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from polymarket_agent.models import MarketInfo
from polymarket_agent.observations import Observation, tokens

STOPWORDS = {
    "will", "the", "and", "for", "with", "this", "that", "from", "before", "after", "than", "more",
    "less", "over", "under", "above", "below", "between", "into", "what", "which", "who", "when",
    "win", "wins", "lose", "price", "reach", "dip", "hit", "end", "yes", "not", "any", "game",
    "match", "vs.", "vs", "market", "markets", "2025", "2026", "2027", "january", "february",
    "march", "april", "may", "june", "july", "august", "september", "october", "november",
    "december", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "today", "tomorrow", "week", "month", "year", "day", "post", "posts", "tweets", "least",
    "des", "les", "une", "pour", "avec", "dans", "sur", "par", "est", "sera", "qui", "que",
}


def keywords(market: MarketInfo, limit: int = 6) -> list[str]:
    """Mots distinctifs de la question (noms propres, actifs…), du plus long au plus court."""
    words = [w for w in tokens(f"{market.question} {market.event_title}")
             if w not in STOPWORDS and not w.replace(",", "").replace(".", "").replace("$", "").isdigit()
             and len(w) >= 4]
    return sorted(set(words), key=lambda w: (-len(w), w))[:limit]


def search_query(market: MarketInfo, n: int = 2) -> str:
    return " ".join(keywords(market, n))


def match(observations: list[Observation], markets: list[MarketInfo], min_hits: int = 2,
          max_markets: int = 5) -> None:
    """Rattache chaque observation aux marchés qui lui correspondent vraiment (15/10/2026) :
    - assez de mots distinctifs du marché (`min_hits`), dont au moins un dans le TITRE ;
    - les mots rares pèsent plus que ceux partagés par beaucoup de marchés (pondération
      « fréquence inverse » : « bitcoin », présent dans 30 marchés, compte peu) ;
    - au plus `max_markets` marchés par observation, les mieux notés (un article général ne se
      retrouve plus sur 40 marchés, ce qui faussait les comptes et les avis de Gemini).
    Les commentaires Polymarket sont rattachés directement à leur événement."""
    import math
    index = [(m, set(keywords(m))) for m in markets]
    df: dict[str, int] = {}
    for _, kws in index:
        for w in kws:
            df[w] = df.get(w, 0) + 1
    n = max(1, len(index))
    weight = {w: math.log(1 + n / c) for w, c in df.items()}
    for obs in observations:
        if obs.source == "polymarket_comments":
            event_id = obs.data.get("event_id")
            obs.market_ids = [m.market_id for m in markets if m.event_id == event_id]
            continue
        if obs.source in ("crypto_prices", "meteo_metar", "meteo_prevision"):
            continue  # prix crypto : par actif ; météo : rattachée directement aux marchés de sa station
        title = tokens(obs.title or "")
        words = title | tokens(obs.text or "")
        scored = []
        for market, kws in index:
            hits = words & kws
            need = min(min_hits, len(kws))
            if not need or len(hits) < need or not (hits & title):
                continue
            scored.append((sum(weight[w] for w in hits) + 0.5 * sum(weight[w] for w in hits & title), market))
        scored.sort(key=lambda x: -x[0])
        for _, market in scored[: max(1, max_markets)]:
            if market.market_id not in obs.market_ids:
                obs.market_ids.append(market.market_id)


@dataclass
class MarketIntel:
    market_id: str
    mentions_1h: int = 0
    mentions_24h: int = 0
    spike: float = 0.0  # mentions de la dernière heure / moyenne horaire sur 24 h
    independent_sources: int = 0  # domaines distincts, copies exclues
    official: int = 0
    rumors: int = 0
    opinions: int = 0
    duplicates: int = 0
    sentiment: float = 0.0  # moyenne pondérée par la fiabilité, -1 à 1
    stance: float = 0.0  # direction estimée par l'IA (-1 = Non, +1 = Oui), 0 si inconnue
    last_published: datetime | None = None
    official_minutes: float | None = None  # âge de la dernière annonce officielle (minutes)
    official_stance: float = 0.0  # direction de cette annonce selon l'IA (-1 à 1), 0 si inconnue
    signal: bool = False
    partial: bool = True
    sources_down: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def summarize(market_id: str, observations: list[Observation], now: datetime,
              sources_down: list[str], stances: dict[str, dict] | None = None) -> MarketIntel:
    stances = stances or {}
    mine = [o for o in observations if market_id in o.market_ids]
    original = [o for o in mine if not o.duplicate_of]

    def when(o: Observation) -> datetime:
        return o.published_at or o.collected_at

    last24 = [o for o in original if when(o) >= now - timedelta(hours=24)]
    last1 = [o for o in last24 if when(o) >= now - timedelta(hours=1)]
    intel = MarketIntel(market_id, mentions_1h=len(last1), mentions_24h=len(last24),
                        duplicates=len(mine) - len(original),
                        sources_down=sorted(set(sources_down) | {"x_api (payant, désactivé)"}))
    intel.partial = True  # X est toujours absent : l'analyse sociale est partielle par nature
    intel.spike = round(len(last1) / max(len(last24) / 24, 1e-9), 2) if last24 else 0.0
    intel.independent_sources = len({o.domain for o in last24 if o.domain})
    intel.official = sum(1 for o in last24 if o.kind == "annonce officielle")
    intel.rumors = sum(1 for o in last24 if o.kind == "rumeur")
    intel.opinions = sum(1 for o in last24 if o.kind == "opinion")
    weight = sum(o.reliability for o in last24)
    if weight:
        intel.sentiment = round(sum(o.sentiment * o.reliability for o in last24) / weight, 3)
    directed = [(stances[o.external_id], o.reliability) for o in last24 if o.external_id in stances]
    if directed:
        num = sum({"oui": 1, "non": -1}.get(s["stance"], 0) * s["confidence"] * r for s, r in directed)
        den = sum(s["confidence"] * r for s, r in directed)
        intel.stance = round(num / den, 3) if den else 0.0
    intel.last_published = max((when(o) for o in last24), default=None)
    officials = sorted((o for o in last24 if o.kind == "annonce officielle"), key=when)
    if officials:
        latest = officials[-1]
        intel.official_minutes = round((now - when(latest)).total_seconds() / 60, 1)
        s = stances.get(latest.external_id)
        if s:
            intel.official_stance = {"oui": 1, "non": -1}.get(s["stance"], 0) * s["confidence"]
    # Signal : jamais sur un message isolé, jamais sur la viralité, jamais sur l'absence.
    if not last24:
        intel.reasons.append("aucune information (l'absence n'est pas un signal)")
    elif intel.independent_sources < 2:
        intel.reasons.append("une seule source : jamais un signal suffisant")
    elif intel.official == 0 and sum(o.reliability for o in last24) / len(last24) < 0.5:
        intel.reasons.append("sources peu fiables (rumeurs, opinions)")
    else:
        intel.signal = True
    return intel
