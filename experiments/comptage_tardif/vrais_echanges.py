"""Piste n° 66 : le meneur à J+d acheté AUX VRAIS ÉCHANGES (data-api v2, trades?condition=), frais du marché
(feeSchedule), un tirage par événement, idea_test.verdict. Prix payé = premier échange preneur dans les 2 h APRÈS
l'instant de décision (achat du jeton ou vente de l'autre issue) ; profondeur = parts achetées à ≤ prix + 0,02 dans l'heure.
Décision : le meneur est lu sur l'historique (prix connu à l'instant), jamais sur l'issue."""
import json, sys, datetime as dt, collections, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from polymarket_agent import idea_test

H = {"User-Agent": "curl/8"}
D = Path(__file__).parent / "donnees"
cas = json.loads((D / "cas.json").read_text())
JOUR = sys.argv[1] if len(sys.argv) > 1 else "1"
LO, HI = (float(x) for x in (sys.argv[2:4] if len(sys.argv) > 3 else ("0.3", "0.95")))


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00").replace(" ", "T").replace("+00:00:00", "+00:00")).timestamp()


def trades(cond):
    out, cur = [], None
    for _ in range(40):
        p = {"condition": cond, "limit": 1000}
        if cur: p["cursor"] = cur
        r = requests.get("https://data-api.polymarket.com/v2/trades", params=p, headers=H, timeout=30).json()
        rows = r.get("data") or []
        out += rows
        pag = r.get("pagination") or {}
        cur = pag.get("next_cursor") if pag.get("has_more") else None
        if not cur or not rows: break
    return out


def un(ev_rows):
    rs = [r for r in ev_rows if JOUR in r["prix"]]
    if not rs: return None
    top = max(rs, key=lambda r: r["prix"][JOUR]); p = top["prix"][JOUR]
    if not (LO <= p < HI): return None
    m = requests.get(f"https://gamma-api.polymarket.com/markets/{top['market']}", headers=H, timeout=30).json()
    toks = json.loads(m["clobTokenIds"]); cond = m["conditionId"]
    fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
    rate = float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0
    t0 = ts(top["vote"]) + int(JOUR) * 86400
    tr = trades(cond)
    rows = []
    for x in tr:
        asset = str(x.get("asset") or x.get("asset_id") or x.get("token_id") or "")
        side = str(x.get("side", "")).upper(); price = float(x.get("price")); size = float(x.get("size") or 0)
        t = int(x.get("timestamp") or 0)
        rows.append([t, asset, side, price, size])
    paid = idea_test.taker_cost([r[:4] for r in rows], toks[0], toks[1], int(t0), after=True)
    if paid is None: return {"event": top["event"], "sans_echange": True}
    prof = sum(r[4] for r in rows if t0 <= r[0] <= t0 + 3600 and ((r[1] == toks[0] and r[2] == "BUY" and r[3] <= paid + 0.02)
               or (r[1] == toks[1] and r[2] == "SELL" and 1 - r[3] <= paid + 0.02)))
    cout = paid + idea_test.fee(paid, rate)
    return {"event": top["event"], "title": top["title"], "item": top["item"], "p_hist": p, "paye": paid, "cout": cout,
            "gagne": top["gagne"], "gain": top["gagne"] / cout - 1, "mois": top["vote"][:7], "profondeur": prof,
            "n_echanges": len(rows)}


if __name__ == "__main__":
    ev = collections.defaultdict(list)
    for r in cas: ev[r["event"]].append(r)
    with ThreadPoolExecutor(6) as ex:
        res = [r for r in ex.map(un, ev.values()) if r]
    (D / f"vrais_J{JOUR}.json").write_text(json.dumps(res))
    ok = [r for r in res if not r.get("sans_echange")]
    print(f"J+{JOUR} meneur {LO}-{HI} : {len(res)} événements, {len(ok)} avec échange dans les 2 h")
    bets = [{"gain": r["gain"], "evenement": r["event"], "mois": r["mois"], "cout": r["cout"]} for r in ok]
    v = idea_test.verdict(bets, min_bets=20)
    print(json.dumps({k: v[k] for k in v if k not in ("par_tranche_de_prix",)}, ensure_ascii=False, default=str)[:900])
    for seuil in (0, 50, 200, 1000):
        s = [r for r in ok if r["profondeur"] >= seuil]
        if s: print(f"   profondeur ≥ {seuil} parts : {len(s)} paris, rendement {sum(r['gain'] for r in s)/len(s):+.1%}, gagnés {sum(r['gagne'] for r in s)}/{len(s)}, coût moyen {sum(r['cout'] for r in s)/len(s):.3f}")
    print("   écart prix payé − prix historique (médiane):", sorted(r["paye"] - r["p_hist"] for r in ok)[len(ok)//2] if ok else None)
