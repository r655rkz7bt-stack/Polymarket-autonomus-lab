"""Prix horaires du OUI (CLOB prices-history, tranches de 14 jours, fidelity 60) des marchés à coordonnées, de leur création à
leur fermeture (ou maintenant). Sortie : donnees/prix.json {market_id: [[t, p], ...]}"""
import json, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "donnees"


def ts(s):
    s = s.replace("Z", "+00:00").replace(" ", "T")
    if "+" not in s[10:]:
        s += "+00:00"
    if s.endswith("+00"):
        s += ":00"
    return datetime.fromisoformat(s).timestamp()


def hist(m):
    if not m["tokens"]:
        return m["id"], []
    a = ts(m["creation"]) if m.get("creation") else time.time() - 200 * 86400
    b = ts(m["ferme"]) if m.get("ferme") else time.time()
    out, s = [], a
    while s < b:
        e = min(s + 13 * 86400, b)
        for _ in range(3):
            try:
                h = requests.get("https://clob.polymarket.com/prices-history", timeout=60,
                                 params={"market": m["tokens"][0], "startTs": int(s), "endTs": int(e), "fidelity": 60}).json()
                out += [[x["t"], x["p"]] for x in h.get("history", [])]
                break
            except Exception:
                time.sleep(2)
        s = e
    return m["id"], sorted(set(map(tuple, out)))


ms = [m for m in json.loads((D / "marches.json").read_text()) if m["lat"] is not None]
with ThreadPoolExecutor(6) as ex:
    res = dict(ex.map(hist, ms))
(D / "prix.json").write_text(json.dumps(res))
print(len(res), "marchés,", sum(1 for v in res.values() if v), "avec prix,", sum(len(v) for v in res.values()), "points")
