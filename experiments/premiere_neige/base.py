"""Première neige (trace comprise) par ville : fréquence historique (RCC-ACIS, sans clé) de la première neige entre le 12/11 et
le 15/11 ou le 30/11, sachant qu'il n'a pas neigé depuis le 1er octobre jusqu'au 11/11 ; saison 2026 lue au même endroit."""
import json, sys, requests
ST = ["BOS", "BUF", "ORD", "DTW", "IND", "MCI", "MSP", "PIT", "SLC", "CVG", "DFW", "BNA", "NYC", "PHL", "STL", "DCA"]
out = {}
for s in ST:
    r = requests.post("https://data.rcc-acis.org/StnData", json={"sid": s, "sdate": "1991-10-01", "edate": "2026-11-11",
                      "elems": [{"name": "snow"}]}, timeout=60).json()
    data = r.get("data") or []
    by = {d: v for d, v in data}
    def snowy(v): return v not in ("0", "0.0", "M", "", None) and v != "S"
    res = {"n": 0, "a15": 0, "a30": 0, "deja": 0}
    for y in range(1991, 2026):
        days = [f"{y}-10-{d:02d}" for d in range(1, 32)] + [f"{y}-11-{d:02d}" for d in range(1, 31)]
        first = next((d for d in days if snowy(by.get(d))), None)
        if first is not None and first <= f"{y}-11-11":
            res["deja"] += 1; continue
        res["n"] += 1
        if first is not None and first <= f"{y}-11-15": res["a15"] += 1
        if first is not None: res["a30"] += 1
    cur = [(d, by.get(d)) for d in sorted(by) if d >= "2026-10-01" and snowy(by.get(d))]
    res["2026"] = cur[:3]
    res["manquants_2026"] = sum(1 for d in by if d >= "2026-10-01" and by[d] == "M")
    out[s] = res
    print(s, res["n"], "hivers sans neige au 11/11 ;", "P(≤15/11)", round(res["a15"] / max(res["n"], 1), 3), "P(≤30/11)", round(res["a30"] / max(res["n"], 1), 3), "| déjà neigé au 11/11 :", res["deja"], "| 2026 :", cur[:2], "M:", res["manquants_2026"])
json.dump(out, open(sys.argv[1], "w"), indent=1)
