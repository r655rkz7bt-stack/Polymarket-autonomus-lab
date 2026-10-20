import json, re, collections, time, requests
from concurrent.futures import ThreadPoolExecutor
D = "donnees/mn"
evs = json.load(open(f"{D}/events.json"))
def speaker(q):
    m = re.match(r'^will (.+?) (?:say|mention|be said)', (q or "").lower())
    return m.group(1) if m else None
def word(t): return re.sub(r"\s*/\s*", "/", (t or "").lower().strip())
rows = []
for e in evs:
    for m in e["markets"]:
        try: r = json.loads(m["res"] or "[]")
        except Exception: continue
        if r not in (["1", "0"], ["0", "1"]): continue
        sp = speaker(m["q"])
        if not sp or not m["t"]: continue
        rows.append({"sp": sp, "w": word(m["t"]), "yes": r == ["1", "0"], "end": m["end"] or e["endDate"],
                     "closed": m["closedTime"], "tok": json.loads(m["tok"] or "[]"), "q": m["q"], "ev": e["slug"], "vol": m["vol"]})
rows.sort(key=lambda r: r["closed"] or r["end"] or "")
seen = collections.Counter(); todo = []
for r in rows:
    if seen[(r["sp"], r["w"])] >= 3 and r["tok"]: todo.append(r)
    seen[(r["sp"], r["w"])] += 1
todo = todo[-3000:]
print("à relever", len(todo), flush=True)
s = requests.Session()
def hist(r):
    for k in range(4):
        try:
            h = s.get("https://clob.polymarket.com/prices-history", params={"market": r["tok"][0], "interval": "max", "fidelity": 60}, timeout=40).json()
            r["hist"] = h.get("history") or []; return
        except Exception: time.sleep(2 ** k)
    r["hist"] = []
with ThreadPoolExecutor(4) as ex:
    for i, _ in enumerate(ex.map(hist, todo)):
        if i % 250 == 0: print(i, flush=True)
json.dump({"rows": rows, "todo": todo}, open(f"{D}/data.json", "w"))
print("fini", flush=True)
