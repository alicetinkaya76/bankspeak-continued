"""Pin the two post-freeze checks, and the properties that make them meaningful.

Both were added after an external review argued that disclosing a miscalibrated
procedure is not the same as showing the conclusion survives one. The tests
matter because both tools could produce reassuring output for uninteresting
reasons — a dispersion "correction" that changes nothing because it is not
actually different, or a Stage-A sensitivity that drops nothing.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_robust = _load("dispersion_robust_inference")
_stagea = _load("stage_a_exposure_sensitivity")

ROBUST_JSON = ROOT / "data" / "analysis" / "dispersion_robust_inference.json"
STAGEA_JSON = ROOT / "data" / "analysis" / "stage_a_exposure_sensitivity.json"


def test_the_corrected_estimator_is_actually_different_from_the_frozen_one():
    """On data with real dispersion and a heavily parameterised mean, the two
    must disagree. If they agreed, S10 would be measuring nothing."""
    rng = np.random.default_rng(11)
    mu = rng.uniform(20, 200, size=54)
    lam = rng.gamma(shape=1 / 0.3, scale=0.3 * mu)
    y = rng.poisson(lam).astype(float)
    frozen = _load("dispersion_robust_inference")
    from bootstrap_engine import mom_alpha                      # noqa: E402
    a_frozen = mom_alpha(y, mu)
    a_fixed = frozen.alpha_dof(y, mu, 30)
    assert a_fixed > a_frozen, (a_fixed, a_frozen)


def test_the_corrected_estimator_returns_zero_when_there_is_no_dispersion():
    """Poisson data with a well-fitting mean must not manufacture dispersion."""
    rng = np.random.default_rng(12)
    mu = np.full(54, 100.0)
    y = rng.poisson(mu).astype(float)
    assert _robust.alpha_dof(y, mu, 2) >= 0.0
    assert _robust.alpha_dof(y, mu, 2) < 0.02


def test_the_exact_enumeration_covers_the_whole_support():
    b = np.array([1.0, -2.0, 3.0, -1.0, 0.5, 2.0, -0.5, 1.5, -1.0])
    hits, support = _robust.exact_p(b)
    assert support == 512
    assert 1 <= hits <= 512
    # the observed pattern (all +1) is always at least as extreme as itself
    assert hits >= 1


@pytest.mark.skipif(not ROBUST_JSON.exists(), reason="run the tool first")
def test_the_verdict_does_not_change_under_the_corrected_procedure():
    d = json.loads(ROBUST_JSON.read_text())
    for panel, e in d["panels"].items():
        assert e["c1_passes_frozen"] == e["c1_passes_corrected"], panel


@pytest.mark.skipif(not STAGEA_JSON.exists(), reason="run the tool first")
def test_the_stage_a_sensitivity_actually_drops_documents_and_keeps_the_years():
    """A sensitivity that removed nothing, or that silently lost years to the
    common-year rule, would look reassuring for the wrong reason."""
    d = json.loads(STAGEA_JSON.read_text())
    assert d["n_stage_a_inspected"] == 748
    for panel, e in d["panels"].items():
        assert e["wb_docs_dropped"] > 0, panel
        assert e["full"]["T"] == e["reduced"]["T"] == 27, panel
        assert e["c1_full"] == e["c1_reduced"], panel


# --- H-SHARED discarded draws --------------------------------------------------

_hs = _load("hshared_draw_diagnostics")
HS_JSON = ROOT / "data" / "analysis" / "hshared_draw_diagnostics.json"


@pytest.mark.skipif(not HS_JSON.exists(), reason="run the tool first")
def test_the_discard_diagnostic_reproduces_the_frozen_counts():
    """It has to walk the same seeds the battery walked, or it is describing a
    different bootstrap. 8,392 valid and a 0.1607 fail rate are the frozen
    battery's own numbers."""
    d = json.loads(HS_JSON.read_text())
    assert d["valid"] == 8392
    assert abs(d["fail_rate"] - 0.1607) < 1e-4


