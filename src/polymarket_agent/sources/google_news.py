"""Source : Google Actualités, flux RSS de recherche (gratuit, sans clé).

Endpoint public : https://news.google.com/rss/search?q=...&hl=en-US&gl=US&ceid=US:en
Une recherche par marché surveillé (mots distinctifs de la question), comme GDELT, qui refuse
souvent les machines de GitHub. Chaque article indique son vrai média dans <source url=...> :
c'est ce domaine qui compte pour les « sources indépendantes », pas news.google.com.
Usage : flux fourni par Google pour la lecture des actualités ; peu de requêtes par cycle.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote_plus

import requests

from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.observations import Observation
from polymarket_agent.sources._util import domain_of, parse_date


def parse_google_news(xml_bytes: bytes) -> list[dict]:
    """[{title, link, published, publisher, publisher_url}] ; le suffixe « - Média » est retiré."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(f"flux illisible : {exc}") from exc
    items = []
    for item in root.iter("item"):
        source = item.find("source")
        publisher = (source.text or "").strip() if source is not None else ""
        title = (item.findtext("title") or "").strip()
        if publisher and title.endswith(f" - {publisher}"):
            title = title[: -len(publisher) - 3].strip()
        items.append({"title": title, "link": (item.findtext("link") or "").strip(),
                      "published": item.findtext("pubDate"), "publisher": publisher,
                      "publisher_url": source.get("url", "") if source is not None else ""})
    return items


class GoogleNewsSource:
    name = "google_news"
    URL = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"

    def __init__(self, timeout: float = 10, user_agent: str = "polymarket-autonomous-lab",
                 session: requests.Session | None = None, per_query: int = 15):
        self.timeout, self.per_query = timeout, per_query
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def fetch(self, queries: list[str], now: datetime) -> list[Observation]:
        out, failures = [], 0
        for query in queries:
            try:
                response = self.session.get(self.URL.format(q=quote_plus(f"{query} when:1d")), timeout=self.timeout)
                if response.status_code != 200:
                    raise SourceUnavailable(f"HTTP {response.status_code}")
                items = parse_google_news(response.content)
            except (requests.RequestException, SourceUnavailable, ValueError):
                failures += 1
                continue
            for it in items[: self.per_query]:
                if not it["title"]:
                    continue
                out.append(Observation(
                    source=self.name, external_id=it["link"] or it["title"], published_at=parse_date(it["published"]),
                    collected_at=now, url=it["link"], title=it["title"][:500], text="",
                    domain=domain_of(it["publisher_url"]) or it["publisher"].lower(), language="en",
                    data={"query": query, "publisher": it["publisher"]}).finalize())
        if queries and failures == len(queries):
            raise SourceUnavailable(f"Google Actualités injoignable ({failures} recherches)")
        return out
