"""Semaines réglées « #1 / #2 Spotify song (in the US) this week? (<vendredi>) » : la semaine du classement = somme des écoutes
quotidiennes du vendredi au jeudi (vérifié : hebdo US de kworb = somme des jours, 3 semaines sur 3, 2 titres). Au mardi 22 h UTC
(jours ven.-lun. publiés), le meneur de la somme gagne-t-il plus souvent que son prix ? Données : kworb.net (pages de titre, 31
derniers jours), Gamma, prices-history. Usage : python hebdo_somme_des_jours.py  (11/11/2026, piste n° 29)."""
import datetime as dt, html, json, re, sys, time
import requests
H = {"User-Agent": "curl/8"}
KW = {"User-Agent": "Mozilla/5.0"}
SEMAINES = {"October 23": dt.date(2026, 10, 22), "October 30": dt.date(2026, 10, 29), "November 6": dt.date(2026, 11, 5)}


def num(c):
    m = re.search(r"\(([\d,]+)\)", c)
    return int(m.group(1).replace(",", "")) if m else 0


def ids_kworb():
    out = {}
    for page in ("country/global_daily_totals.html", "country/us_daily_totals.html"):
        h = requests.get("https://kworb.net/spotify/" + page, headers=KW, timeout=60).text
        for r in re.findall(r"<tr>(.*?)</tr>", h, re.S):
            t = re.findall(r"track/([^.]+)\.html", r)
            name = html.unescape(re.sub(r"<[^>]+>", "", (re.findall(r"<td[^>]*>(.*?)</td>", r, re.S) or [""])[0])).strip()
            if t and name:
                out.setdefault(name.lower(), t[0])
    return out


def jours(track):
    h = requests.get(f"https://kworb.net/spotify/track/{track}.html", headers=KW, timeout=60).text
    tb = re.findall(r"<table[^>]*>(.*?)</table>", h, re.S)[1]
    cells = [[html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
             for r in re.findall(r"<tr[^>]*>(.*?)</tr>", tb, re.S)]
    hdr = cells[0]
    gi, ui = hdr.index("Global"), (hdr.index("US") if "US" in hdr else None)
    return {c[0]: (num(c[gi]), num(c[ui]) if ui else 0) for c in cells[3:]}


def kname(title):   # « Housewife - Tate McRae » → « tate mcrae - housewife » (forme kworb)
    t = title.split(" - ")
    return (t[1].split(",")[0].strip() + " - " + t[0].strip()).lower() if len(t) >= 2 else title.lower()


def main():
    evs = json.load(open(sys.argv[1]))
    kid = ids_kworb()
    cache, res = {}, []
    for eid, (title, end) in evs.items():
        wk = next((k for k in SEMAINES if f"({k})" in title), None)
        if wk is None:
            continue
        thu = SEMAINES[wk]
        fri = thu - dt.timedelta(days=6)
        known = [(fri + dt.timedelta(days=i)).strftime("%Y/%m/%d") for i in range(4)]       # ven.-lun.
        allw = [(fri + dt.timedelta(days=i)).strftime("%Y/%m/%d") for i in range(7)]
        us = "in the US" in title
        place = 2 if title.startswith("#2") else 1
        t_dec = int(dt.datetime.combine(fri + dt.timedelta(days=4), dt.time(22), tzinfo=dt.timezone.utc).timestamp())  # mardi 22 h
        e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=30).json()
        rows = []
        for m in e["markets"]:
            name = m.get("groupItemTitle") or ""
            tid = kid.get(kname(name))
            if not tid or not m.get("outcomePrices"):
                continue
            if tid not in cache:
                cache[tid] = jours(tid)
                time.sleep(0.5)
            d = cache[tid]
            col = 1 if us else 0
            s4 = sum(d.get(x, (0, 0))[col] for x in known)
            s7 = sum(d.get(x, (0, 0))[col] for x in allw)
            tok = json.loads(m["clobTokenIds"])[0]
            hst = requests.get("https://clob.polymarket.com/prices-history", params={"market": tok, "startTs": t_dec - 7200,
                               "endTs": t_dec + 7200, "fidelity": 60}, timeout=30).json().get("history") or []
            prix = min(hst, key=lambda x: abs(x["t"] - t_dec))["p"] if hst else None
            rows.append({"titre": name, "s4": s4, "s7": s7, "prix": prix, "gagne": json.loads(m["outcomePrices"])[0] in ("1", "1.0")})
        if not rows:
            continue
        r4 = sorted(rows, key=lambda r: -r["s4"])
        r7 = sorted(rows, key=lambda r: -r["s7"])
        cand = r4[place - 1]
        res.append({"evenement": title, "meneur_4j": cand["titre"], "prix_mardi": cand["prix"], "gagne": cand["gagne"],
                    "meneur_7j_kworb": r7[place - 1]["titre"], "gagnant": [r["titre"] for r in rows if r["gagne"]],
                    "ecart_4j": cand["s4"] - (r4[place]["s4"] if len(r4) > place else 0)})
    for r in res:
        print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
