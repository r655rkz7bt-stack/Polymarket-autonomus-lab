"""27/10/2026 : « Under » des totaux Over/Under d'e-sport (kills LoL et Dota 2, manches CS2 et Valorant) regroupés, un pari par partie (prix payé le plus proche de 0,5),
décision à H heures du coup d'envoi (fenêtre d'une heure), prix payé 0,35-0,65. Usage : python groupe.py [H=3] [COTE=Under]"""
import os, sys, json, importlib
H = sys.argv[1] if len(sys.argv) > 1 else "3"
COTE = sys.argv[2] if len(sys.argv) > 2 else "Under"
sys.path.insert(0, "experiments/lol_kills/scripts")
tous = []
for serie in ("lol", "dota2", "cs2", "val"):
    os.environ["SERIE"] = serie
    sys.argv = ["x", H, "0"]
    import analyse as A
    importlib.reload(A)
    for m in (json.loads(l) for l in open(A.MARCHES)):
        if not m["debut"]: continue
        rows = A.charge(m)
        if not rows: continue
        s = A.ts(m["debut"]); t0 = s - int(float(H) * 3600)
        b = A.pari(m, rows, COTE, t0, min(t0 + 3600, s))
        if b and 0.35 <= b["cout"] <= 0.65:
            b["serie"] = serie; b["evenement"] = serie + b["evenement"]; tous.append(b)
par = {}
for b in tous:
    k = (b["evenement"], b["jeu"])
    if k not in par or abs(b["cout"] - 0.5) < abs(par[k]["cout"] - 0.5): par[k] = b
A.rapport(list(par.values()), f"{COTE} h={H}, un par partie, payé 0,35-0,65, 4 jeux")
for serie in ("lol", "dota2", "cs2", "val"):
    A.rapport([b for b in par.values() if b["serie"] == serie], f"   {serie}")
for mo in sorted({b["mois"] for b in par.values()}):
    A.rapport([b for b in par.values() if b["mois"] == mo], f"   mois {mo}")
