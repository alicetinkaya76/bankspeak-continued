import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bootstrap_engine import two_pass, _mk

def cells(theta, tokens, seed=7):
    rng = np.random.default_rng(seed); rows = []
    for yy in range(1994, 2026):
        for inst in ("WB", "IMF"):
            bump = theta if (inst == "WB" and 2023 <= yy <= 2025) else 0.0
            lam = np.exp(np.log(6e-5) + bump) * tokens
            rows.append({"institution": inst, "year": yy,
                         "count": int(rng.poisson(lam)), "tokens": tokens})
    return pd.DataFrame(rows)

def test_null_large_coherent():
    r = two_pass(cells(0.0, 2_000_000), B=99)
    assert 0 < r["p_two_sided"] <= 1 and r["p_two_sided"] > 0.02
    lo, hi = r["ci_percentile"]
    assert lo <= r["beta_hat"] <= hi            # round-5 defect 1 repaired
    assert r["method_p"] == "wild_score_block"

def test_effect_detected_ci_contains_beta():
    r = two_pass(cells(0.9, 2_000_000), B=99)
    lo, hi = r["ci_percentile"]
    assert r["p_two_sided"] < 0.05 and lo > 0
    assert lo <= r["beta_hat"] <= hi

def test_small_counts_true_floor_share_positive():
    r = two_pass(cells(0.0, 40_000), B=59)
    assert r["true_floored_share"] > 0          # round-5 defect 2 repaired
    assert 0 < r["p_two_sided"] <= 1

def test_deterministic():
    a = two_pass(cells(0.4, 500_000), B=59)
    b = two_pass(cells(0.4, 500_000), B=59)
    assert a["p_two_sided"] == b["p_two_sided"] and a["ci_percentile"] == b["ci_percentile"]

def test_duplicate_cells_rejected():
    d = cells(0.0, 1_000_000)
    d2 = pd.concat([d, d.iloc[[0]]], ignore_index=True)
    import pytest
    with pytest.raises(ValueError, match="duplicate"):
        two_pass(d2, B=9)

def test_noninteger_mode_no_rounding():
    d = cells(0.4, 500_000).astype({"count": float})
    d["count"] = d["count"] + 0.37
    r = two_pass(d, B=39, allow_noninteger=True)
    assert r["rounding"] == "none" and 0 < r["p_two_sided"] <= 1

def test_nb2_valid_score_runs():
    d = cells(0.0, 2_000_000, seed=11)
    r = two_pass(d, B=59, nb2=True)
    assert r["alpha_hat"] >= 0 and 0 < r["p_two_sided"] <= 1
    lo, hi = r["ci_percentile"]; assert lo <= r["beta_hat"] <= hi

def test_escalation_ladder_via_injected_fit():
    import bootstrap_engine as be
    calls = {"n": 0}
    def flaky(y, X, off, family):
        calls["n"] += 1
        if calls["n"] > 2 and calls["n"] % 3 == 0:      # ~33% CI-refit failures
            raise RuntimeError("boom")
        return be._fit(y, X, off, family)
    r = two_pass(cells(0.3, 1_000_000), B=30, fit_fn=flaky)
    assert r["method_ci"] == "wald_boot" and r["governing_ci"] == "ci_wald_boot"
    calls["n"] = 0
    def dead(y, X, off, family):
        calls["n"] += 1
        if calls["n"] > 2:
            raise RuntimeError("boom")
        return be._fit(y, X, off, family)
    r2 = two_pass(cells(0.3, 1_000_000), B=30, fit_fn=dead)
    assert r2["method_ci"] == "failed" and r2["governing_ci"] == "failed"


def test_trend_ci_from_same_passe_draws():
    """v3.1: the WB_cyear coefficient is recorded from the SAME PASS-E draws
    (PREREG v0.5 SS9); fields exist, are finite, and the percentile interval
    is ordered."""
    r = two_pass(_mk(0.9, 200_000), B=49)
    assert np.isfinite(r["trend_beta_hat"])
    lo, hi = r["trend_ci_percentile"]
    assert np.isfinite(lo) and np.isfinite(hi) and lo <= hi


def test_selftest_values_pinned_cross_platform():
    """Frozen determinism regression: the exact selftest numbers reproduced on
    macOS/arm64, Linux/x86-64 and the round-5 reviewer stack. Any drift here
    means the seeded engine path changed."""
    r = two_pass(_mk(0.9, 2_000_000), B=299)
    assert round(r["p_two_sided"], 3) == 0.003
    assert [round(x, 3) for x in r["ci_percentile"]] == [0.623, 0.898]
    s = two_pass(_mk(0.0, 40_000), B=299)
    assert round(s["p_two_sided"], 3) == 0.193
    assert round(s["true_floored_share"], 4) == 0.0316
