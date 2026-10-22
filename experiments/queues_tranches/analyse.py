"""Piste n° 10 : les petites tranches (OUI à 3-25 %) d'un événement à tranches gagnent-elles moins que leur prix ?
Si oui, acheter leur NON. Prix horaire du CLOB à T-24 h / T-72 h / T-168 h avant l'échéance (jamais après),
règlement relu dans Gamma, frais du marché, écart achat-vente supposé (essayé : 0,01 et 0,02)."""
import json, math, sys, datetime as dt
from collections import defaultdict
sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict

ev = {e["id"]: e for e in json.load(open("experiments/queues_tranches/donnees/evenements.json"))}
mk = {m["id"]: (e, m) for e in ev.values() for m in e["markets"]}
rows = []
for l in open("experiments/queues_tranches/donnees/prix.jsonl"):
    r = json.loads(l)
    if r["market"] in mk:
        rows.append(r)
print(len(rows), "marchés avec historique")

def fam(e):
    t = set(e["tags"]); s = e["slug"] or ""
    if "tweets-markets" in t or "of-tweets" in s or "truth-social" in s: return "tweets"
    if "elections" in t or "primaries" in t or "global-elections" in t: return "elections"
    if "crypto" in t or "crypto-prices" in t: return "crypto"
    if "ai" in t or "ai-rankings" in t: return "ia"
    return "autres"

def price_at(h, ts, maxage=6 * 3600):
    best = None
    for t, p in h:
        if t <= ts: best = (t, p)
        else: break
    return best[1] if best and ts - best[0] <= maxage else None

def fee(p, m):
    fs = m.get("fs") or {}
    return float(fs.get("rate") or 0) * p * (1 - p) if m.get("fees") else 0.0

cases = []
for r in rows:
    e, m = mk[r["market"]]
    if r["final"] not in (0.0, 1.0):
        continue
    for hrs in (24, 72, 168):
        p = price_at(r["hist"], r["end"] - hrs * 3600)
        if p is None or not (0.01 <= p <= 0.99):
            continue
        cases.append(dict(h=hrs, p=p, yes=int(r["final"] == 1.0), ev=e["id"], fam=fam(e), m=m, month=dt.datetime.fromtimestamp(r["end"], dt.timezone.utc).strftime("%Y-%m")))
print(len(cases), "cas (marché × horizon)")
bands = [(0.01, 0.03), (0.03, 0.06), (0.06, 0.10), (0.10, 0.18), (0.18, 0.25), (0.25, 0.40), (0.40, 0.60), (0.60, 0.99)]
for hrs in (24, 72, 168):
    print(f"\n== T-{hrs} h : OUI gagnés / attendus par le prix")
    for lo, hi in bands:
        v = [c for c in cases if c["h"] == hrs and lo <= c["p"] < hi]
        if len(v) < 20: continue
        w = sum(c["yes"] for c in v); ex = sum(c["p"] for c in v); var = sum(c["p"] * (1 - c["p"]) for c in v)
        print(f"  {lo:.2f}-{hi:.2f}: n={len(v)} gagnés {w} attendus {ex:.1f} ({(w-ex)/len(v)*100:+.2f} pts, z {(w-ex)/math.sqrt(var):+.2f})")

def bets(hrs, lo, hi, spread, fams=None):
    out = []
    for c in cases:
        if c["h"] != hrs or not (lo <= c["p"] < hi) or (fams and c["fam"] not in fams): continue
        cost = 1 - c["p"] + spread
        cost += fee(cost, c["m"])
        if cost >= 0.995: continue
        out.append(dict(gain=(0 if c["yes"] else 1) / cost - 1, evenement=c["ev"], mois=c["month"], cout=cost))
    return out
print("\n== Achat du NON des petites tranches : verdict (idea_test.verdict)")
n_essais = 0
for hrs in (24, 72, 168):
    for lo, hi in ((0.03, 0.25), (0.05, 0.20), (0.10, 0.25)):
        for spread in (0.01, 0.02):
            b = bets(hrs, lo, hi, spread); n_essais += 1
            v = verdict(b)
            print(f"T-{hrs}h OUI {lo}-{hi} écart {spread}: {v['paris']} paris, rend {v.get('rendement_moyen')}, t évts {v.get('confiance_evenements')} ({v.get('evenements')} évts), z prix {v.get('z_prix')}, mois {v.get('mois_gagnants')} -> {v['verdict']}")
print(n_essais, "réglages essayés")
print("\n== Par famille (T-72 h, OUI 0,03-0,25, écart 0,01)")
for f in ("tweets", "elections", "crypto", "ia", "autres"):
    b = bets(72, 0.03, 0.25, 0.01, {f}); v = verdict(b)
    print(f"  {f}: {v['paris']} paris, rend {v.get('rendement_moyen')}, t évts {v.get('confiance_evenements')} ({v.get('evenements')} évts), z prix {v.get('z_prix')} -> {v['verdict']}")

# ---- Suite (indice vu sur le premier tiers des données : les tranches à 0,25-0,60 gagnent moins que leur prix)
print("\n== Tranches moyennes : achat du NON, OUI entre 0,25 et 0,60")
n2 = 0
for hrs in (24, 72, 168):
    for lo, hi in ((0.25, 0.60), (0.25, 0.40), (0.40, 0.60)):
        for spread in (0.01, 0.02, 0.03):
            b = bets(hrs, lo, hi, spread); n2 += 1; v = verdict(b)
            print(f"T-{hrs}h OUI {lo}-{hi} écart {spread}: {v['paris']} paris, rend {v.get('rendement_moyen')}, t évts {v.get('confiance_evenements')} ({v.get('evenements')} évts), z prix {v.get('z_prix')}, mois {v.get('mois_gagnants')} {v.get('mois')} -> {v['verdict']}")
print(n2, "réglages essayés ici")
print("\n== Par famille (T-72 h, OUI 0,25-0,60, écart 0,02)")
for f in ("tweets", "elections", "crypto", "ia", "autres"):
    b = bets(72, 0.25, 0.60, 0.02, {f}); v = verdict(b)
    print(f"  {f}: {v['paris']} paris, rend {v.get('rendement_moyen')}, t évts {v.get('confiance_evenements')} ({v.get('evenements')} évts), z prix {v.get('z_prix')} -> {v['verdict']}")
# Somme des prix OUI par événement à T-72 h (événements où tous les marchés ont un prix) : « surcote » globale ?
print("\n== Somme des OUI par événement à T-72 h (exclusifs : devrait faire 1)")
byev = defaultdict(list)
for c in cases:
    if c["h"] == 72: byev[c["ev"]].append(c)
sums = []
for e_id, cs in byev.items():
    nmk = len(ev[e_id]["markets"])
    if len(cs) == nmk and sum(c["yes"] for c in cs) == 1:
        sums.append(sum(c["p"] for c in cs))
sums.sort()
if sums:
    print(f"  {len(sums)} événements complets, médiane {sums[len(sums)//2]:.3f}, moyenne {sum(sums)/len(sums):.3f}, quartiles {sums[len(sums)//4]:.3f}-{sums[3*len(sums)//4]:.3f}")
