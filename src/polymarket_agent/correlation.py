"""Groupes de corrélation : des marchés d'événements différents mais liés.

Règle déterministe et volontairement simple (étape 4) :
  - un marché crypto est rattaché à son actif (« crypto:btc ») : « Bitcoin au-dessus
    de 80 000 $ le 15 ? » et « Bitcoin descend à 80 000 $ le 14 ? » sont corrélés ;
  - sinon le groupe est l'événement lui-même (les marchés d'un même match, d'une
    même élection, partagent déjà leur `event_id`).
Le contrôleur applique au groupe le même plafond qu'à un événement (15 %).
"""

from __future__ import annotations

import re

from polymarket_agent.models import MarketInfo

CRYPTO_ASSETS = {
    "btc": r"\b(bitcoin|btc)\b",
    "eth": r"\b(ethereum|eth|ether)\b",
    "sol": r"\b(solana|sol)\b",
    "xrp": r"\b(xrp|ripple)\b",
    "doge": r"\b(dogecoin|doge)\b",
    "bnb": r"\b(bnb|binance coin)\b",
}
_PATTERNS = {asset: re.compile(pattern, re.IGNORECASE) for asset, pattern in CRYPTO_ASSETS.items()}


def correlation_group(market: MarketInfo) -> str:
    text = f"{market.question} {market.slug.replace('-', ' ')} {market.event_title}"
    for asset, pattern in _PATTERNS.items():
        if pattern.search(text):
            return f"crypto:{asset}"
    return market.event_id
