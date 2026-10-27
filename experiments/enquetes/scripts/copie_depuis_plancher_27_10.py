"""27/10/2026 (midi) : depuis la mise en service du plancher de copie (26/10, 15 h 40 UTC), le principal copie-t-il les paris
des fantômes qui ont une part du capital ? Compte, par stratégie, les jetons achetés par le fantôme (premier achat de chaque jeton)
et ceux que le principal a achetés aussi (même jeton, dans les 6 heures). Depuis la racine, après `fetch_data.sh`."""
import json, sys
from datetime import datetime, timedelta
CUT = sys.argv[1] if len(sys.argv) > 1 else '2026-10-26T15:40'
d = json.load(open('published/data.json'))
P = [json.loads(l) for l in open('published_data/ledger/ledger.jsonl')]
mine = {}
for r in P:
    if r['type'] == 'BUY' and r['ts'] >= CUT:
        mine.setdefault(r['data']['strategy_id'], {}).setdefault(r['data']['token_id'], r['ts'])
t = lambda s: datetime.fromisoformat(s)
tot_g = tot_m = 0
for a in d['arene']:
    if not a.get('part_principal'):
        continue
    rows = [json.loads(l) for l in open(f"published_data/ledger/fantome/{a['nom']}.jsonl")]
    first = {}
    for r in rows:
        if r['type'] == 'BUY' and r['ts'] >= CUT:
            first.setdefault(r['data']['token_id'], r['ts'])
    sid = a['nom'].rsplit('_v', 1)[0]
    m = mine.get(sid, {})
    copied = sum(1 for k, ts in first.items() if k in m and abs((t(m[k]) - t(ts)).total_seconds()) < 6 * 3600)
    tot_g += len(first); tot_m += copied
    print(f"{sid}: part {a['part_principal']:.1%}, jetons du fantôme {len(first)}, copiés {copied}")
print('total', tot_g, tot_m)
