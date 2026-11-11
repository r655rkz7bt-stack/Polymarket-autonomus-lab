"""Test sur le passé de la piste n° 26 : GISS du mois prévu par ERA5 (Climate Pulse) + écart des 3 mois d'avant, contre le prix
des tranches avant publication. Entrées : evenements.json (releve.py), CSV Climate Pulse, GLB.Ts+dSST.txt (chemins en argument).
Regard vers le futur connu : GISS des mois précédents lu dans le fichier d'aujourd'hui (révisions de ±0,01-0,02) ; ERA5 final."""
import collections, json, math, re, statistics as st, sys, time
from datetime import datetime, timezone
import requests

EV, CP, GISS = sys.argv[1:4]
JOUR = int(sys.argv[4]) if len(sys.argv) > 4 else 5
SD = float(sys.argv[5]) if len(sys.argv) > 5 else 0.05
DELTA = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
MOIS = {m: i + 1 for i, m in enumerate("January February March April May June July August September October November December".split())}
era = collections.defaultdict(list)
for l in open(CP):
    if l[0] == "#" or l.startswith("date"): continue
    p = l.strip().split(",")
    if len(p) >= 4: era[(int(p[0][:4]), int(p[0][5:7]))].append(float(p[3]))
giss = {}
for l in open(GISS):
    p = l.split()
    if p and p[0].isdigit() and len(p) > 13:
        for m in range(12):
            if p[m + 1].lstrip("-").isdigit(): giss[(int(p[0]), m + 1)] = int(p[m + 1]) / 100
Phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
prev = lambda y, m: (y, m - 1) if m > 1 else (y - 1, 12)

def bornes(t):
    t = t.replace("ºC", "").replace("°C", "").strip()
    if t.startswith("<"): return -9.0, float(t[1:]) - 0.005
    if t.startswith(">"): return float(t[1:]) + 0.005, 9.0
    a, b = re.split(r"[–-]", t); return float(a) - 0.005, float(b) + 0.005

def prix(token, ts):
    h = requests.get("https://clob.polymarket.com/prices-history", params=dict(market=token, startTs=ts - 86400, endTs=ts, fidelity=60), timeout=30).json().get("history") or []
    return h[-1]["p"] if h else None

rows = []
for e in json.load(open(EV)):
    mt = re.match(r"(\w+) (\d{4}) Temperature Increase", e["title"])
    if not mt: continue
    y, m = int(mt.group(2)), MOIS[mt.group(1)]
    if len(era[(y, m)]) < 28: continue
    ny, nm = (y, m + 1) if m < 12 else (y + 1, 1)
    T = int(datetime(ny, nm, JOUR, 12, tzinfo=timezone.utc).timestamp())
    ks = [prev(y, m)]; ks.append(prev(*ks[-1])); ks.append(prev(*ks[-1]))
    off = st.mean(giss[k] - st.mean(era[k]) for k in ks)
    mu = st.mean(era[(y, m)]) + off + DELTA
    for mk in e["markets"]:
        t = mk.get("groupItemTitle") or ""
        try: lo, hi = bornes(t)
        except Exception: continue
        res = json.loads(mk["outcomePrices"])
        if res not in (["1", "0"], ["0", "1"]): continue
        tok = json.loads(mk["clobTokenIds"])[0]
        p = prix(tok, T)
        q = Phi((hi - mu) / SD) - Phi((lo - mu) / SD)
        rows.append(dict(ev=e["id"], mois=f"{y}-{m:02d}", t=t, gagne=res == ["1", "0"], p=p, q=q, mu=round(mu, 3), giss=giss.get((y, m))))
        time.sleep(0.05)
json.dump(rows, open(EV.replace("evenements", f"lignes_j{JOUR}"), "w"), indent=0)
# log-score par événement (tranche gagnante), modèle contre marché normalisé
ev = collections.defaultdict(list)
for r in rows: ev[r["ev"]].append(r)
lm, lp, n = 0.0, 0.0, 0
for k, rs in ev.items():
    if any(r["p"] is None for r in rs): continue
    s = sum(r["p"] for r in rs) or 1
    w = [r for r in rs if r["gagne"]]
    if not w: continue
    w = w[0]; n += 1
    lm += math.log(max(w["q"], 0.01)); lp += math.log(max(w["p"] / s, 0.01))
    print(w["mois"], "GISS", w["giss"], "prévu", w["mu"], "gagnante", w["t"], "modèle", round(w["q"], 3), "marché", round(w["p"] / s, 3))
print(f"{n} mois ; log-score modèle {lm / max(n,1):.3f} contre marché {lp / max(n,1):.3f}")
# achats simulés : côté dont la chance dépasse le prix + 0,02 (écart) + frais d'au moins 0,05
paris = []
for r in rows:
    if r["p"] is None: continue
    for side, est, px, win in ((1, r["q"], r["p"] + 0.02, r["gagne"]), (0, 1 - r["q"], 1 - r["p"] + 0.02, not r["gagne"])):
        fee = 0.05 * px * (1 - px)
        if 0.03 <= px <= 0.97 and est - px - fee >= 0.05:
            paris.append(dict(mois=r["mois"], t=r["t"], cote="OUI" if side else "NON", px=px, est=est, win=win, gain=(1 if win else 0) - px - fee))
g = sum(p["gain"] for p in paris); mise = sum(p["px"] for p in paris)
print(f"{len(paris)} paris, {sum(p['win'] for p in paris)} gagnés pour {sum(p['px'] for p in paris):.1f} attendus (prix), {sum(p['est'] for p in paris):.1f} (modèle) ; gain {g:+.2f} pour {mise:.2f} misés ({g / max(mise,1e-9):+.1%})")
for p in paris: print("  ", p["mois"], p["t"], p["cote"], round(p["px"], 3), round(p["est"], 3), "gagné" if p["win"] else "perdu")
