#!/usr/bin/env python3
"""Enumerate the exact PASS-P p-value at every distinct block origin.

PASS-P partitions 27 common years into nine non-overlapping three-year blocks, so
the sign support is exactly 2^9 = 512 and the p-value can be computed by
enumeration rather than sampled. The partition has an origin, and the origin was
frozen arbitrarily, so the honest question is what the p-value does across the
origins that were equally available.

There are three offsets -- 0, 1, 2, after which the blocking repeats -- and the
manuscript reported one of them, described it as a two-year shift, and omitted
the third. This computes all six cells.

Written after an external review found the error. The number itself was right;
the sentence attached to it named the wrong offset, and the case that was left
out moves the other panel in the opposite direction.

HOW THE ORIGIN IS SHIFTED, AND WHY THAT CHANGED. The first version of this tool
shifted the origin by ROTATING the year vector (np.roll) and then cutting nine
blocks of three. That keeps nine blocks and a support of 512 at every offset,
which is tidy, and it is wrong: at offset 1 the last block becomes
[2024, 2025, 1999] and at offset 2 it becomes [2025, 1999, 2000]. A block
bootstrap exists to keep dependent neighbours together; wrapping puts the
first year of the series next to the last as if they were adjacent. A second
external review reconstructed the numbers from the deposited cells, found they
reproduced only under rotation, and asked what the values were with time order
kept. They are given below, and they are what the manuscript now reports.

With time order kept, shifting the origin by k years leaves a short block of k
years at the start and a short block at the end, so offsets 1 and 2 have TEN
blocks and a support of 1,024, not nine and 512. The frozen offset 0 is
unchanged -- it never wrapped anything -- and the preregistered result stands
exactly as it was. What changes is the sensitivity table: the two-year shift
no longer "leaves P1 exactly where the frozen origin puts it" (it takes P1 to
8/1024 = 0.0078), and the support is not the same at every row. The rotated
values are still written to the output, labelled as what they are, so the
correction can be checked rather than taken on trust.
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


def time_ordered_blocks(S_year: np.ndarray, offset: int,
                        block_len: int = BLOCK_LEN) -> tuple[np.ndarray, list]:
    """Block sums with the origin moved `offset` years and TIME ORDER KEPT.

    Boundaries fall at offset, offset + block_len, ... so the first `offset`
    years form a short leading block and whatever remains forms a short
    trailing block. Every year keeps the neighbours it has in the calendar;
    nothing wraps. Returns the block sums and the boundary indices so a caller
    can print which years each block holds.
    """
    T = len(S_year)
    bounds = [0] + ([offset] if offset else [])
    k = offset
    while k < T:
        k += block_len
        bounds.append(min(k, T))
    blocks = np.array([S_year[a:b].sum() for a, b in zip(bounds[:-1], bounds[1:])])
    return blocks, bounds


def _hits(blocks: np.ndarray) -> tuple[int, int]:
    nb = len(blocks)
    denom = float(np.sqrt((blocks ** 2).sum()))
    if denom == 0.0:
        return 2 ** nb, 2 ** nb
    t_obs = abs(float(blocks.sum()) / denom)
    hits = sum(1 for eta in itertools.product([-1.0, 1.0], repeat=nb)
               if abs(float(np.dot(eta, blocks)) / denom) >= t_obs - 1e-12)
    return hits, 2 ** nb


def exact_p(S_year: np.ndarray, offset: int) -> tuple[int, int]:
    """Hits and support size at an origin offset, time order kept."""
    blocks, _ = time_ordered_blocks(S_year, offset)
    return _hits(blocks)


def circular_p(S_year: np.ndarray, offset: int) -> tuple[int, int]:
    """What the first version of this tool computed: rotate, then block.

    Kept ONLY so the correction is checkable. Not used for any reported number.
    """
    S = np.roll(S_year, -offset)
    nb = int(np.ceil(len(S) / BLOCK_LEN))
    blocks = np.array([S[b * BLOCK_LEN:(b + 1) * BLOCK_LEN].sum() for b in range(nb)])
    return _hits(blocks)


def main() -> int:
    res: dict = {"block_len": BLOCK_LEN, "frozen_offset": 0, "panels": {}}
    for panel, path in CELLS.items():
        if not path.exists():
            raise SystemExit(f"[blocks] needs {path.relative_to(ROOT)}")
        cells = pd.read_csv(path)[["institution", "year", "count", "tokens"]]
        S, T = year_scores(cells)
        years = [int(y) for y in sorted(cells["year"].unique())]
        res["n_years"] = T
        res["blocking"] = ("time order kept; a shifted origin leaves a short "
                           "leading block and a short trailing block")
        res["panels"][panel] = {}
        for k in range(BLOCK_LEN):
            blocks, bounds = time_ordered_blocks(S, k)
            hits, support = _hits(blocks)
            c_hits, c_support = circular_p(S, k)
            res["panels"][panel][k] = {
                "hits": hits, "support": support, "p": hits / support,
                "n_blocks": len(blocks),
                "first_block_years": [years[bounds[0]], years[bounds[1] - 1]],
                "last_block_years": [years[bounds[-2]], years[bounds[-1] - 1]],
                # the earlier, wrapped computation -- for checking, not for use
                "circular_rotation_as_previously_published": {
                    "hits": c_hits, "support": c_support,
                    "p": c_hits / c_support},
            }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")

    print(f"{'offset':>7s} | " + " | ".join(f"{p:^22s}" for p in CELLS)
          + " | blocks | last block")
    print("-" * (9 + 25 * len(CELLS) + 22))
    for k in range(BLOCK_LEN):
        row = " | ".join(
            f"{res['panels'][p][k]['hits']:4d}/{res['panels'][p][k]['support']:<4d}"
            f" = {res['panels'][p][k]['p']:.4f}" for p in CELLS)
        r1 = res["panels"]["P1"][k]
        tag = "  <- frozen" if k == 0 else ""
        print(f"{k:>7d} | {row} | {r1['n_blocks']:6d} | "
              f"{r1['last_block_years'][0]}-{r1['last_block_years'][1]}{tag}")
    print("\n  (rotated, as previously published: "
          + "; ".join(f"{p} " + "/".join(
              f"{res['panels'][p][k]['circular_rotation_as_previously_published']['p']:.4f}"
              for k in range(BLOCK_LEN)) for p in CELLS) + ")")
    print(f"\n[blocks] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
