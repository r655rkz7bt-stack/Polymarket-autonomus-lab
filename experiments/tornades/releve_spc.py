"""11/11/2026 : rapports préliminaires FILTRÉS de tornades du SPC (NOAA), jour par jour (jour SPC = 12 h UTC → 12 h UTC, daté du
premier jour), du 01/11/2025 à hier. Sortie : experiments/tornades/spc_jours.json {AAAA-MM-JJ: nombre}. Usage :
.venv/bin/python experiments/tornades/releve_spc.py"""
import json, datetime as dt, concurrent.futures as cf, requests
from pathlib import Path
OUT = Path("experiments/tornades/spc_jours.json")
have = json.loads(OUT.read_text()) if OUT.exists() else {}
days = []
d = dt.date(2025, 11, 1)
while d < dt.date.today():
    if d.isoformat() not in have or d >= dt.date.today() - dt.timedelta(days=7):
        days.append(d)
    d += dt.timedelta(days=1)
def get(day):
    r = requests.get(f"https://www.spc.noaa.gov/climo/reports/{day:%y%m%d}_rpts_filtered_torn.csv", timeout=30)
    if r.status_code != 200:
        return day, None
    lines = [l for l in r.text.splitlines()[1:] if l.strip()]
    return day, len(lines)
with cf.ThreadPoolExecutor(6) as ex:
    for day, n in ex.map(get, days):
        if n is not None:
            have[day.isoformat()] = n
OUT.write_text(json.dumps(dict(sorted(have.items())), indent=0))
print(len(have), "jours")
