"""Suite de la sonde (23/10/2026) : quelles heures passées l'API d'ensemble remplit-elle vraiment, et
quels passages (« run= ») récents garde-t-elle ? Résultat ajouté à `resultats_sonde_historique.txt`.
Usage : python experiments/meteo_ensemble/sonde_runs.py
"""
from pathlib import Path

import requests

U = "https://ensemble-api.open-meteo.com/v1/ensemble"
S = "https://single-runs-api.open-meteo.com/v1/forecast"
P = dict(latitude=51.505, longitude=0.055, timezone="UTC", hourly="temperature_2m")
lines = []


class _Failed:
    status_code = "échec réseau"


def call(url, **kw):
    try:
        r = requests.get(url, params=dict(P, **kw), timeout=60, headers={"User-Agent": "curl/8"})
    except requests.RequestException as exc:
        return _Failed(), {"error": True, "reason": type(exc).__name__}
    try:
        return r, r.json()
    except ValueError:
        return r, {}


r, d = call(U, models="gfs025", past_days=30, forecast_days=1)
h = d.get("hourly") or {}
t, v = h.get("time") or [], h.get("temperature_2m") or []
idx = [i for i, x in enumerate(v) if x is not None]
lines.append(f"- past_days=30, GEFS : heures remplies {t[idx[0]] if idx else '-'} → {t[idx[-1]] if idx else '-'} ({len(idx)} sur {len(t)})")
for model in ("gfs025", "ecmwf_ifs025"):
    for run in ("2026-10-23T12:00", "2026-10-23T00:00", "2026-10-22T00:00", "2026-10-19T00:00"):
        for url in (U, S):
            r, d = call(url, models=model if url == U else {"gfs025": "ncep_gefs025", "ecmwf_ifs025": "ecmwf_ifs025_ensemble"}[model],
                        run=run, forecast_days=2)
            hh = d.get("hourly") or {}
            filled = sum(1 for k, vals in hh.items() if k != "time" for x in vals if x is not None)
            series = len([k for k in hh if k != "time"])
            what = d.get("reason") if d.get("error") else f"{series} séries, {filled} valeurs"
            lines.append(f"- run={run} {model} sur {url.split('//')[1].split('/')[0]} : HTTP {r.status_code}, {what}")
            print(lines[-1], flush=True)
out = Path(__file__).parent / "resultats_sonde_historique.txt"
out.write_text(out.read_text() + "\nSuite (sonde_runs.py) :\n" + "\n".join(lines) + "\n")
print(lines[0])
