"""Repère les montées de Budapest (≥ 40 cm en 72 h, lectures DanubeHIS de 6 h UTC) et prépare, pour chaque montée, l'extrait de la
page 4 (prévision à 4 jours) du rapport OVF émis 3 jours avant (`hydroinfo.hu/vt/vt<AAMMJJ>.pdf`), empilé dans une image à lire."""
import json, subprocess, sys
from datetime import datetime, timedelta
from pathlib import Path
import requests
from PIL import Image
data = json.load(open(sys.argv[1])); out_dir = Path(sys.argv[2]); out_dir.mkdir(parents=True, exist_ok=True)
jour = {k[:10]: v for k, v in data.items() if k[11:13] == "06"}
dates = sorted(jour)
montees, last = [], None
for i, d in enumerate(dates):
    d3 = (datetime.fromisoformat(d) + timedelta(days=3)).date().isoformat()
    if d3 in jour and jour[d3] - jour[d] >= 40 and (last is None or d > last):
        montees.append(d); last = (datetime.fromisoformat(d) + timedelta(days=7)).date().isoformat()
print("montées :", [(d, jour[d], jour.get((datetime.fromisoformat(d) + timedelta(days=k)).date().isoformat())) for d in montees for k in (4,)])
crops = []
for d in montees:
    emis = datetime.fromisoformat(d) - timedelta(days=1)
    f = out_dir / f"vt{emis:%y%m%d}.pdf"
    if not f.exists():
        r = requests.get(f"https://www.hydroinfo.hu/vt/vt{emis:%y%m%d}.pdf", headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        if r.status_code != 200: continue
        f.write_bytes(r.content)
    png = out_dir / f"p{emis:%y%m%d}"
    subprocess.run(["pdftoppm", "-f", "4", "-l", "4", "-r", "90", "-png", str(f), str(png)], check=False)
    got = sorted(out_dir.glob(f"p{emis:%y%m%d}*.png"))
    if got: crops.append(Image.open(got[0]).crop((55, 60, 430, 245)))
if crops:
    W = max(c.width for c in crops); H = sum(c.height for c in crops)
    img = Image.new("RGB", (W, H), "white"); y = 0
    for c in crops: img.paste(c, (0, y)); y += c.height
    img.save(out_dir / "pile.png"); print(len(crops), "extraits ->", out_dir / "pile.png")
for d in montees:
    print(d, [(k, jour.get((datetime.fromisoformat(d) + timedelta(days=k)).date().isoformat())) for k in range(0, 6)])
