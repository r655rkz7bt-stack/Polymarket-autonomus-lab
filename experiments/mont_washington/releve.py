"""11/11/2026 : F6 du Mount Washington Observatory (source de règlement de « Highest Mt. Washington wind speed in <mois> »), colonne
« FASTEST MILE SPEED » (= ce que le marché lit : 4 mois réglés retrouvés). Rafale maximale par jour pour un mois donné de plusieurs années.
Usage : .venv/bin/python experiments/mont_washington/releve.py 11 2005 2025"""
import json, re, subprocess, sys, tempfile, requests
from pathlib import Path
mois, a, b = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
out = {}
for y in range(a, b + 1):
    r = requests.get(f"https://mountwashington.org/uploads/pdf/forms/{y}/{mois:02d}.pdf", headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        print(y, "absent", r.status_code); continue
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(r.content); f.flush()
        txt = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True).stdout
    days = {}
    for line in txt.splitlines():
        m = re.match(r"^\s{0,4}(\d{1,2})\s+(.*)$", line)
        if not m or not 1 <= int(m.group(1)) <= 31:
            continue
        # vitesse moyenne (décimale) puis rafale (entier) puis direction : « 52.7    82      290 (W) »
        g = re.search(r"(\d+\.\d)\s+(\d{2,3})\s+(\d{3})\s*\(", m.group(2))
        if g:
            days[int(m.group(1))] = int(g.group(2))
    misc = re.search(r"MISC\.\s*-+>\s*(\d+)", txt)
    out[y] = {"jours": days, "max_publie": int(misc.group(1)) if misc else None}
    print(y, len(days), "jours", "max", max(days.values()) if days else None, "publié", out[y]["max_publie"])
Path(f"experiments/mont_washington/f6_{mois:02d}.json").write_text(json.dumps(out))
