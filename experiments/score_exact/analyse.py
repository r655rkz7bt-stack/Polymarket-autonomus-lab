"""Piste n° 1 (score_exact_poisson), analyse sur le passé aux prix des vrais échanges.

Pour chaque match de football : à T0 = coup d'envoi − DECAL heures, probabilités 1X2 (dernier échange de chaque issue dans les 6 h
avant T0, normalisées) et plus/moins 2,5 buts → deux espérances de buts (loi de Poisson indépendante, ajustement par moindres
carrés) → probabilité de chaque score exact. Prix payé = premier échange d'achat (ou vente de l'autre issue) entre T0 et le coup
d'envoi (jamais après). Règlement relu : un seul score gagnant par événement, cohérent avec le 1X2 réglé.

usage : analyse.py [DECAL_h=3] [FENETRE_h=3] [VOLMAX=10000 échanges]
"""
import gzip, json, math, re, sys, collections, datetime as dt
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent import idea_test as it

D = Path("experiments/score_exact/donnees")
DECAL = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
FEN = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
GRID = 11


def lire(p):
    return json.loads(gzip.decompress(Path(p).read_bytes()))


def ts_of(text):
    return int(dt.datetime.fromisoformat(text.replace(" ", "T").replace("+00", "+00:00")).timestamp())


def poisson(l, k):
    return math.exp(-l) * l ** k / math.factorial(k)


def grille(lh, la):
    ph = [poisson(lh, k) for k in range(GRID)]
    pa = [poisson(la, k) for k in range(GRID)]
    return ph, pa


def sorties(lh, la):
    ph, pa = grille(lh, la)
    home = draw = away = over25 = 0.0
    for i in range(GRID):
        for j in range(GRID):
            p = ph[i] * pa[j]
            if i > j: home += p
            elif i == j: draw += p
            else: away += p
            if i + j >= 3: over25 += p
    return home, draw, away, over25


def ajuster(target, over):
    """moindres carrés sur (home, draw, away[, over2.5]) ; recherche en grille puis raffinée."""
    best = (9e9, 1.3, 1.1)
    def err(lh, la):
        h, d, a, o = sorties(lh, la)
        e = (h - target[0]) ** 2 + (d - target[1]) ** 2 + (a - target[2]) ** 2
        if over is not None: e += (o - over) ** 2
        return e
    for lh in [0.2 + 0.2 * i for i in range(17)]:
        for la in [0.2 + 0.2 * i for i in range(17)]:
            e = err(lh, la)
            if e < best[0]: best = (e, lh, la)
    _, lh, la = best
    step = 0.1
    for _ in range(25):
        moved = False
        for dl, da in ((step, 0), (-step, 0), (0, step), (0, -step)):
            nh, na = lh + dl, la + da
            if nh > 0.05 and na > 0.05:
                e = err(nh, na)
                if e < best[0] - 1e-12: best = (e, nh, na); lh, la = nh, na; moved = True
        if not moved: step /= 2
    return lh, la, best[0]


def dernier(trades, token, t_min, t_max):
    pts = [(t[0], t[3]) for t in trades if t[1] == token and t_min <= t[0] <= t_max]
    return max(pts)[1] if pts else None


def charge():
    evs = [json.loads(l) for l in open(D / "exact_events.jsonl")]
    out = []
    for e in evs:
        base = e["slug"][: -len("-exact-score")]
        f1, f2 = D / "siblings" / f"{base}.json.gz", D / "siblings" / f"{base}-more-markets.json.gz"
        fe = D / "echanges" / f"echanges_{e['id']}.json.gz"
        if not (f1.exists() and f2.exists() and fe.exists()): continue
        m, mm = lire(f1), lire(f2)
        if not m or not mm: continue
        fm, fmm = D / "echanges" / f"echanges_{m['id']}.json.gz", D / "echanges" / f"echanges_{mm['id']}.json.gz"
        if not (fm.exists() and fmm.exists()): continue
        out.append((e, m, mm, lire(fe), lire(fm), lire(fmm)))
    return out


