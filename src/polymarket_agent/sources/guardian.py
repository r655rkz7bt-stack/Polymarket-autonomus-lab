"""Source : The Guardian (API officielle Open Platform), CLÉ GRATUITE requise (GUARDIAN_API_KEY).

Recherche d'articles par marché surveillé, comme Google Actualités, mais avec le texte
d'accroche fourni par le journal lui-même.
Endpoint (open-platform.theguardian.com/documentation) :
  GET https://content.guardianapis.com/search?q=…&api-key=…&order-by=newest&page-size=…&show-fields=trailText
  → {"response": {"status": "ok", "results": [{"id", "webTitle", "webUrl",
      "webPublicationDate", "fields": {"trailText"}}]}}
Offre gratuite : 500 appels par jour, 1 par seconde. Vérifié le 15/10/2026 : 401 sans clé
(format à revérifier au premier cycle avec la clé). Sans clé, la source est désactivée.
"""

from __future__ import annotations

import os
import re
from datetime import datetime

from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.observations import Observation
from polymarket_agent.sources._util import parse_date


class GuardianSource:
    name = "guardian"
    URL = "https://content.guardianapis.com/search"
    KEY = "GUARDIAN_API_KEY"

    def __init__(self, http: HttpClient, per_query: int = 10):
        self.http, self.per_query = http, per_query

    def fetch(self, queries: list[str], now: datetime) -> list[Observation]:
        key = os.environ.get(self.KEY)
        if not key:
            raise SourceUnavailable(f"pas de clé {self.KEY}")
        out = []
        for query in queries:
            try:
                raw = self.http.get_json(self.URL, params={
                    "q": query, "api-key": key, "order-by": "newest", "page-size": self.per_query,
                    "show-fields": "trailText"})
            except SourceUnavailable as exc:
                raise SourceUnavailable(f"Guardian : {str(exc).split(' : ')[-1]}") from None  # sans la clé
            for item in ((raw or {}).get("response") or {}).get("results") or []:
                trail = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", (item.get("fields") or {}).get("trailText") or ""))
                out.append(Observation(
                    source=self.name, external_id=str(item.get("id")),
                    published_at=parse_date(item.get("webPublicationDate")), collected_at=now,
                    url=str(item.get("webUrl", "")), title=str(item.get("webTitle", "")),
                    text=trail.strip()[:1000], domain="theguardian.com", data={"query": query}).finalize())
        return out
