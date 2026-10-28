"""Relevé des marchés « Bitcoin Up or Down » (fenêtres de 5 ou 15 minutes) et de leurs vrais échanges.

Usage : python releve.py <5m|15m> <debut AAAA-MM-JJ> <fin AAAA-MM-JJ> <un_sur_N> [fils]
Pas de pagination d'événements (adresse exacte de chaque fenêtre : le curseur /events/keyset ne sert pas ici ; seuls les échanges data-api se lisent par décalage).
Slug d'un événement : btc-updown-<5m|15m>-<epoch du début de la fenêtre>. Écrit donnees/<pas>_marches.jsonl
(un marché par ligne : issue, jetons, échanges des preneurs).
"""
import sys, json, time, datetime as dt, os, threading
from concurrent.futures import ThreadPoolExecutor
import requests

H = {"User-Agent": "curl/8"}
ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "..", "donnees")
S = threading.local()


def sess():
    if not hasattr(S, "s"):
        S.s = requests.Session(); S.s.headers.update(H)
    return S.s


def get(url, params, essais=5):
    for i in range(essais):
        try:
            r = sess().get(url, params=params, timeout=30)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (404,):
                return None
            time.sleep(1 + i)
        except requests.RequestException:
            time.sleep(1 + i)
    return None


def un_marche(args):
    pas, ep = args
    slug = f"btc-updown-{pas}-{ep}"
    ev = get("https://gamma-api.polymarket.com/events", {"slug": slug})
    if not ev:
        return None
    e = ev[0]; m = e["markets"][0]
    if not m.get("closed"):
        return None
    toks = json.loads(m["clobTokenIds"]); outs = json.loads(m["outcomes"]); pr = [float(x) for x in json.loads(m["outcomePrices"])]
    if sorted(pr) != [0.0, 1.0]:
        return {"slug": slug, "ep": ep, "net": False}
    trades = []
    for off in range(0, 10000, 1000):
        j = get("https://data-api.polymarket.com/trades", {"market": m["conditionId"], "limit": 1000, "offset": off, "takerOnly": "true"})
        if not j:
            break
        trades += [(x["timestamp"], x["asset"], x["side"], x["price"], x["size"]) for x in j]
        if len(j) < 1000:
            break
    return {"slug": slug, "ep": ep, "net": True, "cid": m["conditionId"], "up": toks[outs.index("Up")], "down": toks[outs.index("Down")],
            "gagnant": outs[pr.index(1.0)], "vol": e.get("volume"), "trades": trades}


def main():
    pas, d0, d1, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    fils = int(sys.argv[5]) if len(sys.argv) > 5 else 8
    step = 300 if pas == "5m" else 900
    t0 = int(dt.datetime.fromisoformat(d0).replace(tzinfo=dt.timezone.utc).timestamp()); t0 -= t0 % step
    t1 = int(dt.datetime.fromisoformat(d1).replace(tzinfo=dt.timezone.utc).timestamp())
    eps = list(range(t0, t1, step))[::n]
    out = os.path.join(DON, f"{pas}_marches.jsonl")
    fait = set()
    if os.path.exists(out):
        fait = {json.loads(l)["ep"] for l in open(out)}
    eps = [e for e in eps if e not in fait]
    print(len(eps), "fenêtres à relever", flush=True)
    t = time.time(); k = 0
    with open(out, "a") as f, ThreadPoolExecutor(fils) as ex:
        for r in ex.map(un_marche, [(pas, e) for e in eps]):
            k += 1
            if r:
                f.write(json.dumps(r) + "\n")
            if k % 200 == 0:
                f.flush(); print(k, round(time.time() - t), "s", flush=True)


if __name__ == "__main__":
    main()
