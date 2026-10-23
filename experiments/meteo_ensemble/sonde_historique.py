"""Existe-t-il des prévisions d'ENSEMBLE passées gratuites chez Open-Meteo ? (23/10/2026)

Chaque URL essayée est appelée pour de vrai ; la réponse (code HTTP, erreur, membres trouvés, heures
renvoyées) est écrite dans `resultats_sonde_historique.txt`. Lieu : Londres City (EGLC).
Usage : python experiments/meteo_ensemble/sonde_historique.py
"""
import json
import re
from pathlib import Path

import requests

LAT, LON = 51.505, 0.055
BASE = dict(latitude=LAT, longitude=LON, timezone="UTC")
TRIES = [
    ("ensemble, dates passées (start/end)", "https://ensemble-api.open-meteo.com/v1/ensemble",
     dict(BASE, hourly="temperature_2m", models="gfs025", start_date="2026-10-01", end_date="2026-10-03")),
    ("ensemble, dates passées lointaines", "https://ensemble-api.open-meteo.com/v1/ensemble",
     dict(BASE, hourly="temperature_2m", models="gfs025", start_date="2026-07-01", end_date="2026-07-02")),
    ("ensemble, past_days=30", "https://ensemble-api.open-meteo.com/v1/ensemble",
     dict(BASE, hourly="temperature_2m", models="gfs025", past_days=30, forecast_days=1)),
    ("ensemble, past_days=92", "https://ensemble-api.open-meteo.com/v1/ensemble",
     dict(BASE, hourly="temperature_2m", models="gfs025", past_days=92, forecast_days=1)),
    ("ensemble, variable previous_day1", "https://ensemble-api.open-meteo.com/v1/ensemble",
     dict(BASE, hourly="temperature_2m_previous_day1", models="gfs025", past_days=3, forecast_days=1)),
    ("ensemble, run= (un passage précis)", "https://ensemble-api.open-meteo.com/v1/ensemble",
     dict(BASE, hourly="temperature_2m", models="gfs025", run="2026-10-10T00:00", forecast_days=2)),
    ("previous-runs, modèle d'ensemble", "https://previous-runs-api.open-meteo.com/v1/forecast",
     dict(BASE, hourly="temperature_2m_previous_day1", models="ncep_gefs025", past_days=3)),
    ("historical-forecast, modèle d'ensemble", "https://historical-forecast-api.open-meteo.com/v1/forecast",
     dict(BASE, hourly="temperature_2m", models="ncep_gefs025", start_date="2026-10-01", end_date="2026-10-02")),
    ("single-runs, déterministe (référence)", "https://single-runs-api.open-meteo.com/v1/forecast",
     dict(BASE, hourly="temperature_2m", models="gfs_seamless", run="2026-10-10T00:00", forecast_days=2)),
    ("single-runs, modèle d'ensemble", "https://single-runs-api.open-meteo.com/v1/forecast",
     dict(BASE, hourly="temperature_2m", models="ncep_gefs025", run="2026-10-10T00:00", forecast_days=2)),
    ("ensemble single-runs (sous-domaine)", "https://ensemble-single-runs-api.open-meteo.com/v1/ensemble",
     dict(BASE, hourly="temperature_2m", models="gfs025", run="2026-10-10T00:00", forecast_days=2)),
    ("ensemble, modèles disponibles aujourd'hui", "https://ensemble-api.open-meteo.com/v1/ensemble",
     dict(BASE, hourly="temperature_2m", forecast_days=2,
          models="icon_seamless,icon_global,icon_eu,icon_d2,gfs025,gfs05,ecmwf_ifs025,ecmwf_aifs025,gem_global,"
                 "bom_access_global_ensemble,ukmo_global_ensemble_20km,ukmo_uk_ensemble_2km,meteoswiss_icon_ch1,"
                 "meteoswiss_icon_ch2")),
]


def describe(resp) -> str:
    try:
        d = resp.json()
    except ValueError:
        return f"HTTP {resp.status_code}, pas du JSON : {resp.text[:150]!r}"
    items = d if isinstance(d, list) else [d]
    d = items[0]
    if d.get("error"):
        return f"HTTP {resp.status_code}, erreur : {d.get('reason')}"
    h = d.get("hourly") or {}
    times = h.get("time") or []
    keys = [k for k in h if k != "time"]
    filled = {k: sum(v is not None for v in h[k]) for k in keys}
    models = sorted({re.sub(r"^temperature_2m(_member\d+)?_?", "", k) or "(sans suffixe)" for k in keys})
    members = len([k for k in keys if "member" in k]) + len([k for k in keys if "member" not in k])
    return (f"HTTP {resp.status_code}, {len(times)} heures ({times[0] if times else '-'} → {times[-1] if times else '-'}), "
            f"{members} séries, valeurs non vides {min(filled.values()) if filled else 0}-{max(filled.values()) if filled else 0}, "
            f"modèles : {', '.join(models)[:400]}")


def main():
    lines = []
    for name, url, params in TRIES:
        try:
            r = requests.get(url, params=params, timeout=60, headers={"User-Agent": "curl/8"})
            text = describe(r)
            full = r.url
        except requests.RequestException as exc:
            text, full = f"échec réseau : {exc}", url
        lines.append(f"- {name}\n  {full}\n  → {text}")
        print(lines[-1], flush=True)
    (Path(__file__).parent / "resultats_sonde_historique.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
