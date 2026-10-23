"""Mots prononcés (orateurs nommés) aux prix payés, 23/10/2026 : relevé des événements « mentions » réglés (Gamma keyset, tag
mention-markets), puis des échanges réels de chaque marché dont le mot a déjà au moins 3 précédents chez le même orateur
(comme MotsPrononces, min_count 3). Écrit donnees/events.json, donnees/rows.json et le cache donnees/cache/<conditionId>.json.gz.
À lancer depuis experiments/mots_prix_payes/."""
import collections, gzip, json, re, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests

D = Path("donnees")
S = requests.Session()
S.headers["User-Agent"] = "curl/8"


def get(url, params):
    for k in range(5):
        try:
            return S.get(url, params=params, timeout=40).json()
        except Exception:
            time.sleep(2 ** k)
    return None


events, cursor = [], None
while True:
    params = {"tag_slug": "mention-markets", "closed": "true", "limit": 100}
    if cursor:
        params["after_cursor"] = cursor
    r = get("https://gamma-api.polymarket.com/events/keyset", params)
    if not isinstance(r, dict) or not r.get("events"):
        break
    for e in r["events"]:
        events.append({"slug": e["slug"], "title": e["title"], "endDate": e.get("endDate"), "startDate": e.get("startDate"),
                       "markets": [{"t": m.get("groupItemTitle"), "q": m.get("question"), "res": m.get("outcomePrices"),
                                    "tok": m.get("clobTokenIds"), "cond": m.get("conditionId"), "end": m.get("endDate"),
                                    "closedTime": m.get("closedTime"), "vol": m.get("volume"), "fees": m.get("feeSchedule")}
                                   for m in e.get("markets") or []]})
    cursor = r.get("next_cursor")
    print(len(events), flush=True)
    if not cursor:
        break
json.dump(events, open(D / "events.json", "w"))


def speaker(q):
    m = re.match(r'^will (.+?) (?:say|mention|be said)', (q or "").lower())
    return m.group(1) if m else None


def word(t):
    return re.sub(r"\s*/\s*", "/", (t or "").lower().strip())


rows = []
for e in events:
    for m in e["markets"]:
        try:
            res = json.loads(m["res"] or "[]")
        except Exception:
            continue
        if res not in (["1", "0"], ["0", "1"]):
            continue
        sp = speaker(m["q"])
        if not sp or not m["t"]:
            continue
        rows.append({"sp": sp, "w": word(m["t"]), "yes": res == ["1", "0"], "end": m["end"] or e["endDate"], "closed": m["closedTime"],
                     "tok": json.loads(m["tok"] or "[]"), "cond": m["cond"], "q": m["q"], "ev": e["slug"], "title": e["title"],
                     "vol": m["vol"], "fees": m["fees"]})
rows.sort(key=lambda r: r["closed"] or r["end"] or "")
seen = collections.Counter()
for r in rows:
    r["avant"] = seen[(r["sp"], r["w"])]
    seen[(r["sp"], r["w"])] += 1
todo = [r for r in rows if r["avant"] >= 3 and len(r["tok"]) == 2 and r["cond"] and r["sp"] not in ("the announcers", "anyone")]
print(len(rows), "marchés réglés,", len(todo), "à relever", flush=True)


def trades(r):
    path = D / "cache" / f"{r['cond']}.json.gz"
    if path.exists():
        return
    out = []
    for page in range(10):
        b = get("https://data-api.polymarket.com/trades", {"market": r["cond"], "limit": 1000, "offset": page * 1000})
        if not isinstance(b, list) or not b:
            break
        out += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])] for t in b if t.get("timestamp")]
        if len(b) < 1000:
            break
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(out).encode()))


with ThreadPoolExecutor(8) as ex:
    for i, _ in enumerate(ex.map(trades, todo)):
        if i % 500 == 0:
            print(i, flush=True)
json.dump({"rows": rows}, open(D / "rows.json", "w"))
print("fini", flush=True)
