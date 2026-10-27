"""27/10/2026, piste « totaux de kills du LoL » : calibration aux vrais échanges (data-api) des marchés « Total Kills Over/Under X in Game N ».
Décision à T0 = coup d'envoi − h ; prix payé = premier échange réel qui ACHÈTE le côté dans l'heure qui suit T0 (jamais après le coup d'envoi) ;
frais = taux du marché × p (1 − p) par part ; 50-50 payé 0,5 ; un pari par marché et par côté ; paris d'un même événement liés (idea_test.verdict).
Usage : python analyse.py [H=3] [VOL_MIN=100]"""
import gzip, json, os, sys, math, collections
from datetime import datetime
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent import idea_test as it
H = float(sys.argv[1]) if len(sys.argv) > 1 else 3
VOLMIN = float(sys.argv[2]) if len(sys.argv) > 2 else 100
D = Path("experiments/lol_kills/donnees")
SERIE = os.environ.get("SERIE", "lol")
MARCHES = D / ("marches.jsonl" if SERIE == "lol" else f"marches_{SERIE}.jsonl")
ECH = D / ("echanges" if SERIE == "lol" else f"echanges_{SERIE}")
def ts(s): return int(datetime.fromisoformat(s.replace("+00", "+00:00")).timestamp())
def charge(m):
    p = ECH / f"{m['id']}.json.gz"
    if not p.exists(): return None
    return json.loads(gzip.decompress(p.read_bytes()))["echanges"]
def achat(rows, jeton, autre, t0, fin):
    pts = sorted((t, p if a == jeton else 1 - p) for t, a, s, p, _ in rows if (a == jeton and s == "BUY") or (a == autre and s == "SELL"))
    sel = [(t, p) for t, p in pts if t0 <= t <= fin]
    return sel[0] if sel else None
def pari(m, rows, cote, t0, fin):
    j, a = (m["over"], m["under"]) if cote == "Over" else (m["under"], m["over"])
    x = achat(rows, j, a, t0, fin)
    if not x or not (0.02 < x[1] < 0.98): return None
    p = x[1]; fee = m["taux"] * p * (1 - p)
    pay = 0.5 if m["res"] == "50-50" else 1.0 if m["res"] == cote else 0.0
    return {"cout": p, "gain": (pay - p - fee) / (p + fee), "pay": pay, "evenement": m["event"], "mois": m["debut"][:7], "ligne": m["ligne"], "jeu": m["jeu"], "cote": cote, "t": x[0], "marche": m["id"]}
def main():
    ms = [json.loads(l) for l in open(MARCHES)]
    bets = []
    for m in ms:
        if m["vol"] < VOLMIN or not m["debut"]: continue
        rows = charge(m)
        if not rows: continue
        s = ts(m["debut"]); t0 = s - int(H * 3600)
        for cote in ("Over", "Under"):
            b = pari(m, rows, cote, t0, min(t0 + 3600, s))
            if b: bets.append(b)
    print(f"h={H}: {len(bets)} paris ({len({b['marche'] for b in bets})} marchés)")
    return bets
def rapport(bets, titre):
    if len(bets) < 30: print(titre, "trop peu", len(bets)); return
    v = it.verdict(bets)
    att = sum(b["cout"] for b in bets); gag = sum(b["pay"] for b in bets)
    var = sum(b["cout"] * (1 - b["cout"]) for b in bets)
    z = (gag - att) / math.sqrt(var) if var else 0
    print(f"{titre}: {len(bets)} paris, rendement {100 * sum(b['gain'] for b in bets) / len(bets):+.1f} %, gagné {gag:.0f} pour {att:.1f} attendus (z {z:+.2f}), "
          f"t par événement {v.get('confiance_evenements')} ({v.get('evenements')} événements), mois {v.get('mois_gagnants')}, verdict {v.get('verdict')}")
if __name__ == "__main__":
    bets = main()
    for cote in ("Over", "Under"):
        rapport([b for b in bets if b["cote"] == cote], cote)
        for lo, hi in ((0.02, 0.10), (0.10, 0.20), (0.20, 0.35), (0.35, 0.50), (0.50, 0.65), (0.65, 0.80), (0.80, 0.98)):
            rapport([b for b in bets if b["cote"] == cote and lo <= b["cout"] < hi], f"  {cote} payé {lo}-{hi}")
