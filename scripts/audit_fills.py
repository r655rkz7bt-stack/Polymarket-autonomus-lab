"""Audit indépendant des exécutions simulées (noyau protégé, décision d'Etienne du 15/10/2026).

Pourquoi : le code qui transmet une exécution au journal (main.py) est libre, donc modifiable par
le chercheur. Il pourrait, par erreur, inscrire un achat à un prix qui n'a jamais existé. Cet
audit vérifie chaque achat et chaque vente du journal principal et des fantômes contre une
source externe : l'historique PUBLIC des prix de Polymarket (CLOB, endpoint prices-history).

Où il tourne : dans un job séparé du workflow `cycle` (machine neuve), après le cycle, sans
aucun code libre : ce fichier n'importe que ledger.py (protégé) et la bibliothèque standard, et
il est lancé avec `python -I -S`. Le code libre du cycle ne s'exécute jamais sur cette machine.

Règle (volontairement large, pour ne signaler que de vraies impossibilités) :
- un ACHAT est une anomalie si son prix est inférieur de plus de 0,05 au plus bas prix observé
  dans les 30 minutes autour de l'exécution (acheter moins cher que tout le marché) ;
- une VENTE est une anomalie si son prix dépasse de plus de 0,05 le plus haut prix observé ;
- des frais négatifs ou un nombre de parts nul ou négatif sont toujours des anomalies ;
- sans prix observé (marché très peu actif), l'exécution est « non vérifiable », comptée à part.
Résultat dans la branche data : audit/etat.json. Nouvelle anomalie → code de sortie 1 → le job
échoue et GitHub envoie un e-mail à Etienne.

Usage : LEDGER_KEY=… python -I -S scripts/audit_fills.py --data _data
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))  # en dernier : rien ne peut masquer la bibliothèque standard

from polymarket_agent.ledger import Ledger, LedgerError, load_key_from_env  # noqa: E402

TOLERANCE = 0.05          # écart de prix toléré (granularité de l'historique, écart achat-vente)
WINDOW_SECONDS = 1800     # fenêtre autour de l'exécution
MIN_AGE_SECONDS = 600     # une exécution trop récente attend le passage suivant (historique en retard)
BUDGET = 60               # exécutions vérifiées au plus par passage
MAX_ANOMALIES_KEPT = 200
HISTORY_URL = "https://clob.polymarket.com/prices-history"


def fetch_prices(token_id: str, ts: int) -> list[float] | None:
    """Prix observés autour de `ts` ; None si l'historique est injoignable (réessayé plus tard)."""
    query = urllib.parse.urlencode({"market": token_id, "startTs": ts - WINDOW_SECONDS,
                                    "endTs": ts + WINDOW_SECONDS, "fidelity": 1})
    req = urllib.request.Request(f"{HISTORY_URL}?{query}",
                                 headers={"User-Agent": "polymarket-autonomous-lab-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310 - URL fixe en https
            raw = json.loads(resp.read().decode("utf-8"))
    except (OSError, ValueError):
        return None
    out = []
    for item in (raw or {}).get("history") or []:
        try:
            p = float(item["p"])
        except (KeyError, TypeError, ValueError):
            continue
        if 0 <= p <= 1:
            out.append(p)
    return out


def check_entry(entry: dict, prices: list[float] | None) -> tuple[str, str]:
    """(verdict, détail) ; verdict ∈ ok, anomalie, non vérifiable, réessayer."""
    data = entry.get("data") or {}
    try:
        price, shares, fee = float(data["price"]), float(data["shares"]), float(data.get("fee", 0))
    except (KeyError, TypeError, ValueError):
        return "anomalie", "écriture illisible (prix, parts ou frais)"
    if shares <= 0 or fee < 0:
        return "anomalie", f"parts {shares} ou frais {fee} impossibles"
    if prices is None:
        return "réessayer", "historique des prix injoignable"
    if not prices:
        return "non vérifiable", "aucun prix observé autour de l'exécution"
    lo, hi = min(prices), max(prices)
    if entry["type"] == "BUY" and price < lo - TOLERANCE:
        return "anomalie", f"achat à {price:.4f}, plus bas prix observé {lo:.4f}"
    if entry["type"] == "SELL" and price > hi + TOLERANCE:
        return "anomalie", f"vente à {price:.4f}, plus haut prix observé {hi:.4f}"
    return "ok", f"prix {price:.4f} dans [{lo:.4f} ; {hi:.4f}]"


def ledgers(data_dir: Path) -> dict[str, tuple[Path, Path]]:
    base = data_dir / "ledger"
    out = {"principal": (base / "ledger.jsonl", base / "BANKRUPT.lock")}
    for p in sorted((base / "fantome").glob("*.jsonl")):
        out[f"fantome:{p.stem}"] = (p, p.with_suffix(".BANKRUPT.lock"))
    return out


def audit(data_dir: Path, key: bytes, now: datetime, fetch=fetch_prices) -> tuple[dict, int]:
    """Met à jour l'état d'audit ; retourne (état, nombre de nouvelles anomalies)."""
    state_path = data_dir / "audit" / "etat.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}
    state.setdefault("dernier_seq", {})
    for k in ("verifiees", "non_verifiables"):
        state.setdefault(k, 0)
    state.setdefault("anomalies", [])
    new_anomalies, budget = 0, BUDGET
    for name, (path, lock) in ledgers(data_dir).items():
        if not path.exists():
            continue
        try:
            Ledger.open(path, key, lock)  # signatures et chaîne vérifiées par le noyau
        except LedgerError as exc:
            state["anomalies"].append({"portefeuille": name, "detail": f"journal illisible : {exc}"[:300],
                                       "date": now.isoformat(timespec="seconds")})
            new_anomalies += 1
            continue
        last = int(state["dernier_seq"].get(name, -1))
        for line in path.read_text(encoding="utf-8").splitlines():
            if budget <= 0:
                break
            entry = json.loads(line)
            if entry["seq"] <= last:
                continue
            if entry["type"] not in ("BUY", "SELL"):
                last = entry["seq"]
                continue
            ts = datetime.fromisoformat(entry["ts"])
            if (now - ts).total_seconds() < MIN_AGE_SECONDS:
                break  # trop récent : on reprendra ici au passage suivant
            verdict, detail = check_entry(entry, fetch(str(entry["data"].get("token_id")), int(ts.timestamp())))
            if verdict == "réessayer":
                break
            budget -= 1
            last = entry["seq"]
            if verdict == "ok":
                state["verifiees"] += 1
            elif verdict == "non vérifiable":
                state["non_verifiables"] += 1
            else:
                new_anomalies += 1
                state["anomalies"].append({"portefeuille": name, "seq": entry["seq"], "type": entry["type"],
                                           "date": entry["ts"][:19], "detail": detail,
                                           "op_id": entry["data"].get("op_id")})
        state["dernier_seq"][name] = last
    state["anomalies"] = state["anomalies"][-MAX_ANOMALIES_KEPT:]
    state["derniere_execution"] = now.isoformat(timespec="seconds")
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    return state, new_anomalies


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="_data", help="copie de la branche data")
    args = parser.parse_args()
    state, new = audit(Path(args.data), load_key_from_env(), datetime.now(timezone.utc))
    print(f"Audit : {state['verifiees']} exécutions vérifiées, {state['non_verifiables']} non vérifiables, "
          f"{len(state['anomalies'])} anomalie(s) au total, {new} nouvelle(s).")
    for a in state["anomalies"][-new:] if new else []:
        print(f"ANOMALIE {a.get('portefeuille')} n°{a.get('seq')} : {a.get('detail')}")
    return 1 if new else 0


if __name__ == "__main__":
    raise SystemExit(main())
