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


def stream_seed(*parts: object, master: int = MASTER_SEED) -> int:
    """A collision-free seed for a named simulation stream.

    The post-freeze calibration tools originally derived their seeds by adding
    len(label) to the master seed. External review found what that costs:
    len("P1") == len("P2"), so both panels' size studies ran on one stream, and
    len("poisson") == len("ar1_nb2"), so the two arms a comparison rested on
    were coupled while the pair the conclusion actually used was not. Hashing
    the labels makes the stream a function of the name rather than its length.

    Deliberately separate from cell_seed: that one is frozen sampling machinery
    and its draws are part of the record. This is for post-freeze simulation
    only, and nothing preregistered reads it.
    """
    key = "|".join([str(master), "stream", *(str(p) for p in parts)])
    return int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:16], 16) % (2 ** 63)
