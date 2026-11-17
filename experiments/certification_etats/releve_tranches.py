"""Piste n° 68 (17/11/2026) : marchés « <État>-<n> House Election Margin of Victory » encore ouverts hors Californie. Pour chaque événement,
la tranche que le marché croit courante (meilleur acheteur le plus haut) et son prix vendeur (carnet CLOB). Relevé daté dans releves/."""
import gzip, json, re, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import requests

H = {"User-Agent": "curl/8"}
OUT = Path(__file__).parent / "releves"


def events():
    evs = {}
    for q in ("House Election Margin of Victory", "Senate Election Margin of Victory", "Governor Election Margin of Victory"):
        for page in range(1, 15):
            r = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=30,
                             params={"q": q, "events_status": "active", "limit_per_type": 50, "page": page}).json()
            got = r.get("events") or []
            if not got:
                break
            for e in got:
                if "Margin of Victory" in e.get("title", ""):
                    evs[e["id"]] = e
    return list(evs.values())


def book(tok):
    try:
        b = requests.get("https://clob.polymarket.com/book", params={"token_id": tok}, headers=H, timeout=20).json()
    except Exception:
        return None, None, 0.0
    bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids") or []), reverse=True)
    asks = sorted((float(x["price"]), float(x["size"])) for x in b.get("asks") or [])
    depth = sum(s for p, s in asks if asks and p <= asks[0][0] + 0.02)
    return (bids[0][0] if bids else None), (asks[0][0] if asks else None), depth


def one(e):
    full = requests.get(f"https://gamma-api.polymarket.com/events/{e['id']}", headers=H, timeout=30).json()
    rows = []
    for m in full.get("markets") or []:
        if m.get("closed"):
            continue
        toks = json.loads(m.get("clobTokenIds") or "[]")
        if not toks:
            continue
        bid, ask, depth = book(toks[0])
        rows.append({"event": e["id"], "titre": e["title"], "marche": m["id"], "tranche": m.get("groupItemTitle"),
                     "question": m.get("question"), "bid": bid, "ask": ask, "profondeur": depth, "frais": m.get("feeType")})
    return rows


def main():
    evs = [e for e in events() if not e["title"].startswith("CA-")]
    with ThreadPoolExecutor(8) as ex:
        rows = [r for rs in ex.map(one, evs) for r in rs]
    OUT.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M")
    with gzip.open(OUT / f"tranches_{stamp}.jsonl.gz", "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(evs), "événements", len(rows), "tranches ->", OUT / f"tranches_{stamp}.jsonl.gz")


if __name__ == "__main__":
    main()
