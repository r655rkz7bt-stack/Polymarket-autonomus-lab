"""PIB trimestriel brésilien (IBGE, SIDRA 1621, volume désaisonnalisé) contre IBC-Br (BCB SGS 24364, désaisonnalisé).
Données d'aujourd'hui (révisées) : donne l'écart-type de « PIB t/t − IBC-Br t/t », borne basse de l'erreur réelle (premier chiffre)."""
import json, statistics, sys, requests
H = {"User-Agent": "curl/8"}
sid = requests.get("https://apisidra.ibge.gov.br/values/t/1621/n1/all/v/584/p/all/c11255/90707", headers=H, timeout=60).json()
gdp = {r["D3C"]: float(r["V"]) for r in sid[1:] if r["V"] not in ("...", "-", "X")}
ibc = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.24364/dados?formato=json", headers=H, timeout=60).json()
m = {}
for r in ibc:
    d, mo, y = r["data"].split("/")
    m[(int(y), int(mo))] = float(r["valor"])
q = {}
for (y, mo), v in m.items():
    q.setdefault(f"{y}0{(mo - 1) // 3 + 1}", []).append(v)
q = {k: sum(v) / 3 for k, v in q.items() if len(v) == 3}
keys = sorted(k for k in gdp if k in q)
rows = []
for a, b in zip(keys, keys[1:]):
    g = 100 * (gdp[b] / gdp[a] - 1); i = 100 * (q[b] / q[a] - 1)
    rows.append((b, round(g, 2), round(i, 2), round(g - i, 2)))
json.dump(rows, open(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdout", "w"))
