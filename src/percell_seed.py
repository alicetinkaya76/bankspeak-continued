"""Stable per-cell RNG (PREREG v0.3 App. B.7). Round-4 precondition 3:
adding/removing/reordering any other stratum can never change a cell's draw."""
from __future__ import annotations
import hashlib, random

MASTER_SEED = 20260806

def cell_seed(institution: str, genre: str, year: int | str,
              master: int = MASTER_SEED) -> int:
    key = f"{master}|{institution}|{genre}|{year}".encode("utf-8")
    return int(hashlib.sha256(key).hexdigest()[:16], 16)

def cell_rng(institution: str, genre: str, year: int | str,
             master: int = MASTER_SEED) -> random.Random:
    return random.Random(cell_seed(institution, genre, year, master))
