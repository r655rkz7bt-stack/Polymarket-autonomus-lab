"""27/10/2026 : proxy du test de `classement_appstore` sur le passé. Apple n'archive pas le classement ; on prend le FAVORI DU MARCHÉ (le candidat le plus cher) à midi (Est) - h comme « n°1 du moment »
et on regarde s'il est n°1 à midi (règlement Gamma) et ce qu'il coûte (premier échange de preneur dans l'heure). Événements hebdomadaires « #1 Free / Paid App in the US Apple App Store on <date> ? » (125 réglés)."""
import json, re, sys, gzip, datetime as dt, collections, requests, math
from pathlib import Path
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
D = Path("experiments/appstore_direct/donnees"); ET = ZoneInfo("America/New_York"); H = {"User-Agent": "curl/8"}
MOIS = {m: i + 1 for i, m in enumerate(("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"))}
def releve():
    ev = {}
    for q in ("#1 Free App in the US Apple App Store", "#1 Paid App in the US Apple App Store"):
        for pg in range(1, 9):
            r = requests.get("https://gamma-api.polymarket.com/public-search", params={"q": q, "events_status": "closed", "limit_per_type": 50, "page": pg}, headers=H, timeout=60).json()
            for e in r.get("events", []):
                if re.match(r"#1 (Free|Paid) App in the US Apple App Store on", e["title"]): ev[e["id"]] = e
            if not r.get("events") or not r.get("pagination", {}).get("hasMore"): break
    json.dump(list(ev.values()), open(D / "evenements.json", "w"))
    http = HttpClient(min_interval=0.05)
    with ThreadPoolExecutor(8) as ex: list(ex.map(lambda i: it.fetch_event_trades(http, D / "echanges", str(i)), list(ev)))
def midi(e):
    m = re.search(r"on (\w+) (\d+)", e["title"]); y = int(e["endDate"][:4])
    return int(dt.datetime(y, MOIS[m.group(1)], int(m.group(2)), 12, 0, tzinfo=ET).timestamp())
def analyse(h, fen=3 * 3600, W=3600):
    res = []
    for e in json.load(open(D / "evenements.json")):
        p = D / "echanges" / f"echanges_{e['id']}.json.gz"
        if not p.exists(): continue
        tr = json.loads(gzip.decompress(p.read_bytes())); T = midi(e) - int(h * 3600)
        cands = []
        for m in e["markets"]:
            try: op = [float(x) for x in json.loads(m["outcomePrices"])]; yes, no = json.loads(m["clobTokenIds"])
            except Exception: continue
            last = [(t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr if t[1] in (yes, no) and T - fen <= t[0] <= T]
            if not last: continue
            cands.append((max(last)[1], m, yes, no, op))
        if len(cands) < 2: continue
        price, m, yes, no, op = max(cands, key=lambda c: c[0])
        buys = sorted((t[0], t[3] if t[1] == yes else 1 - t[3]) for t in tr if T <= t[0] <= T + W and ((t[1] == yes and t[2] == "BUY") or (t[1] == no and t[2] == "SELL")))
        if not buys or max(op) < 0.99: continue
        pay = buys[0][1]
        res.append(dict(eid=e["id"], kind="free" if "Free" in e["title"] else "paid", leader=price, pay=pay, win=op[0] > 0.5, titre=m["question"][:50]))
    return res
if __name__ == "__main__":
    if "--releve" in sys.argv: releve()
    for h in (6, 3, 1):
        R = analyse(h)
        for kind in ("free", "paid", None):
            s = [r for r in R if kind is None or r["kind"] == kind]
            if not s: continue
            w = sum(r["win"] for r in s); ex = sum(r["pay"] for r in s); var = sum(r["pay"] * (1 - r["pay"]) for r in s)
            g = sum(r["win"] - r["pay"] for r in s) / sum(r["pay"] for r in s)
            print(f"h={h} {kind or 'tous':5s} n={len(s):3d} le favori du marché gagne {w:3d} fois pour {ex:5.1f} attendues (z {(w - ex) / math.sqrt(var):+.2f}), prix payé moyen {sum(r['pay'] for r in s) / len(s):.3f}, rendement {100 * g:+.1f} % (sans frais : 0 frais sur ces marchés)")
