"""11/11/2026 : piste n° 21, tornades du mois. Marchés « How many Tornadoes in the US in <mois> ? » / « US Tornadoes in <mois> 2026 »
réglés (novembre 2025 → août 2026). Règlement = premier décompte NCEI publié après la date prévue (≈ 8-10 jours après la fin du mois),
égal à la somme des rapports FILTRÉS du SPC à cette date.
Modèle au jour d du mois (14 h UTC) : compte SPC des jours SPC ≤ d − 2 (jour SPC = 12 h UTC → 12 h UTC, publié le lendemain) + reste
tiré de la base finale SPC 1995-2024 (même fenêtre de jours du même mois, 30 années, lissage +0,5). Prix : prices-history (≤ T)
et premier vrai achat (preneur) dans les 6 h après T. Usage : .venv/bin/python experiments/tornades/test_passe.py"""
import csv, json, math, re, datetime as dt, collections, requests
UA = {"User-Agent": "curl/8"}
EVENTS = {"96596": (2025, 11), "96598": (2025, 12), "131185": (2026, 1), "193610": (2026, 2), "232628": (2026, 3), "304644": (2026, 4),
          "424754": (2026, 5), "528237": (2026, 6), "577021": (2026, 7), "762873": (2026, 8)}
spc = json.load(open("experiments/tornades/spc_jours.json"))
# base finale : (année, mois, jour) -> nombre
seen, daily = set(), collections.Counter()
for r in csv.DictReader(open("experiments/tornades/donnees/actual.csv")):
    if r["sg"] == "2" or (r["yr"], r["om"]) in seen:
        continue
    seen.add((r["yr"], r["om"]))
    daily[(int(r["yr"]), int(r["mo"]), int(r["dy"]))] += 1
def bracket(label):
    s = label.replace("–", "-").replace(" ", "").lower()
    if m := re.match(r"(?:<|under)(\d+)$", s): return (0, int(m.group(1)) - 1)
    if m := re.match(r"(\d+)(?:\+|ormore)$", s): return (int(m.group(1)), 10**6)
    if m := re.match(r"(\d+)-(\d+)$", s): return (int(m.group(1)), int(m.group(2)))
    return None
def ndays(y, mo):
    return ((dt.date(y + (mo == 12), mo % 12 + 1, 1)) - dt.date(y, mo, 1)).days
def model(y, mo, d):
    so_far = sum(spc.get(dt.date(y, mo, k).isoformat(), 0) for k in range(1, d - 1))
    rest = [sum(daily[(yy, mo, k)] for k in range(d - 1, ndays(y, mo) + 1)) for yy in range(1995, 2025)]
    return so_far, [so_far + x for x in rest]
def history(tok, a, b):
    h = []
    while a < b:
        c = min(a + dt.timedelta(days=12), b)
        h += requests.get("https://clob.polymarket.com/prices-history", params={"market": tok, "startTs": int(a.timestamp()), "endTs": int(c.timestamp()),
                          "fidelity": 60}, headers=UA, timeout=30).json().get("history", [])
        a = c
    return sorted((x["t"], x["p"]) for x in h)
rows = []
for eid, (y, mo) in EVENTS.items():
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=UA, timeout=30).json()
    start = dt.datetime(y, mo, 1, tzinfo=dt.timezone.utc)
    ms = []
    for m in e["markets"]:
        br = bracket(m.get("groupItemTitle") or "")
        res = json.loads(m.get("outcomePrices") or "[]")
        if br is None or not res:
            continue
        toks = json.loads(m["clobTokenIds"])
        ms.append((m["groupItemTitle"], br, float(res[0]), toks, m.get("conditionId")))
    trades = []
    try:
        from polymarket_agent.http_client import HttpClient
        from polymarket_agent import data_api
        trades = data_api.echanges_evenement(HttpClient(), eid, pages=30)
    except Exception as exc:
        print("échanges", eid, exc)
    for title, br, won, toks, cond in ms:
        h = history(toks[0], start - dt.timedelta(days=3), start + dt.timedelta(days=ndays(y, mo) + 9))
        for d in (5, 10, 15, 20, 25):
            T = start + dt.timedelta(days=d - 1, hours=14)
            so_far, tot = model(y, mo, d)
            k = sum(br[0] <= t <= br[1] for t in tot)
            p = (k + 0.5) / (len(tot) + 0.5 * len(ms))
            px = [q for t, q in h if t <= T.timestamp()]
            # premiers vrais achats après T (preneur) : OUI acheté, ou NON acheté
            buy_yes = buy_no = None
            for t in sorted(trades, key=lambda t: int(t["timestamp"])):
                ts = int(t["timestamp"])
                if t.get("conditionId") != cond or not T.timestamp() <= ts <= T.timestamp() + 6 * 3600 or t.get("side") != "BUY":
                    continue
                if str(t.get("asset")) == toks[0] and buy_yes is None: buy_yes = (float(t["price"]), float(t["size"]))
                if str(t.get("asset")) == toks[1] and buy_no is None: buy_no = (float(t["price"]), float(t["size"]))
            rows.append({"evt": eid, "mois": f"{y}-{mo:02d}", "tranche": title, "jour": d, "deja": so_far, "p": round(p, 4),
                         "prix": px[-1] if px else None, "gagne": won, "achat_oui": buy_yes, "achat_non": buy_no})
json.dump(rows, open("experiments/tornades/test_passe.json", "w"), indent=0)
print(len(rows), "lignes")
