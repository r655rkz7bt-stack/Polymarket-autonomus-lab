"""Fin de match (17/10/2026) : le match MLB est officiellement fini, le marché Polymarket n'est pas encore
réglé ; peut-on encore ACHETER le vainqueur sous ~0,99 ? Test sur le passé, aux échanges RÉELLEMENT exécutés.

Usage : .venv/bin/python -I experiments/fin_de_match/fin_de_match.py [début AAAA-MM-JJ] [fin AAAA-MM-JJ]
(par défaut du 2026-09-17 au 2026-10-16). Sorties : experiments/fin_de_match/resultats.json (par match)
et un résumé à l'écran. Les téléchargements bruts sont gardés (gzip) dans experiments/fin_de_match/cache/ :
relancer le script ne retélécharge rien.

Sources (gratuites, publiques, sans clé) :
- MLB : statsapi.mlb.com (calendrier + « feed/live » de chaque match). Fin officielle T_fin = heure de fin
  (about.endTime) du DERNIER jeu du match (dernier lancer), recoupée avec firstPitch + gameDurationMinutes.
- Polymarket Gamma : marchés « moneyline » MLB clos (tag 100381), barème de frais (feeType, feeSchedule).
- Polymarket data-api /trades : les échanges réels (preneur seulement, un enregistrement par ordre preneur).

Règles anti « regard vers le futur » :
- la fenêtre commence à T_fin + délai de réaction (5 ou 10 min), jamais à l'heure de clôture du marché ;
- l'heure de clôture (closedTime) ne sert que de borne de fin (après, on ne peut plus échanger) ;
- « achetable à p » = un preneur a réellement ACHETÉ le vainqueur à p (il existait donc une offre de vente
  à p). Les ventes de preneurs (side=SELL) prouvent seulement qu'un acheteur attendait à ce prix : ce sont
  des occasions pour un ordre limite posé à l'avance (rôle « maker »), comptées à part.
"""
import gzip
import hashlib
import json
import os
import re
import ssl
import statistics as st
import sys
import time
import unicodedata
from collections import Counter
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
GAMMA = "https://gamma-api.polymarket.com"
DATA = "https://data-api.polymarket.com"
MLB = "https://statsapi.mlb.com"
MLB_TAG = 100381
START = sys.argv[1] if len(sys.argv) > 1 else "2026-09-17"
END = sys.argv[2] if len(sys.argv) > 2 else "2026-10-16"
DELAYS = [0, 1, 5, 10]           # délai de réaction en minutes (notre robot relève toutes les 5 min : 5 et 10)
SEUILS = [0.99, 0.985, 0.98]
BEST_AFTER = [1, 5, 15]          # meilleur prix après T_fin + 1 / 5 / 15 min
FEE_BOUNDS = [0.0, 0.03]         # bornes demandées si le barème était inconnu
PRE = 1800                       # on garde aussi 30 min d'échanges avant T_fin (contexte)

_ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)
_last = [0.0]


