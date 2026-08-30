#!/usr/bin/env python3
"""Calibrate PASS-P under the error process the preregistration actually named.

Supplement S9 and S10.1 measure size under i.i.d. per-cell noise — Poisson, or a
gamma-mixed Poisson for overdispersion. Neither carries any serial dependence.
That is a real defect in those studies and it was found by external review, not
here: **under an i.i.d. null a three-year block has nothing to absorb**, so
S10.1's conclusion that the residual size inflation must live in the block
construction is a diagnosis by elimination that cannot perform the elimination.
It cannot distinguish "blocking is broken" from "blocking is unnecessary here".

The preregistration names a different process. `src/mde_sim.py` implements it for
the power analysis:

    delta[t] = rho * delta[t-1] + normal(0, sigma_delta)

a World-Bank-specific differential AR(1) shock, rho = 0.5, sigma_delta = 0.3205 —
which the SAP calls the binding constraint on power. Blocks exist to absorb
exactly that. So this runs the same size study under it.

Three arms, same design, same seeds, so the comparison is like for like:
  poisson    i.i.d. per cell, no dependence  (what S9 and S10.1 used)
  ar1        the preregistered differential AR(1) shock
  ar1_nb2    that shock plus the corrected dispersion

If size is near nominal under ar1, the blocks are doing their job and the
manuscript's block-construction claim must be withdrawn. If it is inflated there
too, the claim survives — but on evidence that can actually support it.
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
from bootstrap_engine import (build_design, _fit, _pair_index,      # noqa: E402
                              wild_score_p, SEED, BLOCK_LEN)

RHO, SIGMA_DELTA = 0.5, 0.3205          # PREREG / mde_sim defaults
PANELS = {"P1": ROOT / "data/analysis/panels/cells_P1.csv",
          "P2": ROOT / "data/analysis/panels/cells_P2.csv"}
ALPHA_CORRECTED = {"P1": 0.0520, "P2": 0.0425}
OUT = ROOT / "data" / "analysis" / "ar1_null_calibration.json"


def draw(rng, mu, df, wb_mask, arm, alpha):
    """Counts under the null, with the shock applied to the World Bank arm only.

    Differential, not common: a shock hitting both institutions in a year is
    absorbed by the saturated year dummies, which is the defect the
    preregistration itself recorded and replaced this process for."""
    eta = np.log(mu).copy()
    if arm.startswith("ar1"):
        years = np.array(sorted(df["year"].unique()))
        d = np.zeros(len(years))
        for t in range(1, len(years)):
            d[t] = RHO * d[t - 1] + rng.normal(0, SIGMA_DELTA)
        d[0] = rng.normal(0, SIGMA_DELTA / np.sqrt(1 - RHO ** 2))   # stationary start
        pos = {y: i for i, y in enumerate(years)}
        eta = eta + wb_mask * np.array([d[pos[y]] for y in df["year"]])
    lam = np.exp(eta)
    if arm.endswith("nb2") and alpha > 0:
        lam = rng.gamma(shape=1.0 / alpha, scale=alpha * lam)
    return rng.poisson(lam).astype(float)


def main(reps: int = 1500, B: int = 999) -> int:
    res = {"reps": reps, "B": B, "rho": RHO, "sigma_delta": SIGMA_DELTA,
           "panels": {}}
    print(f"{'panel':6s} {'null':10s} {'size@0.05':>10s} {'median p':>9s}  "
          f"(MC SE {np.sqrt(.05*.95/reps):.4f})")
    for panel, path in PANELS.items():
        cells = pd.read_csv(path)[["institution", "year", "count", "tokens"]]
        df, X, names, y, off, years = build_design(cells, "WB")
        pair, T = _pair_index(df, years, "WB")
        j = names.index("WB_post")
        Xr = np.delete(X, j, axis=1)
        mu0 = np.asarray(_fit(y, Xr, off, sm.families.Poisson()).fittedvalues)
        wb = (df["institution"] == "WB").astype(float).to_numpy()
        res["panels"][panel] = {}
        for arm in ("poisson", "ar1", "ar1_nb2"):
            rng = np.random.default_rng(SEED + 97 + len(arm) + len(panel))
            ps = []
            for r in range(reps):
                ysim = draw(rng, mu0, df, wb, arm, ALPHA_CORRECTED[panel])
                try:
                    p, _, _ = wild_score_p(ysim, X, off, names, pair, T,
                                           B, BLOCK_LEN, SEED + r, nb2=False)
                except Exception:
                    continue
                ps.append(p)
            a = np.asarray(ps)
            size = float((a < 0.05).mean())
            res["panels"][panel][arm] = {"size_05": size, "n": int(a.size),
                                         "median_p": float(np.median(a))}
            print(f"{panel:6s} {arm:10s} {size:10.4f} {np.median(a):9.3f}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"\n[ar1] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    a = [int(x) for x in sys.argv[1:]] or [1500, 999]
    sys.exit(main(*a))
