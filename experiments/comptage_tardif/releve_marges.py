"""Piste n° 66 (16/11/2026) : relevé daté des marchés encore ouverts des élections américaines du 03/11/2026
(étiquette `midterms` 102289, /events/keyset), pour les juger quand les résultats certifiés seront publiés :
le prix à J+13 tient-il compte des bulletins tardifs (Californie, Oregon, Washington : courrier) ?
Écrit releves/marges_<AAAAMMJJTHHMM>.jsonl.gz (une ligne par marché : prix Gamma, carnet acheteur/vendeur)."""
import gzip, json, sys, datetime as dt, requests
from pathlib import Path

H = {"User-Agent": "curl/8"}


def evenements(tag=102289):
    out, cur = [], None
    while True:
        p = {"tag_id": tag, "closed": "false", "limit": 100}
        if cur:
            p["after_cursor"] = cur
        r = requests.get("https://gamma-api.polymarket.com/events/keyset", params=p, headers=H, timeout=30).json()
        out += r.get("events") or []
        cur = r.get("next_cursor")
        if not cur or not r.get("events"):
            return out


def main():
    now = dt.datetime.now(dt.timezone.utc)
    lignes = []
    for e in evenements():
        for m in e.get("markets", []):
            if m.get("closed") or not m.get("outcomePrices"):
                continue
            lignes.append({"ts": now.isoformat(timespec="seconds"), "event_id": e["id"], "event": e["title"],
                           "market_id": m["id"], "item": m.get("groupItemTitle") or m.get("question"),
                           "prices": json.loads(m["outcomePrices"]), "bid": m.get("bestBid"), "ask": m.get("bestAsk"),
                           "volume": m.get("volume"), "fee": m.get("feeType"), "end": m.get("endDate")})
    path = Path(__file__).parent / "releves" / f"marges_{now:%Y%m%dT%H%M}.jsonl.gz"
    with gzip.open(path, "wt") as f:
        for l in lignes:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")
    print(len(lignes), "marchés ->", path)


if __name__ == "__main__":
    main()
