"""Contrôle « guard » : refuse toute pull request qui modifie un fichier protégé.

Exécuté par .github/workflows/guard.yml avec le code de la branche `main` (jamais celui de la
pull request). Lit PROTECTED_PATHS.txt depuis `main` et la liste des fichiers modifiés (un par
ligne sur l'entrée standard, anciens noms des fichiers renommés compris).

Usage : python scripts/guard_check.py PROTECTED_PATHS.txt < fichiers_modifiés.txt
Code de sortie : 0 aucun fichier protégé touché, 1 sinon (la pull request est bloquée).
"""

from __future__ import annotations

import sys
from pathlib import Path, PurePosixPath


def load_patterns(text: str) -> list[str]:
    """Une ligne = un chemin exact, ou un dossier terminé par « / ». « # » = commentaire."""
    patterns = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            patterns.append(line)
    if not patterns:
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


def violations(patterns: list[str], changed: list[str]) -> list[str]:
    hits = []
    for path in changed:
        p = normalize(path)
        if not p:
            continue
        for pattern in patterns:
            q = normalize(pattern)
            if (pattern.endswith("/") and (p == q or p.startswith(q + "/"))) or p == q:
                hits.append(path.strip())
                break
    return sorted(set(hits))


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    patterns = load_patterns(Path(sys.argv[1]).read_text(encoding="utf-8"))
    changed = [line for line in sys.stdin.read().splitlines() if line.strip()]
    hits = violations(patterns, changed)
    if hits:
        print("BLOQUÉ : cette pull request modifie des fichiers protégés (seul Etienne peut les changer) :")
        for path in hits:
            print(f"  - {path}")
        print("Si ce changement est nécessaire : écrire une proposition dans proposals/ et l'expliquer à Etienne.")
        return 1
    print(f"OK : {len(changed)} fichier(s) modifié(s), aucun fichier protégé.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
