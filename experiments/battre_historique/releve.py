"""Piste n° 61 (15/11/2026) : l'historique de « beat » de chaque société, lu sur les marchés Polymarket réglés des trimestres
précédents, bat-il le prix ? Relevé par l'étiquette `earnings` (1013) sur /events/keyset (jamais offset), puis prix horaires
du CLOB (fenêtres de 12 h avant T-1 j, T-3 j et T-7 j). -> experiments/battre_historique/donnees/marches.json (ignoré par Git)."""
import json, re, time, requests, concurrent.futures as cf
from datetime import datetime, timezone
H = {"User-Agent": "curl/8"}
S = requests.Session(); S.headers.update(H)
def get(url, params):
    for i in range(4):
        try:
            r = S.get(url, params=params, timeout=60)
            if r.status_code == 200: return r.json()
            time.sleep(1 + i)
        except requests.RequestException: time.sleep(1 + i)
evs, cur = [], None
for _ in range(400):
    p = {"tag_id": 1013, "closed": "true", "limit": 500, "order": "endDate", "ascending": "false"}
    if cur: p["after_cursor"] = cur
    r = get("https://gamma-api.polymarket.com/events/keyset", p) or {}
    page = r.get("events") or []
    evs += page; cur = r.get("next_cursor")
    if not page or not cur: break
print(len(evs), "événements de l'étiquette earnings")
rx = re.compile(r"^Will (.+?) \(([A-Z.\-]+)\) beat quarterly earnings", re.I)
rows = []
for e in evs:
    m0 = rx.match(e.get("title") or "")
    if not m0 or len(e.get("markets") or []) != 1: continue
    m = e["markets"][0]
    try: toks = json.loads(m["clobTokenIds"]); pr = json.loads(m["outcomePrices"])
    except Exception: continue
    if sorted(pr) != ["0", "1"]: continue
    rows.append(dict(eid=e["id"], ticker=m0.group(2).upper(), name=m0.group(1), yes=toks[0], won=int(pr[0] == "1"),
                     end=m.get("endDate"), closed=m.get("closedTime"), vol=float(m.get("volume") or 0), cond=m.get("conditionId"),
                     created=m.get("createdAt"), fee=m.get("feeSchedule"), desc=(m.get("description") or "")[:300]))
print(len(rows), "marchés « beat » réglés net")
def ts(s): return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
def prix(r):
    # T0 = heure de fermeture réelle (closedTime) si connue, sinon endDate ; le résultat est publié avant la fermeture.
    t_end = ts(r["closed"]) if r.get("closed") else ts(r["end"])
    out = {}
    for d in (1, 3, 7):
        t0 = t_end - d * 86400
        h = (get("https://clob.polymarket.com/prices-history", {"market": r["yes"], "startTs": int(t0 - 12 * 3600), "endTs": int(t0), "fidelity": 60}) or {}).get("history") or []
        out[f"p{d}"] = h[-1]["p"] if h else None
    r.update(out); return r
with cf.ThreadPoolExecutor(10) as ex:
    rows = list(ex.map(prix, rows))
json.dump(rows, open("experiments/battre_historique/donnees/marches.json", "w"))
print(sum(r["p1"] is not None for r in rows), "avec prix à T-1 j")