def main():
    cas, bets_rows = charge(), []
    stats = collections.Counter()
    reglement_ok = reglement_total = 0
    log_modele = log_marche = 0.0
    nlog = 0
    for e, m, mm, te, tm, tmm in cas:
        stats["matchs_complets"] += 1
        if len(te) >= 10000 or len(tm) >= 10000 or len(tmm) >= 10000:
            stats["tronque"] += 1; continue
        ms = e["markets"]
        try:
            K = ts_of(ms[0]["gameStartTime"])
        except Exception:
            stats["sans_heure"] += 1; continue
        gagnants = [x for x in ms if sorted(json.loads(x["outcomePrices"])) == ["0", "1"] and json.loads(x["outcomePrices"])[0] == "1"]
        if len(gagnants) != 1:
            stats["reglement_non_net"] += 1; continue
        T0 = K - int(DECAL * 3600)
        # 1X2
        mon = {}
        for x in m["markets"]:
            toks = json.loads(x["clobTokenIds"]); g = x.get("groupItemTitle") or ""
            if x.get("sportsMarketType") != "moneyline": continue
            key = "draw" if "Draw" in g else None
            mon.setdefault("liste", []).append((x, toks[0], key))
        if "liste" not in mon or len(mon["liste"]) != 3: stats["pas_1x2"] += 1; continue
        draw = [t for t in mon["liste"] if t[2] == "draw"]
        if len(draw) != 1: stats["pas_1x2"] += 1; continue
        # équipes dans l'ordre de la question « Exact Score: A a - b B? » ; match mon[ ] par le titre
        q = ms[0]["question"]
        mt = re.match(r"Exact Score: (.+?) (\d+) - (\d+) (.+?)\?$", q)
        if not mt: stats["question_illisible"] += 1; continue
        home, away = mt.group(1), mt.group(4)
        px = {}
        for x, tok, key in mon["liste"]:
            g = x.get("groupItemTitle") or ""
            lab = "draw" if key else ("home" if g.strip() == home.strip() else "away" if g.strip() == away.strip() else None)
            if lab is None: break
            p = dernier(tm, tok, T0 - 6 * 3600, T0)
            if p is None: break
            px[lab] = p
        else:
            px = px
        if len(px) != 3: stats["pas_de_prix_1x2"] += 1; continue
        s = sum(px.values()); tgt = (px["home"] / s, px["draw"] / s, px["away"] / s)
        over = None
        for x in mm["markets"]:
            if x.get("sportsMarketType") == "totals" and str(x.get("line")) == "2.5":
                toks = json.loads(x["clobTokenIds"]); ov = dernier(tmm, toks[0], T0 - 6 * 3600, T0); un = dernier(tmm, toks[1], T0 - 6 * 3600, T0)
                if ov is not None and un is not None: over = ov / (ov + un)
                elif ov is not None: over = ov
        lh, la, resid = ajuster(tgt, over)
        stats["modeles"] += 1
        if resid > 0.01: stats["ajustement_mauvais"] += 1
        # règlement : le score gagnant doit être cohérent avec le 1X2 réglé
        wq = gagnants[0]["question"]; wm = re.match(r"Exact Score: (.+?) (\d+) - (\d+) (.+?)\?$", wq)
        sc_win = (int(wm.group(2)), int(wm.group(3))) if wm else None
        res12 = {}
        for x, tok, key in mon["liste"]:
            pr = json.loads(x["outcomePrices"])
            res12["draw" if key else "home" if (x.get("groupItemTitle") or "").strip() == home.strip() else "away"] = pr[0] == "1"
        if sc_win:
            ok = (sc_win[0] > sc_win[1] and res12.get("home")) or (sc_win[0] == sc_win[1] and res12.get("draw")) or (sc_win[0] < sc_win[1] and res12.get("away"))
            reglement_total += 1; reglement_ok += bool(ok)
        else:
            stats["autre_score_gagne"] += 1
        # score exact : modèle contre marché
        ph, pa = grille(lh, la)
        grid_sum = 0.0
        rows = []
        for x in ms:
            toks = json.loads(x["clobTokenIds"]); mm_ = re.match(r"Exact Score: (.+?) (\d+) - (\d+) (.+?)\?$", x["question"])
            if mm_:
                a, b = int(mm_.group(2)), int(mm_.group(3)); pm = ph[a] * pa[b]; grid_sum += pm
            else:
                a = b = None; pm = None
            rows.append((x, toks, a, b, pm))
        rate = float((ms[0].get("feeSchedule") or {}).get("rate") or 0) if ms[0].get("feesEnabled") else 0.0
        mois = dt.datetime.fromtimestamp(K, dt.timezone.utc).strftime("%Y-%m")
        for x, toks, a, b, pm in rows:
            if pm is None: pm = max(0.0, 1 - grid_sum)  # « tout autre score »
            yes = json.loads(x["outcomePrices"])[0] == "1"
            cy = it.taker_cost(te, toks[0], toks[1], T0, window=int(FEN * 3600), after=True)
            cn = it.taker_cost(te, toks[1], toks[0], T0, window=int(FEN * 3600), after=True)
            if cy is not None and K < T0: continue
            # tout échange après le coup d'envoi est exclu
            for side, c, pwin in (("oui", cy, pm), ("non", cn, 1 - pm)):
                if c is None or c <= 0.005 or c >= 0.995: continue
                got = yes if side == "oui" else (not yes)
                t_exec = None
                bets_rows.append(dict(match=e["slug"], mois=mois, side=side, cout=c, modele=pwin, gain_brut=(1.0 if got else 0.0), fee=it.fee(c, rate),
                                      yes_price=(c if side == "oui" else 1 - c), pm=pm, gagne=got, score=("autre" if a is None else f"{a}-{b}")))
            # scores : calibrage du modèle contre le dernier prix connu
            py = dernier(te, toks[0], T0 - 6 * 3600, T0)
            if py is not None and pm is not None and 0.005 < py < 0.995:
                nlog += 1
                log_modele += math.log(pm if yes else 1 - pm) if 0 < pm < 1 else 0
                log_marche += math.log(py if yes else 1 - py)
    print("stats", dict(stats))
    print("règlement cohérent (score gagnant vs 1X2 réglé):", reglement_ok, "/", reglement_total)
    print("log-score (par marché-score avec prix connu à T0) modèle", round(log_modele / max(1, nlog), 5), "marché", round(log_marche / max(1, nlog), 5), "n", nlog)
    json.dump(bets_rows, open(D / f"paris_{DECAL:g}_{FEN:g}.json", "w"))
    print(len(bets_rows), "paris candidats (oui + non)")


if __name__ == "__main__":
    main()
