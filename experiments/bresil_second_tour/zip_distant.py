"""Lire UN fichier d'une grande archive zip publique du TSE sans tout télécharger (requêtes HTTP Range).

Les archives « votação nominal por município e zona » du portail dadosabertos.tse.jus.br pèsent
400-600 Mo (tous les postes) ; seul le fichier de la présidence nous sert. Le serveur cdn.tse.jus.br
accepte les requêtes partielles (réponse 206, vérifié le 22/10/2026) : on lit le répertoire de
l'archive puis le seul membre voulu. Lecture publique normale, aucune protection contournée.
"""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import requests


class RangeFile(io.RawIOBase):
    def __init__(self, url: str, timeout: float = 60):
        self.url, self.timeout, self.pos = url, timeout, 0
        head = requests.head(url, timeout=timeout)
        head.raise_for_status()
        self.size = int(head.headers["content-length"])
        self.session = requests.Session()

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=io.SEEK_SET):
        self.pos = {io.SEEK_SET: 0, io.SEEK_CUR: self.pos, io.SEEK_END: self.size}[whence] + offset
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        if n == 0 or self.pos >= self.size:
            return b""
        end = min(self.size, self.pos + n) - 1
        r = self.session.get(self.url, headers={"Range": f"bytes={self.pos}-{end}"}, timeout=self.timeout)
        if r.status_code != 206:
            raise IOError(f"HTTP {r.status_code} pour une lecture partielle")
        self.pos += len(r.content)
        return r.content

    def readinto(self, b):
        data = self.read(len(b))
        b[: len(data)] = data
        return len(data)


def members(url: str) -> list[tuple[str, int]]:
    with zipfile.ZipFile(io.BufferedReader(RangeFile(url), buffer_size=1 << 20)) as zf:
        return [(i.filename, i.compress_size) for i in zf.infolist()]


def extract(url: str, name: str, out: Path) -> Path:
    with zipfile.ZipFile(io.BufferedReader(RangeFile(url), buffer_size=1 << 22)) as zf:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(zf.read(name))
    return out


if __name__ == "__main__":
    for name, size in members(sys.argv[1]):
        print(size, name)
