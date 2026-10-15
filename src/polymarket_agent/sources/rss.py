"""Source : flux RSS / Atom de médias et de sources officielles (bibliothèque standard).

Les flux sont listés dans config/settings.yaml (`sources.rss.feeds`), chacun marqué
`official: true` s'il s'agit d'une source officielle. Analyse avec xml.etree (aucune
dépendance) ; un flux illisible est ignoré sans bloquer les autres.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.observations import Observation
from polymarket_agent.sources._util import domain_of, parse_date

ATOM = "{http://www.w3.org/2005/Atom}"
RSS1 = "{http://purl.org/rss/1.0/}"


def parse_feed(xml_text: str | bytes) -> list[dict]:
    """Retourne [{title, link, summary, published}] pour RSS 2.0, RSS 1.0 (RDF) et Atom.

    Accepte des octets bruts (préférable : l'encodage déclaré dans le XML et un éventuel
    BOM UTF-8 sont alors gérés correctement, cf. flux de la Fed).
    """
    if isinstance(xml_text, str):
        xml_text = xml_text.lstrip("\ufeff").lstrip("ï»¿")
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError(f"flux illisible : {exc}") from exc
    items = []
    for item in root.iter("item"):
        items.append({"title": (item.findtext("title") or "").strip(),
                      "link": (item.findtext("link") or "").strip(),
                      "summary": (item.findtext("description") or "").strip(),
                      "published": item.findtext("pubDate") or item.findtext("{http://purl.org/dc/elements/1.1/}date")})
    for item in root.iter(f"{RSS1}item"):  # RSS 1.0 (RDF), ex. DW
        items.append({"title": (item.findtext(f"{RSS1}title") or "").strip(),
                      "link": (item.findtext(f"{RSS1}link") or "").strip(),
                      "summary": (item.findtext(f"{RSS1}description") or "").strip(),
                      "published": item.findtext("{http://purl.org/dc/elements/1.1/}date")})
    for entry in root.iter(f"{ATOM}entry"):
        link = entry.find(f"{ATOM}link")
        items.append({"title": (entry.findtext(f"{ATOM}title") or "").strip(),
                      "link": (link.get("href") if link is not None else "") or "",
                      "summary": (entry.findtext(f"{ATOM}summary") or "").strip(),
                      "published": entry.findtext(f"{ATOM}updated") or entry.findtext(f"{ATOM}published")})
    return items


class RssSource:
    name = "rss"

    def __init__(self, feeds: list[dict], timeout: float = 10, user_agent: str = "polymarket-autonomous-lab",
                 session: requests.Session | None = None, workers: int = 8):
        self.feeds = feeds
        self.timeout, self.workers = timeout, max(1, workers)
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.failures: dict[str, str] = {}

    def _download(self, feed: dict):
        """(flux, éléments, erreur) — jamais d'exception : un flux en panne n'arrête pas les autres."""
        try:
            response = self.session.get(feed["url"], timeout=self.timeout)
            if response.status_code != 200:
                raise SourceUnavailable(f"HTTP {response.status_code}")
            return feed, parse_feed(response.content), None  # octets : BOM et encodage gérés
        except (requests.RequestException, SourceUnavailable, ValueError) as exc:
            return feed, [], f"{type(exc).__name__}: {exc}"[:200]

    def fetch(self, now: datetime) -> list[Observation]:
        out, self.failures = [], {}
        # Plusieurs dizaines de flux : téléchargement en parallèle pour garder le cycle court.
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            results = list(pool.map(self._download, self.feeds))
        for feed, items, error in results:
            url = feed["url"]
            if error:
                self.failures[url] = error
                continue
            source = "rss_officiel" if feed.get("official") else "rss"
            for it in items[: int(feed.get("max_items", 30))]:
                if not it["link"] and not it["title"]:
                    continue
                out.append(Observation(
                    source=source, external_id=it["link"] or it["title"], published_at=parse_date(it["published"]),
                    collected_at=now, url=it["link"], title=it["title"][:500], text=it["summary"][:1500],
                    domain=domain_of(it["link"]) or domain_of(url), language=feed.get("language", ""),
                    data={"feed": feed.get("name", url)}).finalize())
        if self.feeds and len(self.failures) == len(self.feeds):
            raise SourceUnavailable(f"aucun flux RSS joignable ({len(self.feeds)} essayés)")
        return out
