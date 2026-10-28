"""Contrôle « guard » : refuse toute pull request qui touche le noyau protégé.

Exécuté par .github/workflows/guard.yml avec le code de la branche `main` (jamais celui de la
pull request). Deux vérifications :

1. Chemins : PROTECTED_PATHS.txt (lu depuis `main`) contre la liste des fichiers modifiés (un
   par ligne sur l'entrée standard, anciens noms des fichiers renommés compris).
     python scripts/guard_check.py PROTECTED_PATHS.txt < fichiers_modifiés.txt
2. Workflows libres (`.github/workflows/labo-*.yml`) : leur contenu (lu via l'API, jamais
   exécuté) ne doit donner accès à aucun secret, aucun droit d'écriture, et ne pas pouvoir
   imiter les contrôles exigés `guard` et `tests`.
     python scripts/guard_check.py --workflow fichier.yml [...]

Code de sortie : 0 accepté, 1 refusé (la pull request est bloquée par le ruleset de `main`).
"""

from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path, PurePosixPath

REQUIRED_CHECKS = ("guard", "tests")

# Ce qu'un workflow libre ne peut jamais contenir. Liste volontairement large : en cas de doute,
# le refus est la bonne réponse (le chercheur peut toujours écrire une proposition).
FORBIDDEN_IN_FREE_WORKFLOWS = [
    (r"secrets", "accès aux secrets"),
    (r"\benvironment\b", "accès à un environnement (et à ses secrets)"),
    (r":\s*write\b|write-all", "droit d'écriture"),
    (r"id-token", "jeton d'identité OIDC"),
    (r"pull_request", "déclenchement sur une pull request"),
    (r"^\s*push\s*:|^\s*-\s*push\s*$|\[\s*[^\]]*\bpush\b", "déclenchement sur un push"),
    (r"\b(merge_group|check_run|check_suite|status|workflow_run)\b", "déclenchement sur un contrôle"),
]


def load_patterns(text: str) -> list[str]:
    """Une ligne = un chemin exact, un dossier terminé par « / » ou un motif (* ?).
    « !motif » = exception (chemin libre malgré une règle plus large). « # » = commentaire."""
    patterns = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            patterns.append(line)
    if not [p for p in patterns if not p.startswith("!")]:
        raise ValueError("PROTECTED_PATHS.txt est vide : refus par prudence")
    return patterns


def normalize(path: str) -> str:
    """Forme canonique : séparateurs « / », sans « ./ » ni « .. », comparée sans la casse
    (un « claude.md » ne doit pas contourner « CLAUDE.md » sur un système insensible à la casse)."""
    parts = []
    for part in PurePosixPath(path.strip().replace("\\", "/")).parts:
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts).casefold()


def _matches(pattern: str, path: str) -> bool:
    q = normalize(pattern)
    if pattern.endswith("/"):
        return path == q or path.startswith(q + "/")
    if any(c in pattern for c in "*?["):
        return fnmatch.fnmatchcase(path, q)
    return path == q


def is_protected(patterns: list[str], path: str) -> bool:
    p = normalize(path)
    if not p:
        return False
    if any(_matches(pat[1:], p) for pat in patterns if pat.startswith("!")):
        return False
    return any(_matches(pat, p) for pat in patterns if not pat.startswith("!"))


def violations(patterns: list[str], changed: list[str]) -> list[str]:
    return sorted({path.strip() for path in changed if is_protected(patterns, path)})


def workflow_violations(text: str) -> list[str]:
    """Raisons de refuser un workflow libre (vide = accepté)."""
    reasons = []
    for regex, label in FORBIDDEN_IN_FREE_WORKFLOWS:
        if re.search(regex, text, re.IGNORECASE | re.MULTILINE):
            reasons.append(label)
    if not re.search(r"^permissions\s*:", text, re.MULTILINE):
        reasons.append("bloc « permissions: » absent au premier niveau (droits par défaut interdits)")
    names = re.findall(r"^\s*(?:-\s*)?name\s*:\s*(.+?)\s*$", text, re.MULTILINE)
    job_ids = re.findall(r"^  ([\w-]+)\s*:", text, re.MULTILINE)
    for value in names + job_ids:
        bare = value.strip("'\" ").casefold()
        if "${{" in value:
            reasons.append(f"nom calculé « {value} » (il pourrait imiter un contrôle exigé)")
        elif bare in REQUIRED_CHECKS:
            reasons.append(f"nom « {value} » réservé au contrôle exigé du même nom")
    return sorted(set(reasons))


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--workflow":
        refused = False
        for name in sys.argv[2:]:
            reasons = workflow_violations(Path(name).read_text(encoding="utf-8"))
            if reasons:
                refused = True
                print(f"BLOQUÉ : workflow libre {Path(name).name} refusé :")
                for reason in reasons:
                    print(f"  - {reason}")
        if not refused:
            print(f"OK : {len(sys.argv) - 2} workflow(s) libre(s) sans secret, sans écriture, sans imitation.")
        return 1 if refused else 0
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    patterns = load_patterns(Path(sys.argv[1]).read_text(encoding="utf-8"))
    changed = [line for line in sys.stdin.read().splitlines() if line.strip()]
    hits = violations(patterns, changed)
    if hits:
        print("BLOQUÉ : cette pull request modifie le noyau protégé (seul Etienne peut le changer) :")
        for path in hits:
            print(f"  - {path}")
        print("Si ce changement est nécessaire : écrire une proposition dans proposals/ et l'expliquer à Etienne.")
        return 1
    print(f"OK : {len(changed)} fichier(s) modifié(s), aucun fichier protégé.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
