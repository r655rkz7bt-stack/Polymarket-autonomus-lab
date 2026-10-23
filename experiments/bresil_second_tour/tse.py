"""Résultats officiels du TSE (Brésil), fichiers JSON publics de resultados.tse.jus.br.

Chemins vérifiés le 22/10/2026 depuis ce poste :
- configuration des élections : /oficial/comum/config/ele-c.json (codes : 2026 1er tour fédéral 6257,
  2e tour fédéral 6258 le 25/10/2026) ;
- résultat d'un État (ou « br », « zz » = étranger) :
  /oficial/ele2026/<code>/dados/<uf>/<uf>-c0001-e00<code>-u.json (c0001 = présidente) ;
- état d'avancement de chaque État (heure du dernier envoi) : /oficial/ele2026/<code>/dados/br/br-e00<code>-ab.json.
Les fichiers 2022 (/oficial/ele2022/544/dados-simplificados/...) ne sont plus servis (404).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cache_http import cached_json  # noqa: E402

BASE = "https://resultados.tse.jus.br/oficial"
UFS = ["ac", "al", "am", "ap", "ba", "ce", "df", "es", "go", "ma", "mg", "ms", "mt", "pa", "pb", "pe", "pi",
       "pr", "rj", "rn", "ro", "rr", "rs", "sc", "se", "sp", "to", "zz"]


def num(text) -> float:
    return float(str(text or "0").replace(",", "."))


def result_url(code: int, uf: str, cycle: str = "ele2026") -> str:
    return f"{BASE}/{cycle}/{code}/dados/{uf}/{uf}-c0001-e{code:06d}-u.json"


def summary(data: dict) -> dict:
    """Résumé d'un fichier « -u » : avancement, électeurs non comptés, voix par candidat."""
    cands = []
    for cargo in data.get("carg") or []:
        for agr in cargo.get("agr") or []:
            for par in agr.get("par") or []:
                for c in par.get("cand") or []:
                    cands.append({"nome": c.get("nmu"), "numero": c.get("n"), "votos": int(c.get("vap") or 0),
                                  "pct_validos": num(c.get("pvapn") or c.get("pvap"))})
    cands.sort(key=lambda c: -c["votos"])
    s, e, v = data.get("s") or {}, data.get("e") or {}, data.get("v") or {}
    return {"uf": data.get("cdabr"), "data": data.get("dt"), "hora": data.get("ht"),
            "pct_secoes": num(s.get("pstn") or s.get("pst")), "eleitores_nao_totalizados": int(e.get("esnt") or 0),
            "eleitorado": int(e.get("te") or 0), "comparecimento": int(e.get("c") or 0),
            "validos": int(v.get("vv") or 0), "candidatos": cands}


def fetch(code: int, uf: str, refresh: bool = False) -> dict:
    return summary(cached_json(result_url(code, uf), name=f"tse_{code}_{uf}", refresh=refresh))


if __name__ == "__main__":
    code = int(sys.argv[1]) if len(sys.argv) > 1 else 6257
    rows = {}
    for uf in UFS:
        r = fetch(code, uf)
        rows[uf] = r
        top = r["candidatos"][:3]
        print(uf, r["data"], r["hora"], f"{r['pct_secoes']:.2f}%", " | ".join(f"{c['nome']} {c['pct_validos']:.2f}" for c in top))
    out = Path(__file__).resolve().parent / f"tse_{code}_etats.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    print("écrit", out)
