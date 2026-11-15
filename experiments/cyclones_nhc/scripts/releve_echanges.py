"""Piste n° 63 : vrais échanges (data-api v2, filtre `condition`) de chaque marché de donnees/evenements.json → donnees/echanges.jsonl."""
import json, sys, time, requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from polymarket_agent.data_api import lire

D = Path(__file__).resolve().parents[1] / "donnees"

class Http:
    def __init__(self): self.s = requests.Session(); self.s.headers["User-Agent"] = "curl/8"
    def get_json(self, url, params=None, **_):
        r = self.s.get(url, params=params, timeout=40); r.raise_for_status(); return r.json()

def un(m):
    http = Http()
    rows = []
    for essai in range(5):
        try:
            rows = lire(http, "https://data-api.polymarket.com/v2/trades", {"condition": m["condition"]}, pages=30); break
        except Exception as ex:
            print("essai", essai, m["id"], str(ex)[:60]); time.sleep(3 * (essai + 1))
    return [dict(marche=m["id"], ts=int(r.get("timestamp")), cote=r.get("side"), issue=r.get("outcome"), jeton=r.get("asset"),
                 prix=float(r.get("price")), parts=float(r.get("size")), condition=r.get("conditionId")) for r in rows]

if __name__ == "__main__":
    ev = json.loads((D / "evenements.json").read_text())
    ms = [m for e in ev for m in e["marches"] if m.get("condition")]
    with ThreadPoolExecutor(4) as ex, open(D / "echanges.jsonl", "w") as f:
        for rows in ex.map(un, ms):
            bad = [r for r in rows if r["condition"] != rows[0]["condition"]] if rows else []
            for r in rows: f.write(json.dumps(r) + "\n")
            print(rows[0]["marche"] if rows else "-", len(rows), "échanges", "CONDITION MÉLANGÉE" if bad else "")
