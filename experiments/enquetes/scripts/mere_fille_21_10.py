"""Une fille (même classe, mêmes paramètres, un filtre de plus) achète-t-elle des jetons que sa mère, qui voit le même scanner et a du cash, n'achète pas ?
Pour chaque couple mère/fille aux paramètres identiques : achats de la fille dont le jeton n'est pas dans la mère ; cash de la mère à ce moment (dernier battement avant).
Lecture seule des journaux signés (published_data/)."""
import json, yaml, bisect, collections, sys
c = yaml.safe_load(open('config/strategies.yaml')); S = c.get('strategies', c)
def params(k): return {a: b['value'] for a, b in S[k].get('params', {}).items()}
def load(n):
    import glob
    p = glob.glob(f'published_data/ledger/fantome/{n}_v[0-9]*.jsonl')
    if not p: return None
    buys, beats = [], []
    for l in open(p[0]):
        d = json.loads(l)
        if d['type'] == 'BUY': buys.append(d)
        elif d['type'] == 'HEARTBEAT': beats.append((d['ts'], float(d['data']['cash'])))
    return buys, beats
out = []
for k, v in S.items():
    if not isinstance(v, dict) or not v.get('mere') or v.get('enabled', True) is False: continue
    m = v['mere']
    if m not in S or S[m].get('class', m) != v.get('class', k) and S[m].get('class') != v.get('class'): continue
    if S[m].get('enabled', True) is False: continue
    pm, pk = params(m), params(k)
    diff = {a for a in set(pm) | set(pk) if pm.get(a) != pk.get(a) and a not in ('max_candidates',)}
    if diff: continue
    if S[m].get('filtres') or v.get('limit_ticks') or 'limit_ticks' in pm: continue  # mère filtrée : comparaison moins directe
    a, b = load(m), load(k)
    if not a or not b: continue
    held = {x['data']['token_id'] for x in a[0]}
    ts = [t for t, _ in a[1]]
    miss = []
    for x in b[0]:
        if x['data']['token_id'] in held: continue
        i = bisect.bisect_right(ts, x['ts']) - 1
        cash = a[1][i][1] if i >= 0 else None
        miss.append((x['ts'][:16], x['data']['market_id'], float(x['data']['price']), cash))
    out.append((k, m, len(b[0]), len(miss), miss))
for k, m, n, nm, miss in sorted(out, key=lambda r: -r[3]):
    cash = [c for *_, c in miss if c is not None]
    print(f'{k:38s} mère {m:16s} achats fille {n:3d}, jetons absents de la mère {nm:3d}, cash de la mère à ces moments : médiane {sorted(cash)[len(cash)//2] if cash else None}')
    if k in ('nf_court', 'nf_moyen', 'nf_sport'):
        print('   ', miss[:4])
