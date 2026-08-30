"""Pin the two facts that make condition 2's NB2 arm uninformative.

An external review argued that `mom_alpha` has no degrees-of-freedom correction
and is applied to a design with 30 parameters on 54 cells, so it cannot detect
overdispersion. Measured, that is right: it recovers roughly an eighth of a
dispersion that is really there, and PASS-P's size at a nominal 0.05 goes to
0.095 when the dispersion is there and unseen.

The full study is `tools/dispersion_calibration.py` at 1,000 replicates and takes
minutes. These tests are the fast version: they pin the design shape, which is
the mechanism, and demonstrate the downward bias on a small synthetic case, so a
future change to the estimator or the design cannot quietly remove the finding
the supplement now reports.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bootstrap_engine import build_design, mom_alpha, _fit          # noqa: E402

CELLS = ROOT / "data" / "analysis" / "panels" / "cells_P1.csv"
needs_cells = pytest.mark.skipif(
    not CELLS.exists(),
    reason="needs data/analysis/panels/cells_P1.csv (deposited, not in git)")


def test_the_dispersion_estimator_has_no_dof_correction():
    """The estimator is a ratio of sums with no n-p anywhere. If someone adds a
    correction, this fails and supplement S9's numbers must be regenerated."""
    src = (ROOT / "src" / "bootstrap_engine.py").read_text(encoding="utf-8")
    body = src.split("def mom_alpha", 1)[1].split("def ", 1)[0]
    for token in ("n - p", "n-p", "dof", "df_resid", "len(y) -"):
        assert token not in body, f"mom_alpha now corrects for {token!r}"


@needs_cells
def test_the_confirmatory_design_fits_thirty_parameters_on_fifty_four_cells():
    """The mechanism. 24 residual degrees of freedom is why the fitted mean
    absorbs the dispersion the estimator is supposed to measure."""
    cells = pd.read_csv(CELLS)[["institution", "year", "count", "tokens"]]
    _, X, _, _, _, _ = build_design(cells, "WB")
    assert X.shape == (54, 30), X.shape


@needs_cells
def test_the_estimator_recovers_a_small_fraction_of_a_known_dispersion():
    """Simulate at a known alpha and check the estimate comes back several times
    too small. Loose bounds on purpose: this pins the direction and the order of
    magnitude, which is what the supplement claims, not an exact figure."""
    cells = pd.read_csv(CELLS)[["institution", "year", "count", "tokens"]]
    _, X, _, y, off, _ = build_design(cells, "WB")
    import statsmodels.api as sm
    mu = np.asarray(_fit(y, X, off, sm.families.Poisson()).fittedvalues)
    rng = np.random.default_rng(20260806)
    true_a, ests = 0.25, []
    for _ in range(60):
        lam = rng.gamma(shape=1.0 / true_a, scale=true_a * mu)
        ysim = rng.poisson(lam).astype(float)
        m = np.asarray(_fit(ysim, X, off, sm.families.Poisson()).fittedvalues)
        ests.append(mom_alpha(ysim, m))
    mean = float(np.mean(ests))
    assert 0 < mean < true_a / 3, (
        f"recovered {mean:.4f} of a true {true_a}; supplement S9 reports roughly "
        "a seventh to a twentieth, and this bound is deliberately loose")
