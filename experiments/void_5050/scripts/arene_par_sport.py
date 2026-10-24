"""Pour chaque marché acheté par les portefeuilles nf_*/principal : sport (série Gamma), type de pari, règlement. Sortie : arene_marches.json"""
import json, glob, requests, concurrent.futures as cf
H = {"User-Agent": "curl/8"}
mk = set()
for f in glob.glob("published_data/ledger/fantome/*.jsonl") + ["published_data/ledger/ledger.jsonl"]:
    for l in open(f):
        r = json.loads(l)
        if r["type"] == "BUY" and r["data"].get("extra", {}).get("depuis_coup_d_envoi_h") is not None or (r["type"] == "BUY" and "nf_" in r["data"]["strategy_id"]):
            mk.add(r["data"]["market_id"])
def get(m):
    for _ in range(3):
        try:
            j = requests.get(f"https://gamma-api.polymarket.com/markets/{m}", headers=H, timeout=30).json()
            ev = {"seriesSlug": (j.get("slug") or "").split("-")[0]}
            return m, dict(sp=ev.get("seriesSlug"), t=j.get("sportsMarketType"), q=j.get("question"), op=j.get("outcomePrices"), gs=j.get("gameStartTime"))
        except Exception:
            pass
    return m, None
with cf.ThreadPoolExecutor(8) as ex:
    res = dict(ex.map(get, sorted(mk)))
json.dump(res, open("experiments/void_5050/arene_marches.json", "w"))
print(len(res))
