import json, collections, time, requests
from concurrent.futures import ThreadPoolExecutor
D = "donnees/mn"
d = json.load(open(f"{D}/data.json"))
rows = sorted(d["rows"], key=lambda r: r["closed"] or r["end"] or "")
seen = collections.Counter(); todo = []
for r in rows:
    k = (r["sp"], r["w"])
    if seen[k] == 0 and r["tok"] and not r["sp"].startswith('"'):
        r["prev_sp"] = sum(v for (s, _), v in seen.items() if s == r["sp"])
        if r["prev_sp"] >= 10: todo.append(r)
    seen[k] += 1
todo = todo[-2500:]
print("à relever", len(todo), flush=True)
s = requests.Session()
def hist(r):
    for k in range(4):
        try:
            r["hist"] = s.get("https://clob.polymarket.com/prices-history", params={"market": r["tok"][0], "interval": "max", "fidelity": 60}, timeout=40).json().get("history") or []; return
        except Exception: time.sleep(2 ** k)
    r["hist"] = []
with ThreadPoolExecutor(4) as ex: list(ex.map(hist, todo))
json.dump(todo, open(f"{D}/new.json", "w")); print("fini", flush=True)
