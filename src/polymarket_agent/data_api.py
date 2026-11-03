"""Data API de Polymarket, version 2 (03/11/2026).

La v1 (`data-api.polymarket.com/trades`, `/activity`, `/positions`, `/traded`) répond HTTP 410 « Data API v1 has been retired »
depuis le 02-03/11/2026 : la source `inities` était « indisponible » et `suivre_inities*` muettes (enquête du 03/11,
experiments/enquetes/2026-11-03_data_api_v1_retiree.md). La v2 change trois choses :
  - noms de champs en snake_case (`proxy_wallet`, `token_id`, `condition_id`) au lieu de `proxyWallet`, `asset`, `conditionId` ;
  - réponse `{"data": [...], "pagination": {"has_more", "next_cursor"}}`, pages par CURSEUR (plus d'`offset`, plus de plafond de 10 000) ;
  - un paramètre inconnu est IGNORÉ sans erreur (`market=`, `event=` rendent les échanges de tout Polymarket) : seuls
    `event_id` / `eventId` et `condition` (alias `condition_id`, `conditionId`) filtrent.
`/traded` n'existe plus : `/user-stats?user=` donne `join_date` et `trades` (nombre d'échanges, pas de marchés).
Ce module rend des lignes au format v1 pour que les scripts et les stratégies écrits avant restent valables."""

from __future__ import annotations

from typing import Any

DATA = "https://data-api.polymarket.com/v2"
TRADES = DATA + "/trades"
ACTIVITY = DATA + "/activity"
USER_STATS = DATA + "/user-stats"

_V1 = {"proxy_wallet": "proxyWallet", "token_id": "asset", "condition_id": "conditionId", "event_slug": "eventSlug",
       "outcome_index": "outcomeIndex", "transaction_hash": "transactionHash"}


def au_format_v1(ligne: dict) -> dict:
    """Une ligne v2 avec les noms de champs de la v1 (les deux écritures restent présentes)."""
    out = dict(ligne)
    for neuf, ancien in _V1.items():
        if neuf in ligne:
            out.setdefault(ancien, ligne[neuf])
    return out


def corps(reponse: Any) -> tuple[list[dict], str | None]:
    """(lignes, curseur suivant) d'une réponse v2 ; accepte aussi une liste brute (v1, tests)."""
    if isinstance(reponse, list):
        return [r for r in reponse if isinstance(r, dict)], None
    if not isinstance(reponse, dict):
        return [], None
    pag = reponse.get("pagination") or {}
    suivant = pag.get("next_cursor") if pag.get("has_more") else None
    data = reponse.get("data")
    return ([r for r in data if isinstance(r, dict)] if isinstance(data, list) else []), suivant


def lire(http, url: str, params: dict, pages: int = 1, limite: int = 1000) -> list[dict]:
    """Jusqu'à `pages` pages d'un point d'accès v2 (par curseur), lignes au format v1. Une page qui échoue après la première
    laisse ce qui est déjà lu ; une première page qui échoue lève l'erreur de la source."""
    from polymarket_agent.http_client import SourceUnavailable
    rows: list[dict] = []
    curseur = None
    for page in range(max(1, pages)):
        p = dict(params, limit=limite)
        if curseur:
            p["cursor"] = curseur
        try:
            lot, curseur = corps(http.get_json(url, params=p))
        except SourceUnavailable:
            if page == 0:
                raise
            break
        rows += [au_format_v1(r) for r in lot]
        if not curseur or not lot:
            break
    return rows


def echanges_evenement(http, event_id: str, pages: int = 2) -> list[dict]:
    """Derniers échanges (preneurs) d'un événement, plus récents d'abord."""
    return lire(http, TRADES, {"event_id": str(event_id)}, pages)


def profil(http, adresse: str) -> dict:
    """{"premiere": date d'arrivée (s), "marches": nombre d'échanges (borne haute du nombre de marchés)} d'un compte.
    Le nombre de marchés n'est plus donné par l'API : on compte les échanges, toujours ≥ aux marchés, donc le filtre « compte
    concentré » devient plus strict, jamais plus large."""
    r = http.get_json(USER_STATS, params={"user": adresse})
    d = r.get("data") if isinstance(r, dict) else None
    d = d if isinstance(d, dict) else {}
    return {"premiere": int(d["join_date"]) if d.get("join_date") else None,
            "marches": int(d["trades"]) if d.get("trades") is not None else None}
