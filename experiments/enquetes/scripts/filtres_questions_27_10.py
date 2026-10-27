"""27/10/2026 famille 4 : les achats des fantômes respectent-ils les filtres de question (disciplines, types_pari, issue,
question_contient/exclut) ? Relit la question dans market_rules (sauvegarde) et applique les MÊMES fonctions que le moteur."""
import glob, json, os, sqlite3, sys, yaml
sys.path.insert(0, "src")
from polymarket_agent.pareto import bet_type, discipline
from polymarket_agent.resolution_sources import domain_of

db = sqlite3.connect(sys.argv[1])
rules = {r[0]: (r[1], r[2]) for r in db.execute("select market_id, question, resolution_source from market_rules")}
cfg = yaml.safe_load(open("config/strategies.yaml"))
items = [dict(v, name=k) for k, v in cfg.items() if isinstance(v, dict)]
bad, tot, noq = {}, {}, 0
for s in items:
    f = s.get("filtres") or {}
    keys = {"disciplines", "types_pari", "issue", "question_contient", "question_exclut", "sources", "sources_exclues"} & set(f)
    if not keys:
        continue
    path = f"published_data/ledger/fantome/{s['name']}_v{s.get('version', '1.0.0')}.jsonl"
    if not os.path.exists(path):
        continue
    for line in open(path):
        x = json.loads(line)
        if x["type"] != "BUY":
            continue
        d = x["data"]; q, src = rules.get(d["market_id"], (None, None))
        if q is None:
            noq += 1; continue
        tot[s["name"]] = tot.get(s["name"], 0) + 1
        ql = q.lower(); why = None
        if "disciplines" in f and discipline(q, src) not in f["disciplines"]: why = "disciplines"
        elif "types_pari" in f and bet_type(q, None) not in f["types_pari"]: why = None  # sports_market_type absent du journal
        if "question_contient" in f and not any(w.lower() in ql for w in f["question_contient"]): why = "question_contient"
        if any(w.lower() in ql for w in f.get("question_exclut", ())): why = "question_exclut"
        if "issue" in f:
            o = d["outcome"].lower(); kind = "oui" if o == "yes" else "non" if o == "no" else "autre"
            if kind not in ([f["issue"]] if isinstance(f["issue"], str) else f["issue"]): why = "issue"
        if "sources" in f and domain_of(src or "") not in f["sources"]: why = "sources"
        if why:
            bad.setdefault(s["name"], []).append((x["ts"][:16], why, q[:70], d["outcome"]))
print("achats sans question connue :", noq, "; stratégies contrôlées :", len(tot), "; achats :", sum(tot.values()))
for n, v in bad.items():
    print(n, len(v), "/", tot[n]); [print("  ", *r) for r in v[:4]]