def get(url, params=None, cache=True):
    """GET JSON, poli (0,4 s entre appels), réessais sur 429/5xx, cache disque gzip."""
    full = url + ("?" + urllib.parse.urlencode(params) if params else "")
    key = hashlib.sha256(full.encode()).hexdigest()[:24]
    path = CACHE / key[:2] / f"{key}.json.gz"
    if cache and path.exists():
        return json.loads(gzip.decompress(path.read_bytes()))
    for attempt in range(8):
        wait = 0.4 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            req = urllib.request.Request(full, headers={"User-Agent": "polymarket-lab-backtest",
                                                        "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60, context=_ctx) as r:
                data = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 7:
                time.sleep(2 * (attempt + 1))
                continue
            print("échec", e.code, full[:120])
            return None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if attempt < 7:
                time.sleep(2 * (attempt + 1))
                continue
            print("échec", e, full[:120])
            return None
    if cache:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(gzip.compress(json.dumps(data).encode()))
    return data


def ts(text):
    if not text:
        return None
    t = str(text).replace("Z", "+00:00").replace(" ", "T")
    if re.search(r"[+-]\d\d$", t):
        t += ":00"
    return int(datetime.fromisoformat(t).timestamp())


def iso(t):
    return datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def norm(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(s.split())


def taker_fee(p, rate):
    return rate * p * (1 - p)  # par part (docs.polymarket.com/trading/fees, exposant 1)


def gain_per_dollar(p, rate):
    return (1 - p - taker_fee(p, rate)) / p


# ---------------------------------------------------------------- 1. matchs MLB terminés et heure de fin
def mlb_games():
    sched = get(f"{MLB}/api/v1/schedule", {"sportId": 1, "startDate": START, "endDate": END})
    games = []
    for d in sched.get("dates", []):
        for g in d["games"]:
            if g["status"].get("codedGameState") != "F" or g.get("gameType") not in "RFDLW":
                continue
            games.append(g)
    fields = ("gameData,datetime,dateTime,status,codedGameState,detailedState,gameInfo,firstPitch,"
              "gameDurationMinutes,teams,away,home,name,liveData,plays,allPlays,about,endTime,startTime,"
              "linescore,runs")
    out = []
    for g in games:
        pk = g["gamePk"]
        f = get(f"{MLB}/api/v1.1/game/{pk}/feed/live", {"fields": fields})
        if not f:
            continue
        plays = f["liveData"]["plays"].get("allPlays") or []
        ends = [ts(p["about"].get("endTime")) for p in plays if p["about"].get("endTime")]
        if not ends:
            continue
        t_end = max(ends)
        info = f["gameData"].get("gameInfo") or {}
        check = None
        if info.get("firstPitch") and info.get("gameDurationMinutes"):
            check = ts(info["firstPitch"]) + 60 * int(info["gameDurationMinutes"])
        ls = f["liveData"]["linescore"]["teams"]
        ra, rh = ls["away"].get("runs"), ls["home"].get("runs")
        if ra is None or rh is None or ra == rh:
            continue
        away, home = f["gameData"]["teams"]["away"]["name"], f["gameData"]["teams"]["home"]["name"]
        out.append({"gamePk": pk, "gameType": g["gameType"], "date": g.get("officialDate"),
                    "start": ts(g["gameDate"]), "away": away, "home": home, "runs": [ra, rh],
                    "winner": away if ra > rh else home, "t_end": t_end,
                    "t_end_check": check, "t_end_iso": iso(t_end)})
    return out


# ---------------------------------------------------------------- 2. marchés Polymarket « vainqueur du match »
def pm_markets():
    end_max = (datetime.fromisoformat(END) + timedelta(days=9)).strftime("%Y-%m-%d")
    params = {"closed": "true", "tag_id": MLB_TAG, "sports_market_types": "moneyline", "limit": 100,
              "end_date_min": f"{START}T00:00:00Z", "end_date_max": f"{end_max}T23:59:59Z"}
    res, ok = [], True
    for page in range(100):
        batch = get(f"{GAMMA}/markets", {**params, "offset": page * 100})
        if not isinstance(batch, list):
            ok = False
            break
        res += batch
        if len(batch) < 100:
            break
    if not ok:  # grands décalages en échec (HTTP 500 connu) : on relit jour par jour
        res, day = [], datetime.fromisoformat(START)
        while day <= datetime.fromisoformat(end_max):
            nxt = day + timedelta(days=1)
            for page in range(20):
                batch = get(f"{GAMMA}/markets", {**params, "offset": page * 100,
                                                 "end_date_min": day.strftime("%Y-%m-%dT00:00:00Z"),
                                                 "end_date_max": nxt.strftime("%Y-%m-%dT00:00:00Z")})
                if not isinstance(batch, list):
                    break
                res += batch
                if len(batch) < 100:
                    break
            day = nxt
    seen, keep = set(), []
    for m in res:
        if m["id"] in seen or not re.fullmatch(r".+ vs\. .+", m.get("question") or ""):
            continue
        outs = json.loads(m.get("outcomes") or "[]")
        if len(outs) != 2 or m.get("sportsMarketType") not in (None, "moneyline"):
            continue
        seen.add(m["id"])
        keep.append(m)
    return keep


def match(games, markets):
    by_teams = {}
    for m in markets:
        outs = json.loads(m["outcomes"])
        by_teams.setdefault(frozenset(norm(o) for o in outs), []).append(m)
    pairs = []
    for g in games:
        cands = by_teams.get(frozenset([norm(g["away"]), norm(g["home"])]), [])
        cands = [m for m in cands if m.get("gameStartTime") and abs(ts(m["gameStartTime"]) - g["start"]) < 12 * 3600]
        if not cands:
            continue
        m = min(cands, key=lambda m: abs(ts(m["gameStartTime"]) - g["start"]))
        pairs.append((g, m))
    # un marché ne sert qu'une fois (programmes doubles) : on garde le plus proche
    used, out = {}, []
    for g, m in pairs:
        d = abs(ts(m["gameStartTime"]) - g["start"])
        if m["id"] not in used or d < used[m["id"]][0]:
            used[m["id"]] = (d, g, m)
    return [(g, m) for _, g, m in used.values()]


# ---------------------------------------------------------------- 3. échanges réels autour de la fin
def trades_after(cid, t_from):
    """Échanges preneurs du marché, du plus récent au plus ancien, jusqu'à t_from."""
    out = []
    for page in range(40):
        batch = get(f"{DATA}/trades", {"market": cid, "limit": 500, "offset": page * 500})
        if not isinstance(batch, list) or not batch:
            break
        out += batch
        if batch[-1]["timestamp"] < t_from or len(batch) < 500:
            break
    return [t for t in out if t["timestamp"] >= t_from]


def analyse(g, m):
    outs = json.loads(m["outcomes"])
    toks = json.loads(m["clobTokenIds"])
    prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
    i_win = [norm(o) for o in outs].index(norm(g["winner"]))
    pm_win = prices.index(max(prices)) if prices and max(prices) > 0.5 else None
    fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
    rate = float(fs["rate"]) if fs.get("rate") is not None and m.get("feesEnabled") else None
    close = ts(m.get("closedTime")) or ts(m.get("umaEndDate"))
    t_end = g["t_end"]
    tr = trades_after(m["conditionId"], t_end - PRE)
    win = sorted([t for t in tr if t["asset"] == toks[i_win]], key=lambda t: t["timestamp"])
    r = {"gamePk": g["gamePk"], "date": g["date"], "type": g["gameType"], "match": m["question"],
         "slug": m["slug"], "winner": g["winner"], "t_end": g["t_end_iso"],
         "t_end_ecart_duree_officielle_min": round((t_end - g["t_end_check"]) / 60, 1) if g["t_end_check"] else None,
         "close": iso(close) if close else None,
         "fenetre_min": round((close - t_end) / 60, 1) if close else None,
         "feeType": m.get("feeType"), "fee_rate": rate, "takerBaseFee": m.get("takerBaseFee"),
         "uma": m.get("umaResolutionStatus"), "pm_vainqueur_ok": pm_win == i_win,
         "n_trades_vainqueur_apres_fin": sum(1 for t in win if t["timestamp"] > t_end)}
    before = [t for t in win if t["timestamp"] <= t_end]
    r["dernier_prix_avant_fin"] = before[-1]["price"] if before else None
    late = [t for t in win if t["timestamp"] > t_end and (close is None or t["timestamp"] <= close + 60)]
    buys = [t for t in late if t["side"] == "BUY"]
    sells = [t for t in late if t["side"] == "SELL"]
    r["apres_fin_tout_dernier_min"] = round((late[-1]["timestamp"] - t_end) / 60, 1) if late else None
    for d in BEST_AFTER:
        a = t_end + 60 * d
        r[f"min_achat_apres_{d}m"] = min((t["price"] for t in buys if t["timestamp"] > a), default=None)
        r[f"min_tout_apres_{d}m"] = min((t["price"] for t in late if t["timestamp"] > a), default=None)
    for d in DELAYS:
        a = t_end + 60 * d
        b = [t for t in buys if t["timestamp"] > a]
        s = [t for t in sells if t["timestamp"] > a]
        r[f"premier_achat_apres_{d}m"] = b[0]["price"] if b else None
        r[f"premier_achat_apres_{d}m_delai"] = round((b[0]["timestamp"] - t_end) / 60, 1) if b else None
        for x in SEUILS:
            k = f"{d}m_{x}"
            bx = [t for t in b if t["price"] <= x + 1e-9]
            sx = [t for t in s if t["price"] <= x + 1e-9]
            r[f"achat_n_{k}"] = len(bx)
            r[f"achat_usd_{k}"] = round(sum(t["price"] * t["size"] for t in bx), 2)
            r[f"achat_dernier_min_{k}"] = round((bx[-1]["timestamp"] - t_end) / 60, 1) if bx else None
            r[f"achat_premier_{k}"] = bx[0]["price"] if bx else None
            r[f"achat_5min_{k}"] = any(t["timestamp"] <= a + 300 for t in bx)  # dans les 5 min qui suivent
            for fr in sorted({rate or 0.0} | set(FEE_BOUNDS)):
                r[f"achat_gain_usd_{k}_taux_{fr}"] = round(
                    sum(t["size"] * (1 - t["price"] - taker_fee(t["price"], fr)) for t in bx), 2)
            r[f"achat_dernier_s_{k}"] = bx[-1]["timestamp"] - t_end if bx else None
            r[f"vente_n_{k}"] = len(sx)
            r[f"vente_usd_{k}"] = round(sum(t["price"] * t["size"] for t in sx), 2)
            r[f"vente_dernier_min_{k}"] = round((sx[-1]["timestamp"] - t_end) / 60, 1) if sx else None
            # ordre limite d'achat (maker, sans frais) servi par ces ventes : gain = parts × (1 − p)
            r[f"vente_gain_maker_usd_{k}"] = round(sum(t["size"] * (1 - t["price"]) for t in sx), 2)
    return r


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 4) if xs else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), 5) if xs else None


