"""Piste n° 65 : les signaux du rejeu (écart modèle - prix >= seuil) aux VRAIS échanges : premier achat preneur du côté voulu
dans les 6 h après T, et parts achetées par des preneurs à <= ce prix + 0,02 dans ces 6 h (profondeur)."""
import json, os, sys, time, requests, concurrent.futures as cf
from datetime import datetime
S = requests.Session(); S.headers["User-Agent"] = "curl/8"
D = os.path.join(os.path.dirname(__file__), '..', 'donnees')
ev = {e['id']: e for e in json.load(open(os.path.join(D, 'evenements.json')))}
L = json.load(open(os.path.join(D, 'rejeu.json')))
cond_of = {}
for e in ev.values():
    for m in e['markets']: cond_of[(e['id'], m.get('groupItemTitle'))] = m.get('conditionId')
def trades(cond):
    out, cur = [], None
    for _ in range(20):
        p = {"condition": cond, "limit": 1000}
        if cur: p["cursor"] = cur
        r = S.get("https://data-api.polymarket.com/v2/trades", params=p, timeout=60)
        if r.status_code != 200: break
        j = r.json(); rows = j.get("data") or []
        out += [(int(x["timestamp"]), x["side"], x["outcome"], float(x["price"]), float(x["size"])) for x in rows if x.get("condition_id") == cond]
        cur = (j.get("pagination") or {}).get("next_cursor")
        if not rows or not (j.get("pagination") or {}).get("has_more") or not cur: break
    return cond, out
conds = sorted({cond_of[(l['ev'], l['lab'])] for l in L})
with cf.ThreadPoolExecutor(8) as ex: TR = dict(ex.map(trades, conds))
print(sum(len(v) for v in TR.values()), 'échanges sur', len(conds), 'tranches')
for j in (1, 2, 3):
    for seuil in (0.05, 0.08, 0.12):
        res = []
        for l in L:
            if l['j'] != j: continue
            fin = int(datetime.fromisoformat(ev[l['ev']]['endDate'].replace('Z', '+00:00')).timestamp()); T = fin - j * 86400
            for cote, ecart, gagne in (('Yes', l['modele'] - l['prix'], l['res']), ('No', l['prix'] - l['modele'], 1 - l['res'])):
                if ecart < seuil: continue
                tr = sorted(t for t in TR[cond_of[(l['ev'], l['lab'])]] if T <= t[0] <= T + 6 * 3600 and t[1] == 'BUY' and t[2] == cote)
                if not tr: res.append((None, gagne, 0, l['ev'])); continue
                px = tr[0][3]; prof = sum(t[4] for t in tr if t[3] <= px + 0.02)
                res.append((px, gagne, prof, l['ev']))
        ex_ = [r for r in res if r[0] is not None and r[0] < 0.97]
        for mini in (0, 50, 200):
            x = [r for r in ex_ if r[2] >= mini]
            if not x: continue
            c = sum(r[0] for r in x); g = sum(r[1] for r in x)
            print(f"J-{j} seuil {seuil} profondeur >= {mini} parts : {len(x)} paris ({len({r[3] for r in x})} év.) sur {len(res)} signaux, "
                  f"gagnés {g:.0f} pour {c:.2f} payés, {g/c-1:+.1%}")
