"""Source : X (Twitter). DÉSACTIVÉE : l'API est payante (≈ 0,005 $ par publication lue).

Interdit absolu n°2 de CLAUDE.md : aucun service payant. Remplacée par Bluesky, GDELT et
les flux RSS. L'analyse sociale est donc explicitement PARTIELLE.
"""

from __future__ import annotations

from polymarket_agent.http_client import SourceUnavailable


class XSource:
    name = "x_api"

    def fetch(self, *args, **kwargs):
        raise SourceUnavailable("X désactivé : API payante (interdit n°2 de CLAUDE.md)")
