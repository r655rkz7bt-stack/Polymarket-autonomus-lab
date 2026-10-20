"""Source : cotes des bookmakers (The Odds API), CLÉ GRATUITE requise (variable ODDS_API_KEY).

Pourquoi : les bookmakers fixent leurs cotes avec beaucoup d'argent et d'information. Leur
probabilité implicite (cotes inversées puis normalisées, moyenne des bookmakers) est un point
de comparaison direct avec le prix d'un marché sportif de Polymarket.

Endpoint (documentation officielle, the-odds-api.com/liveapi/guides/v4) :
  GET https://api.the-odds-api.com/v4/sports/{sport}/odds?apiKey=…&regions=eu&markets=h2h&oddsFormat=decimal
  → [{"id", "sport_title", "commence_time", "home_team", "away_team",
      "bookmakers": [{"key", "markets": [{"key": "h2h", "outcomes": [{"name", "price"}]}]}]}]
Coût : 1 crédit par sport et par appel ; l'offre gratuite donne 500 crédits par mois. Sans clé, la
source est désactivée.

Cotes fraîches avant les matchs (AMELIORATION du 19/10/2026) : relevées toutes les 12 h, les cotes
étaient souvent trop vieilles au coup d'envoi (cotes_bookmakers s'abstenait). Désormais :
- chaque passage (toutes les heures) lit la liste des matchs à venir de chaque ligue
  (GET /v4/sports/{sport}/events, GRATUIT d'après la documentation ; vérifié à chaque appel par
  l'en-tête « x-requests-last » : s'il coûte quelque chose, on revient à l'ancien rythme) ;
- seules les ligues qui ont un match dans les `window_hours` heures et dont les cotes ont plus de
  `refresh_hours` heures sont relevées, le match le plus proche d'abord, dans la limite de
  `daily_budget` crédits par jour (15 × 30 = 450 crédits par mois, sous les 500 gratuits) ;
- en plus de la moyenne des bookmakers, la probabilité de Pinnacle (le bookmaker le plus précis,
  celui que les autres suivent) est gardée à part (« reference ») et préférée par sports_link.
Vérifié le 15/10/2026 : l'API répond 401 « API key is not valid » sans clé (format à revérifier
au premier cycle avec la clé).
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.observations import Observation
from polymarket_agent.sources._util import parse_date

log = logging.getLogger(__name__)


def implied(bookmakers: list[dict]) -> dict[str, float]:
    """Probabilité implicite moyenne par issue, marge du bookmaker retirée (normalisation)."""
    sums: dict[str, float] = {}
    count = 0
    for book in bookmakers or []:
        market = next((m for m in book.get("markets") or [] if m.get("key") == "h2h"), None)
        if not market:
            continue
        inv = {}
        for o in market.get("outcomes") or []:
            try:
                price = float(o["price"])
            except (KeyError, TypeError, ValueError):
                continue
            if price > 1:
                inv[str(o.get("name"))] = 1 / price
        total = sum(inv.values())
        if total <= 0 or len(inv) < 2:
            continue
        count += 1
        for name, v in inv.items():
            sums[name] = sums.get(name, 0.0) + v / total
    return {k: round(v / count, 4) for k, v in sums.items()} if count else {}


class OddsApiSource:
    name = "odds_api"
    URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds"
    EVENTS_URL = "https://api.the-odds-api.com/v4/sports/{sport}/events"
    KEY = "ODDS_API_KEY"
    REFERENCE = "pinnacle"

    def __init__(self, http: HttpClient, sports: list[str], regions: str = "eu", state=None,
                 window_hours: float = 6, refresh_hours: float = 2.5, daily_budget: int = 15,
                 fallback_hours: float = 12):
        """`state` : petite mémoire entre cycles (get_value / set_value de la base) ; sans elle,
        toutes les ligues sont relevées à chaque passage (ancien comportement)."""
        self.http, self.sports, self.regions, self.state = http, sports, regions, state
        self.window, self.refresh, self.budget = window_hours, refresh_hours, daily_budget
        self.fallback = fallback_hours

    def _get(self, key: str) -> str | None:
        return self.state.get_value(key) if self.state is not None else None

    def _set(self, key: str, value: str) -> None:
        if self.state is not None:
            self.state.set_value(key, value)

    def _age_hours(self, sport: str, now: datetime) -> float:
        last = parse_date(self._get(f"odds_api:dernier:{sport}") or "")
        return (now - last).total_seconds() / 3600 if last else 1e9

    def plan(self, key: str, now: datetime) -> list[str]:
        """Ligues à relever maintenant, le match le plus proche d'abord."""
        if self.state is None:
            return list(self.sports)
        if self._get("odds_api:events_payants") == "oui":  # la liste des matchs coûte : ancien rythme
            return [s for s in self.sports if self._age_hours(s, now) >= self.fallback]
        soon = []
        for sport in self.sports:
            if self._age_hours(sport, now) < self.refresh:
                continue
            try:
                events = self.http.get_json(self.EVENTS_URL.format(sport=sport), params={"apiKey": key})
            except SourceUnavailable:
                continue
            if str(self.http.last_headers.get("x-requests-last", "0")) not in ("0", ""):
                self._set("odds_api:events_payants", "oui")
                log.warning("odds_api : la liste des matchs n'est pas gratuite, retour au rythme de %s h", self.fallback)
                return [s for s in self.sports if self._age_hours(s, now) >= self.fallback]
            starts = [t for t in (parse_date(e.get("commence_time")) for e in events or [] if isinstance(e, dict))
                      if t is not None and now <= t <= now + timedelta(hours=self.window)]
            if starts:
                soon.append((min(starts), sport))
        return [sport for _, sport in sorted(soon)]

    def fetch(self, now: datetime) -> list[Observation]:
        key = os.environ.get(self.KEY)
        if not key:
            raise SourceUnavailable(f"pas de clé {self.KEY}")
        day = f"odds_api:credits:{now:%Y-%m-%d}"
        used = int(self._get(day) or 0)
        out, errors = [], []
        for sport in self.plan(key, now):
            if self.state is not None and used >= self.budget:
                break
            try:
                events = self.http.get_json(self.URL.format(sport=sport), params={
                    "apiKey": key, "regions": self.regions, "markets": "h2h", "oddsFormat": "decimal"})
            except SourceUnavailable as exc:
                # L'URL contient la clé : on ne garde que le nom du sport et le code d'erreur.
                errors.append(f"{sport} : {str(exc).split(' : ')[-1]}")
                continue
            used += 1
            self._set(day, str(used))
            self._set(f"odds_api:dernier:{sport}", now.isoformat(timespec="seconds"))
            for ev in events or []:
                probs = implied(ev.get("bookmakers"))
                if not probs:
                    continue
                ref = implied([b for b in ev.get("bookmakers") or [] if b.get("key") == self.REFERENCE])
                home, away = ev.get("home_team", "?"), ev.get("away_team", "?")
                text = ", ".join(f"{k} {v:.0%}" for k, v in sorted(probs.items(), key=lambda kv: -kv[1]))
                start = parse_date(ev.get("commence_time"))
                out.append(Observation(
                    source=self.name, external_id=f"odds-{ev.get('id')}-{now:%Y%m%d%H}",
                    published_at=now, collected_at=now, url="https://the-odds-api.com",
                    title=f"Cotes {ev.get('sport_title', sport)} : {away} contre {home}",
                    text=f"Probabilités implicites des bookmakers : {text}", domain="the-odds-api.com",
                    data={"sport": sport, "domicile": home, "exterieur": away, "probabilites": probs,
                          "reference": ref or None, "reference_nom": self.REFERENCE if ref else None,
                          "bookmakers": len(ev.get("bookmakers") or []),
                          "debut": start.isoformat() if start else None}).finalize())
        if errors and not out:
            raise SourceUnavailable("; ".join(errors)[:200])
        return out
