"""Même relevé que experiments/vingt_pistes/scripts/tweets_releve_marches.py (marchés « combien de messages » de 7 comptes, 3/7 → 20/10/2026,
prix horaires du CLOB), en parallèle (6 fils) : l'original prend plus d'une heure. Écrit donnees/xt/marches.json."""
import json, time, requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
D = "donnees/xt"
PREFIX = {"elonmusk": "elon-musk-of-tweets", "WhiteHouse": "white-house-of-tweets", "tedcruz": "ted-cruz-of-tweets",
          "ZelenskyyUa": "zelenskyy-of-tweets", "realDonaldTrump": "donald-trump-of-truth-social-posts",
          "NYCMayor": "nyc-mayor-of-tweets", "cz_binance": "cz-binance-of-tweets"}
H = {"User-Agent": "curl/8"}
def get(url, params):
    for k in range(5):
        try:
            return requests.get(url, params=params, headers=H, timeout=40).json()
        except Exception:
            time.sleep(2 ** k)
    return {}
def one(job):
    h, p, day = job
    end = day + timedelta(days=7)
    tag = f"{day:%B}-{day.day}-{end:%B}-{end.day}-{end.year}".lower()
    ev = get("https://gamma-api.polymarket.com/events", {"slug": f"{p}-{tag}"})
    if not ev:
        return None
    ev = ev[0]; mk = []
    for m in ev.get("markets") or []:
        tok = json.loads(m.get("clobTokenIds") or "[]")
        if not tok:
            continue
        hist = get("https://clob.polymarket.com/prices-history", {"market": tok[0], "startTs": int(day.timestamp()),
                                                                  "endTs": int(end.timestamp()), "fidelity": 60}).get("history") or []
        mk.append({"titre": m.get("groupItemTitle"), "prix_final": m.get("outcomePrices"), "hist": hist})
    print(h, tag, len(mk), flush=True)
    return {"compte": h, "debut": day.isoformat(), "fin": end.isoformat(), "slug": ev["slug"], "volume": ev.get("volume"), "marches": mk}
jobs, day = [], datetime(2026, 7, 1, 16, tzinfo=timezone.utc)
while day < datetime(2026, 10, 24, tzinfo=timezone.utc):
    if day.weekday() in (1, 4) and day + timedelta(days=7) < datetime.now(timezone.utc) - timedelta(hours=6):
        jobs += [(h, p, day) for h, p in PREFIX.items()]
    day += timedelta(days=1)
with ThreadPoolExecutor(6) as ex:
    out = [r for r in ex.map(one, jobs) if r]
json.dump(out, open(f"{D}/marches.json", "w"))
print(len(jobs), "essais,", len(out), "périodes trouvées")
