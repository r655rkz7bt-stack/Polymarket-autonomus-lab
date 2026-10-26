"""Invariant : une fille à FILTRE seul (même classe et mêmes paramètres que sa mère) ne devrait acheter que des jetons que sa mère achète aussi.
Pour chaque fille, part des jetons achetés par la fille (après sa naissance) absents du journal de la mère. Un écart = filtre ou plafond caché."""
import json, yaml, os, collections
cfg = yaml.safe_load(open('config/strategies.yaml'))
cfg = cfg.get('strategies', cfg)
def toks(name, since=None):
    p = f'published_data/ledger/fantome/{name}.jsonl'
    if not os.path.exists(p): return None
    out = {}
    for l in open(p):
        r = json.loads(l)
        if r['type'] == 'BUY' and (since is None or r['ts'] >= since): out.setdefault(r['data']['token_id'], r['ts'])
    return out
res = []
for k, c in cfg.items():
    if not isinstance(c, dict) or not c.get('mere') or not c.get('enabled', True): continue
    m = cfg.get(str(c['mere']))
    if not isinstance(m, dict): continue
    same = c.get('class') == m.get('class') and not c.get('limit_ticks') and not m.get('limit_ticks') and c.get('params') == m.get('params')
    if not same: continue
    f = toks(f"{k}_v{c.get('version','1.0.0')}"); mo = toks(f"{c['mere']}_v{m.get('version','1.0.0')}")
    if not f or mo is None: continue
    born = min(f.values()) if f else None
    cand = {t: ts for t, ts in f.items()}
    manq = [t for t in cand if t not in mo]
    res.append((k, c['mere'], len(cand), len(manq)))
for k, m, n, x in sorted(res, key=lambda r: -r[3]):
    print(f"{k:50s} mère {m:30s} jetons {n:3d}  absents de la mère {x:3d} ({x/n:.0%})")
