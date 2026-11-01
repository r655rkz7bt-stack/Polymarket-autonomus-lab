"""Stop-loss (demande d'Etienne, 01/11/2026) : positions réelles de l'arène et historique de prix de chaque jeton.

1. Positions réglées de tous les fantômes (journaux publiés : `bash scripts/fetch_data.sh`) : achat(s), règlement, prix payé,
   borne basse de la stratégie, coup d'envoi.
2. Historique du CLOB (`prices-history`, pas de 5 minutes) de 24 h avant le premier achat jusqu'au règlement.
Sortie : experiments/stop_loss/donnees/positions.json.gz et prix/<jeton>.json.gz (dossier ignoré par Git).
Usage : .venv/bin/python experiments/stop_loss/scripts/releve.py
"""

from __future__ import annotations

import glob
import gzip
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[3]
DONNEES = ROOT / "experiments" / "stop_loss" / "donnees"
CLOB = "https://clob.polymarket.com/prices-history"


def ts(s: str) -> int:
    return int(datetime.fromisoformat(s).timestamp())


def positions() -> list[dict]:
    out = []
    for f in sorted(glob.glob(str(ROOT / "published_data" / "ledger" / "fantome" / "*.jsonl"))):
        nom = Path(f).stem
        ouvertes: dict[str, dict] = {}
        for line in open(f, encoding="utf-8"):
            e = json.loads(line)
            d = e.get("data") or {}
            if e["type"] == "RESET":
                ouvertes.clear()
            elif e["type"] == "BUY":
                p = ouvertes.setdefault(d["token_id"], {"strategie": nom, "jeton": d["token_id"], "marche": d.get("market_id"),
                                                       "evenement": d.get("event_id"), "achat": ts(e["ts"]), "cout": 0.0,
                                                       "parts": 0.0, "prob_low": None, "coup_envoi": None, "posee": False})
                x = d.get("extra") or {}
                p["cout"] += float(d["price"]) * float(d["shares"]) + float(d.get("fee") or 0)
                p["parts"] += float(d["shares"])
                if p["prob_low"] is None and x.get("prob_low"):
                    p["prob_low"] = float(x["prob_low"])
                if p["coup_envoi"] is None and x.get("depuis_coup_d_envoi_h") not in (None, ""):
                    p["coup_envoi"] = ts(e["ts"]) - float(x["depuis_coup_d_envoi_h"]) * 3600
                p["posee"] = p["posee"] or x.get("order_type") == "limite"
            elif e["type"] == "SELL" and d.get("token_id") in ouvertes:
                ouvertes.pop(d["token_id"])  # revendue avant le règlement : hors du test
            elif e["type"] == "SETTLE" and d.get("token_id") in ouvertes:
                p = ouvertes.pop(d["token_id"])
                p["reglement"] = ts(e["ts"])
                p["paiement"] = float(d["payout_per_share"])
                out.append(p)
    return out


def relever(jeton: str, debut: int, fin: int) -> int:
    path = DONNEES / "prix" / f"{jeton}.json.gz"
    if path.exists():
        return -1
    pts = []
    t = debut
    while t < fin:
        bout = min(fin, t + 13 * 86400)
        try:
            r = requests.get(CLOB, params={"market": jeton, "startTs": t, "endTs": bout, "fidelity": 5}, timeout=30)
            hist = r.json().get("history", []) if r.status_code == 200 else []
        except (requests.RequestException, ValueError):
            hist = []
        pts += [(int(h["t"]), float(h["p"])) for h in hist]
        t = bout
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        json.dump(sorted(set(pts)), fh)
    return len(pts)


def main() -> None:
    (DONNEES / "prix").mkdir(parents=True, exist_ok=True)
    pos = positions()
    with gzip.open(DONNEES / "positions.json.gz", "wt", encoding="utf-8") as fh:
        json.dump(pos, fh)
    fenetres: dict[str, list[int]] = {}
    for p in pos:
        w = fenetres.setdefault(p["jeton"], [p["achat"] - 86400, p["reglement"]])
        w[0], w[1] = min(w[0], p["achat"] - 86400), max(w[1], p["reglement"])
    print(f"{len(pos)} positions réglées, {len(fenetres)} jetons", flush=True)
    with ThreadPoolExecutor(8) as pool:
        done = 0
        for _ in pool.map(lambda kv: relever(kv[0], *kv[1]), fenetres.items()):
            done += 1
            if done % 500 == 0:
                print(f"  {done}/{len(fenetres)}", flush=True)
    print("fini")


if __name__ == "__main__":
    main()
