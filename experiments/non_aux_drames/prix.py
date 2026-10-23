"""Piste n° 11 : historique de prix du OUI (CLOB prices-history, pas de 12 h) des marchés vol >= 5 000 $ et vie >= 14 j."""
import json, os, requests, datetime as dt, concurrent.futures as cf
H = {"User-Agent": "curl/8"}
M = json.load(open("experiments/non_aux_drames/donnees/marches.json"))
def ts(s):
    try: return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception: return None
sel = []
for m in M:
    s, e = ts(m["start"] or ""), ts(m["closed"] or m["end"] or "")
    if s and e and m["vol"] >= 5000 and (e - s) / 86400 >= 14:
        m["t_start"], m["t_close"] = s, e; sel.append(m)
OUT = "experiments/non_aux_drames/donnees/prix.json"
have = json.load(open(OUT)) if os.path.exists(OUT) else {}
def get(m):
    if m["id"] in have: return m["id"], have[m["id"]]
    out, a, end = [], int(m["t_start"]), int(m["t_close"]) + 3600
    while a < end:  # le CLOB refuse les fenêtres trop longues : tranches de 15 jours
        b = min(a + 15 * 86400, end); ok = False
        for _ in range(3):
            try:
                r = requests.get("https://clob.polymarket.com/prices-history", headers=H, timeout=60,
                                 params={"market": m["yes"], "startTs": a, "endTs": b, "fidelity": 720})
                if r.status_code == 200:
                    out += [[p["t"], p["p"]] for p in r.json().get("history", [])]; ok = True; break
            except requests.RequestException: pass
        if not ok: return m["id"], None
        a = b
    return m["id"], out
with cf.ThreadPoolExecutor(6) as ex:
    for mid, h in ex.map(get, sel):
        if h is not None: have[mid] = h
json.dump(have, open(OUT, "w"))
json.dump(sel, open("experiments/non_aux_drames/donnees/selection.json", "w"))
print(len(sel), "marchés,", len(have), "historiques,", sum(1 for h in have.values() if h), "non vides")
