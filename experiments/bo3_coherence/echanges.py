"""Échanges RÉELS des preneurs (data-api publique), communs aux pistes n° 1, 4 et 5.

`echanges(cle, params)` : [[heure, jeton, côté, prix, parts], ...] pour un événement (`eventId`) ou une liste de
marchés (`market` = conditionIds séparés par des virgules), avec filtre de montant facultatif (`filterType=CASH`,
`filterAmount`). La data-api renvoie les plus RÉCENTS d'abord et refuse un décalage au-delà de 10 000 : la liste
est alors « tronquée » (les plus anciens manquent) ; `tronque(rows)` le dit (11 pages pleines).
Cache gzip dans le dossier `donnees/echanges` de l'étude appelante. Plusieurs fils, chacun son HttpClient poli."""
from __future__ import annotations

import gzip
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from polymarket_agent.http_client import HttpClient, SourceUnavailable  # noqa: E402

TRADES = "https://data-api.polymarket.com/trades"
MAX_PAGES = 11
_local = threading.local()


def _http() -> HttpClient:
    if not hasattr(_local, "http"):
        _local.http = HttpClient(timeout=40, min_interval=0.15)
    return _local.http


def echanges(cache: Path, cle: str, params: dict, max_pages: int = MAX_PAGES) -> list[list] | None:
    """None si la data-api n'a pas répondu (rien mis en cache : réessayé au prochain passage)."""
    path = Path(cache) / f"{cle}.json.gz"
    if path.exists():
        return json.loads(gzip.decompress(path.read_bytes()))
    rows: list[list] = []
    for page in range(max_pages):
        try:
            batch = _http().get_json(TRADES, params=dict(params, limit=1000, offset=page * 1000))
        except SourceUnavailable:
            return None
        if not isinstance(batch, list) or not batch:
            break
        rows += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])]
                 for t in batch if t.get("timestamp") and t.get("price") is not None]
        if len(batch) < 1000:
            break
    Path(cache).mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(rows).encode()))
    return rows


def tronque(rows: list[list] | None) -> bool:
    return rows is not None and len(rows) >= MAX_PAGES * 1000


def en_parallele(taches: list[tuple[str, dict]], cache: Path, fils: int = 4) -> dict[str, list[list] | None]:
    """taches : [(clé, paramètres), ...] -> {clé: échanges}. Affiche l'avancement."""
    out: dict[str, list[list] | None] = {}

    def un(t):
        return t[0], echanges(cache, t[0], t[1])

    with ThreadPoolExecutor(fils) as ex:
        for i, (k, v) in enumerate(ex.map(un, taches), 1):
            out[k] = v
            if i % 250 == 0:
                print(f"   échanges : {i}/{len(taches)}", flush=True)
    return out


def prix_equivalent(rows: list[list], jeton: str, autre: str, debut: int, fin: int) -> list[tuple[int, float]]:
    """Prix des échanges réels du marché exprimés en prix de `jeton` (achat ou vente de `jeton` au prix p,
    ou de l'autre issue au prix 1 − p), entre `debut` et `fin` (inclus), triés par heure."""
    pts = []
    for ts, asset, _side, p, _size in rows:
        if debut <= ts <= fin:
            if asset == jeton:
                pts.append((ts, p))
            elif asset == autre:
                pts.append((ts, 1 - p))
    return sorted(pts)


def cout_preneur(rows: list[list], jeton: str, autre: str, t0: int, fenetre: int, apres: bool, fin_max: int | None = None) -> tuple[int, float] | None:
    """Prix RÉELLEMENT payé pour ACHETER `jeton` (achat de `jeton` à p, ou vente de l'autre issue à p = `jeton` à 1 − p).
    `apres` False : dernier échange dans `fenetre` AVANT t0 (prix connu à la décision) ;
    `apres` True : premier échange dans `fenetre` APRÈS t0 (prix qu'on aurait payé), jamais après `fin_max`.
    Même règle que `idea_test.taker_cost`, avec l'heure de l'échange en plus."""
    pts = sorted((ts, p if asset == jeton else 1 - p) for ts, asset, side, p, _s in rows
                 if (asset == jeton and side == "BUY") or (asset == autre and side == "SELL"))
    if apres:
        fin = t0 + fenetre if fin_max is None else min(t0 + fenetre, fin_max)
        sel = [(ts, p) for ts, p in pts if t0 <= ts <= fin]
        return sel[0] if sel else None
    sel = [(ts, p) for ts, p in pts if t0 - fenetre <= ts <= t0]
    return sel[-1] if sel else None
