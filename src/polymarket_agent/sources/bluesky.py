"""Source : Bluesky (réseau social ouvert), recherche de publications.

Endpoint : `app.bsky.feed.searchPosts` ; sans compte via https://public.api.bsky.app, ou avec
un mot de passe d'application (optionnel, variables BLUESKY_HANDLE et BLUESKY_APP_PASSWORD,
jamais dans le code) via https://bsky.social. Réponse : {"posts": [{"uri", "author": {"handle"},
"record": {"text", "createdAt"}, "likeCount", "repostCount"}]}.
Les likes et reposts ne sont jamais une preuve de vérité : stockés comme simple contexte.
LIMITE : domaine bloqué dans l'environnement de construction ; format à revérifier en réel.
"""

from __future__ import annotations

import os
from datetime import datetime

from polymarket_agent.http_client import HttpClient
from polymarket_agent.observations import Observation
from polymarket_agent.sources._util import parse_date


class BlueskySource:
    name = "bluesky"

    def __init__(self, http: HttpClient, limit: int = 25):
        self.http, self.limit = http, limit
        self._token = None

    def _base_and_headers(self) -> tuple[str, dict]:
        handle, password = os.environ.get("BLUESKY_HANDLE"), os.environ.get("BLUESKY_APP_PASSWORD")
        if not (handle and password):
            return "https://public.api.bsky.app", {}
        if self._token is None:
            session = self.http.post_json("https://bsky.social/xrpc/com.atproto.server.createSession",
                                          {"identifier": handle, "password": password})
            self._token = session["accessJwt"]
        return "https://bsky.social", {"Authorization": f"Bearer {self._token}"}

    def fetch(self, queries: list[str], now: datetime) -> list[Observation]:
        base, headers = self._base_and_headers()
        self.http.session.headers.update(headers)
        out = []
        for query in queries:
            raw = self.http.get_json(f"{base}/xrpc/app.bsky.feed.searchPosts",
                                     params={"q": query, "limit": self.limit, "sort": "latest"})
            for post in (raw or {}).get("posts") or []:
                record = post.get("record") or {}
                if not record.get("text"):
                    continue
                handle = (post.get("author") or {}).get("handle", "")
                out.append(Observation(
                    source=self.name, external_id=str(post.get("uri")), published_at=parse_date(record.get("createdAt")),
                    collected_at=now, url=f"https://bsky.app/profile/{handle}", title="",
                    text=str(record["text"])[:2000], author=handle, domain="bsky.app",
                    engagement=int(post.get("likeCount") or 0) + int(post.get("repostCount") or 0),
                    data={"query": query}).finalize())
        return out