def main():
    games = mlb_games()
    markets = pm_markets()
    pairs = match(games, markets)
    print(f"Matchs MLB terminés {START}..{END} : {len(games)} | marchés moneyline lus : {len(markets)} "
          f"| appariés : {len(pairs)}")
    rows = []
    for g, m in sorted(pairs, key=lambda p: p[0]["t_end"]):
        rows.append(analyse(g, m))
    json.dump(rows, open(HERE / "resultats.json", "w"), indent=1, ensure_ascii=False)
    unmatched = sorted({(g["date"], g["away"], g["home"]) for g in games} -
                       {(g["date"], g["away"], g["home"]) for g, _ in pairs})
    summary = {"n_matchs_mlb": len(games), "n_apparies": len(rows), "non_apparies": unmatched,
               "litiges": [r["slug"] for r in rows if not r["pm_vainqueur_ok"]],
               "feeTypes": sorted({str(r["feeType"]) for r in rows}),
               "fee_rates": sorted({str(r["fee_rate"]) for r in rows}),
               "fenetre_min_mediane": med([r["fenetre_min"] for r in rows]),
               "fenetre_min_min_max": [min(r["fenetre_min"] for r in rows), max(r["fenetre_min"] for r in rows)],
               "ecart_t_end_vs_duree_officielle_min_median": med([r["t_end_ecart_duree_officielle_min"] for r in rows]),
               "dernier_prix_avant_fin_median": med([r["dernier_prix_avant_fin"] for r in rows]),
               "compte_feeType": dict(Counter(str(r["feeType"]) for r in rows)),
               "compte_uma": dict(Counter(str(r["uma"]) for r in rows)),
               "compte_type_match": dict(Counter(r["type"] for r in rows)),
               "fenetre_min_quartiles": [round(q, 1) for q in st.quantiles([r["fenetre_min"] for r in rows], n=4)],
               "n_matchs_sans_aucun_achat_preneur_vainqueur_apres_5m":
                   sum(1 for r in rows if r["premier_achat_apres_5m"] is None),
               "dernier_echange_vainqueur_apres_fin_min_median": med([r["apres_fin_tout_dernier_min"] for r in rows])}
    for d in BEST_AFTER:
        summary[f"min_achat_apres_{d}m_median"] = med([r[f"min_achat_apres_{d}m"] for r in rows])
        summary[f"min_tout_apres_{d}m_median"] = med([r[f"min_tout_apres_{d}m"] for r in rows])
    n = len(rows)
    rates = sorted({r["fee_rate"] for r in rows if r["fee_rate"] is not None}) or FEE_BOUNDS
    for d in DELAYS:
        summary[f"premier_achat_apres_{d}m_median"] = med([r[f"premier_achat_apres_{d}m"] for r in rows])
        for x in SEUILS:
            k = f"{d}m_{x}"
            hit = [r for r in rows if r[f"achat_n_{k}"] > 0]
            hit5 = [r for r in rows if r[f"achat_5min_{k}"]]
            s = {"pct_matchs_achat_possible": round(100 * len(hit) / n, 1),
                 "pct_matchs_achat_dans_5min": round(100 * len(hit5) / n, 1),
                 "n_matchs_achat_possible": len(hit),
                 "usd_median_si_possible": med([r[f"achat_usd_{k}"] for r in hit]),
                 "usd_total": round(sum(r[f"achat_usd_{k}"] for r in rows), 0),
                 "prix_premier_median": med([r[f"achat_premier_{k}"] for r in hit]),
                 "duree_derniere_occasion_min_mediane": med([r[f"achat_dernier_min_{k}"] for r in hit]),
                 "pct_matchs_vente_preneur": round(100 * sum(1 for r in rows if r[f"vente_n_{k}"]) / n, 1),
                 "usd_vente_median_si": med([r[f"vente_usd_{k}"] for r in rows if r[f"vente_n_{k}"]]),
                 "usd_vente_total": round(sum(r[f"vente_usd_{k}"] for r in rows), 0),
                 "gain_maker_total_usd_borne_haute": round(sum(r[f"vente_gain_maker_usd_{k}"] for r in rows), 2),
                 "secondes_derniere_occasion_mediane": med([r[f"achat_dernier_s_{k}"] for r in hit]),
                 "secondes_derniere_occasion_max": max((r[f"achat_dernier_s_{k}"] for r in hit), default=None)}
            for rate in sorted(set(rates) | set(FEE_BOUNDS)):
                gains = [gain_per_dollar(r[f"achat_premier_{k}"], rate) for r in hit]
                s[f"gain_net_moyen_par_dollar_taux_{rate}"] = mean(gains)
                # borne haute : on aurait raflé TOUT le volume acheté à ces prix (impossible en vrai)
                s[f"gain_net_total_usd_tout_volume_taux_{rate}"] = round(
                    sum(r.get(f"achat_gain_usd_{k}_taux_{rate}", 0) for r in rows), 2)
            summary[k] = s
    json.dump(summary, open(HERE / "resume.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
