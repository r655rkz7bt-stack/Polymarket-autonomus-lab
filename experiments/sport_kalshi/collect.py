"""Test sport Kalshi, étape 1 : listes des matchs RÉGLÉS sur les deux plateformes (API publiques, sans clé).

Usage : python3 -I experiments/sport_kalshi/collect.py <dossier_de_travail> src [début AAAA-MM-JJ] [fin AAAA-MM-JJ]
Écrit <dossier>/kalshi_<ligue>.json et <dossier>/pm_<ligue>.json (et un cache brut dans <dossier>/cache/).
"""
import json, sys, time
from datetime import datetime, timedelta
from pathlib import Path
W, SRC = sys.argv[1], sys.argv[2]
sys.path[:0] = [str(Path(__file__).resolve().parent), SRC]
from common import CLOB, GAMMA, KALSHI, LEAGUES, cached_get, ts  # noqa: E402

START = sys.argv[3] if len(sys.argv) > 3 else "2026-09-01"
END = sys.argv[4] if len(sys.argv) > 4 else "2026-10-15"
Path(W).mkdir(parents=True, exist_ok=True)
t0, t1 = ts(START + "T00:00:00Z"), ts(END + "T23:59:59Z")
# Les marchés Kalshi d'un match ferment à la fin du match ; on prend 2 jours de marge.
for lg, (tag, series, _) in LEAGUES.items():
    out, cursor = [], ""
    for page in range(50):
        params = {"series_ticker": series, "status": "settled", "limit": 1000,
                  "min_close_ts": t0, "max_close_ts": t1 + 2 * 86400}
        if cursor:
            params["cursor"] = cursor
        d = cached_get(W, SRC, f"{KALSHI}/markets", params) or {}
        out += d.get("markets") or []
        time.sleep(1)
        cursor = d.get("cursor") or ""
        if not cursor:
            break
    json.dump(out, open(f"{W}/kalshi_{lg}.json", "w"))
    # Polymarket : marchés « moneyline » (vainqueur du match) clos. L'échéance (endDate) d'un match
    # américain est le coup d'envoi + 7 jours, celle d'un match de football le coup d'envoi : fenêtre large,
    # puis tri sur l'heure du coup d'envoi (gameStartTime).
    pm, end_max = [], (datetime.fromisoformat(END) + timedelta(days=9)).strftime("%Y-%m-%d")
    for page in range(200):
        batch = cached_get(W, SRC, f"{GAMMA}/markets", {
            "closed": "true", "tag_id": tag, "sports_market_types": "moneyline", "limit": 100, "offset": page * 100,
            "end_date_min": f"{START}T00:00:00Z", "end_date_max": f"{end_max}T23:59:59Z"})
        if not isinstance(batch, list):
            break
        pm += batch
        if len(batch) < 100:
            break
    keep = [m for m in pm if m.get("gameStartTime") and t0 <= ts(m["gameStartTime"]) <= t1]
    json.dump(keep, open(f"{W}/pm_{lg}.json", "w"))
    print(f"{lg:5s} Kalshi {len(out):5d} marchés réglés | Polymarket {len(keep):5d} marchés vainqueur "
          f"(sur {len(pm)} lus)")
    time.sleep(0.5)
