#!/usr/bin/env python3
"""What the estimate does when the functional form is changed one piece at a time.

An external review made the point that with three post-period years, saturated
year effects and an institution-specific linear trend, beta is largely determined
by extrapolating a linear counterfactual -- and asked to see, in one table, the
specification without the institution trend, alternative pre-period start years,
each post year dropped in turn, and the 2020-2021 composition years excluded.

Two of those five were already in the manuscript: leave-one-post-year-out IS
preregistered condition C4 (SS5), and the trend-free descriptive contrast is the
event study of Table 6b. The other three were not, and are computed here. They
need nothing but the two frozen 54-cell panels, so there is no reason not to.

WHAT CHANGES WITH THE SPECIFICATION, AND WHY THE ROWS ARE NOT INTERCHANGEABLE.
Dropping WB x centred-year does not give a better-identified version of the same
quantity. It changes the estimand: beta stops being the post-2023 departure from
the World Bank's own fitted differential trend and becomes a pre/post contrast
that absorbs the whole 1999-2022 divergence. That row is reported because the
reviewer asked what the trend assumption is worth, and the answer is "most of the
estimate" -- not because it is a defensible alternative headline.

Restricting the pre-period does two things at once, and the second is the one
worth watching: it shortens the series, so the number of three-year sign-flip
blocks falls, so the exact p-value's support -- 2^n_blocks -- shrinks. At 27
years there are nine blocks and 512 attainable p-values; at 15 years there are
five and 32. The minimum attainable p rises accordingly. A row whose p moves is
therefore not necessarily reporting a change in the data; the support size is in
the table so the reader can tell the two apart.

The inner p here is ENUMERATED over all sign patterns, not sampled, exactly as
in tools/joint_holm_calibration.py, so nothing in this table carries Monte Carlo
noise. The block-origin sweep keeps time order -- a shifted origin has a short
block at each end, ten blocks and a support of 1,024 on the full series, rather
than the nine and 512 a rotation would give by wrapping 1999 next to 2025 (see
tools/block_origin_enumeration.py for the correction and the rotated values).
Reproduce with `python tools/functional_form_sensitivity.py`.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from bootstrap_engine import POST_LO, POST_HI, BLOCK_LEN     # noqa: E402
from joint_holm_calibration import Design, irls_poisson      # noqa: E402
from block_origin_enumeration import time_ordered_blocks    # noqa: E402

PANELS = ("P1", "P2")
CELLS = {p: ROOT / "data" / "analysis" / "panels" / f"cells_{p}.csv" for p in PANELS}
OUT = ROOT / "data" / "analysis" / "functional_form_sensitivity.json"
FRAME = ROOT / "data" / "analysis" / "imf_frame_publication.csv"


class NoTrendDesign(Design):
    """The frozen design with WB x centred-year deleted.

    Everything else -- the offset, the year dummies, the pairing, the block
    partition, the enumeration -- is untouched, so the only difference between
    this row and the baseline is the column.
    """

    def __init__(self, cells: pd.DataFrame):
        super().__init__(cells)
        k = self.names.index("WB_cyear")
        self.X = np.delete(self.X, k, axis=1)
        self.names = [n for n in self.names if n != "WB_cyear"]
        self.j = self.names.index("WB_post")
        self.Xr = np.delete(self.X, self.j, axis=1)
        self.xj = self.X[:, self.j]


def year_scores(des: Design, y: np.ndarray) -> np.ndarray:
    """PASS-P's per-year restricted score. Same arithmetic as Design.exact_p,
    stopped one step earlier so the blocking can be varied."""
    mu0, _ = irls_poisson(y, des.Xr, des.off)
    coef, *_ = np.linalg.lstsq(des.Xr.T @ (des.Xr * mu0[:, None]),
                               des.Xr.T @ (mu0 * des.xj), rcond=None)
    s = (des.xj - des.Xr @ coef) * (y - mu0)
    return np.array([s[des.pair[k]].sum() for k in range(des.T)])


def p_at_offset(S_year: np.ndarray, offset: int) -> tuple[float, int]:
    """p and support at an origin offset, TIME ORDER KEPT.

    The first version rotated the year vector before blocking, copying
    tools/block_origin_enumeration.py as it then was, which put the first year
    of the series in the same block as the last. An external review caught it
    there and it was wrong here for the same reason. The shared helper now
    leaves short blocks at the ends instead, so a shifted origin has one more
    block than the frozen one and a support of 2^(n_blocks) that differs by
    offset -- which is why the support is returned with the p.
    """
    blocks, _ = time_ordered_blocks(S_year, offset, BLOCK_LEN)
    nb = len(blocks)
    denom = float(np.sqrt((blocks ** 2).sum()))
    if denom == 0.0:
        return 1.0, 2 ** nb
    t_obs = abs(float(blocks.sum())) / denom
    signs = np.array(list(itertools.product([-1.0, 1.0], repeat=nb)))
    stat = np.abs(signs @ blocks) / denom
    return float((stat >= t_obs - 1e-12).sum()) / signs.shape[0], 2 ** nb


def fit(des: Design) -> dict:
    """One row: the estimate, the frozen-offset p, and the p under every other
    block origin.

    The offset sweep is not decoration. Deleting a single year renumbers every
    later year, so it moves the block partition as well as the data, and the two
    effects are not separable from a single p. Reporting the range under all
    BLOCK_LEN origins says how much of a row's movement could be partition
    alone: a row whose range still brackets the published p has not shown that
    its deletion mattered.
    """
    y = des.y0
    S = year_scores(des, y)
    pairs = [p_at_offset(S, o) for o in range(BLOCK_LEN)]
    ps = [p for p, _ in pairs]
    floor = 2.0 / (2 ** des.n_blocks)
    return {
        "beta": round(float(des.beta_post(y)), 6),
        "exact_p": round(float(des.exact_p(y)), 8),
        "blocking": "time order kept at every origin; nothing wraps",
        "p_by_block_origin": [round(v, 8) for v in ps],
        "support_by_block_origin": [sup for _, sup in pairs],
        "p_min_over_origins": round(float(min(ps)), 8),
        "p_max_over_origins": round(float(max(ps)), 8),
        # The stable quantity is not the p but how many of the three origins
        # clear the threshold. Any single p is one draw from this set.
        "origins_below_05": int(sum(v < 0.05 for v in ps)),
        "n_years": int(des.T),
        "n_blocks": int(des.n_blocks),
        "support": int(2 ** des.n_blocks),
        "min_attainable_p": round(floor, 8),
        # A short series can put 0.05 below the smallest p the enumeration can
        # return, in which case the row cannot be significant whatever the data
        # say. Reading such a row as evidence of anything would be reading the
        # support size.
        "significance_arithmetically_possible": bool(floor < 0.05),
        "n_cells": int(len(des.df)),
    }


def variants(cells: pd.DataFrame) -> list[tuple[str, str, dict]]:
    """(key, human label, fitted row) for one panel, in reporting order."""
    yrs = np.array(sorted(cells["year"].unique()))
    lo, hi = int(yrs.min()), int(yrs.max())
    out: list[tuple[str, str, dict]] = []

    out.append(("as_published",
                f"as published ({lo}-{hi}, WB trend in)",
                fit(Design(cells))))

    out.append(("no_wb_trend",
                "WB x centred-year deleted (DIFFERENT estimand)",
                fit(NoTrendDesign(cells))))

    # Alternative pre-period starts. Chosen as the two-, four- and six-block
    # truncations rather than round years, so each row moves the support by a
    # known amount instead of an incidental one.
    for start in (lo + 4, lo + 8, lo + 12):
        sub = cells[cells["year"] >= start]
        out.append((f"pre_start_{start}",
                    f"pre-period starts {start} instead of {lo}",
                    fit(Design(sub))))

    # Composition years. 2020-2021 is where the manuscript's own corpus work
    # says the document mix moves; the reviewer asked for it excluded.
    for drop, label in (((2020,), "2020 dropped"),
                        ((2021,), "2021 dropped"),
                        ((2020, 2021), "2020 and 2021 dropped")):
        sub = cells[~cells["year"].isin(drop)]
        out.append((f"drop_{'_'.join(str(d) for d in drop)}", label,
                    fit(Design(sub))))

    # Inverse-probability weighting of the comparator, which a review asked for
    # and which turns out to be degenerate here.
    #
    # The IMF arm is a capped annual cross-section with per-year inclusion
    # probabilities running 0.31 to 1.00, so a reviewer reasonably asked for the
    # result reweighted to the population. Inflating a sampled cell to its
    # population total means scaling BOTH the count and the token denominator by
    # 1 / pi. The estimand is a rate, so that leaves the rate unchanged and beta
    # cannot move except through the rounding of counts back to integers. The
    # row is computed rather than argued, because "the sensitivity is degenerate"
    # is a claim about arithmetic that a reader is entitled to check.
    #
    # Scaling the count alone WOULD move beta -- and is simply a different,
    # wrong quantity: it inflates a numerator without its denominator. That row
    # is here too, labelled, so the difference is visible instead of assumed.
    if FRAME.exists():
        frame = pd.read_csv(FRAME)
        pi = dict(zip(frame["year"].astype(int),
                      frame["inclusion_probability"].astype(float)))
        if set(cells.loc[cells["institution"] == "IMF", "year"]) <= set(pi):
            for key, label, scale_tokens in (
                    ("ipw_comparator", "IMF reweighted to population (IPW)", True),
                    ("ipw_counts_only", "IMF counts scaled, tokens not (NOT IPW)", False)):
                w = cells.copy().astype({"tokens": float})
                m = w["institution"] == "IMF"
                inv = 1.0 / w.loc[m, "year"].map(pi)
                w.loc[m, "count"] = (w.loc[m, "count"] * inv).round()
                if scale_tokens:
                    w.loc[m, "tokens"] = w.loc[m, "tokens"] * inv
                out.append((key, label, fit(Design(w))))

    # C4's arms, recomputed here so the reviewer's five requests sit in one
    # table. These are not new: PREREG SS5 condition 4 gates on them and SS6.2
    # reports that both panels fail it.
    for yy in range(POST_LO, POST_HI + 1):
        sub = cells[cells["year"] != yy]
        out.append((f"drop_post_{yy}",
                    f"post year {yy} dropped (this is C4's arm)",
                    fit(Design(sub))))

    return out


def main() -> int:
    res: dict = {
        "source": "data/analysis/panels/cells_{P1,P2}.csv (frozen)",
        "inner_p": "enumerated over all 2^n_blocks sign patterns; not sampled",
        "estimand_warning": (
            "The no_wb_trend row is NOT a better-identified version of the "
            "published beta. Deleting WB x centred-year makes beta a pre/post "
            "contrast that absorbs the 1999-2022 divergence, so it answers a "
            "different question and is reported as such."),
        "support_warning": (
            "Rows that shorten the series also shrink the sign support "
            "(2^n_blocks) and raise the minimum attainable p. Compare p across "
            "rows only with the support column beside it."),
        "panels": {},
    }
    for p in PANELS:
        cells = pd.read_csv(CELLS[p])
        rows = variants(cells)
        res["panels"][p] = {k: dict(label=lab, **row) for k, lab, row in rows}

    OUT.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")

    for p in PANELS:
        base = res["panels"][p]["as_published"]
        print(f"\n{p}   (as published: beta {base['beta']:+.4f}, "
              f"p {base['exact_p']:.6f}, support {base['support']})")
        print(f"  {'variant':46s} {'beta':>9s} {'exact p':>10s} "
              f"{'yrs':>4s} {'supp':>6s} {'p over all block origins':>26s}")
        print("  " + "-" * 100)
        for k, row in res["panels"][p].items():
            span = " ".join(f"{v:.4f}" for v in row["p_by_block_origin"])
            flag = "" if row["significance_arithmetically_possible"] else "  <- p<.05 UNREACHABLE"
            print(f"  {row['label']:46s} {row['beta']:+9.4f} "
                  f"{row['exact_p']:10.6f} {row['n_years']:4d} "
                  f"{row['support']:6d}   {span:>24s}  {row['origins_below_05']}/3{flag}")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
