"""Famille 4 (15/11) : achats des fantômes v2 depuis le dernier contrôle (14/11 10 h 52 UTC)
contre les réglages de config/strategies.yaml (plage de prix, horizon, avantage net, borne basse, mise)."""
import glob, json, sys, yaml
from pathlib import Path

DEPUIS = sys.argv[1] if len(sys.argv) > 1 else "2026-11-14T10:52"
cfg = yaml.safe_load(open("config/strategies.yaml"))
strats = {k: {"params": {n: (v["value"] if isinstance(v, dict) else v) for n, v in (s.get("params") or {}).items()}} for k, s in cfg.items() if isinstance(s, dict)}
ecarts, n = [], 0
for f in sorted(glob.glob("published_data/ledger/fantome_v2/*.jsonl")):
    cash = None
    for line in open(f):
        r = json.loads(line)
        d = r.get("data", {})
        if r["type"] == "INIT" or "capital" in d:
            cash = float(d.get("capital", d.get("amount", 1000)))
        if r["type"] != "BUY" or r["ts"] < DEPUIS:
            continue
        n += 1
        sid = d["strategy_id"]; p = strats.get(sid, {}).get("params", {}) or {}
        x = d["extra"]; price = float(d["price"]); cost = price * float(d["shares"])
        if not p: ecarts.append((sid, "réglages introuvables"))
        lo, hi = p.get("min_price"), p.get("max_price")
        if sid == "non_aux_drames": lo, hi = 1 - float(p["yes_max"]), 1 - float(p["yes_min"])
        if lo is not None and price < float(lo) - 1e-9: ecarts.append((sid, "sous la plage", price, lo))
        if hi is not None and price > float(hi) + 1e-9: ecarts.append((sid, "au-dessus de la plage", price, hi))
        h = float(x.get("horizon_hours") or 0)
        if p.get("min_days") is not None and not (float(p["min_days"]) * 24 <= h <= float(p["max_days"]) * 24): ecarts.append((sid, "horizon jours", h))
        if p.get("min_hours") is not None and h < float(p["min_hours"]): ecarts.append((sid, "horizon court", h))
        if p.get("max_hours") is not None and h > float(p["max_hours"]): ecarts.append((sid, "horizon long", h))
        ne = x.get("net_edge"); mne = p.get("min_net_edge", p.get("min_edge"))
        if ne is not None and mne is not None and float(ne) < float(mne) - 1e-9: ecarts.append((sid, "avantage", ne, mne))
        pl = x.get("prob_low")
        if pl is not None and float(pl) < price: ecarts.append((sid, "borne basse sous le prix", pl, price))
        if p.get("mise_max_pari") and cost > float(p["mise_max_pari"]) * 1000 * 1.05: ecarts.append((sid, "mise > mise_max_pari", round(cost, 2)))
        if cost > 250: ecarts.append((sid, "mise > 25 %", round(cost, 2)))
        print(r["ts"][:16], sid, d["outcome"], round(price, 3), "est", x.get("est_probability"), "bas", pl, "net", ne, "mise", round(cost, 2), "h", round(h))
print(f"{n} achats depuis {DEPUIS} ; écarts : {len(ecarts)}")
for e in ecarts: print("  ", e)
