"""Phrases chiffrées (force d'El Niño, seuils de l'indice) des discussions ENSO archivées du CPC (releves/discussions/)."""
import glob, html, re, pathlib
R = pathlib.Path(__file__).resolve().parent.parent / "releves" / "discussions"
ORDRE = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}
def cle(f):
    m = re.search(r"enso_disc_([a-z]{3})(\d{4})", f)
    return (int(m.group(2)), ORDRE[m.group(1)])
for f in sorted(glob.glob(str(R / "enso_disc_*.html")), key=cle):
    x = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", open(f, encoding="utf-8", errors="replace").read())))
    print("==", pathlib.Path(f).stem)
    for s in re.split(r"(?<=[.)])\s+(?=[A-Z])", x):
        if re.search(r"\d+\s?%", s) and re.search(r"strong|historic|exceed|\+\d\.\d|°C", s, re.I):
            print("   ", s.strip()[:420])
