"""scripts/robots_ok.py : les cas réels du 14/11/2026 (NASA GISS et BLS interdits aux robots)."""

from __future__ import annotations

import sys

from conftest import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import robots_ok  # noqa: E402

NASA = """User-agent: *
Disallow: /cgi-bin/
Disallow: /gistemp/graphs/
Disallow: /gistemp/station_data_v4/
Disallow: /gistemp/stdata/
Disallow: /gistemp/tabledata_v4/
Disallow: /gfx/
"""


def test_nasa_graph_txt_et_tabledata_interdits():
    """Le 14/11, `head` coupait le robots.txt avant la ligne `tabledata_v4` : les deux fichiers de GISTEMP sont interdits."""
    base = "https://data.giss.nasa.gov/gistemp/"
    assert robots_ok.verdict(NASA, base + "graphs/graph_data/Global_Mean_Estimates_based_on_Land_and_Ocean_Data/graph.txt") == "INTERDIT"
    assert robots_ok.verdict(NASA, base + "tabledata_v4/GLB.Ts+dSST.txt") == "INTERDIT"
    assert robots_ok.verdict(NASA, base + "news/") == "permis"


def test_site_entierement_interdit():
    assert robots_ok.verdict("User-agent: *\nDisallow: /\n", "https://api.bls.gov/publicAPI/v1/timeseries/data/X") == "INTERDIT"


def test_robots_absent_ou_illisible():
    assert robots_ok.verdict("", "https://exemple.org/donnees.csv") == "permis"
    assert robots_ok.verdict(None, "https://download.bls.gov/pub/") == "pas de robots.txt lisible"


# Chemins lus et trouvés interdits par leur robots.txt (règle n° 7). Toute nouvelle découverte s'ajoute ici.
INTERDITS_CONNUS = [
    "www.weather.gov.hk/cis/",                 # Daily Extract de Hong Kong (14/11/2026) : utiliser RYES du portail ouvert
    "data.giss.nasa.gov/gistemp/graphs",       # GISTEMP (14/11/2026)
    "data.giss.nasa.gov/gistemp/tabledata_v4",
    "api.bls.gov",                             # BLS : Disallow: / (14/11/2026)
    "api.db.nomics.world",                     # DBnomics : Disallow: / (14/11/2026)
    "boxofficemojo.com",                       # IMDb : collecte automatisée interdite (12/11/2026)
    "www.githubstatus.com/api/",               # GitHub status : /api/ interdit, /history.json permis (14/11/2026)
    "treasurydirect.gov/NP_WS/",               # TreasuryDirect : /NP_WS/ interdit (15/11/2026) : Fiscal Data « debt_to_penny »
    "api.weather.gov",                         # NWS : Disallow (17/11/2026) : CLI par forecast.weather.gov/product.php ou IEM
]


def test_production_never_reads_a_known_forbidden_path():
    trouves = []
    for f in (ROOT / "src" / "polymarket_agent").rglob("*.py"):
        for i, ligne in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            code = ligne.split("#", 1)[0]
            trouves += [f"{f.name}:{i} {x}" for x in INTERDITS_CONNUS if x in code]
    assert trouves == []


# 17/11/2026 (passage de 21 h) : 12 modules se présentaient comme un navigateur (« Mozilla/5.0 ») ou comme curl alors que leurs
# sites acceptent l'identité du labo (`HttpClient`, « polymarket-autonomous-lab ») ; Statistique Canada répond 403 à tous.
# Seule exception en attente d'Etienne : la page de la rougeole du CDC refuse l'identité du labo (403) et accepte « curl/8 ».
DEGUISEMENTS = ("Mozilla/", "curl/", "Chrome/", "Safari/", "python-requests")
DEGUISEMENTS_EN_ATTENTE = {"rougeole.py"}


def test_production_se_presente_sous_son_nom():
    trouves = []
    for f in (ROOT / "src" / "polymarket_agent").rglob("*.py"):
        if f.name in DEGUISEMENTS_EN_ATTENTE:
            continue
        for i, ligne in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            code = ligne.split("#", 1)[0]
            trouves += [f"{f.name}:{i} {x}" for x in DEGUISEMENTS if x in code]
    assert trouves == []
