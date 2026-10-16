"""Test sport Kalshi, étape 2 : retrouver le MÊME match sur les deux plateformes.

Usage : python3 -I experiments/sport_kalshi/match.py <dossier_de_travail> src
Lit kalshi_<ligue>.json et pm_<ligue>.json (étape 1), écrit <dossier>/props.json : une ligne par
proposition binaire identique des deux côtés (« l'équipe A gagne », et en football « match nul »).

Règles d'appariement (sans regarder le résultat) :
- même ligue ; coup d'envoi Polymarket (gameStartTime) à moins de 3 h du coup d'envoi Kalshi estimé
  (expected_expiration_time − 3 h, vérifié sur les données : écart médian 0 min), au plus 3 h en baseball
  et 8 h ailleurs ; le plus proche doit l'être nettement (2 h) pour départager deux matchs ;
- les DEUX équipes reconnues : même abréviation (après table d'équivalences) OU même nom (mots de Kalshi =
  débuts des mots de Polymarket) ; appariement un pour un, sinon le match est écarté (ambigu) ;
- marché Kalshi réglé « yes »/« no » (pas « scalar » = annulé), marché Polymarket réglé net à 1/0 ;
- les résultats des deux côtés doivent concorder (sinon : règles différentes, écarté et compté).
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
W, SRC = sys.argv[1], sys.argv[2]
sys.path[:0] = [str(Path(__file__).resolve().parent), SRC]
from common import LEAGUES, norm, same_team, ts  # noqa: E402

# Abréviations : Kalshi (suffixe du ticker) -> forme Polymarket (slug), quand elles diffèrent.
ABBR = {"nfl": {"LA": "la", "LAR": "la", "JAC": "jax", "WSH": "was", "LV": "lv"},
        "mlb": {"AZ": "ari", "ATH": "oak", "CWS": "cws", "WSH": "wsh", "KC": "kc", "SD": "sd", "SF": "sf", "TB": "tb"},
        "nhl": {"MTL": "mon", "LA": "la", "NJ": "nj", "SJ": "sj", "TB": "tb", "UTA": "uta", "VGK": "las",
                "WSH": "wsh", "CBJ": "cbj", "CGY": "cal", "LA": "lak"},
        "nba": {"GS": "gsw", "NY": "nyk", "NO": "nop", "SA": "sas", "PHX": "phx", "UTA": "uta", "WSH": "was"},
        "mls": {"NYRB": "nyr"},
        "lal": {"SAN": "rrc", "ATH": "bil", "ATM": "mad", "RVC": "ray", "MCF": "mala"},
        "uel": {"NIJ": "nec", "AZA": "az"},
        "bun": {"BMG": "moe", "SGE": "ein", "BVB": "dor", "LEV": "b04", "SVW": "wer", "RBL": "lei", "SVE": "elv",
                "M05": "mai", "VFB": "stu", "FCA": "aug", "SCF": "fre", "BMU": "bay"},
        "wnba": {"GS": "gsv", "LV": "las", "WSH": "was"}}
# Écart maximal entre les deux heures de début : 3 h en baseball (programmes doubles le même jour),
# 8 h ailleurs (deux mêmes équipes ne jouent pas deux fois en 2 jours ; certaines heures Kalshi sont
# approximatives en football universitaire). La seconde candidate doit être à 2 h de plus au moins.
MAXGAP = {"mlb": 3 * 3600}
LAG = 3 * 3600  # expected_expiration_time ≈ coup d'envoi + 3 h (vérifié : moyenne imprimée plus bas)


def kalshi_games(lg):
    """Événements Kalshi -> {équipes: {abréviation: (nom, ticker, résultat)}, nul, début estimé}."""
    by_ev = defaultdict(list)
    for m in json.load(open(f"{W}/kalshi_{lg}.json")):
        by_ev[m["event_ticker"]].append(m)
    games = []
    for ev, ms in by_ev.items():
        if any(m.get("result") not in ("yes", "no") for m in ms):
            continue
        teams, tie = {}, None
        for m in ms:
            ab = m["ticker"].rsplit("-", 1)[1]
            item = {"name": m.get("yes_sub_title") or "", "ticker": m["ticker"], "won": int(m["result"] == "yes"),
                    "close": ts(m.get("close_time"))}
            if ab == "TIE":
                tie = item
            else:
                teams[ab] = item
        exp = ts(ms[0].get("expected_expiration_time"))
        if len(teams) == 2 and exp:
            games.append({"event": ev, "series": ms[0]["event_ticker"].split("-")[0], "teams": teams, "tie": tie,
                          "start": exp - LAG, "close": min(t["close"] or 0 for t in teams.values())})
    return games


def pm_games(lg, three_way):
    """Marchés Polymarket « vainqueur » -> matchs {équipes: {abréviation: (nom, jeton, gagné)}, nul}."""
    out = defaultdict(lambda: {"teams": {}, "tie": None})
    for m in json.load(open(f"{W}/pm_{lg}.json")):
        prices, toks, outs = (json.loads(m.get(k) or "[]") for k in ("outcomePrices", "clobTokenIds", "outcomes"))
        if len(toks) != 2 or sorted(prices) != ["0", "1"] or m.get("umaResolutionStatus") not in (None, "", "resolved"):
            continue
        fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
        rate = float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0
        ev = (m.get("events") or [{}])[0].get("slug") or m["slug"]
        g = out[ev]
        g.update(start=ts(m["gameStartTime"]), event=ev)
        base = dict(market=str(m["id"]), token=toks[0], won=int(prices[0] == "1"), fee=rate, slug=m["slug"])
        if three_way:
            # « Will X win on … ? » (Oui/Non) ou « … end in a draw? »
            if m["slug"].endswith("-draw"):
                g["tie"] = dict(base, name="Tie")
            else:
                name = re.sub(r"^Will (.*) win on .*$", r"\1", m["question"])
                g["teams"][m["slug"].rsplit("-", 1)[1]] = dict(base, name=name)
        else:
            # « A vs. B », issues = noms des équipes : jeton 0 = l'équipe A (première issue).
            parts = re.match(rf"^{lg}-([a-z0-9]+)-([a-z0-9]+)-\d{{4}}-\d\d-\d\d", ev)
            if not parts or len(outs) != 2:
                continue
            g["teams"] = {parts.group(1): dict(base, name=outs[0]), parts.group(2): dict(base, name=outs[1], flip=True)}
    return [g for g in out.values() if g.get("start") and len(g["teams"]) == 2 and (not three_way or g["tie"])]


def team_map(lg, kg, pg):
    """Équipes Kalshi -> équipes Polymarket (un pour un), ou None."""
    alias = ABBR.get(lg, {})
    pairs = {}
    for ka, kt in kg["teams"].items():
        level = {pa: 4 if alias.get(ka, ka.lower()) == pa or ka.lower() == pa else same_team(kt["name"], pt["name"])
                 for pa, pt in pg["teams"].items()}
        best = max(level.values())
        hits = [pa for pa, v in level.items() if v == best and v > 0]
        if len(hits) != 1:
            return None
        pairs[ka] = hits[0]
    return pairs if len(set(pairs.values())) == 2 else None


props, stats = [], {}
for lg, (_, _, three) in LEAGUES.items():
    kgs, pgs = kalshi_games(lg), pm_games(lg, three)
    cand = defaultdict(list)
    for i, kg in enumerate(kgs):
        near = sorted((abs(pg["start"] - kg["start"]), j) for j, pg in enumerate(pgs)
                      if abs(pg["start"] - kg["start"]) <= 12 * 3600 and team_map(lg, kg, pg))
        if near and near[0][0] <= MAXGAP.get(lg, 8 * 3600) and (len(near) == 1 or near[1][0] >= near[0][0] + 2 * 3600):
            cand[near[0][1]].append((i, near[0][0]))
    c = Counter(kalshi=len(kgs), polymarket=len(pgs))
    lags = []
    for j, lst in cand.items():
        if len(lst) != 1:
            c["ambigus"] += 1
            continue
        kg, pg = kgs[lst[0][0]], pgs[j]
        lags.append(pg["start"] - kg["start"])
        if kg["close"] and kg["close"] < pg["start"]:
            c["kalshi_clos_avant_debut"] += 1  # heure du match incohérente entre les deux : écarté
            continue
        tmap = team_map(lg, kg, pg)
        rows = [(kg["teams"][ka], pg["teams"][pa], ka) for ka, pa in tmap.items()]
        if three:
            rows.append((kg["tie"], pg["tie"], "TIE"))
        # Contrôle : le vainqueur doit être le même des deux côtés.
        agree = all(kt["won"] == (1 - pt["won"] if pt.get("flip") else pt["won"]) for kt, pt, _ in rows if kt)
        if not agree:
            c["resultats_differents"] += 1
            continue
        c["apparies"] += 1
        opp = {ka: kg["teams"][kb]["ticker"] for ka in tmap for kb in tmap if kb != ka}
        for kt, pt, ka in rows:
            if not kt or (not three and pt.get("flip")):
                continue  # match à 2 issues : une seule proposition (« l'équipe A gagne »), l'autre est son contraire
            props.append({"league": lg, "series": kg["series"], "event": kg["event"], "pm_event": pg["event"],
                          "start": pg["start"], "label": f"{pg['event']} : {pt['name']}", "kind": "nul" if ka == "TIE" else "equipe",
                          "pm_market": pt["market"], "pm_token": pt["token"], "won": pt["won"], "fee": pt["fee"],
                          "k_ticker": kt["ticker"], "k_opp": None if three else opp[ka], "three_way": three})
    lags.sort()
    c["ecart_median_min"] = round(lags[len(lags) // 2] / 60) if lags else None
    stats[lg] = dict(c)
    print(f"{lg:5s}", dict(c))
json.dump(props, open(f"{W}/props.json", "w"))
json.dump(stats, open(f"{W}/match_stats.json", "w"), indent=1)
print(len(props), "propositions appariées")
