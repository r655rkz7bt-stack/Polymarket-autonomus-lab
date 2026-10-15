"""Laboratoire de stratégies (niveau 1 : adaptation des paramètres dans leurs bornes).

Pour chaque stratégie rejouable sur l'historique (naive_favorite, calibration, reversion) :
  1. une grille de variantes de paramètres, à l'intérieur des bornes de strategies.yaml ;
  2. chaque variante est évaluée en walk-forward (4 plis, l'ajustement ne voit que le passé) ;
  3. la meilleure n'est recommandée que si son score PÉNALISÉ pour les essais multiples dépasse
     la configuration actuelle, avec une majorité de plis positifs et aucune faillite.
Rapport : experiments/lab_<date>.md (+ .json). `--apply` écrit les recommandations dans
config/strategies.yaml (chaque changement est documenté dans le rapport).

LIMITE : le prix historique n'est pas un prix exécutable (voir experiments/BILAN_2026-10-14.md).
Le laboratoire propose des hypothèses ; seule l'arène, sur de vrais carnets, tranche.

Usage : python scripts/lab.py [--apply] [--folds 4]
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import yaml

from _common import ROOT

from polymarket_agent import calibration
from polymarket_agent.backtest import Decision, build_samples, deflated_score, walk_forward
from polymarket_agent.history import load_dataset
from polymarket_agent.lab_rules import HALF_SPREAD, MIN_CHANGES, fit_reversion, make_calibrated, make_reversion
from polymarket_agent.safety_controller import RiskLimits

STRATEGIES_FILE = ROOT / "config" / "strategies.yaml"
# Uniquement les paramètres réellement utilisés par chaque règle (sinon des variantes identiques
# gonfleraient artificiellement la pénalité des essais multiples).
GRIDS = {
    "naive_favorite": {"kelly_fraction": [0.25, 0.5, 1.0], "bias": [0.02, 0.05]},
    "calibration": {"min_net_edge": [0.0, 0.02, 0.05], "kelly_fraction": [0.25, 0.5, 1.0]},
    "reversion": {"min_net_edge": [0.0, 0.02, 0.05], "kelly_fraction": [0.25, 0.5, 1.0]},
}


def make_naive(params):
    bias, unc = float(params["bias"]), float(params["uncertainty"])
    lo_ask, hi_ask = float(params["min_ask"]), float(params["max_ask"])

    def rule(s):
        if s.changes_24h < MIN_CHANGES:
            return None
        fav = 0 if s.price_yes >= 0.5 else 1
        f = s.price_yes if fav == 0 else 1 - s.price_yes
        if not lo_ask <= f + HALF_SPREAD <= hi_ask:
            return None
        est = min(f + bias, 0.99)
        return Decision(fav, est - unc, est, min(est + unc, 0.995))
    return rule


def setups(config: dict) -> dict:
    """Pour chaque stratégie : (ajustement, fabrique de règle selon les paramètres)."""
    def params(name):
        return {k: v["value"] for k, v in config[name]["params"].items()}
    return {
        "naive_favorite": (lambda train, outs: None, lambda model, p: make_naive(p), params("naive_favorite")),
        "calibration": (lambda train, outs: calibration.fit(train, outs, min_changes=MIN_CHANGES),
                        lambda model, p: make_calibrated(model, min_events=int(p["min_events"]),
                                                         floor=float(p["min_net_edge"])),
                        params("calibration")),
        "reversion": (fit_reversion,
                      lambda model, p: make_reversion(model, min_events=int(p["min_events"]),
                                                      floor=float(p["min_net_edge"])),
                      params("reversion")),
    }


def in_bounds(config, name, key, value):
    spec = config[name]["params"].get(key)
    return spec is not None and spec["min"] <= value <= spec["max"]


def set_param(text: str, strategy: str, key: str, value) -> str:
    """Remplace `value:` d'un paramètre dans le bloc d'une stratégie (commentaires conservés)."""
    start = re.search(rf"(?m)^{re.escape(strategy)}:\s*$", text)
    if not start:
        raise KeyError(strategy)
    end = re.search(r"(?m)^\S", text[start.end():])
    block_end = start.end() + (end.start() if end else len(text) - start.end())
    block = text[start.end():block_end]
    new_block, n = re.subn(rf"(?m)^(\s+{re.escape(key)}:\s*\{{value:\s*)[^,]+", rf"\g<1>{value}", block)
    if n != 1:
        raise KeyError(f"{strategy}.{key}")
    return text[:start.end()] + new_block + text[block_end:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="écrit les recommandations dans strategies.yaml")
    parser.add_argument("--folds", type=int, default=4)
    parser.add_argument("--data", default=str(ROOT / "data" / "history"))
    args = parser.parse_args()
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    config = yaml.safe_load(STRATEGIES_FILE.read_text(encoding="utf-8"))
    samples, outcomes = build_samples(load_dataset(Path(args.data)))
    now = datetime.now(timezone.utc)
    lines = [f"# Laboratoire — {now:%Y-%m-%d %H:%M} UTC", "",
             f"Walk-forward {args.folds} plis sur {len(samples)} marchés. Score = croissance log moyenne par pli, "
             "pénalisée pour le nombre de variantes testées. **Hypothèses seulement : l'arène tranche.**", ""]
    recommendations = {}
    for name, (fit, make_rule, current) in setups(config).items():
        cache = {}

        def cached_fit(train, outs, _fit=fit, _cache=cache):
            key = len(train)
            if key not in _cache:
                _cache[key] = _fit(train, outs)
            return _cache[key]

        variants = []
        grid = GRIDS[name]
        keys = [k for k in grid if k in current]
        for combo in itertools.product(*(grid[k] for k in keys)):
            p = dict(current, **dict(zip(keys, combo)))
            if not all(in_bounds(config, name, k, v) for k, v in zip(keys, combo)):
                continue
            variants.append(p)
        if current not in variants:
            variants.insert(0, dict(current))
        results = []
        for p in variants:
            res = walk_forward(samples, outcomes, cached_fit, lambda m, p=p: make_rule(m, p), limits,
                               n_folds=args.folds, kelly_fraction=Decimal(str(p.get("kelly_fraction", 1))),
                               name=name)
            results.append((p, res))
        n = len(results)
        lines += [f"## {name} ({n} variantes)", "",
                  "| variante | croissance log moy. | écart-type | plis > 0 | opérations | faillite | score pénalisé |",
                  "|---|---|---|---|---|---|---|"]
        cur_res = next(r for p, r in results if p == current)
        best_p, best_r, best_score = None, None, float("-inf")
        for p, r in results:
            score = deflated_score(r["croissance_log_moyenne"], r["ecart_type"], r["n_plis"], n)
            label = ", ".join(f"{k}={p[k]}" for k in keys) + (" (actuelle)" if p == current else "")
            lines.append(f"| {label} | {r['croissance_log_moyenne']:+.4f} | {r['ecart_type']:.4f} | "
                         f"{r['plis_positifs']}/{r['n_plis']} | {r['operations']} | {r['faillite']} | {score:+.4f} |")
            if score > best_score and not r["faillite"]:
                best_p, best_r, best_score = p, r, score
        accept = (best_p is not None and best_p != current
                  and best_score > cur_res["croissance_log_moyenne"]
                  and best_r["plis_positifs"] >= 0.75 * best_r["n_plis"])
        if accept:
            change = {k: best_p[k] for k in keys if best_p[k] != current[k]}
            recommendations[name] = change
            lines += ["", f"**Recommandation** : {change} (score pénalisé {best_score:+.4f} > actuel "
                          f"{cur_res['croissance_log_moyenne']:+.4f})", ""]
        else:
            lines += ["", "**Recommandation** : garder les paramètres actuels (aucune variante ne bat la "
                          "configuration actuelle de façon robuste).", ""]
    out = ROOT / "experiments" / f"lab_{now:%Y%m%d_%H%M}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(recommendations, indent=1), encoding="utf-8")
    if args.apply and recommendations:
        text = STRATEGIES_FILE.read_text(encoding="utf-8")
        for name, change in recommendations.items():
            for key, value in change.items():
                text = set_param(text, name, key, value)
        STRATEGIES_FILE.write_text(text, encoding="utf-8")
        print(f"Appliqué dans {STRATEGIES_FILE.relative_to(ROOT)} : {recommendations}")
    print("\n".join(lines))
    print(f"\nRapport : {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
