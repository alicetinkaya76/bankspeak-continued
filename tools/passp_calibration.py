#!/usr/bin/env python3
"""Does PASS-P hold its nominal size on this design? Simulate and find out.

The third-eye review of 2026-08-29 objected that the paper offers a bespoke
inference engine as a transferable contribution without ever showing it behaves
as intended. Transparency is not calibration. This is the missing check.

## Design of the simulation

The null data-generating process is the fitted confirmatory model with the
post-2022 coefficient set to zero and everything else kept: the real token
offsets, the real year effects, the real World Bank level and differential trend.
Counts are drawn Poisson around that mean, with a year-level shock added on the
log scale at the preregistration's own method-of-moments value, sigma_delta =
0.3205 — the quantity §6.3 identifies as the binding constraint on power. A pure
Poisson null would understate the variance the design actually faces and would
flatter the test.

## Why the p-values here are exact rather than simulated

27 common years in three-year blocks gives nine blocks, so the wild sign support
is exactly 2^9 = 512 patterns. Rather than run 9,999 Monte Carlo draws inside
every replicate, each replicate's p-value is obtained by enumerating all 512.
That removes simulation noise from the inner loop entirely, so the only Monte
Carlo error left is across replicates, and it makes the whole study cheap enough
to run honestly at a useful number of replicates.

It also means the finest achievable p-value is 1/512 = 0.00195, and that no
nominal level between 1/512 and 2/512 can be attained. Discreteness of that order
is itself a property worth reporting: a test whose support has 512 points cannot
be conservative and exact at 0.05 simultaneously.
"""
from __future__ import annotations

import csv
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bootstrap_engine import build_design, _pair_index, _fit  # noqa: E402

PANELS = ROOT / "data" / "analysis" / "panels"
OUT = ROOT / "data" / "analysis" / "passp_calibration.json"
SIGMA_DELTA = 0.3205          # PREREG §8 frozen MoM hook
BLOCK_LEN = 3
SEED = 42

SIGNS = np.array(list(itertools.product([-1.0, 1.0], repeat=9)))   # 512 x 9


def cells(panel: str) -> pd.DataFrame:
    with (PANELS / f"cells_{panel}.csv").open(encoding="utf-8") as fh:
        rs = list(csv.DictReader(fh))
    return pd.DataFrame([{"institution": r["institution"], "year": int(r["year"]),
                          "count": float(r["count"]), "tokens": float(r["tokens"])}
                         for r in rs])


def score_blocks(df: pd.DataFrame):
    """Block scores for the WB_post wild score statistic, Poisson working variance."""
    d, X, names, y, off, years = build_design(df, "WB")
    pair, T = _pair_index(d, years, "WB")
    j = names.index("WB_post")
    Xr = np.delete(X, j, axis=1)
    mu0 = np.asarray(_fit(y, Xr, off, sm.families.Poisson()).fittedvalues)
    xj = X[:, j]
    A = Xr * mu0[:, None]
    coef, *_ = np.linalg.lstsq(Xr.T @ A, Xr.T @ (mu0 * xj), rcond=None)
    s = (xj - Xr @ coef) * (y - mu0)
    S = np.array([s[pair[k]].sum() for k in range(T)])
    nb = int(np.ceil(T / BLOCK_LEN))
    return np.array([S[b * BLOCK_LEN:(b + 1) * BLOCK_LEN].sum() for b in range(nb)])


def exact_p(SB) -> float:
    den = float(np.sqrt((SB ** 2).sum()))
    if den == 0.0:
        return 1.0
    obs = abs(float(SB.sum()) / den)
    stat = np.abs(SIGNS @ SB) / den
    return float((stat >= obs - 1e-12).sum()) / len(SIGNS)


def null_dgp(panel: str, n_rep: int, rng):
    """Fit the real model, zero the post effect, redraw counts under the null."""
    df = cells(panel)
    d, X, names, y, off, years = build_design(df, "WB")
    fit = _fit(y, X, off, sm.families.Poisson())
    beta = np.asarray(fit.params).copy()
    beta[names.index("WB_post")] = 0.0                 # impose the null
    eta0 = X @ beta + off
    yr = d["year"].to_numpy()
    uy = np.array(sorted(set(yr)))
    reps = []
    for _ in range(n_rep):
        shock = rng.normal(0.0, SIGMA_DELTA, size=len(uy))
        eta = eta0 + np.array([shock[np.searchsorted(uy, v)] for v in yr])
        sim = d.copy()
        sim["count"] = rng.poisson(np.exp(eta)).astype(float)
        reps.append(sim[["institution", "year", "count", "tokens"]])
    return reps


def main() -> int:
    n_rep = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    rng = np.random.default_rng(SEED)
    out = {"n_replicates": n_rep, "sigma_delta": SIGMA_DELTA,
           "block_len": BLOCK_LEN, "support": len(SIGNS),
           "inner_p": "exact enumeration of all 512 sign patterns", "panels": {}}
    print(f"PASS-P size under the null — {n_rep} replicates, exact inner p\n")
    for panel in ("P1", "P2"):
        ps = []
        for sim in null_dgp(panel, n_rep, rng):
            try:
                ps.append(exact_p(score_blocks(sim)))
            except Exception:
                continue
        ps = np.array(ps)
        rec = {"n_usable": int(len(ps))}
        for a in (0.01, 0.05, 0.10):
            r = float((ps <= a + 1e-12).mean())
            mcse = float(np.sqrt(r * (1 - r) / max(len(ps), 1)))
            rec[f"size_at_{a}"] = r
            rec[f"mcse_at_{a}"] = mcse
            print(f"  {panel}  nominal {a:.2f}  ->  empirical {r:.4f}  "
                  f"(± {1.96*mcse:.4f})")
        rec["median_p"] = float(np.median(ps))
        out["panels"][panel] = rec
        print(f"  {panel}  median null p = {rec['median_p']:.4f}  "
              f"(0.50 would be ideal)\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"[calib] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
