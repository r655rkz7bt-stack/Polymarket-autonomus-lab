"""Petits outils partagés par les sources."""

from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse


def parse_date(value) -> datetime | None:
    """ISO 8601, RFC 822 (RSS) ou format compact GDELT (AAAAMMJJTHHMMSSZ)."""
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    for attempt in (
        lambda t: datetime.fromisoformat(t.replace("Z", "+00:00")),
        lambda t: parsedate_to_datetime(t),
        lambda t: datetime.strptime(t, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc),
    ):
        try:
            result = attempt(text)
        except (ValueError, TypeError, IndexError):
            continue
        if result is not None:
            return result if result.tzinfo else result.replace(tzinfo=timezone.utc)
    return None


def domain_of(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").removeprefix("www.")
    except ValueError:
        return ""
