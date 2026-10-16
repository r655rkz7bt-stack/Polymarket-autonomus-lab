"""Test sport Kalshi / Polymarket : outils communs (cache disque, ligues, noms d'équipes)."""
import gzip, hashlib, json, re, sys, threading, unicodedata
from datetime import datetime, timezone
from pathlib import Path

KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"

# Ligue -> (tag Gamma de Polymarket, série Kalshi « match », match à 3 issues ?)
LEAGUES = {
    "mlb": (100381, "KXMLBGAME", False), "nfl": (450, "KXNFLGAME", False), "nhl": (899, "KXNHLGAME", False),
    "nba": (745, "KXNBAGAME", False), "wnba": (100254, "KXWNBAGAME", False), "cfb": (100351, "KXNCAAFGAME", False),
    "epl": (306, "KXEPLGAME", True), "ucl": (100977, "KXUCLGAME", True), "uel": (101787, "KXUELGAME", True),
    "lal": (780, "KXLALIGAGAME", True), "bun": (1494, "KXBUNDESLIGAGAME", True), "sea": (101962, "KXSERIEAGAME", True),
    "fl1": (102070, "KXLIGUE1GAME", True), "mls": (100100, "KXMLSGAME", True),
}

_local = threading.local()


def http(src):
    """Un client HTTP par fil d'exécution (le client du dépôt : poli, délais progressifs)."""
    if not hasattr(_local, "c"):
        sys.path.insert(0, src)
        from polymarket_agent.http_client import HttpClient
        _local.c = HttpClient(timeout=40, max_retries=6, backoff=2.0, min_interval=0.3, user_agent="polymarket-lab-backtest")
    return _local.c


def cached_get(workdir, src, url, params):
    """GET JSON gardé sur disque (gzip) : relancer le script ne retélécharge rien."""
    key = hashlib.sha256(json.dumps([url, sorted(params.items())]).encode()).hexdigest()[:24]
    path = Path(workdir) / "cache" / key[:2] / f"{key}.json.gz"
    if path.exists():
        return json.loads(gzip.decompress(path.read_bytes()))
    from polymarket_agent.http_client import SourceUnavailable
    try:
        data = http(src).get_json(url, params=params)
    except SourceUnavailable as exc:
        print("échec", url[:90], exc)
        return None  # pas mis en cache : réessayé la prochaine fois
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(data).encode()))
    return data


def ts(text):
    if not text:
        return None
    t = str(text).replace("Z", "+00:00").replace(" ", "T")
    if re.search(r"[+-]\d\d$", t):
        t += ":00"
    return int(datetime.fromisoformat(t).timestamp())


def day(t):
    return datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d")


STOP = {"fc", "afc", "cf", "sc", "ac", "ssc", "as", "us", "cd", "ud", "rc", "rcd", "sd", "vfb", "vfl", "tsg", "fsv",
        "sv", "bv", "1", "de", "the", "club", "calcio", "football", "and", "&", "1899", "1904", "1909", "04", "05",
        "sk", "sl", "fk", "if", "bk", "nk", "hsc", "ogc", "losc", "stade", "olympique"}
ALIAS = {"st": "state", "intl": "international", "utd": "united", "wolves": "wolverhampton", "spurs": "tottenham",
         "man": "manchester", "inter": "internazionale", "psg": "paris", "nottm": "nottingham", "atl": "atletico",
         "munchen": "munich", "koln": "cologne", "prague": "praha", "rb": "red"}


def norm(name):
    """Nom d'équipe -> liste de mots simples (sans accents, ponctuation ni « FC »)."""
    s = str(name).lower().translate(str.maketrans({"ø": "o", "æ": "ae", "ß": "ss", "ł": "l", "đ": "d", "'": "", "`": "", "’": ""}))
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().replace("oe", "o")
    s = re.sub(r"\(([^)]*)\)", r" \1 ", s)
    s = re.sub(r"[^a-z0-9& ]+", " ", s.replace(".", " "))
    words = [ALIAS.get(w, w) for w in s.split()]
    return [w for w in words if w not in STOP]


def same_team(kname, pname):
    """Niveau de ressemblance de deux noms d'équipe (0 = différents, 3 = identiques).
    3 : mêmes mots ; 2 : les mots de l'un sont des débuts des premiers mots de l'autre (« New York Y » ~
    « New York Yankees », « Tampa Bay » ~ « Tampa Bay Rays ») ; 1 : idem mais n'importe où, à la suite
    (« Frankfurt » ~ « Eintracht Frankfurt »). On ne compare qu'aux DEUX équipes d'un match qui commence
    à la même heure, et on garde le niveau le plus strict qui trouve quelque chose."""
    a, b = norm(kname), norm(pname)
    if not a or not b:
        return 0
    if a == b:
        return 3
    def pref(x, y, anywhere):
        starts = range(len(y) - len(x) + 1) if anywhere else range(min(1, len(y) - len(x) + 1))
        return any(all(y[k + i].startswith(x[i]) for i in range(len(x))) for k in starts)
    if pref(a, b, False) or pref(b, a, False):
        return 2
    return 1 if pref(a, b, True) or pref(b, a, True) else 0
