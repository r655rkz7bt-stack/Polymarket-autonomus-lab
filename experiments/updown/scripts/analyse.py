"""Up or Down : le prix du marché retarde-t-il le cours Binance ? (15m ou 5m)

Aucun regard vers le futur : à l'instant T on n'utilise que les barres d'une minute FINIES (début ≤ T − 60 s),
la volatilité des 240 minutes avant la fenêtre, et, pour le prix payé, le premier échange réel d'un preneur qui ACHÈTE
le côté voulu dans les 60 s après T (prix et taille réels). Frais crypto 0,07·p·(1−p) par part.
Usage : python analyse.py <5m|15m>
"""
import json, sys, os, bisect, math, collections, statistics as st
ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "..", "donnees")
pas = sys.argv[1]; W = 300 if pas == "5m" else 900
K = json.load(open(os.path.join(DON, "klines_btc.json")))
T0 = [k[0] for k in K]; OPEN = [k[1] for k in K]; CLOSE = [k[4] for k in K]
def Phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def bar(t):  # index de la barre qui commence à t
    i = bisect.bisect_left(T0, t)
    return i if i < len(T0) and T0[i] == t else None

def sigma(E):  # écart-type des rendements d'une minute sur les 240 minutes avant la fenêtre
    i = bar(E)
    if i is None or i < 241: return None
    r = [math.log(CLOSE[j] / CLOSE[j - 1]) for j in range(i - 240, i)]
    return st.pstdev(r)

M = [json.loads(l) for l in open(os.path.join(DON, f"{pas}_marches.jsonl"))]
nets = [m for m in M if m["net"]]
print(pas, len(M), "marchés lus,", len(nets), "réglés net")

# contrôle du règlement : close de la dernière barre de la fenêtre >= open de la première ?
ok = n = 0
for m in nets:
    i, j = bar(m["ep"]), bar(m["ep"] + W - 60)
    if i is None or j is None: continue
    n += 1; ok += ((CLOSE[j] >= OPEN[i]) == (m["gagnant"] == "Up"))
print(f"contrôle du règlement (Binance contre Chainlink) : {ok}/{n} = {ok/n:.4f}")

def fee(p): return 0.07 * p * (1 - p)
rows = []   # (k, evenement, côté, p_modele, p_marche_dernier, prix_paye, taille, gain/part, up_gagne, mois)
for m in nets:
    E = m["ep"]; i0 = bar(E); sg = sigma(E)
    if i0 is None or not sg: continue
    up = m["gagnant"] == "Up"
    tr = sorted(m["trades"])
    ts = [t[0] for t in tr]
    for kmin in range(1, W // 60):
        T = E + kmin * 60
        i = bar(T - 60)
        if i is None: continue
        mv = math.log(CLOSE[i] / OPEN[i0]); rem = (W - kmin * 60) / 60
        pm = Phi(mv / (sg * math.sqrt(rem)))
        # dernier prix du marché (équivalent OUI) avant T
        a = bisect.bisect_left(ts, T)
        last = None
        for t in reversed(tr[:a]):
            last = t[3] if t[1] == m["up"] else 1 - t[3]; break
        # premier échange d'un preneur qui ACHÈTE un côté, dans les 60 s après T
        b = bisect.bisect_left(ts, T + 60)
        ach = {}
        for t in tr[a:b]:
            if t[2] == "BUY":
                side = "Up" if t[1] == m["up"] else "Down"
                ach.setdefault(side, (t[3], t[4]))
        rows.append(dict(k=kmin, ev=E, mv=mv, pm=pm, last=last, ach=ach, up=up, mois=dt_mois(E) if False else E // (30 * 86400)))

import pickle
pickle.dump(rows, open(os.path.join(DON, f"{pas}_lignes.pkl"), "wb"))
print(len(rows), "lignes (marché, minute)")

# 1) log-score modèle contre marché
def ls(p, y):
    p = min(max(p, 1e-4), 1 - 1e-4); return math.log(p if y else 1 - p)
print("\nminute | n | log-score modèle | log-score marché | écart (modèle − marché)")
for k in range(1, W // 60):
    R = [r for r in rows if r["k"] == k and r["last"] is not None]
    if not R: continue
    a = sum(ls(r["pm"], r["up"]) for r in R) / len(R); b = sum(ls(r["last"], r["up"]) for r in R) / len(R)
    print(f"{k:2d} | {len(R):5d} | {a:+.4f} | {b:+.4f} | {a-b:+.4f}")

# 2) achats simulés aux prix réels
def sim(thr, ks, pmin=0.05, pmax=0.95, taille_min=20):
    res = []
    for r in rows:
        if r["k"] not in ks: continue
        for side in ("Up", "Down"):
            if side not in r["ach"]: continue
            px, sz = r["ach"][side]
            if sz < taille_min or not (pmin <= px <= pmax): continue
            pmod = r["pm"] if side == "Up" else 1 - r["pm"]
            if pmod - px - fee(px) < thr: continue
            win = r["up"] if side == "Up" else not r["up"]
            res.append((r["ev"], px, pmod, (1.0 if win else 0.0) - px - fee(px), win))
    return res
print("\nrègle : acheter le côté dont (proba modèle − prix payé − frais) ≥ seuil ; un achat par (marché, minute, côté)")
for ks in (range(1, W // 60), [W // 60 // 2], [W // 60 - 2], [W // 60 - 1]):
    for thr in (0.03, 0.06, 0.10, 0.15):
        R = sim(thr, list(ks))
        if len(R) < 30: continue
        ev = collections.defaultdict(float)
        for e, px, pmod, g, w in R: ev[e] += g
        tot = sum(g for _, _, _, g, _ in R); mise = sum(px for _, px, _, _, _ in R)
        evs = list(ev.values()); mu = st.mean(evs); sd = st.pstdev(evs) or 1
        print(f"minutes {list(ks)[:1]}..{list(ks)[-1:]} seuil {thr:.2f}: {len(R)} paris sur {len(ev)} marchés, rendement {tot/mise:+.2%}, gagnés {sum(w for *_, w in R)} pour {sum(pmod for _, _, pmod, _, _ in R):.1f} (modèle) / {sum(px for _, px, *_ in R):.1f} (prix), t par marché {mu/(sd/math.sqrt(len(evs))):+.2f}")
