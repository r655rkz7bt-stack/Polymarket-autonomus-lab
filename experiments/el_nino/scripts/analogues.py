"""Années d'El Niño (RONI ASO ≥ 1,0) : hausse du pic (SON, OND, NDJ, DJF) au-dessus d'ASO, et OISST d'octobre → novembre."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lien import roni, hebdo
Ro, H = roni(), hebdo()
print("année ASO JAS pic hausse | OISST oct nov déc jan")
for y in range(1950, 2026):
    aso = Ro.get((y, 8))
    if aso is None or aso < 1.0:
        continue
    suite = [Ro.get((y, 9)), Ro.get((y, 10)), Ro.get((y, 11)), Ro.get((y + 1, 0))]
    pic = max(v for v in suite + [aso] if v is not None)
    o = [H.get((y, 10)), H.get((y, 11)), H.get((y, 12)), H.get((y + 1, 1))]
    print(y, aso, Ro.get((y, 7)), pic, round(pic - aso, 2), "|", " ".join("—" if v is None else f"{v:.2f}" for v in o))
