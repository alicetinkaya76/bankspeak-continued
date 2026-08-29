#!/usr/bin/env python3
"""Enumerate the exact PASS-P p-value at every distinct block origin.

PASS-P partitions 27 common years into nine non-overlapping three-year blocks, so
the sign support is exactly 2^9 = 512 and the p-value can be computed by
enumeration rather than sampled. The partition has an origin, and the origin was
frozen arbitrarily, so the honest question is what the p-value does across the
origins that were equally available.

There are exactly THREE distinct partitions -- offsets 0, 1, 2, after which the
blocking repeats -- and the manuscript reported one of them, described it as a
two-year shift, and omitted the third. This computes all six cells.

Written after an external review found the error. The number itself was right;
the sentence attached to it named the wrong offset, and the case that was left
out moves the other panel in the opposite direction.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bootstrap_engine import build_design, _fit, _pair_index   # noqa: E402

CELLS = {"P1": ROOT / "data" / "analysis" / "panels" / "cells_P1.csv",
         "P2": ROOT / "data" / "analysis" / "panels" / "cells_P2.csv"}
OUT = ROOT / "data" / "analysis" / "block_origin_enumeration.json"
BLOCK_LEN = 3


def year_scores(cells: pd.DataFrame) -> tuple[np.ndarray, int]:
    """The per-year restricted score, exactly as wild_score_p computes it.

    Poisson working variance, alpha = 0: the confirmatory run's PASS-P is the
    Poisson QML arm, and the NB2 arm is a separate reported variant.
    """
    df, X, names, y, off, years = build_design(cells, "WB")
    pair, T = _pair_index(df, years, "WB")
    j = names.index("WB_post")
    Xr = np.delete(X, j, axis=1)
    mu0 = np.asarray(_fit(y, Xr, off, sm.families.Poisson()).fittedvalues)
    xj = X[:, j]
    coef, *_ = np.linalg.lstsq(Xr.T @ (Xr * mu0[:, None]), Xr.T @ (mu0 * xj),
                               rcond=None)
    s = (xj - Xr @ coef) * (y - mu0)
    return np.array([s[pair[k]].sum() for k in range(T)]), T


def exact_p(S_year: np.ndarray, offset: int) -> tuple[int, int]:
    """Hits and support size, by enumerating every sign pattern.

    The origin shift rotates the year vector before blocking, so the blocks stay
    non-overlapping and exhaust the 27 years; no year is dropped or reused.
    """
    S = np.roll(S_year, -offset)
    nb = int(np.ceil(len(S) / BLOCK_LEN))
    blocks = np.array([S[b * BLOCK_LEN:(b + 1) * BLOCK_LEN].sum() for b in range(nb)])
    denom = float(np.sqrt((blocks ** 2).sum()))
    t_obs = abs(float(blocks.sum()) / denom)
    hits = sum(1 for eta in itertools.product([-1.0, 1.0], repeat=nb)
               if abs(float(np.dot(eta, blocks)) / denom) >= t_obs - 1e-12)
    return hits, 2 ** nb


def main() -> int:
    res: dict = {"block_len": BLOCK_LEN, "frozen_offset": 0, "panels": {}}
    for panel, path in CELLS.items():
        if not path.exists():
            raise SystemExit(f"[blocks] needs {path.relative_to(ROOT)}")
        cells = pd.read_csv(path)[["institution", "year", "count", "tokens"]]
        S, T = year_scores(cells)
        if T % BLOCK_LEN:
            raise SystemExit(f"[blocks] {T} years is not a multiple of {BLOCK_LEN}; "
                             "the offsets would not be a clean rotation")
        res["n_years"] = T
        res["panels"][panel] = {}
        for k in range(BLOCK_LEN):
            hits, support = exact_p(S, k)
            res["panels"][panel][k] = {"hits": hits, "support": support,
                                       "p": hits / support}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")

    print(f"{'offset':>7s} | " + " | ".join(f"{p:^18s}" for p in CELLS))
    print("-" * (9 + 21 * len(CELLS)))
    for k in range(BLOCK_LEN):
        row = " | ".join(
            f"{res['panels'][p][k]['hits']:4d}/512 = {res['panels'][p][k]['p']:.4f}"
            for p in CELLS)
        tag = "  <- frozen" if k == 0 else ""
        print(f"{k:>7d} | {row}{tag}")
    print(f"\n[blocks] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
