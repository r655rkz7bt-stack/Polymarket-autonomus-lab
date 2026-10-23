"""Comptes de l'inventaire par type, détroit, clos / ouvert (tableau d'experiments/detroits.md)."""
import collections
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import commun as c  # noqa: E402


def famille(t):
    t = t.lower()
    if "how many ships transit" in t:
        return "hebdomadaire"
    if t.startswith("avg. #"):
        return "moyenne à une date"
    if "on any day" in t:
        return "un jour ≥ N"
    if "return" in t and "normal" in t:
        return "returns to normal"
    if "0 ships" in t:
        return "0 ships"
    if "effectively closed" in t:
        return "effectively closed"
    return "autre"


cnt = collections.Counter((famille(e["titre"]), (e["detroit"] or "?")[:13], "clos" if e["clos"] else "ouvert") for e in c.charge_inventaire())
for k, n in sorted(cnt.items()):
    print(k, n)
print("total", sum(cnt.values()))
