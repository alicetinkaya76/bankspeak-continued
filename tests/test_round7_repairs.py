"""Round-7 flip regressions: every reviewer counterexample must stay dead,
every legitimate neighboring behavior must stay alive."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

from bootstrap_engine import (build_design, two_pass, passe_multi,
                              _jackknife_multi, _mk, _fit, SEED)
import bootstrap_engine as be
from s09a_imf_articleiv_frame import SEED_ALIASES, build_frame as imf_build
from s09b_wb_p0_frame import resolve_country
from g1_audit import score, draw
from s13_validation_battery import (holm_family, make_bins, event_study,
                                    standardized_variant)

B_FIX = 99


# ---------------------------------------------- R1: exact integer contract --
def test_integer_contract_exact_rejects_near_integer():
    d = _mk(0.0, 1e6)
    d["count"] = d["count"].astype(float)
    d.loc[0, "count"] = 1000000.4              # allclose rtol would accept
    with pytest.raises(ValueError):
        build_design(d, "WB")


def test_integer_contract_accepts_true_integers():
    d = _mk(0.0, 1e6)
    d["count"] = d["count"].astype(float)      # float dtype, integer values
    build_design(d, "WB")


# ------------------------------------- R2: alias-first country resolution --
def test_tto_resolves_single_country_s09b():
    assert resolve_country("Trinidad and Tobago",
                           dict(SEED_ALIASES)) == ("TTO", None)


def test_true_multi_and_regional_still_excluded_s09b():
    al = dict(SEED_ALIASES)
    assert resolve_country("Kenya; Uganda", al)[1] \
        == "excluded_regional_multicountry"
    assert resolve_country("Western Africa", al)[1] \
        == "excluded_regional_multicountry"


def test_tto_article_iv_included_s09a():
    fx = pd.DataFrame([{"title": "Trinidad and Tobago: 2024 Article IV "
                        "Consultation; IMF Country Report No. 24/100",
                        "url": "u", "pub_date": "2024-05-01"}])
    _f, audit = imf_build(fx)
    assert audit.iloc[0]["status"] == "included"
    assert audit.iloc[0]["country_iso3"] == "TTO"


# --------------------------------------------------- FSSA text resolution --
def test_fssa_cotitled_included_with_flag():
    fx = pd.DataFrame([{"title": "Canada: 2024 Article IV Consultation and "
                        "Financial System Stability Assessment; IMF Country "
                        "Report No. 24/321", "url": "u",
                        "pub_date": "2024-07-01"}])
    _f, audit = imf_build(fx)
    assert audit.iloc[0]["status"] == "included"
    assert bool(audit.iloc[0]["fssa_cotitled"]) is True


def test_standalone_fssa_excluded():
    fx = pd.DataFrame([{"title": "Canada: Financial System Stability "
                        "Assessment; IMF Country Report No. 24/322",
                        "url": "u", "pub_date": "2024-07-02"}])
    _f, audit = imf_build(fx)
    assert audit.iloc[0]["status"].startswith("excluded")


# ------------------------------------------------------- G1 exactly-20 rule --
def _sheet(n, npass):
    cols = ["i1_recurring_country_surveillance", "i2_not_project_tied",
            "i3_staff_analytical_report", "i4_periodic_cycle"]
    d = pd.DataFrame({c: [1] * n for c in cols})
    for c in cols:
        d.loc[npass:, c] = 0
    return d


def test_g1_sixteen_row_sheet_fails():
    r = score(_sheet(16, 16))
    assert r["sheet_size_valid"] is False and r["g1_pass"] is False


def test_g1_twenty_row_sixteen_pass_passes():
    r = score(_sheet(20, 16))
    assert r["sheet_size_valid"] is True and r["g1_pass"] is True


def test_g1_draw_refuses_small_frames():
    with pytest.raises(ValueError):
        draw(pd.DataFrame({"id": range(16)}))


# ------------------------------------------------ family invalid zero state --
def test_family_zero_state_raises_without_p0_failure():
    with pytest.raises(ValueError):
        holm_family({}, [], p0_failed=False)


def test_family_fallback_valid_after_p0_failure():
    assert holm_family({}, [], p0_failed=True)["state"] == "fallback"


def test_family_five_states_synthetic():
    def pr(p):
        return {"conditions": {"c1_holm_p": {"p_pass_p": p},
                               "c2_stability": {"ok": True},
                               "c3_concentration_guard": {"ok": True},
                               "c4_lopo": {"ok": True}}}
    one = holm_family({"P0": pr(0.001)}, ["P0"], p0_failed=False)
    assert one["state"] == "singleton"
    pair = holm_family({"P1": pr(0.001), "P2": pr(0.002)}, ["P1", "P2"],
                       p0_failed=True)
    assert pair["state"] == "holm_pair"
    solo1 = holm_family({"P1": pr(0.01)}, ["P1"], p0_failed=True)
    assert solo1["state"] == "singleton" and "P1" in solo1["decisions"]
    solo2 = holm_family({"P2": pr(0.01)}, ["P2"], p0_failed=True)
    assert solo2["state"] == "singleton" and "P2" in solo2["decisions"]
    fb = holm_family({}, [], p0_failed=True)
    assert fb["state"] == "fallback" and fb["family_pass"] is False


# --------------------------------------------------------- event-study bins --
def test_make_bins_gap_sequence_no_stopiteration():
    bins, ref = make_bins([1994] + list(range(1997, 2026)))
    assert bins[0] == (1994, 1998)             # observed-count merge
    assert bins[ref] == (2008, 2010)           # lower-median observed year


def test_make_bins_full_span_reference_unchanged():
    bins, ref = make_bins(list(range(1994, 2026)))
    assert bins[ref] == (2008, 2010)


def test_make_bins_cascading_merge():
    bins, ref = make_bins([1990] + list(range(1999, 2026)))
    assert bins[0][0] == 1990 and bins[0][1] >= 2001
    assert sum(1 for y in [1990] + list(range(1999, 2026))
               if bins[0][0] <= y <= bins[0][1]) >= 2


# ---------------------------------------------- standardization gates (SS6) --
def _std_world(support_c_tokens):
    rows = []
    for inst in ("WB", "IMF"):
        for yr in (2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025):
            for g, tok in (("A", 500_000), ("B", 500_000)):
                rows.append({"institution": inst, "year": yr, "group": g,
                             "count": 0.0001 * tok, "tokens": tok})
            if yr >= 2023 and support_c_tokens:
                rows.append({"institution": inst, "year": yr,
                             "group": f"C_{inst}", "count": 33,
                             "tokens": support_c_tokens})
    return pd.DataFrame(rows)


def test_std_75pct_support_infeasible():
    res = standardized_variant(_std_world(333_334), B=49)
    assert res["feasible"] is False
    assert res["reason"] == "post_token_support_below_0.80"
    assert abs(res["post_token_support"]["WB"] - 0.75) < 1e-6
    assert any(e["excluded_token_share"] > 0
               for e in res["excluded_token_shares"])


def test_std_high_support_feasible_and_reported():
    res = standardized_variant(_std_world(0), B=49)
    assert res["feasible"] is True
    assert min(res["post_token_support"].values()) == 1.0
    assert res["dropped_cells"] == []


def test_std_zero_coverage_post_cell_explicit():
    rows = []
    for inst in ("WB", "IMF"):
        for yr in (2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025):
            if inst == "WB" and yr == 2025:
                rows.append({"institution": inst, "year": yr, "group": "C_WB",
                             "count": 10, "tokens": 100_000})
                continue
            for g, tok in (("A", 500_000), ("B", 500_000)):
                rows.append({"institution": inst, "year": yr, "group": g,
                             "count": 0.0001 * tok, "tokens": tok})
    res = standardized_variant(pd.DataFrame(rows), B=49)
    assert res["feasible"] is False
    assert res["reason"] == "zero_coverage_post_cell"
    assert {"institution": "WB", "year": 2025} in res["dropped_cells"]


# ------------------------------------- event study: full PASS-E machinery --
def test_event_study_exposes_full_machinery():
    res = event_study(_mk(0.4, 500_000), B=B_FIX)
    for k in ("method_ci", "governing_ci", "ci_fail_rate",
              "true_floored_share", "small_count_regime", "rounding",
              "B_valid_ci"):
        assert k in res
    nonref = [r for r in res["bins"] if not r["reference"]]
    assert all("ci_wald_boot" in r for r in nonref)
    assert res["rounding"] == "numpy-ties-to-even"


def test_event_study_noninteger_mode():
    d = _mk(0.3, 500_000)
    d["count"] = d["count"].astype(float) + 0.25
    res = event_study(d, B=49, allow_noninteger=True)
    assert res["rounding"] == "none" and res["status"] == "ok"


# --------------------------- passe_multi NB2 fallback + fail-closed states --
def _wbpost_design(df):
    wb = (df["institution"] == "WB").astype(float).to_numpy()
    post = ((df["year"] >= 2023) & (df["year"] <= 2025)
            ).astype(float).to_numpy()
    ydum = pd.get_dummies(df["year"], drop_first=True, dtype=float)
    X = np.column_stack([np.ones(len(df)), ydum.to_numpy(), wb, wb * post])
    return X, ["const"] + [f"y{c}" for c in ydum.columns] + ["WB", "WB_post"]


def test_passe_multi_nb2_jackknife_fallback():
    rng = np.random.default_rng(7)
    d = _mk(0.4, 200_000)
    d["count"] = (d["count"].astype(float)
                  * rng.gamma(2.0, 0.5, size=len(d))).round()

    def ff(y, X, off, fam):
        if isinstance(fam, sm.families.NegativeBinomial):
            raise RuntimeError("forced NB2 failure")
        return _fit(y, X, off, fam)

    res = passe_multi(d, _wbpost_design, ["WB_post"], B=9, nb2=True,
                      fit_fn=ff)
    assert res["governing_ci"] == "jackknife_poisson"
    assert "se_jackknife" in res["coefs"]["WB_post"]


def test_passe_multi_jackknife_failed_state():
    d = _mk(0.4, 200_000)
    calls = {"n": 0}

    def ff(y, X, off, fam):
        calls["n"] += 1
        if calls["n"] == 1:                     # first full Poisson only
            return _fit(y, X, off, fam)
        raise RuntimeError("forced universal failure")

    res = passe_multi(d, _wbpost_design, ["WB_post"], B=9, nb2=True,
                      fit_fn=ff)
    assert res["governing_ci"] == "failed"
    assert res["method_ci"] == "jackknife_failed"


def test_estimation_ci_jackknife_failed_state(monkeypatch):
    rng = np.random.default_rng(11)
    d = _mk(0.4, 200_000)
    d["count"] = (d["count"].astype(float)
                  * rng.gamma(2.0, 0.5, size=len(d))).round()  # alpha > 0
    orig = be._fit

    def ff(y, X, off, fam):
        if isinstance(fam, sm.families.NegativeBinomial):
            raise RuntimeError("forced NB2 failure")
        return orig(y, X, off, fam)

    def jk_raise(*a, **k):
        raise RuntimeError("forced jackknife failure")

    monkeypatch.setattr(be, "_fit", ff)
    monkeypatch.setattr(be, "jackknife_ci", jk_raise)
    res = two_pass(d, B=9, nb2=True)
    assert res["method_ci"] == "jackknife_failed"
    assert res["governing_ci"] == "failed"
    assert res["B_valid_ci"] == 0


def test_jackknife_multi_fail_closed():
    d = _mk(0.4, 200_000)

    def ff(y, X, off, fam):
        r = _fit(y, X, off, fam)
        class Fake:
            params = r.params
            fittedvalues = r.fittedvalues
            mle_retvals = {"converged": False}
            converged = False
        return Fake()

    with pytest.raises(RuntimeError):
        _jackknife_multi(d, _wbpost_design, ["WB_post"], "WB", False, ff)
