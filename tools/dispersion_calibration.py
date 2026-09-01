#!/usr/bin/env python3
"""Two questions about dispersion the frozen design never asked itself.

An external review observed that `mom_alpha` carries no degrees-of-freedom
correction and is applied to a design with 30 parameters on 54 cells, and argued
that condition 2's NB2 arm therefore cannot fail. That is a claim about a frozen
component, so it is measured here rather than argued.

  1. RECOVERY. Simulate from the real design and offsets with a KNOWN NB2 alpha,
     refit, and ask what mom_alpha returns.

  2. SIZE. The more important question, and one the paper's existing calibration
     does not cover: if the data carry dispersion the estimator cannot see, does
     the GOVERNING test still hold its nominal size? Simulated under H0 — the
     restricted fit's values as the null mean, NB2 noise on top, then the frozen
     PASS-P.

The paper's §6.2 said "the engine holds its size" on the strength of an
800-replicate study under a Poisson-with-year-shock null. That claim survives
only for the null it was run under.

Deterministic: every stream is seeded from SEED, so reruns reproduce exactly.
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
from percell_seed import stream_seed              # noqa: E402
from bootstrap_engine import (build_design, _fit, _pair_index,      # noqa: E402
                              wild_score_p, mom_alpha, SEED, BLOCK_LEN)

PANELS = {"P1": ROOT / "data" / "analysis" / "panels" / "cells_P1.csv",
          "P2": ROOT / "data" / "analysis" / "panels" / "cells_P2.csv"}
OUT = ROOT / "data" / "analysis" / "dispersion_calibration.json"
ALPHAS = (0.0, 0.05, 0.10, 0.25, 0.50)


def nb2_draw(rng, mu, alpha):
    """NB2 with var = mu + alpha*mu^2, as a gamma-mixed Poisson."""
    if alpha <= 0:
        return rng.poisson(mu).astype(float)
    lam = rng.gamma(shape=1.0 / alpha, scale=alpha * mu)
    return rng.poisson(lam).astype(float)


def main(reps: int = 1000, b_inner: int = 999) -> int:
    res: dict = {"reps": reps, "b_inner": b_inner, "seed": SEED, "panels": {}}

    for panel, path in PANELS.items():
        if not path.exists():
            raise SystemExit(f"[disp] needs {path.relative_to(ROOT)}")
        cells = pd.read_csv(path)[["institution", "year", "count", "tokens"]]
        df, X, names, y, off, years = build_design(cells, "WB")
        pair, T = _pair_index(df, years, "WB")
        j = names.index("WB_post")
        Xr = np.delete(X, j, axis=1)
        mu_full = np.asarray(_fit(y, X, off, sm.families.Poisson()).fittedvalues)
        mu_null = np.asarray(_fit(y, Xr, off, sm.families.Poisson()).fittedvalues)

        entry = {"n_cells": int(X.shape[0]), "n_parameters": int(X.shape[1]),
                 "residual_df": int(X.shape[0] - X.shape[1]),
                 "alpha_hat_observed": mom_alpha(y, mu_full),
                 "recovery": {}, "size": {}}

        for a in ALPHAS:
            # len('P1') == len('P2'): both panels ran this recovery study on
            # one stream. Found by the round-18 class-level check, after an
            # external reading had found the same defect in three other
            # tools and missed this one.
            rng = np.random.default_rng(stream_seed('disp_recovery', panel, a))
            ests = []
            for _ in range(reps):
                ysim = nb2_draw(rng, mu_full, a)
                try:
                    m = np.asarray(_fit(ysim, X, off,
                                        sm.families.Poisson()).fittedvalues)
                except Exception:
                    continue
                ests.append(mom_alpha(ysim, m))
            e = np.asarray(ests)
            entry["recovery"][str(a)] = {"mean": float(e.mean()),
                                         "median": float(np.median(e)),
                                         "n": int(e.size)}

            rng = np.random.default_rng(stream_seed('disp_size', panel, a))
            ps = []
            for r in range(reps):
                ysim = nb2_draw(rng, mu_null, a)
                try:
                    p, _, _ = wild_score_p(ysim, X, off, names, pair, T,
                                           b_inner, BLOCK_LEN, SEED + r, nb2=False)
                except Exception:
                    continue
                ps.append(p)
            pv = np.asarray(ps)
            se = float(np.sqrt(0.05 * 0.95 / max(pv.size, 1)))
            entry["size"][str(a)] = {"size_05": float((pv < 0.05).mean()),
                                     "mc_se_at_05": se,
                                     "median_p": float(np.median(pv)),
                                     "n": int(pv.size)}
        res["panels"][panel] = entry

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")

    for panel, e in res["panels"].items():
        print(f"\n{panel}: {e['n_cells']} cells, {e['n_parameters']} parameters, "
              f"{e['residual_df']} residual d.o.f.; "
              f"alpha_hat on the real data = {e['alpha_hat_observed']:.4f}")
        print(f"  {'true alpha':>10s} {'alpha_hat':>10s} {'shrunk by':>10s} "
              f"{'PASS-P size @0.05':>18s}")
        for a in ALPHAS:
            r, s = e["recovery"][str(a)], e["size"][str(a)]
            shrink = f"{a / r['mean']:.1f}x" if r["mean"] > 1e-9 else "—"
            flag = " *" if s["size_05"] > 0.05 + 2 * s["mc_se_at_05"] else ""
            print(f"  {a:10.2f} {r['mean']:10.4f} {shrink:>10s} "
                  f"{s['size_05']:18.4f}{flag}")
    print(f"\n* size is more than two Monte Carlo standard errors above nominal")
    print(f"[disp] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000))
