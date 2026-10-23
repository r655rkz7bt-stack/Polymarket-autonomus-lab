"""Piste « gagnant de saison » (23/10/2026) : événements de sport à plusieurs candidats (neg-risk), clos, hors matchs.
Usage depuis experiments/saison_sport : python scripts/releve_evenements.py  -> donnees/evenements.json"""
import json, re, time, os, requests
TAG = os.environ.get("TAG", "sports")  # "" = sans filtre de tag ; sortie donnees/evenements_<NOM>.json
NOM = os.environ.get("NOM", "")
from concurrent.futures import ThreadPoolExecutor
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def page(off):
    for k in range(5):
        try:
            return s.get("https://gamma-api.polymarket.com/events", params={"closed": "true", "limit": 100, "offset": off, **({"tag_slug": TAG} if TAG else {}),
                         "order": "volume", "ascending": "false"}, timeout=60).json()
        except Exception: time.sleep(2 ** k)
    return []
out, seen = [], set()
off = 0
with ThreadPoolExecutor(4) as ex:
    while off < 8000:
        batches = list(ex.map(page, [off + 100 * i for i in range(4)])); off += 400
        stop = False
        for b in batches:
            if not isinstance(b, list) or not b: stop = True; continue
            for ev in b:
                if ev["id"] in seen: continue
                seen.add(ev["id"])
                ms = ev.get("markets") or []
                if not TAG and any((t.get('slug') in ('sports','soccer','nba','nfl','mlb','nhl','tennis','esports','golf','f1','basketball','football')) for t in (ev.get('tags') or [])): continue
                if not ev.get("negRisk") or len(ms) < 5 or re.search(r" vs\.? | v ", ev["title"]) or float(ev.get("volume") or 0) < 20000: continue
                rows = []
                for m in ms:
                    try: prs = json.loads(m["outcomePrices"]); toks = json.loads(m["clobTokenIds"])
                    except Exception: continue
                    if sorted(prs) != ["0", "1"]: continue
                    fs = m.get("feeSchedule") or {}
                    rows.append({"id": m["id"], "q": m["question"], "yes_won": prs[0] == "1", "tok": toks[0], "vol": m.get("volumeNum"),
                                 "fee": fs.get("rate") if m.get("feesEnabled") else 0, "closed": m.get("closedTime"), "end": m.get("endDate"), "start": m.get("startDate")})
                if len(rows) >= 5: out.append({"id": ev["id"], "title": ev["title"], "end": ev.get("endDate"), "closed": ev.get("closedTime"), "vol": ev.get("volume"), "markets": rows})
        print(off, len(seen), len(out), flush=True)
        if stop: break
json.dump(out, open("donnees/evenements%s.json" % NOM, "w"))
print("événements", len(out), "marchés", sum(len(e["markets"]) for e in out))
