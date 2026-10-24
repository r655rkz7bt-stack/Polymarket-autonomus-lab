"""Outils communs : catalogue USGS, événements, fenêtres, règlement relu."""
import gzip, json, re, bisect
from datetime import datetime, timezone, timedelta
R = "experiments/seismes/"
CAT = json.load(gzip.open(R + "releves/usgs_m5.json.gz", "rt"))  # [id, t, mag, maj, type, statut]
TIMES = [c[1] for c in CAT]
EV = {e["id"]: e for e in json.load(gzip.open(R + "releves/evenements.json.gz", "rt"))}
MOIS = {m: i + 1 for i, m in enumerate("January February March April May June July August September October November December".split())}

def ts(s): return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())

def count(a, b, mag):  # séismes M >= mag, a <= t < b
    i, j = bisect.bisect_left(TIMES, a), bisect.bisect_left(TIMES, b)
    return sum(1 for c in CAT[i:j] if c[2] is not None and round(c[2] + 1e-9, 1) >= mag)

def maxmag(a, b):
    i, j = bisect.bisect_left(TIMES, a), bisect.bisect_left(TIMES, b)
    v = [c[2] for c in CAT[i:j] if c[2] is not None]
    return max(v) if v else 0.0

def weekly(e, tz=None):
    """(magnitude, début, fin) en secondes UTC, d'après le titre ; jours entiers à l'heure de l'Est (UTC-4 d'avril à octobre, UTC-5 sinon)."""
    m = re.search(r"How many ([\d.]+) or above earthquakes.*?(\w+) (\d+) - (?:(\w+) )?(\d+)\?", e["title"])
    if not m or "by " in e["title"]: return None
    mag = float(m.group(1)); end_ref = ts(e["end"]); y = datetime.fromtimestamp(end_ref, timezone.utc).year
    mo1 = MOIS[m.group(2)]; d1 = int(m.group(3)); mo2 = MOIS[m.group(4)] if m.group(4) else mo1; d2 = int(m.group(5))
    y1 = y - 1 if mo1 > mo2 else y
    def utc(yy, mo, d, h=0):
        off = 4 if 3 < mo < 11 else 5
        return int((datetime(yy, mo, d, tzinfo=timezone.utc) + timedelta(hours=h + off)).timestamp())
    if tz == "utc":
        return mag, int(datetime(y1, mo1, d1, tzinfo=timezone.utc).timestamp()), int(datetime(y, mo2, d2, tzinfo=timezone.utc).timestamp()) + 86400
    return mag, utc(y1, mo1, d1), utc(y, mo2, d2, 24)

def bucket_of(m):
    q = m["q"]; g = m["git"]
    if q.startswith("Will there be more than"): return (int(re.search(r"more than (\d+)", q).group(1)) + 1, 10**6)
    mm = re.search(r"(\d+) or fewer", q) or re.search(r"≤\s*(\d+)", q)
    if mm: return (0, int(mm.group(1)))
    mm = re.search(r"(\d+) earthquake", q)
    if mm: return (int(mm.group(1)), int(mm.group(1)))
    return None

def winner(e):
    for m in e["markets"]:
        p = json.loads(m["prices"]) if m["prices"] else None
        if p and float(p[0]) > 0.99: return m
    return None
