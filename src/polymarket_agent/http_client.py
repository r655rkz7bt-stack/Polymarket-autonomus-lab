"""Client HTTP poli et robuste : délais progressifs, limite de fréquence, erreurs explicites."""

from __future__ import annotations

import logging
import time
from typing import Any

import requests

log = logging.getLogger(__name__)
RETRY_STATUS = {429, 500, 502, 503, 504}


class SourceUnavailable(Exception):
    """La source n'a pas répondu correctement après plusieurs tentatives."""


class HttpClient:
    def __init__(self, timeout: float = 15, max_retries: int = 3, backoff: float = 1.0,
                 min_interval: float = 0.2, user_agent: str = "polymarket-autonomous-lab",
                 session: requests.Session | None = None, sleep=time.sleep):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff
        self.min_interval = min_interval
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept": "application/json"})
        self._sleep = sleep
        self._last_call = 0.0

    def request_json(self, method: str, url: str, *, params: dict | None = None,
                     json_body: Any = None) -> Any:
        last_error = "inconnue"
        for attempt in range(self.max_retries + 1):
            wait = self.min_interval - (time.monotonic() - self._last_call)
            if wait > 0:
                self._sleep(wait)
            self._last_call = time.monotonic()
            try:
                response = self.session.request(method, url, params=params, json=json_body,
                                                timeout=self.timeout)
            except requests.RequestException as exc:
                last_error = f"{type(exc).__name__}"
            else:
                if response.status_code == 200:
                    try:
                        return response.json()
                    except ValueError:
                        last_error = "réponse non JSON"
                elif response.status_code in RETRY_STATUS:
                    last_error = f"HTTP {response.status_code}"
                    retry_after = response.headers.get("Retry-After", "")
                    if retry_after.isdigit() and attempt < self.max_retries:
                        self._sleep(min(int(retry_after), 30))
                        continue
                else:
                    raise SourceUnavailable(f"{method} {url} : HTTP {response.status_code}")
            if attempt < self.max_retries:
                delay = self.backoff * (2 ** attempt)
                log.warning("%s %s : %s, nouvel essai dans %.1f s", method, url, last_error, delay)
                self._sleep(delay)
        raise SourceUnavailable(f"{method} {url} : échec après {self.max_retries + 1} essais ({last_error})")

    def get_json(self, url: str, params: dict | None = None) -> Any:
        return self.request_json("GET", url, params=params)

    def post_json(self, url: str, body: Any) -> Any:
        return self.request_json("POST", url, json_body=body)
