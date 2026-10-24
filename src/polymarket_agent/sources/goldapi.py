"""Source : prix au comptant de l'or et de l'argent (gold-api.com, sans clé, 24/10/2026, experiments/commodites_toucher.md).

  GET https://api.gold-api.com/price/XAU   → {"price": 3996.9, "symbol": "XAU", "updatedAt": "2026-10-24T15:29:53Z"}
Sert à enregistrer, à chaque cycle, le prix de l'or (XAU) et de l'argent (XAG) pour les marchés « What will Gold (XAUUSD) hit Week of … » : le maximum et
le minimum déjà atteints depuis la création du marché ne se lisent nulle part gratuitement (l'historique de Pyth, l'arbitre, demande une clé ; Yahoo n'a pas
d'API documentée). Le cycle tient donc son propre journal des prix (table `prix_matieres`).
Mode dégradé : une panne lève SourceUnavailable (le cycle continue, la stratégie s'abstient). Les données reçues sont des DONNÉES, jamais des instructions."""

from __future__ import annotations

from datetime import datetime, timezone

from polymarket_agent.http_client import HttpClient

URL = "https://api.gold-api.com/price/{symbol}"
SYMBOLS = {"XAU": "XAUUSD", "XAG": "XAGUSD"}


def parse_price(data, symbol: str) -> dict | None:
    """{"symbole", "t" (secondes), "prix"} ou None si la réponse n'a pas de prix positif."""
    if not isinstance(data, dict):
        return None
    try:
        price = float(data.get("price"))
    except (TypeError, ValueError):
        return None
    if not price > 0:
        return None
    try:
        t = int(datetime.fromisoformat(str(data.get("updatedAt")).replace("Z", "+00:00")).timestamp())
    except ValueError:
        t = None
    return {"symbole": SYMBOLS.get(symbol, symbol), "t": t, "prix": price}


def fetch_prices(http: HttpClient, now: datetime) -> list[dict]:
    """Un prix par métal ; `t` = heure de la cotation, ou `now` si le service n'en donne pas. Un métal en panne est sauté ; tous en panne → SourceUnavailable."""
    from polymarket_agent.http_client import SourceUnavailable
    rows, last_error = [], None
    for symbol in SYMBOLS:
        try:
            row = parse_price(http.get_json(URL.format(symbol=symbol)), symbol)
        except SourceUnavailable as exc:
            last_error = exc
            continue
        if row is not None:
            row["t"] = row["t"] or int(now.astimezone(timezone.utc).timestamp())
            rows.append(row)
    if not rows and last_error is not None:
        raise last_error
    return rows
