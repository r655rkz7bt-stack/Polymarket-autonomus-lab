"""Source : GDELT DOC 2.0 (actualités mondiales, gratuit, sans clé).

Endpoint (documentation GDELT) : GET https://api.gdeltproject.org/api/v2/doc/doc
  ?query=...&mode=artlist&format=json&maxrecords=50&timespan=1h&sort=datedesc
  → {"articles": [{"url", "title", "seendate": "AAAAMMJJTHHMMSSZ", "domain", "language", ...}]}
GDELT demande au plus une requête toutes les 5 secondes : on interroge peu de mots-clés par cycle.
LIMITE : domaine bloqué dans l'environnement de construction ; format à revérifier en réel.
"""

from __future__ import annotations

import time
from datetime import datetime

from polymarket_agent.http_client import HttpClient
from polymarket_agent.observations import Observation
from polymarket_agent.sources._util import parse_date


class GdeltSource:
    name = "gdelt"
    URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(self, http: HttpClient, timespan: str = "3h", max_records: int = 50,
                 pause_seconds: float = 5.0, sleep=time.sleep):
        self.http, self.timespan, self.max_records = http, timespan, max_records
        self.pause, self._sleep = pause_seconds, sleep

    def fetch(self, queries: list[str], now: datetime) -> list[Observation]:
        out = []
        for i, query in enumerate(queries):
            if i:
                self._sleep(self.pause)
            raw = self.http.get_json(self.URL, params={
                "query": query, "mode": "artlist", "format": "json", "maxrecords": self.max_records,
                "timespan": self.timespan, "sort": "datedesc"})
            for a in (raw or {}).get("articles") or []:
                if not isinstance(a, dict) or not a.get("url"):
                    continue
                out.append(Observation(
                    source=self.name, external_id=str(a["url"]), published_at=parse_date(a.get("seendate")),
                    collected_at=now, url=str(a["url"]), title=str(a.get("title") or "")[:500], text="",
                    domain=str(a.get("domain") or ""), language=str(a.get("language") or ""),
                    data={"query": query}).finalize())
        return out
