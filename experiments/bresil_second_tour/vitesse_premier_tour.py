"""Piste 15 (`depouillement_officiel`) : à quelle vitesse Polymarket a-t-il fixé le prix du 1er tour (4/10/2026) ?

Pour chaque marché « 1re place dans <État> » du 1er tour (27 États + étranger) et pour les marchés
nationaux (vainqueur du 1er tour, marge), on lit les ÉCHANGES RÉELS du vainqueur (data-api /trades,
preneurs) et on les compare au calendrier du dépouillement :
- fermeture des bureaux : 17 h heure de Brasília (20 h UTC), partout au Brésil ;
- fin du dépouillement de chaque État : fichier officiel du TSE br-e006257-ab.json (heure du dernier envoi) ;
- moment où l'issue est devenue MATHÉMATIQUEMENT certaine (avance > électeurs pas encore comptés) :
  pas de chronologie 2026 publiée ; estimée avec la chronologie officielle 2022 du TSE
  (Historico_Totalizacao_Presidente_BR_1T_2022.csv, même système, mêmes horaires) et la marge 2026.
  Ce fichier ne couvre que le Brésil entier : la même courbe sert pour chaque État (approximation).

« Achetable à p » = un preneur a réellement ACHETÉ le vainqueur à p (il y avait un vendeur).
Aucun regard vers le futur : on ne retient que les échanges postérieurs à l'instant de décision.

Lancer : .venv/bin/python -I experiments/bresil_second_tour/vitesse_premier_tour.py
Écrit vitesse_premier_tour.json (résumé par marché).
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cache_http import DONNEES, HTTP, SourceUnavailable, cached_json  # noqa: E402

GAMMA = "https://gamma-api.polymarket.com"
TRADES = "https://data-api.polymarket.com/trades"
BRT = timezone(timedelta(hours=-3))  # Brasília, sans heure d'été depuis 2019
POLLS_CLOSE = datetime(2026, 10, 4, 17, 0, tzinfo=BRT)
SLUG_UF = {"acre": "ac", "alagoas": "al", "amapa": "ap", "amazonas": "am", "bahia": "ba", "ceara": "ce",
           "espirito-santo": "es", "federal-district": "df", "goias": "go", "maranhao": "ma", "mato-grosso": "mt",
           "mato-grosso-do-sul": "ms", "minas-gerais": "mg", "para": "pa", "paraiba": "pb", "parana": "pr",
           "pernambuco": "pe", "piaui": "pi", "rio-de-janeiro": "rj", "rio-grande-do-norte": "rn",
           "rio-grande-do-sul": "rs", "rondonia": "ro", "roraima": "rr", "santa-catarina": "sc",
           "sao-paulo": "sp", "sergipe": "se", "tocantins": "to", "abroad": "zz"}
THRESHOLDS = (0.90, 0.95, 0.97, 0.99)


def market_trades(condition_id: str) -> list[dict]:
    """Tous les échanges preneurs d'un marché (au plus 11 000, les plus récents d'abord)."""
    path = DONNEES / f"trades_{condition_id[:18]}.json"
    if path.exists():
        return json.loads(path.read_text())
    rows: list[dict] = []
    for page in range(11):
        try:
            batch = HTTP.get_json(TRADES, params={"market": condition_id, "limit": 1000, "offset": page * 1000})
        except SourceUnavailable:
            break
        if not isinstance(batch, list) or not batch:
            break
        rows += [{"t": int(x["timestamp"]), "asset": x["asset"], "side": x["side"], "p": float(x["price"]),
                  "q": float(x["size"])} for x in batch]
        if len(batch) < 1000:
            break
    path.write_text(json.dumps(rows))
    return rows


def history_2022(path: Path) -> dict[str, list[tuple[float, float]]]:
    """Chronologie officielle 2022 : {uf: [(minutes après 17 h, part des électeurs comptés), ...]}."""
    out: dict[str, list[tuple[float, float]]] = {}
    close = None  # 17 h le jour du vote (première ligne) ; les retardataires des jours suivants comptent en plus
    with path.open(encoding="latin-1") as fh:
        reader = csv.reader(fh, delimiter=";")
        header = [h.strip() for h in next(reader)]
        idx = {h: i for i, h in enumerate(header)}
        for row in reader:
            row = [c.strip() for c in row]
            if len(row) < len(header):
                continue
            uf = row[idx["SG_UE_UF"]].lower() if "SG_UE_UF" in idx else "br"  # fichiers 2022 : national seulement
            when = datetime.strptime(row[idx["DT_TOTALIZACAO"]], "%d/%m/%Y %H:%M:%S")
            if close is None:
                close = when.replace(hour=17, minute=0, second=0)
            minutes = (when - close).total_seconds() / 60
            share = int(row[idx["QT_APTOS_TOT_ACUMULADO"]]) / max(1, int(row[idx["QT_APTOS_TOTAL"]]))
            out.setdefault(uf, []).append((minutes, share))
    for uf in out:
        out[uf].sort()
    return out


def minutes_to_share(curve: list[tuple[float, float]], share: float) -> float | None:
    for minutes, s in curve:
        if s >= share:
            return minutes
    return None


def path_10min(win: list[dict], start: float, end: float) -> list[dict]:
    """Achats du vainqueur par tranche de 10 min : prix le plus bas, le plus haut, dollars échangés."""
    out = []
    t = start
    while t < end:
        sel = [x for x in win if t <= x["t"] < t + 600 and x["side"] == "BUY"]
        if sel:
            out.append({"min_apres_17h": round((t - POLLS_CLOSE.timestamp()) / 60), "achat_min": min(x["p"] for x in sel),
                        "achat_max": max(x["p"] for x in sel), "usd": round(sum(x["p"] * x["q"] for x in sel))})
        t += 600
    return out


def winner_market(event: dict) -> dict | None:
    for m in event.get("markets") or []:
        prices = json.loads(m.get("outcomePrices") or "[]")
        if prices and float(prices[0]) > 0.5 and m.get("closed"):
            return m
    return None


def analyse(event_id: str, uf: str, margin: float, valid_ratio: float, t100: datetime | None,
            curve: list[tuple[float, float]] | None) -> dict:
    event = cached_json(f"{GAMMA}/events/{event_id}", name=f"event_{event_id}")
    m = winner_market(event)
    yes = json.loads(m["clobTokenIds"])[0]
    trades = market_trades(m["conditionId"])
    win = sorted((x for x in trades if x["asset"] == yes), key=lambda x: x["t"])
    buys = [x for x in win if x["side"] == "BUY"]
    oldest = min((x["t"] for x in trades), default=None)
    close_ts = POLLS_CLOSE.timestamp()
    # Estimation du moment « mathématiquement décidé » : f* = 1 / (1 + marge × votes valides/électeurs)
    f_star = 1 / (1 + margin * valid_ratio) if margin > 0 else 1.0
    m_dec = minutes_to_share(curve, f_star) if curve else None
    t_dec = close_ts + m_dec * 60 if m_dec is not None else None
    if t100 is not None and (t_dec is None or t_dec > t100.timestamp()):
        t_dec = t100.timestamp()  # au plus tard : l'État est compté à 100 %
        m_dec = round((t_dec - close_ts) / 60, 1)

    def last_trade_before(ts):
        sel = [x for x in win if x["t"] <= ts]
        return sel[-1]["p"] if sel else None

    out = {"event_id": event_id, "uf": uf, "vainqueur": m.get("groupItemTitle"), "market_id": m["id"],
           "condition_id": m["conditionId"], "marge_finale_points": round(100 * margin, 2),
           "part_a_compter_pour_decider": round(f_star, 4), "decide_estime_min_apres_17h": m_dec,
           "fin_depouillement_min_apres_17h": round((t100.timestamp() - close_ts) / 60, 1) if t100 else None,
           "echanges_lus": len(trades), "plus_ancien_echange": datetime.fromtimestamp(oldest, timezone.utc).isoformat() if oldest else None,
           "couverture_complete": bool(oldest and oldest < close_ts - 6 * 3600),
           "prix_a_17h": last_trade_before(close_ts), "prix_a_17h30": last_trade_before(close_ts + 1800),
           "prix_a_18h": last_trade_before(close_ts + 3600), "prix_a_19h": last_trade_before(close_ts + 7200),
           "prix_a_decision": last_trade_before(t_dec) if t_dec else None,
           "prix_a_fin_depouillement": last_trade_before(t100.timestamp()) if t100 else None,
           "chemin_10min": path_10min(win, close_ts - 3600, close_ts + 9 * 3600)}
    for thr in THRESHOLDS:
        cheap = [x for x in buys if x["p"] <= thr and x["t"] >= close_ts]
        out[f"dernier_achat_<={thr}_min_apres_17h"] = round((cheap[-1]["t"] - close_ts) / 60, 1) if cheap else None
        for label, start in (("apres_decision", t_dec), ("apres_decision_plus_10min", t_dec + 600 if t_dec else None),
                             ("apres_decision_plus_15min", t_dec + 900 if t_dec else None),
                             ("apres_fin_depouillement", t100.timestamp() if t100 else None)):
            if start is None:
                continue
            sel = [x for x in buys if x["p"] <= thr and x["t"] >= start]
            out[f"usd_achats_<={thr}_{label}"] = round(sum(x["p"] * x["q"] for x in sel), 2)
            out[f"n_achats_<={thr}_{label}"] = len(sel)
    return out


def main() -> None:
    allev = json.loads((DONNEES / "all_events_search.json").read_text())
    tse = json.loads((HERE / "tse_6257_etats.json").read_text())
    ab = json.loads((DONNEES / "r1_br_ab.json").read_text()) if (DONNEES / "r1_br_ab.json").exists() else \
        cached_json("https://resultados.tse.jus.br/oficial/ele2026/6257/dados/br/br-e006257-ab.json", name="r1_br_ab")
    t100 = {a["cdabr"]: datetime.strptime(a["dt"] + " " + a["ht"], "%d/%m/%Y %H:%M:%S").replace(tzinfo=BRT)
            for a in ab["abr"]}
    hist = history_2022(DONNEES / "hist2022" / "t1" / "Historico_Totalizacao_Presidente_BR_1T_2022.csv")
    rows = []
    for e in sorted(allev.values(), key=lambda e: e["slug"]):
        slug = e["slug"]
        if "brazil-presidential-election-first-round-1st-place-in-" in slug:
            uf = SLUG_UF[slug.rsplit("-in-", 1)[1]]
        elif slug in ("brazil-presidential-election-first-round-winner",
                      "brazil-presidential-election-first-round-margin-of-victory"):
            uf = "br"  # la tranche « Flávio < 5 % » se décide en même temps que le vainqueur (marge finale 1,9 point)
        else:
            continue
        r = tse[uf] if uf in tse else None
        if r is None:  # national
            r = __import__("tse").summary(json.loads((DONNEES / "r1_br_u.json").read_text()))
        c1, c2 = r["candidatos"][0], r["candidatos"][1]
        margin = (c1["votos"] - c2["votos"]) / max(1, r["validos"])
        valid_ratio = r["validos"] / max(1, r["eleitorado"])
        # Chronologie 2022 publiée pour le Brésil entier seulement : même courbe pour chaque État (approximation).
        curve = hist.get("br")
        rows.append(analyse(e["id"], uf, margin, valid_ratio, t100.get(uf), curve))
        x = rows[-1]
        print(f"{uf} {x['vainqueur'][:16]:<16} marge {x['marge_finale_points']:>6} f* {x['part_a_compter_pour_decider']:.3f} "
              f"décidé~{x['decide_estime_min_apres_17h']} fin {x['fin_depouillement_min_apres_17h']} | prix 17h {x['prix_a_17h']} "
              f"18h {x['prix_a_18h']} déc {x['prix_a_decision']} | dernier achat<=0.97 {x['dernier_achat_<=0.97_min_apres_17h']} "
              f"$<=0.97 après déc+10 {x.get('usd_achats_<=0.97_apres_decision_plus_10min')} | couverture {x['couverture_complete']}")
    (HERE / "vitesse_premier_tour.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
