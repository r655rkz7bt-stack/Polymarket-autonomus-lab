"""Source : prix crypto publics (Binance, repli Coinbase puis Kraken), sans clé.

Binance d'abord (15/10/2026) : c'est la SOURCE DE RÉSOLUTION des marchés crypto « au-dessus de /
en hausse ou en baisse » de Polymarket (69 marchés sur 500 dans l'inventaire du 15/10/2026).
  Binance  : GET https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=169
             (point d'accès « données de marché seulement » documenté par Binance)
             → [[ouverture ms, ouv, haut, bas, clôture, volume, fermeture ms, ...], ...] du plus
             ancien au plus récent. Vérifié par un appel réel le 15/10/2026 (accessibilité depuis
             les serveurs de GitHub à confirmer au premier cycle ; sinon repli automatique).
Endpoints de repli (documentation publique des deux plateformes) :
  Coinbase : GET https://api.exchange.coinbase.com/products/{BTC-USD}/candles?granularity=3600
             → [[temps, bas, haut, ouverture, clôture, volume], ...] du plus récent au plus ancien.
  Kraken   : GET https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=60
             → {"result": {"XXBTZUSD": [[temps, ouv, haut, bas, clôt, vwap, vol, n], ...]}}.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone

from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.observations import Observation

BINANCE = {"btc": "BTCUSDT", "eth": "ETHUSDT", "sol": "SOLUSDT", "xrp": "XRPUSDT", "doge": "DOGEUSDT"}
COINBASE = {"btc": "BTC-USD", "eth": "ETH-USD", "sol": "SOL-USD", "xrp": "XRP-USD", "doge": "DOGE-USD"}
KRAKEN = {"btc": "XBTUSD", "eth": "ETHUSD", "sol": "SOLUSD", "xrp": "XRPUSD", "doge": "XDGUSD"}


@dataclass(frozen=True)
class CryptoQuote:
    asset: str
    price: float
    hourly_vol: float  # écart-type des rendements log horaires sur ~7 jours
    as_of: datetime
    source: str


def _vol(closes: list[float]) -> float:
    rets = [math.log(b / a) for a, b in zip(closes, closes[1:]) if a > 0 and b > 0]
    if len(rets) < 24:
        raise ValueError("historique de prix trop court pour estimer la volatilité")
    mean = sum(rets) / len(rets)
    return math.sqrt(sum((r - mean) ** 2 for r in rets) / (len(rets) - 1))


class CryptoPricesSource:
    name = "crypto_prices"

    def __init__(self, http: HttpClient):
        self.http = http

    def quote(self, asset: str) -> CryptoQuote:
        errors = []
        for fetch in (self._binance, self._coinbase, self._kraken):
            try:
                return fetch(asset)
            except (SourceUnavailable, ValueError, KeyError, TypeError, IndexError) as exc:
                errors.append(f"{fetch.__name__.strip('_')}: {exc}")
        raise SourceUnavailable(f"prix {asset} indisponible ({'; '.join(errors)})")

    def _binance(self, asset: str) -> CryptoQuote:
        rows = self.http.get_json("https://data-api.binance.vision/api/v3/klines",
                                  params={"symbol": BINANCE[asset], "interval": "1h", "limit": 169})
        rows = sorted((r for r in rows if isinstance(r, list) and len(r) >= 5), key=lambda r: r[0])
        closes = [float(r[4]) for r in rows][-169:]
        return CryptoQuote(asset, closes[-1], _vol(closes),
                           datetime.fromtimestamp(rows[-1][0] / 1000, tz=timezone.utc), "binance")

    def _coinbase(self, asset: str) -> CryptoQuote:
        rows = self.http.get_json(f"https://api.exchange.coinbase.com/products/{COINBASE[asset]}/candles",
                                  params={"granularity": 3600})
        rows = sorted((r for r in rows if isinstance(r, list) and len(r) >= 5), key=lambda r: r[0])
        closes = [float(r[4]) for r in rows][-169:]
        return CryptoQuote(asset, closes[-1], _vol(closes),
                           datetime.fromtimestamp(rows[-1][0], tz=timezone.utc), "coinbase")

    def _kraken(self, asset: str) -> CryptoQuote:
        raw = self.http.get_json("https://api.kraken.com/0/public/OHLC",
                                 params={"pair": KRAKEN[asset], "interval": 60})
        if raw.get("error"):
            raise ValueError(str(raw["error"]))
        series = next(v for k, v in raw["result"].items() if k != "last")
        closes = [float(r[4]) for r in series][-169:]
        return CryptoQuote(asset, closes[-1], _vol(closes),
                           datetime.fromtimestamp(series[-1][0], tz=timezone.utc), "kraken")

    def fetch(self, assets: list[str], now: datetime) -> list[Observation]:
        out = []
        for asset in assets:
            q = self.quote(asset)
            out.append(Observation(
                source=self.name, external_id=f"{q.source}-{asset}-{int(q.as_of.timestamp())}",
                published_at=q.as_of, collected_at=now, url=f"https://{q.source}.com", title=f"{asset} {q.price}",
                text="", domain=f"{q.source}.com",
                data={"asset": asset, "price": q.price, "hourly_vol": q.hourly_vol}).finalize())
        return out
