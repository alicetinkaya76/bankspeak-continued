#!/usr/bin/env python3
"""Measure what the PASS-E intervals actually cover.

Table 4 labels them "nominal 95%" because no coverage study existed. §7 said so
honestly, but the intervals are still read — a lower bound clearing zero by 0.003
is interpreted somewhere in §6 — and an interval whose coverage is unknown cannot
carry that reading. So this measures it.

Simulate at a KNOWN beta from the real design, offsets and fitted values, run the
frozen PASS-E, and count how often the interval contains the truth. Two nulls:
Poisson, and NB2 at the dispersion the degrees-of-freedom-corrected estimator
reports (supplement S10), because S9 established that the frozen estimator cannot
see it.

B is reduced from the frozen 9,999 to keep this feasible: PASS-E refits the model
once per draw, so a coverage study at the frozen B would be tens of millions of
fits. The reduction affects the resolution of each interval's endpoints, not the
direction of the answer, and the value used is printed with the result.

Post-freeze. Nothing here gates anything.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bootstrap_engine import build_design, _fit, two_pass, SEED    # noqa: E402

PANELS = {"P1": ROOT / "data/analysis/panels/cells_P1.csv",
          "P2": ROOT / "data/analysis/panels/cells_P2.csv"}
ALPHA_CORRECTED = {"P1": 0.0520, "P2": 0.0425}      # from S10.1
OUT = ROOT / "data" / "analysis" / "passe_coverage.json"


def main(reps: int = 200, B: int = 299) -> int:
    res = {"reps": reps, "B": B, "frozen_B": 9999, "panels": {}}
    for panel, path in PANELS.items():
        cells = pd.read_csv(path)[["institution", "year", "count", "tokens"]]
        df, X, names, y, off, years = build_design(cells, "WB")
        j = names.index("WB_post")
        fit = _fit(y, X, off, sm.families.Poisson())
        beta = np.asarray(fit.params).copy()
        res["panels"][panel] = {}

        for label, true_beta in (("beta=0", 0.0),
                                 ("beta=observed", float(fit.params[j]))):
            b = beta.copy()
            b[j] = true_beta
            eta = X @ b + off
            mu = np.exp(eta)
            for null, a in (("poisson", 0.0), ("nb2_corrected", ALPHA_CORRECTED[panel])):
                rng = np.random.default_rng(SEED + int(true_beta * 1000) + len(null))
                cov = n_ok = 0
                for _ in range(reps):
                    if a <= 0:
                        ysim = rng.poisson(mu).astype(float)
                    else:
                        lam = rng.gamma(shape=1.0 / a, scale=a * mu)
                        ysim = rng.poisson(lam).astype(float)
                    sim = df.copy()
                    sim["count"] = ysim
                    try:
                        r = two_pass(sim[["institution", "year", "count", "tokens"]],
                                     wb_label="WB", B=B)
                    except Exception:
                        continue
                    ci = r.get("ci_percentile")
                    if not ci or ci[0] != ci[0]:
                        continue
                    n_ok += 1
                    if ci[0] <= true_beta <= ci[1]:
                        cov += 1
                c = cov / n_ok if n_ok else float("nan")
                se = float(np.sqrt(c * (1 - c) / n_ok)) if n_ok else float("nan")
                res["panels"][panel][f"{label}/{null}"] = {
                    "coverage": c, "mc_se": se, "n_valid": n_ok}
                print(f"  {panel:3s} {label:14s} {null:14s} "
                      f"coverage {c:.3f} ± {se:.3f}  (n={n_ok})")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"\n[coverage] nominal 0.95; wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    a = [int(x) for x in sys.argv[1:]] or [200, 299]
    sys.exit(main(*a))
