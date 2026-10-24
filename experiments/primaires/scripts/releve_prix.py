"""Historique de prix (CLOB prices-history, pas d'une heure) de chaque candidat réel des primaires réglées, de J-35 à la date du scrutin.
Reprend où il s'est arrêté (donnees/prix.jsonl). À lancer depuis experiments/primaires/."""
import json, os, re, time, requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
PLACEHOLDER = re.compile(r"\b(Person|Candidate|Party|Player|Team|Option)\s+[A-Z]\b|^Other|another|someone else|Any other", re.I)
def jl(x): return json.loads(x) if isinstance(x, str) else x
def ts(x): return int(datetime.fromisoformat(x.replace("Z", "+00:00").replace(" ", "T").replace("+00", "+00:00") if "+00:00" not in x else x.replace("Z", "+00:00")).timestamp())
todo = []
for l in open("donnees/events.jsonl"):
    e = json.loads(l)
    if float(e["volume"] or 0) < 10000 or not e["endDate"]: continue
    cands = []
    for m in e["markets"] or []:
        try: pr = sorted(str(p) for p in jl(m["outcomePrices"])); toks = jl(m["clobTokenIds"])
        except Exception: continue
        if pr != ["0", "1"] or m.get("umaResolutionStatus") not in (None, "", "resolved"): continue
        if PLACEHOLDER.search(m.get("question") or "") or PLACEHOLDER.search(m.get("groupItemTitle") or ""): continue
        cands.append(m)
    if len(cands) >= 2:
        for m in cands:
            fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
            todo.append({"event": e["id"], "title": e["title"], "end": e["endDate"], "market": m["id"], "q": m["question"], "tok": jl(m["clobTokenIds"])[0],
                         "won": 1 if jl(m["outcomePrices"])[0] == "1" else 0, "rate": float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0,
                         "vol": float(m.get("volumeNum") or 0), "n_cands": len(cands)})
done = set()
if os.path.exists("donnees/prix.jsonl"): done = {json.loads(l)["market"] for l in open("donnees/prix.jsonl")}
todo = [t for t in todo if t["market"] not in done]
print("à relever", len(todo), flush=True)
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
def get(t):
    end = int(datetime.fromisoformat(t["end"].replace("Z", "+00:00")).timestamp())
    hist = []
    for a, b in ((end - 35 * 86400, end - 21 * 86400), (end - 21 * 86400, end - 7 * 86400), (end - 7 * 86400, end + 3600)):  # le CLOB refuse plus de ~14 jours à pas d'une heure
        for k in range(5):
            try:
                h = s.get("https://clob.polymarket.com/prices-history", params={"market": t["tok"], "startTs": a, "endTs": b, "fidelity": 60}, timeout=40).json()
                hist += [[p["t"], p["p"]] for p in h.get("history") or []]
                break
            except Exception: time.sleep(2 ** k)
        else:
            return None
    return dict(t, endts=end, h=hist)
with open("donnees/prix.jsonl", "a") as f, ThreadPoolExecutor(6) as ex:
    for i, out in enumerate(ex.map(get, todo)):
        if out: f.write(json.dumps(out) + "\n"); f.flush()
        if i % 300 == 0: print(i, len(todo), flush=True)
