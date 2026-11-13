"""Événements « Largest / 2nd / 3rd Largest Company end of <mois> » réglés (Gamma) et prix horaires de leurs marchés
(CLOB prices-history, tranches de 14 jours sur les 21 derniers jours avant la fin). Sortie : donnees/marches.json."""
import json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import requests

H = {"User-Agent": "curl/8"}
OUT = Path(__file__).parent / "donnees"
evs = json.loads((Path(__file__).parent / "releves" / "evenements_clos.json").read_text())
evs = [e for e in evs if "private" not in e["title"].lower() and "indian" not in e["title"].lower()]


def history(token, start, end):
    pts = []
    s = start
    while s < end:
        e = min(end, s + 13 * 86400)
        for _ in range(3):
            try:
                r = requests.get("https://clob.polymarket.com/prices-history",
                                 params={"market": token, "startTs": s, "endTs": e, "fidelity": 60}, timeout=30)
                pts += r.json().get("history", [])
                break
            except Exception:
                time.sleep(2)
        s = e
    return sorted({p["t"]: p["p"] for p in pts}.items())


def one(ev):
    e = requests.get(f"https://gamma-api.polymarket.com/events/{ev['id']}", headers=H, timeout=30).json()
    out = []
    for m in e.get("markets", []):
        if not m.get("closed") or not m.get("clobTokenIds"):
            continue
        prices = json.loads(m.get("outcomePrices") or "[]")
        if not prices or float(prices[0]) not in (0.0, 1.0):
            continue
        tok = json.loads(m["clobTokenIds"])[0]
        end = datetime.fromisoformat(m["endDate"].replace("Z", "+00:00")).timestamp()
        hist = history(tok, int(end - 22 * 86400), int(end + 86400))
        if not hist:
            continue
        out.append({"event": ev["id"], "title": e["title"], "end": m["endDate"], "company": m.get("groupItemTitle"),
                    "market": m["id"], "won": float(prices[0]), "feeType": m.get("feeType"), "volume": m.get("volume"),
                    "hist": hist})
    print(ev["id"], e["title"][:50], len(out), file=sys.stderr)
    return out


with ThreadPoolExecutor(6) as ex:
    res = [x for r in ex.map(one, evs) for x in r]
(OUT / "marches.json").write_text(json.dumps(res))
print(len(res), file=sys.stderr)