@pytest.mark.skipif(not HS_JSON.exists(), reason="run the tool first")
def test_every_discarded_draw_failed_the_same_way():
    """The point of the diagnostic. If failures were mixed, the discarded set
    might be near-neutral; they are not mixed at all."""
    d = json.loads(HS_JSON.read_text())
    assert d["failed_no_pre_year"] == 0
    assert d["failed_no_post_year"] == d["failed"] > 0


# --- PASS-E interval coverage ---------------------------------------------------

COV_JSON = ROOT / "data" / "analysis" / "passe_coverage.json"


@pytest.mark.skipif(not COV_JSON.exists(), reason="run tools/passe_coverage.py first")
def test_the_intervals_under_cover_and_the_paper_says_the_measured_range():
    """Nominal 0.95, measured 0.805-0.907. If a future change made them cover,
    the supplement's claim would be stale and this fails."""
    d = json.loads(COV_JSON.read_text())
    vals = [v["coverage"] for panel in d["panels"].values() for v in panel.values()]
    assert vals, d
    assert max(vals) < 0.95, vals
    assert min(vals) > 0.7, vals


@pytest.mark.skipif(not COV_JSON.exists(), reason="run tools/passe_coverage.py first")
def test_coverage_is_worse_under_the_dispersion_the_data_suggest():
    """The direction that matters: the realistic null is the harsher one."""
    d = json.loads(COV_JSON.read_text())
    for panel, cells in d["panels"].items():
        pois = [v["coverage"] for k, v in cells.items() if k.endswith("poisson")]
        nb2 = [v["coverage"] for k, v in cells.items() if k.endswith("nb2_corrected")]
        assert sum(nb2) / len(nb2) < sum(pois) / len(pois), panel


# --- the null the design was preregistered against -----------------------------

_ar1 = _load("ar1_null_calibration")
AR1_JSON = ROOT / "data" / "analysis" / "ar1_null_calibration.json"


def test_the_ar1_null_uses_the_preregistered_parameters():
    """rho and sigma_delta must be the preregistration's, not convenient ones."""
    assert _ar1.RHO == 0.5
    assert abs(_ar1.SIGMA_DELTA - 0.3205) < 1e-9


def test_the_shock_is_differential_not_common():
    """A shock hitting both institutions in a year is absorbed by the saturated
    year dummies — the defect the preregistration recorded and replaced. If this
    became common, the study would silently measure nothing again."""
    src = (ROOT / "tools" / "ar1_null_calibration.py").read_text(encoding="utf-8")
    assert "wb_mask *" in src or "wb_mask*" in src, "the shock is no longer WB-specific"


@pytest.mark.skipif(not AR1_JSON.exists(), reason="run tools/ar1_null_calibration.py")
def test_size_is_worse_under_serial_dependence_than_under_iid():
    """The finding S10.4 rests on. If these ever converge, the supplement's
    diagnosis — that the fault is serial dependence, not overdispersion — is
    stale and must be rewritten rather than quietly left standing."""
    d = json.loads(AR1_JSON.read_text())
    for panel, arms in d["panels"].items():
        assert arms["ar1"]["size_05"] > arms["poisson"]["size_05"], panel
        assert arms["ar1"]["size_05"] > 0.09, (panel, arms["ar1"])


@pytest.mark.skipif(not COV_JSON.exists(), reason="run tools/passe_coverage.py first")
def test_coverage_is_measured_under_the_preregistered_serial_null_too():
    """S10.4 established that an i.i.d. null cannot test a block procedure. The
    coverage study inherited that defect and now carries AR(1) arms; if they
    disappear, S10.3's range is describing the wrong nulls again."""
    d = json.loads(COV_JSON.read_text())
    keys = {k for panel in d["panels"].values() for k in panel}
    assert any("ar1" in k for k in keys), sorted(keys)
    ar1 = [v["coverage"] for p in d["panels"].values() for k, v in p.items()
           if k.endswith("/ar1")]
    pois = [v["coverage"] for p in d["panels"].values() for k, v in p.items()
            if k.endswith("/poisson")]
    assert sum(ar1)/len(ar1) < sum(pois)/len(pois), (ar1, pois)
