"""Source : cotes des bookmakers (The Odds API), CLÉ GRATUITE requise (variable ODDS_API_KEY).

Pourquoi : les bookmakers fixent leurs cotes avec beaucoup d'argent et d'information. Leur
probabilité implicite (cotes inversées puis normalisées, moyenne des bookmakers) est un point
de comparaison direct avec le prix d'un marché sportif de Polymarket.

Endpoint (documentation officielle, the-odds-api.com/liveapi/guides/v4) :
  GET https://api.the-odds-api.com/v4/sports/{sport}/odds?apiKey=…&regions=eu&markets=h2h&oddsFormat=decimal
  → [{"id", "sport_title", "commence_time", "home_team", "away_team",
      "bookmakers": [{"key", "markets": [{"key": "h2h", "outcomes": [{"name", "price"}]}]}]}]
Coût : 1 crédit par sport et par appel ; l'offre gratuite donne 500 crédits par mois. Réglage
par défaut : 5 sports toutes les 12 h ≈ 300 crédits par mois. Sans clé, la source est désactivée.
Vérifié le 15/10/2026 : l'API répond 401 « API key is not valid » sans clé (format à revérifier
au premier cycle avec la clé).
"""

from __future__ import annotations

import os
from datetime import datetime

from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.observations import Observation
from polymarket_agent.sources._util import parse_date


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
    KEY = "ODDS_API_KEY"

    def __init__(self, http: HttpClient, sports: list[str], regions: str = "eu"):
        self.http, self.sports, self.regions = http, sports, regions

    def fetch(self, now: datetime) -> list[Observation]:
        key = os.environ.get(self.KEY)
        if not key:
            raise SourceUnavailable(f"pas de clé {self.KEY}")
        out, errors = [], []
        for sport in self.sports:
            try:
                events = self.http.get_json(self.URL.format(sport=sport), params={
                    "apiKey": key, "regions": self.regions, "markets": "h2h", "oddsFormat": "decimal"})
            except SourceUnavailable as exc:
                # L'URL contient la clé : on ne garde que le nom du sport et le code d'erreur.
                errors.append(f"{sport} : {str(exc).split(' : ')[-1]}")
                continue
            for ev in events or []:
                probs = implied(ev.get("bookmakers"))
                if not probs:
                    continue
                home, away = ev.get("home_team", "?"), ev.get("away_team", "?")
                text = ", ".join(f"{k} {v:.0%}" for k, v in sorted(probs.items(), key=lambda kv: -kv[1]))
                start = parse_date(ev.get("commence_time"))
                out.append(Observation(
                    source=self.name, external_id=f"odds-{ev.get('id')}-{now:%Y%m%d%H}",
                    published_at=now, collected_at=now, url="https://the-odds-api.com",
                    title=f"Cotes {ev.get('sport_title', sport)} : {away} contre {home}",
                    text=f"Probabilités implicites des bookmakers : {text}", domain="the-odds-api.com",
                    data={"sport": sport, "domicile": home, "exterieur": away, "probabilites": probs,
                          "bookmakers": len(ev.get("bookmakers") or []),
                          "debut": start.isoformat() if start else None}).finalize())
        if errors and not out:
            raise SourceUnavailable("; ".join(errors)[:200])
        return out
