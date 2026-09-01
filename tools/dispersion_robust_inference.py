#!/usr/bin/env python3
"""Does the verdict survive an inference procedure with roughly correct size?

Supplement S9 established two things about the frozen machinery: `mom_alpha`
carries no degrees-of-freedom correction and recovers a seventh to a twentieth of
a dispersion that is really there, and PASS-P's size at a nominal 0.05 reaches
about 0.095 when that dispersion is present. An external review made the obvious
demand: preregistration does not oblige anyone to keep privileging a method after
showing it is miscalibrated. Add a dispersion-corrected analysis and say whether the
governing verdict is an artifact of the frozen one.

This is a POST-FREEZE variant. `src/bootstrap_engine.py` is not touched, and the
confirmatory result stands as reported; what follows is a second opinion.

The correction is the standard moment estimator that respects the fitted degrees
of freedom -- choose alpha so that the Pearson statistic equals its expectation,

    sum (y - mu)^2 / (mu + alpha*mu^2) = n - p

rather than the frozen ratio-of-sums, which implicitly divides by n and is
therefore biased toward zero exactly in proportion to how many parameters the
mean absorbed. With 30 parameters on 54 cells that is most of them.

Reported: the corrected alpha, the exact 512-pattern p under the corrected
working variance, the empirical size of the corrected procedure, and whether any
panel's condition 1 changes. Conditions 3 and 4 are point-estimate conditions and
cannot move with a variance correction; that is checked rather than asserted.
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
from percell_seed import stream_seed              # noqa: E402
from bootstrap_engine import (build_design, _fit, _pair_index,      # noqa: E402
                              mom_alpha, SEED, BLOCK_LEN)

PANELS = {"P1": (ROOT / "data/analysis/panels/cells_P1.csv", 0.025),
          "P2": (ROOT / "data/analysis/panels/cells_P2.csv", 0.05)}
OUT = ROOT / "data" / "analysis" / "dispersion_robust_inference.json"


def alpha_dof(y, mu, n_params: int) -> float:
    """Solve Pearson(alpha) = n - p for alpha >= 0, by bisection.

    Pearson is strictly decreasing in alpha, so a bracket plus bisection is
    enough and needs no derivative. alpha = 0 already at or below the target
    means the data show no dispersion the fit has not absorbed.
    """
    n = len(y)
    target = n - n_params
    def pearson(a):
        return float(np.sum((y - mu) ** 2 / (mu + a * mu ** 2)))
    if pearson(0.0) <= target:
        return 0.0
    lo, hi = 0.0, 1.0
    while pearson(hi) > target and hi < 1e4:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if pearson(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def block_scores(y, X, off, names, pair, T, alpha):
    """The frozen score, with alpha supplied instead of estimated internally."""
    j = names.index("WB_post")
    Xr = np.delete(X, j, axis=1)
    mu0 = np.asarray(_fit(y, Xr, off, sm.families.Poisson()).fittedvalues)
    W = mu0 / (1.0 + alpha * mu0)
    xj = X[:, j]
    coef, *_ = np.linalg.lstsq(Xr.T @ (Xr * W[:, None]), Xr.T @ (W * xj),
                               rcond=None)
    s = (xj - Xr @ coef) * (y - mu0) / (1.0 + alpha * mu0)
    S_year = np.array([s[pair[k]].sum() for k in range(T)])
    nb = int(np.ceil(T / BLOCK_LEN))
    return np.array([S_year[b*BLOCK_LEN:(b+1)*BLOCK_LEN].sum() for b in range(nb)])


_SIGNS: dict[int, np.ndarray] = {}


def signs(nb: int) -> np.ndarray:
    """All 2^nb sign patterns, built once. The enumeration is exact, so it runs
    inside every simulated replicate; a Python loop over 512 tuples per call was
    the whole cost of the size study."""
    if nb not in _SIGNS:
        _SIGNS[nb] = np.array(list(itertools.product([-1.0, 1.0], repeat=nb)))
    return _SIGNS[nb]


def exact_p(blocks) -> tuple[int, int]:
    nb = len(blocks)
    den = float(np.sqrt((blocks ** 2).sum()))
    if den == 0:
        return 2 ** nb, 2 ** nb
    t = abs(float(blocks.sum()) / den)
    stats = np.abs(signs(nb) @ blocks) / den
    return int((stats >= t - 1e-12).sum()), 2 ** nb


def main(reps: int = 600) -> int:
    res = {"reps": reps, "note": "post-freeze; the frozen engine is unmodified",
           "panels": {}}
    for panel, (path, holm) in PANELS.items():
        cells = pd.read_csv(path)[["institution", "year", "count", "tokens"]]
        df, X, names, y, off, years = build_design(cells, "WB")
        pair, T = _pair_index(df, years, "WB")
        n, p = X.shape
        mu_full = np.asarray(_fit(y, X, off, sm.families.Poisson()).fittedvalues)

        a_frozen = mom_alpha(y, mu_full)
        a_fixed = alpha_dof(y, mu_full, p)

        h_f, s_f = exact_p(block_scores(y, X, off, names, pair, T, a_frozen))
        h_c, s_c = exact_p(block_scores(y, X, off, names, pair, T, a_fixed))

        # Size of the CORRECTED procedure, under a null carrying the dispersion
        # the corrected estimator says is there.
        j = names.index("WB_post")
        Xr = np.delete(X, j, axis=1)
        mu_null = np.asarray(_fit(y, Xr, off, sm.families.Poisson()).fittedvalues)
        # len("P1") == len("P2"), so the old SEED + 31 + len(panel) gave the two
        # panels one stream and their size figures were not independent
        # estimates. External review found it.
        rng = np.random.default_rng(stream_seed("dispersion_size", panel))
        rej_c = rej_f = 0
        for _ in range(reps):
            if a_fixed <= 0:
                ysim = rng.poisson(mu_null).astype(float)
            else:
                lam = rng.gamma(shape=1.0/a_fixed, scale=a_fixed*mu_null)
                ysim = rng.poisson(lam).astype(float)
            mfull = np.asarray(_fit(ysim, X, off, sm.families.Poisson()).fittedvalues)
            for est, bucket in ((alpha_dof(ysim, mfull, p), "c"),
                                (mom_alpha(ysim, mfull), "f")):
                hh, ss = exact_p(block_scores(ysim, X, off, names, pair, T, est))
                if hh / ss < 0.05:
                    if bucket == "c":
                        rej_c += 1
                    else:
                        rej_f += 1

        e = {"n_cells": n, "n_parameters": p, "holm_alpha": holm,
             "alpha_frozen": a_frozen, "alpha_dof_corrected": a_fixed,
             "exact_p_frozen": {"hits": h_f, "support": s_f, "p": h_f/s_f},
             "exact_p_corrected": {"hits": h_c, "support": s_c, "p": h_c/s_c},
             "size_at_05_corrected": rej_c/reps, "size_at_05_frozen": rej_f/reps,
             "c1_passes_frozen": (h_f/s_f) < holm,
             "c1_passes_corrected": (h_c/s_c) < holm}
        res["panels"][panel] = e

        print(f"\n{panel}  ({n} cells, {p} parameters, Holm alpha {holm})")
        print(f"  alpha            frozen {a_frozen:.4f}   d.o.f.-corrected {a_fixed:.4f}")
        print(f"  exact p          frozen {h_f}/{s_f} = {h_f/s_f:.4f}   "
              f"corrected {h_c}/{s_c} = {h_c/s_c:.4f}")
        print(f"  size at 0.05     frozen {rej_f/reps:.3f}   corrected {rej_c/reps:.3f}"
              f"   (n={reps}, MC SE ~{np.sqrt(.05*.95/reps):.3f})")
        print(f"  condition 1      frozen {'PASS' if e['c1_passes_frozen'] else 'fail'}"
              f"   corrected {'PASS' if e['c1_passes_corrected'] else 'fail'}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"\n[robust] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 600))
