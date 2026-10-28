"""Tire 60 règlements des 72 dernières heures dans tous les journaux de fantômes et relit le marché sur Gamma (/markets/<id>) : le paiement par part du journal
est-il celui d'outcomePrices pour ce jeton ? Racine du dépôt."""
import json, glob, random, requests, datetime
random.seed(2810)
s = requests.Session(); s.headers["User-Agent"] = "curl/8"
lim = (datetime.datetime(2026, 10, 28, 11, tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=72)).isoformat()
achats, rg = {}, []
for f in glob.glob("published_data/ledger/fantome/*.jsonl") + ["published_data/ledger/ledger.jsonl"]:
    for l in open(f):
        r = json.loads(l); d = r["data"]
        if r["type"] == "BUY": achats[d["token_id"]] = (d["market_id"], d["outcome"], f.split("/")[-1][:30], d.get("extra", {}).get("fill_status"))
        elif r["type"] == "SETTLE" and r["ts"] >= lim: rg.append((f.split("/")[-1][:30], d["token_id"], d["payout_per_share"], r["ts"]))
print(len(rg), "règlements récents")
tires = random.sample(rg, min(60, len(rg)))
ok = ko = 0
for strat, tok, pay, ts in tires:
    if tok not in achats: continue
    mid, outcome, _, _ = achats[tok]
    m = s.get(f"https://gamma-api.polymarket.com/markets/{mid}", timeout=30).json()
    toks = json.loads(m["clobTokenIds"]); prices = [float(x) for x in json.loads(m["outcomePrices"])]
    if tok not in toks: print("jeton absent", strat, mid); ko += 1; continue
    attendu = prices[toks.index(tok)]
    bon = abs(attendu - float(pay)) < 1e-6 and m.get("closed")
    ok += bool(bon); ko += not bon
    if not bon: print("ÉCART", strat, mid, m.get("question", "")[:70], "journal", pay, "Gamma", attendu, "closed", m.get("closed"), m.get("umaResolutionStatus"))
print("conformes", ok, "écarts", ko)
