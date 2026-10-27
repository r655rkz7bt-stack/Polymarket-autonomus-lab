"""Juste après midi (Est), le côté gagnant d'une échelle quotidienne « above ___ on <date> » se paie-t-il encore moins de 0,97 ? (27/10/2026)
Le résultat est connu d'une bougie Binance de 12 h ; le côté gagnant est pris sur le règlement Gamma (en direct : lu sur le prix de la bougie, à contrôler). Prix payé = premier échange de preneur
qui ACHÈTE le côté gagnant dans [midi + 60 s ; midi + W]. Seuls les marchés dont le côté gagnant n'était PAS déjà coté >= 0,985 à midi - 60 s comptent (les autres n'ont rien à offrir)."""
import json, gzip, re, sys, datetime as dt, collections, statistics
from pathlib import Path
from zoneinfo import ZoneInfo
sys.path.insert(0, "src")
from polymarket_agent import idea_test as it
D = Path("experiments/crypto_apres_midi/donnees"); ET = ZoneInfo("America/New_York")
MOIS = {m: i + 1 for i, m in enumerate(("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"))}
DAILY = re.compile(r"^(Bitcoin|Ethereum|Solana|XRP) above ___ on \w+ \d+\?$")
def midi(title):
    m = re.search(r"on (\w+) (\d+)\?", title)
    if not m or m.group(1) not in MOIS: return None
    for y in (2026, 2025):
        try: return int(dt.datetime(y, MOIS[m.group(1)], int(m.group(2)), 12, 0, tzinfo=ET).timestamp())
        except ValueError: pass
def run(W=1800, delai=60):
    res = []
    for l in open(D / "echelles.jsonl"):
        e = json.loads(l)
        if not DAILY.match(e["title"]): continue
        T0 = midi(e["title"]); p = D / "echanges" / f"echanges_{e['id']}.json.gz"
        if T0 is None or not p.exists(): continue
        tr = json.loads(gzip.decompress(p.read_bytes())); by = collections.defaultdict(list)
        for t in tr: by[t[1]].append(t)
        for m in e["markets"]:
            try:
                op = [float(x) for x in json.loads(m["outcomePrices"])]; yes, no = json.loads(m["clobTokenIds"])
            except Exception: continue
            if max(op) < 0.99: continue
            win, lose = (yes, no) if op[0] > 0.5 else (no, yes)
            rate = ((m.get("feeSchedule") or {}).get("rate")) or 0.0
            avant = [(t[0], t[3] if t[1] == win else 1 - t[3]) for t in by[win] + by[lose] if t[0] <= T0 - delai]
            deja = max(avant)[1] if avant else None
            if deja is not None and deja >= 0.985: continue
            achats = sorted((t[0], t[3] if t[1] == win else 1 - t[3], t[4]) for t in by[win] + by[lose]
                            if T0 + delai <= t[0] <= T0 + W and ((t[1] == win and t[2] == "BUY") or (t[1] == lose and t[2] == "SELL")))
            if not achats: res.append(dict(eid=e["id"], pay=None, titre=m["question"][:50])); continue
            when, price, size = achats[0]
            res.append(dict(eid=e["id"], pay=price, size=size, dt=when - T0, deja=deja, titre=m["question"][:60], gain=(1 - price - it.fee(price, rate)) / (price + it.fee(price, rate))))
    return res
if __name__ == "__main__":
    for W in (300, 900, 3600):
        R = run(W); got = [r for r in R if r["pay"] is not None]
        print(f"== fenêtre {W // 60} min après midi+60 s : marchés non encore à 0,985 : {len(R)}, avec un achat du gagnant : {len(got)}")
        if not got: continue
        for seuil in (0.99, 0.97, 0.95, 0.90):
            s = [r for r in got if r["pay"] <= seuil]
            print(f"   payé <= {seuil}: {len(s)} marchés, gain moyen {100 * sum(r['gain'] for r in s) / max(1, len(s)):+.1f} %, parts du premier échange médiane {statistics.median([r['size'] for r in s]) if s else 0:.0f}")
        print("   par événements:", len({r["eid"] for r in got if r["pay"] <= 0.97}), "| prix payé médian", round(statistics.median(r["pay"] for r in got), 3))
