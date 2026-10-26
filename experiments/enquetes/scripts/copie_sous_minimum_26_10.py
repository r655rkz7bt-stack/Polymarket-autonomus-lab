"""26/10/2026 (soir) : quels paris des fantômes à part du capital principal le principal pouvait-il copier (minimum de 5 parts du marché) ?
Facteur de copie = part × capital du principal / capital du fantôme × (base / prudence du fantôme) (main.Weighted._copy).
Lancer depuis la racine après `bash scripts/fetch_data.sh` et `bash scripts/fetch_published.sh`."""
import json
d = json.load(open('published/data.json'))
principal = float(d['capital']['capital_total_estime'])
principal_buys = [json.loads(l) for l in open('published_data/ledger/ledger.jsonl')]
mine = {}
for r in principal_buys:
    if r['type'] == 'BUY':
        mine.setdefault(r['data']['strategy_id'], set()).add(r['data']['token_id'])
base = 0.5
print('capital principal %.0f' % principal)
for a in d['arene']:
    if not a.get('part_principal'):
        continue
    rows = [json.loads(l) for l in open(f"published_data/ledger/fantome/{a['nom']}.jsonl")]
    last = [r for r in rows if r['type'] == 'HEARTBEAT' and r['data'].get('total_estimated')][-1]
    cap_ghost = float(last['data']['total_estimated'])
    prud = a['sante']['prudence'] or 1.0
    factor = a['part_principal'] * principal / cap_ghost * (base / prud)
    first = {}
    for r in rows:
        if r['type'] == 'BUY':
            first.setdefault(r['data']['token_id'], r)
    sh = [float(r['data']['shares']) * factor for r in first.values()]
    cost = [float(r['data']['shares']) * factor * float(r['data']['price']) for r in first.values()]
    ok = sum(1 for s in sh if s >= 5)
    floored = sum(1 for s, c, r in zip(sh, cost, first.values()) if s < 5 and 5 * float(r['data']['price']) <= 0.01 * principal)
    sid = a['nom'].rsplit('_v', 1)[0]
    print(f"{sid}: part {a['part_principal']:.1%}, facteur {factor:.4f}, {len(first)} jetons du fantôme, "
          f"copie >= 5 parts : {ok}, plancher : {floored} de plus, copiés par le principal : {len(mine.get(sid, set()) & set(first))}")
