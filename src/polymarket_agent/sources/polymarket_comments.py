"""Source : commentaires publics des événements Polymarket (Gamma `GET /comments`).

Vérifié le 15/10/2026 par appel réel : paramètres `parent_entity_type=Event`,
`parent_entity_id`, `limit`, `order=createdAt`, `ascending=false` ; champs `id`, `body`,
`createdAt`, `profile.pseudonym`, `reactionCount`. Fiabilité faible : ce sont des avis de
parieurs, souvent intéressés (« easy money »). Jamais un signal à eux seuls.
"""

from __future__ import annotations

from datetime import datetime

from polymarket_agent.http_client import HttpClient
from polymarket_agent.observations import Observation
from polymarket_agent.sources._util import parse_date


class CommentsSource:
    name = "polymarket_comments"

    def __init__(self, http: HttpClient, base_url: str = "https://gamma-api.polymarket.com",
                 per_event: int = 20):
        self.http, self.base_url, self.per_event = http, base_url.rstrip("/"), per_event

    def fetch(self, event_ids: list[str], now: datetime) -> list[Observation]:
        out = []
        for event_id in event_ids:
            if not str(event_id).isdigit():
                continue
            raw = self.http.get_json(f"{self.base_url}/comments", params={
                "parent_entity_type": "Event", "parent_entity_id": event_id,
                "limit": self.per_event, "order": "createdAt", "ascending": "false"})
            for c in raw if isinstance(raw, list) else []:
                if not isinstance(c, dict) or not c.get("body"):
                    continue
                profile = c.get("profile") or {}
                out.append(Observation(
                    source=self.name, external_id=f"pm-comment-{c.get('id')}",
                    published_at=parse_date(c.get("createdAt")), collected_at=now,
                    url=f"https://polymarket.com/event/{event_id}", title="",
                    text=str(c["body"])[:2000], author=str(profile.get("pseudonym") or ""),
                    domain="polymarket.com", engagement=int(c.get("reactionCount") or 0),
                    data={"event_id": str(event_id)}).finalize())
        return out
