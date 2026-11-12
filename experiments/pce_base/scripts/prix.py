"""Prix horaires (prices-history CLOB, tranches de 14 jours) du OUI de chaque tranche des événements réglés -> donnees/prix.json."""
import json, pathlib, time, requests
from datetime import datetime, timezone
d = pathlib.Path(__file__).resolve().parent.parent / "donnees"
ev = json.loads((d / "evenements.json").read_text())
out = {}
for e in ev:
    for m in e["markets"]:
        tok = json.loads(m["clobTokenIds"])[0]
        t0 = int(datetime.fromisoformat(m["createdAt"].replace("Z", "+00:00")).timestamp())
        t1 = int(datetime.fromisoformat((m.get("closedTime") or e["endDate"]).replace(" ", "T").replace("Z", "+00:00").replace("+00+00:00","+00:00")).timestamp()) if e.get("closed") else int(time.time())
        pts = []
        s = t0
        while s < t1:
            r = requests.get("https://clob.polymarket.com/prices-history", timeout=30,
                             params={"market": tok, "startTs": s, "endTs": min(s + 13 * 86400, t1), "fidelity": 60})
            pts += r.json().get("history", [])
            s += 13 * 86400
        out[m["id"]] = {"event": e["id"], "title": e["title"], "tranche": m.get("groupItemTitle"), "win": json.loads(m["outcomePrices"])[0],
                        "closed": m.get("closedTime"), "pts": sorted({p["t"]: p["p"] for p in pts}.items())}
(d / "prix.json").write_text(json.dumps(out))
print(len(out))
