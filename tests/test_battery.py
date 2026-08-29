import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bootstrap_engine import _mk
from s13_validation_battery import (make_bins, run_panel, holm_family,
                                    standardized_variant, _ess_tokens,
                                    placebo_2016, hshared)

B_FIX = 49  # fixture bootstrap size; production B = 9,999


# ---------------------------------------------------------- pure helpers --
def test_make_bins_anchor_merge_reference():
    bins, ref = make_bins(range(1994, 2026))
    assert bins[-1] == (2023, 2025)
    assert bins[0] == (1994, 1995)                 # 2-year earliest bin: kept
    assert bins[ref] == (2008, 2010)               # m = 2009.5 -> its bin
    bins2, _ = make_bins(range(1995, 2026))
    assert bins2[0] == (1995, 1998)                # 1-year bin merged upward

def _std_from_cells(cells):
    rows = []
    for _, r in cells.iterrows():
        for g in ("A", "B"):
            rows.append({"institution": r["institution"], "year": int(r["year"]),
                         "group": g, "count": r["count"] * 0.5,
                         "tokens": r["tokens"] * 0.5})
    return pd.DataFrame(rows)

def _docs(theta, seed=11, n=6):
    rng = np.random.default_rng(seed)
    rows = []
    for yy in range(1994, 2026):
        for inst in ("WB", "IMF"):
            post = inst == "WB" and 2023 <= yy <= 2025 and theta > 0
            for _ in range(n):
                rows.append({"institution": inst, "year": yy,
                             "tokens": float(rng.integers(150_000, 250_000)),
                             "hit": int(rng.random() < (0.80 if post else 0.45)),
                             "breadth": int(rng.binomial(13, 0.50 if post else 0.25))})
    return pd.DataFrame(rows)


# ------------------------------------------------------------ full panel --
def test_effect_world_passes_all_conditions():
    cells = _mk(0.9, 2_000_000)
    cells["count_ex_underscore"] = np.floor(cells["count"] * 0.7)
    cells["count_ex_underscore_pivotal"] = np.floor(cells["count"] * 0.6)
    res = run_panel(cells, "P1", docs=_docs(0.9),
                    std_docs=_std_from_cells(cells), B=B_FIX)
    c = res["conditions"]
    assert c["c1_holm_p"]["ok"] is True
    assert c["c2_stability"]["variants"]["nb2"]["ok"] is True
    assert c["c2_stability"]["variants"]["standardized"]["ok"] is True
    assert c["c3_concentration_guard"]["ok"] is True
    assert c["c4_lopo"]["ok"] is True and len(c["c4_lopo"]["deletions"]) == 3
    assert res["panel_pass_at_supplied_alpha"] is True
    # trend CI comes from the SAME PASS-E draws (engine fields)
    tr = res["trend"]
    assert np.isfinite(tr["beta"]) and len(tr["ci_percentile"]) == 2
    # event-study structure: one reference bin, CIs elsewhere
    bins = res["event_study"]["bins"]
    assert sum(b["reference"] for b in bins) == 1
    assert all("ci_percentile" in b for b in bins if not b["reference"])
    # H-SHARED on a flat IMF series: CI covers 0
    lo, hi = res["h_shared"]["ci_percentile"]
    assert lo < 0 < hi
    # validation outcomes agree in sign -> no downgrade
    assert res["validation"]["consistency"]["downgrade_to_count_specific"] is False
    assert res["guard_stress_nongating"] is not None

def test_null_world_fails_condition1():
    res = run_panel(_mk(0.0, 2_000_000), "P1", B=B_FIX)
    assert res["conditions"]["c1_holm_p"]["ok"] is False
    assert res["conditions"]["c2_stability"]["variants"]["standardized"][
        "reason"] == "std_docs_not_supplied"
    assert res["panel_pass_at_supplied_alpha"] is False


# -------------------------------------------------- SS6 infeasibility ----
def test_std_post_coverage_hard_fail():
    rows = []
    for inst in ("WB", "IMF"):
        for yy, groups in [(2020, "AB"), (2021, "AB"), (2023, "AB"),
                           (2024, "AB" if inst == "IMF" else "A")]:
            for g in groups:
                rows.append({"institution": inst, "year": yy, "group": g,
                             "count": 50.0, "tokens": 500_000.0})
    out = standardized_variant(pd.DataFrame(rows), B=9)
    assert out["feasible"] is False
    assert out["reason"] == "post_coverage_below_floor"

def test_ess_token_floor():
    pi = pd.Series({"A": 0.9, "B": 0.1})
    skew = pd.DataFrame([
        {"institution": "WB", "year": 2020, "group": "A", "count": 1, "tokens": 10.0},
        {"institution": "WB", "year": 2020, "group": "B", "count": 1, "tokens": 1e6},
    ])
    assert _ess_tokens(skew, pi)[0]["ok"] is False
    bal = pd.DataFrame([
        {"institution": "WB", "year": 2020, "group": "A", "count": 1, "tokens": 9e5},
        {"institution": "WB", "year": 2020, "group": "B", "count": 1, "tokens": 1e5},
    ])
    assert _ess_tokens(bal, pi)[0]["ok"] is True      # pi matches token shares

def test_placebo_restricted_to_pre2023():
    out = placebo_2016(_mk(0.9, 200_000), B=B_FIX)
    assert out["years_used"][1] <= 2022
    assert 0.0 < out["p_pass_p"] <= 1.0


# ---------------------------------------------------- B6 four-state rule --
def _fake_panel(p, ok=True, beta=0.8):
    return {"primary_m2": {"beta_hat": beta, "ci_percentile": [0.6, 1.0]},
            "conditions": {
                "c1_holm_p": {"p_pass_p": p, "alpha_holm": 0.05, "ok": None},
                "c2_stability": {"ok": ok},
                "c3_concentration_guard": {"ok": ok},
                "c4_lopo": {"ok": ok}}}

def test_holm_pair_and_singleton_and_fallback():
    two = {"P1": _fake_panel(0.001), "P2": _fake_panel(0.20)}
    fam = holm_family(two, ["P1", "P2"])
    assert fam["state"] == "holm_pair"
    assert fam["decisions"]["P1"]["alpha_holm"] == 0.025
    assert fam["passing_panels"] == ["P1"] and fam["family_pass"] is True
    assert "panel P2" in fam["headline_template"]      # other panel in-sentence
    one = holm_family({"P0": _fake_panel(0.03)}, ["P0"])
    assert one["state"] == "singleton"
    assert one["decisions"]["P0"]["alpha_holm"] == 0.05
    assert one["family_pass"] is True
    zero = holm_family({}, [], p0_failed=True)
    assert zero["state"] == "fallback" and zero["family_pass"] is False
