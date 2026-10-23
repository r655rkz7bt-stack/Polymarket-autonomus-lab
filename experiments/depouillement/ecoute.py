"""Piste n° 15 `depouillement_officiel` (2e tour au Brésil, 25/10/2026) : UNE ligne CSV par appel.
Résultats officiels en direct (TSE, fichier public `…/ele2026/6258/dados/br/br-c0001-e006258-u.json`, ~1 mise à jour par minute)
+ prix Polymarket (CLOB) du OUI de Lula et de Flávio dans « Brazil presidential election » (marchés 601819 et 601826).
Colonnes : heure UTC, heure TSE, % des sections totalisées, votes Lula, votes Flávio, avance de Flávio (votes), sections restantes,
avance maximale rattrapable (sections restantes × 350 électeurs ≈ borne large), meilleur achat/vente du OUI de chaque candidat.
Aucune clé, aucun secret. Usage : python3 ecoute.py [--entete]"""
import json, os, sys, datetime as dt, urllib.request
UA = {"User-Agent": "Mozilla/5.0"}
ELE = os.environ.get("ELE", "6258")  # 6258 = 2e tour (25/10/2026) ; 6257 = 1er tour (essai sur un scrutin fini)
TSE = f"https://resultados.tse.jus.br/oficial/ele2026/{ELE}/dados/br/br-c0001-e00{ELE}-u.json"
TOKENS = {"lula": "601819", "flavio": "601826"}

def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25))

def book(market_id):
    m = get("https://gamma-api.polymarket.com/markets/" + market_id)
    tok = json.loads(m["clobTokenIds"])[0]
    b = get("https://clob.polymarket.com/book?token_id=" + tok)
    bid = max((float(x["price"]) for x in b.get("bids", [])), default=None)
    ask = min((float(x["price"]) for x in b.get("asks", [])), default=None)
    return bid, ask

if "--entete" in sys.argv:
    print("utc,tse,pct_sections,sections_totalisees,sections_total,votes_lula,votes_flavio,avance_flavio,lula_bid,lula_ask,flavio_bid,flavio_ask")
    sys.exit()
d = get(TSE)
votes = {}
for ag in d["carg"][0]["agr"]:
    for par in ag["par"]:
        for c in par["cand"]:
            votes[c["nmu"]] = int(c["vap"])
lula = next((v for k, v in votes.items() if "LULA" in k.upper()), 0)
flavio = next((v for k, v in votes.items() if "FLAVIO" in k.upper() or "FLÁVIO" in k.upper()), 0)
s = d["s"]
row = [dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), f"{d['dg']} {d['hg']}", s["pst"].replace(",", "."), s["st"], s["ts"], lula, flavio, flavio - lula]
for who in ("lula", "flavio"):
    try: row += list(book(TOKENS[who]))
    except Exception as exc: row += ["", ""]
print(",".join(str(x) for x in row))
