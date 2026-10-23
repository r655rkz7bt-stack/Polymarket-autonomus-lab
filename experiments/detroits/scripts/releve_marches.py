"""Relève les événements Gamma sur Ormuz / Bab el-Mandeb (ouverts et réglés) : titre, marchés, volumes."""
import json, sys, requests
H = {"User-Agent": "curl/8"}
G = "https://gamma-api.polymarket.com"
mots = ("hormuz", "bab el-mandeb", "bab-el-mandeb", "red sea", "suez", "strait", "transit")
seen = {}
for closed in ("false", "true"):
    for off in range(0, 3000, 100):
        r = requests.get(f"{G}/events", params=dict(closed=closed, limit=100, offset=off, order="volume", ascending="false"), headers=H, timeout=40)
        ev = r.json()
        if not isinstance(ev, list) or not ev:
            print('arrêt', closed, off, str(ev)[:100])
            break
        for e in ev:
            t = (e.get("title", "") + " " + e.get("slug", "")).lower()
            if any(m in t for m in mots):
                seen[e["id"]] = e
        if closed == "true" and off >= 2900:
            break
print(len(seen))
rows = []
for e in seen.values():
    rows.append(dict(id=e["id"], title=e["title"], slug=e["slug"], closed=e["closed"], end=e.get("endDate"), vol=e.get("volume"), n=len(e["markets"])))
rows.sort(key=lambda r: r["end"] or "")
json.dump(rows, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
for r in rows: print(r["id"], r["closed"], (r["end"] or "")[:10], round(float(r["vol"] or 0)), r["n"], r["title"][:80])
