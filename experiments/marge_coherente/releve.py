"""Piste n° 3 (marge_coherente), relevé en direct : Brésil, 2e tour. Les tranches « marge de victoire » d'un candidat, additionnées,
doivent redonner son prix « vainqueur ». Écrit la ligne de relevé (heure, sommes des meilleurs achats / ventes, prix vainqueur) dans
experiments/marge_coherente/releves.csv. À relancer plusieurs fois avant le 25/10/2026."""
import requests, json, datetime as dt, os, re
H = {"User-Agent": "curl/8"}
def ev(slug): return requests.get("https://gamma-api.polymarket.com/events", headers=H, params={"slug": slug}, timeout=60).json()[0]
def book(tok):
    b = requests.get("https://clob.polymarket.com/book", headers=H, params={"token_id": tok}, timeout=60).json()
    bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids", [])), reverse=True)
    asks = sorted((float(x["price"]), float(x["size"])) for x in b.get("asks", []))
    return (bids[0] if bids else (0.0, 0.0)), (asks[0] if asks else (1.0, 0.0))
win = ev("brazil-presidential-election")["markets"]
mar = ev("brazil-presidential-election-second-round-margin-of-victory")["markets"]
row = [dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes")]
for name, key in (("Flávio", "Flávio"), ("Lula", "Luiz")):
    w = [m for m in win if key in m["question"] and "win the 2026 Brazilian presidential election?" in m["question"]][0]
    wb, wa = book(json.loads(w["clobTokenIds"])[0])
    ts = [m for m in mar if key in m["question"]]
    sb = sa = 0.0; smin_b = smin_a = 1e9
    for m in ts:
        b, a = book(json.loads(m["clobTokenIds"])[0]); sb += b[0]; sa += a[0]; smin_b = min(smin_b, b[1]); smin_a = min(smin_a, a[1])
    print(f"{name}: vainqueur achat {wa[0]:.3f} (taille {wa[1]:.0f}) vente {wb[0]:.3f} ; {len(ts)} tranches : somme des ventes {sb:.3f} (plus petite taille {smin_b:.0f}), somme des achats {sa:.3f} (plus petite taille {smin_a:.0f})")
    print(f"   écart « vendre les tranches − acheter le vainqueur » = {sb - wa[0]:+.3f} ; « vendre le vainqueur − acheter les tranches » = {wb[0] - sa:+.3f}")
    row += [f"{wa[0]:.3f}", f"{wb[0]:.3f}", f"{sa:.3f}", f"{sb:.3f}"]
p = "experiments/marge_coherente/releves.csv"
new = not os.path.exists(p)
with open(p, "a") as f:
    if new: f.write("heure,flavio_vainq_achat,flavio_vainq_vente,flavio_tranches_achat,flavio_tranches_vente,lula_vainq_achat,lula_vainq_vente,lula_tranches_achat,lula_tranches_vente\n")
    f.write(",".join(row) + "\n")
