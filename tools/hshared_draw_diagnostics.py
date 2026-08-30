#!/usr/bin/env python3
"""Why 1,607 of H-SHARED's 9,999 draws were discarded, and whether it is neutral.

§6.3 reports that the comparator's own pre/post change excludes zero by 0.0029
log points on 8,392 valid draws out of 9,999. An external review asked the right
questions: why did each failed draw fail, were the failures asymmetric, and how
sensitive is that 0.0029 endpoint to the discarded set.

The answer is not numerical. `hshared` discards a draw when the resampled year
set puts every year on one side of the 2023 boundary, so one arm of the pre/post
contrast is empty and the statistic is undefined. With 27 years resampled as nine
circular blocks of three, and only three post-period years, that degeneracy is
overwhelmingly one-sided by construction: it is far easier to draw no post year
than no pre year.

This reproduces the frozen draw sequence exactly — same seeds, same block
construction — and classifies each failure instead of counting it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bootstrap_engine import BLOCK_LEN, SEED, POST_LO, POST_HI     # noqa: E402
from s13_validation_battery import HS_SEED_OFFSET                  # noqa: E402

OUT = ROOT / "data" / "analysis" / "hshared_draw_diagnostics.json"


def main(B: int = 9999) -> int:
    cells = pd.read_csv(ROOT / "data/analysis/panels/cells_P1.csv")
    years = np.array(sorted(cells["year"].unique()))
    T = len(years)
    post = (years >= POST_LO) & (years <= POST_HI)
    n_blocks = int(np.ceil(T / BLOCK_LEN))

    no_post = no_pre = ok = 0
    for b in range(B):
        rng = np.random.default_rng(SEED + HS_SEED_OFFSET + b)
        starts = rng.integers(0, T, size=n_blocks)
        order = np.concatenate([(s0 + np.arange(BLOCK_LEN)) % T
                                for s0 in starts])[:T]
        pm = post[order]
        if pm.sum() == 0:
            no_post += 1
        elif (~pm).sum() == 0:
            no_pre += 1
        else:
            ok += 1

    fails = no_post + no_pre
    res = {"B": B, "years": int(T), "post_years": int(post.sum()),
           "blocks": n_blocks, "valid": ok, "failed": fails,
           "failed_no_post_year": no_post, "failed_no_pre_year": no_pre,
           "fail_rate": fails / B}
    print(f"{T} years, {int(post.sum())} of them post-period, "
          f"{n_blocks} circular blocks of {BLOCK_LEN}\n")
    print(f"  valid draws                    {ok:6d}")
    print(f"  discarded: no post-period year {no_post:6d}")
    print(f"  discarded: no pre-period year  {no_pre:6d}")
    print(f"  fail rate                      {fails/B:.4f}")
    print("\n  The discard is structural, not numerical: a draw is dropped when")
    print("  the resampled years all fall on one side of the 2023 boundary. With")
    print(f"  {int(post.sum())} post years in {T}, the two ways of failing are not")
    print("  remotely equally likely, and the discarded set is therefore NOT a")
    print("  random subsample of the intended draws.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"\n[hshared] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
