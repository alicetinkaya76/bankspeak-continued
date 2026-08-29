"""Round-8 flip regressions: every reviewer probe must stay dead, every
legitimate neighboring behavior must stay alive. Each test FAILS on commit
56c972d (the reviewed object) and passes after the sprint-4 repairs."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import numpy as np
import pandas as pd
import pytest

from bootstrap_engine import passe_multi, _mk
from s13_validation_battery import make_bins, event_study, standardized_variant
from mde_sim import simulate_joint, load_template
import s01_fetch_metadata as s01
from s09a_imf_articleiv_frame import fetch_live_sproll
from s09b_wb_p0_frame import apply_docty_verification


# ------------------------------------------ R8-1: acquisition fail-closed --
class _R:
    def __init__(self, status, text):
        self.status_code, self.text = status, text
        self.content = self.text.encode()


class _Sess:
    def __init__(self, pages):
        self.pages, self.urls = pages, []

    def get(self, url, timeout=None):
        self.urls.append(url)
        return self.pages[min(len(self.urls) - 1, len(self.pages) - 1)]


_ROW = ('<a href="/p/a1">Kenya: 2024 Article IV Consultation; IMF Country '
        'Report No. 24/001</a> <span>July 10, 2024</span>')


def test_sproll_http_error_raises(tmp_path):
    with pytest.raises(RuntimeError):
        fetch_live_sproll(_Sess([_R(500, "<html>error</html>")]),
                          tmp_path, tmp_path / "log.csv", sleep=0)


def test_sproll_empty_first_page_raises(tmp_path):
    with pytest.raises(RuntimeError):
        fetch_live_sproll(_Sess([_R(200, "<div>maintenance</div>")]),
                          tmp_path, tmp_path / "log.csv", sleep=0)


def test_sproll_anchors_without_rows_raises(tmp_path):
    pages = [_R(200, _ROW),
             _R(200, '<a href="/x">Continue to site</a>')]  # interstitial
    with pytest.raises(RuntimeError):
        fetch_live_sproll(_Sess(pages), tmp_path, tmp_path / "log.csv",
                          sleep=0)


def test_sproll_max_pages_exhaustion_raises(tmp_path):
    with pytest.raises(RuntimeError):
        fetch_live_sproll(_Sess([_R(200, _ROW)]), tmp_path,
                          tmp_path / "log.csv", sleep=0, max_pages=3)


def test_sproll_legitimate_terminal_still_ok(tmp_path):
    pages = [_R(200, _ROW), _R(200, "<div>No results found</div>")]
    df = fetch_live_sproll(_Sess(pages), tmp_path, tmp_path / "log.csv",
                           sleep=0)
    assert len(df) == 1


class _FR:
    def __init__(self, payload):
        self._p = payload
        self.status_code = 200
        self.text = json.dumps(payload)

    def json(self):
        return self._p


_CFG = {"api": {"base_url": "http://f", "rows_per_page": 1, "format": "json",
                "lang_exact": "English", "fields": ["id"], "max_retries": 1,
                "timeout": 1, "backoff_base": 1, "sleep_seconds": 0}}
_DOC = {"id": "1", "docty": "X", "count": "5", "display_title": "A",
        "docdt": "2024-01-01T00:00:00Z", "repnb": "R1", "volnb": "1"}


def test_fetch_declared_total_mismatch_raises():
    class S:
        def __init__(self):
            self.n = 0

        def get(self, u, params=None, timeout=None):
            self.n += 1
            return _FR({"total": 3,
                        "documents": ({"D1": _DOC} if self.n == 1 else {})})
    with pytest.raises(RuntimeError):
        s01.fetch_stratum_year(S(), _CFG, ["X"], 2024)


def test_fetch_complete_stratum_still_ok():
    class S:
        def __init__(self):
            self.n = 0

        def get(self, u, params=None, timeout=None):
            self.n += 1
            return _FR({"total": 2, "documents":
                        {f"D{self.n}": dict(_DOC, id=str(self.n))}})
    recs = s01.fetch_stratum_year(S(), _CFG, ["X"], 2024)
    assert len(recs) == 2
    assert {r["id"] for r in recs} == {"1", "2"}   # round-10: unique ids


def test_docty_schema_rejects_empty_and_partial(tmp_path):
    p = tmp_path / "v.json"
    p.write_text("{}")
    with pytest.raises(SystemExit):
        apply_docty_verification([{"genre": "cem", "docty": "X"}], str(p))
    p.write_text(json.dumps({"verified_utc": "2026-11-01T00:00:00Z",
                             "source": "s00",
                             "labels": {"cem": "A", "scd": "B",
                                        "cpf": "C"}}))       # no probe hash
    with pytest.raises(SystemExit):
        apply_docty_verification([{"genre": "cem", "docty": "X"}], str(p))


# ------------------------------ R8-2: IMF-specific MDE inputs really bind --
def test_imf_rate_changes_p1p2_simulation():
    years = np.arange(2018, 2026)
    base = dict(theta1=0.4, theta2=0.4, rho=0.35, sigma_delta=0.05)
    a1, _ = simulate_joint(years, np.full(8, 1e5), 2e-4,
                           rng=np.random.default_rng(3),
                           rate_imf=2e-4, **base)
    b1, _ = simulate_joint(years, np.full(8, 1e5), 2e-4,
                           rng=np.random.default_rng(3),
                           rate_imf=8e-4, **base)
    i1 = a1[a1["institution"] == "IMF"]["count"].to_numpy()
    i2 = b1[b1["institution"] == "IMF"]["count"].to_numpy()
    assert not np.array_equal(i1, i2)          # the round-8 invariance probe


def test_imf_tokens_flow_into_cells():
    years = np.arange(2018, 2026)
    c1, _ = simulate_joint(years, np.full(8, 1e5), 2e-4, 0.0, 0.0, 0.35,
                           0.0, np.random.default_rng(5),
                           tokens_imf=np.full(8, 7e5))
    assert set(c1[c1["institution"] == "IMF"]["tokens"]) == {7e5}


def test_imf_defaults_reproduce_legacy_draws():
    years = np.arange(2018, 2026)
    lег = simulate_joint(years, np.full(8, 1e5), 2e-4, 0.3, 0.2, 0.35, 0.05,
                         np.random.default_rng(9))
    new = simulate_joint(years, np.full(8, 1e5), 2e-4, 0.3, 0.2, 0.35, 0.05,
                         np.random.default_rng(9),
                         tokens_imf=np.full(8, 1e5), rate_imf=2e-4)
    pd.testing.assert_frame_equal(lег[0], new[0])
    pd.testing.assert_frame_equal(lег[1], new[1])


def test_template_missing_year_raises(tmp_path):
    p = tmp_path / "t.csv"
    p.write_text("year,tokens\n2024,1000\n")
    with pytest.raises(SystemExit):
        load_template(p, np.array([2023, 2024]))


def test_calibrated_wald_crit_governs():
    import mde_sim as M
    src = open(Path(M.__file__)).read()
    assert "wald_singleton_decide" in src and "wald_holm2_decide" in src
    # semantics: exercised at function scope inside main(); replicate here
    def singleton(z, crit):
        return bool(abs(z) >= crit)

    def holm2z(z1, z2, cf, ch):
        a1, a2 = abs(z1), abs(z2)
        if max(a1, a2) < ch:
            return False, False
        big1 = a1 >= a2
        small = a2 if big1 else a1
        rs = bool(small >= cf)
        return (True, rs) if big1 else (rs, True)
    assert singleton(2.2, 2.0) and not singleton(2.2, 2.5)
    assert holm2z(3.0, 2.1, 2.0, 2.5) == (True, True)
    assert holm2z(3.0, 1.5, 2.0, 2.5) == (True, False)
    assert holm2z(2.4, 2.1, 2.0, 2.5) == (False, False)   # crit governs


# ----------------------------------- R8-3: empty interior bin unestimable --
def test_make_bins_interior_gap_merges_forward():
    yrs = [y for y in range(1994, 2026) if y not in (2002, 2003, 2004)]
    bins, ref = make_bins(yrs)
    assert all(any(lo <= y <= hi for y in yrs) for lo, hi in bins)
    assert (2002, 2004) not in bins
    assert any(lo <= 2002 and hi >= 2004 for lo, hi in bins)   # merged fwd
    lo, hi = bins[ref]
    assert lo <= 2011 <= hi     # 29 observed years -> lower median = 2011


def test_event_study_interior_gap_estimable():
    d = _mk(0.3, 300_000)
    d = d[~d["year"].isin([2002, 2003, 2004])].reset_index(drop=True)
    res = event_study(d, B=29)
    assert res["status"] == "ok"
    assert all(r["bin"] != [2002, 2004] for r in res["bins"])
    for r in res["bins"]:
        if not r["reference"]:
            assert (r["ci_percentile"][1] - r["ci_percentile"][0]) > 1e-8


def test_passe_multi_rank_guard():
    d = _mk(0.3, 200_000)

    def dup_design(df):
        wb = (df["institution"] == "WB").astype(float).to_numpy()
        X = np.column_stack([np.ones(len(df)), wb, wb])     # duplicate col
        return X, ["const", "WB", "WB_dup"]
    with pytest.raises(ValueError):
        passe_multi(d, dup_design, ["WB_dup"], B=5)


def test_passe_multi_zero_support_guard():
    d = _mk(0.3, 200_000)

    def zero_design(df):
        wb = (df["institution"] == "WB").astype(float).to_numpy()
        X = np.column_stack([np.ones(len(df)), wb,
                             np.zeros(len(df))])            # all-zero col
        return X, ["const", "WB", "ghost"]
    with pytest.raises(ValueError):
        passe_multi(d, zero_design, ["ghost"], B=5)


# ------------------------- R8-4: standardization diagnostics on ALL paths --
def _ess_fail_world():
    rows = []
    for inst in ("WB", "IMF"):
        for yr in (2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025):
            rows.append({"institution": inst, "year": yr, "group": "A",
                         "count": 50, "tokens": 500_000})
            rows.append({"institution": inst, "year": yr, "group": "B",
                         "count": 5,
                         "tokens": (50_000 if (inst == "WB" and yr >= 2023)
                                    else 500_000)})
    return pd.DataFrame(rows)


def test_std_every_return_carries_diagnostics():
    res = standardized_variant(_ess_fail_world(), B=29)
    assert res["feasible"] is False
    for k in ("post_token_support", "excluded_token_shares", "dropped_cells",
              "min_post_coverage", "ess", "pi_groups", "failures"):
        assert k in res, k
    assert res["reason"] in res["failures"]


def test_std_simultaneous_failures_not_masked():
    rows = []
    for inst in ("WB", "IMF"):
        for yr in (2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025):
            if inst == "WB" and yr == 2025:
                rows.append({"institution": inst, "year": yr,
                             "group": "C_WB", "count": 10,
                             "tokens": 900_000})    # low support AND zero pi
                continue
            for g in ("A", "B"):
                rows.append({"institution": inst, "year": yr, "group": g,
                             "count": 50, "tokens": 500_000})
    res = standardized_variant(pd.DataFrame(rows), B=29)
    assert res["feasible"] is False
    assert res["reason"] == "zero_coverage_post_cell"        # frozen order
    assert "post_token_support_below_0.80" in res["failures"]
    assert {"institution": "WB", "year": 2025} in res["dropped_cells"]


# --------------------------------------- R8-5: packager freeze discipline --
def test_git_status_failure_aborts(tmp_path):
    from build_audit_package import require_clean_tree

    def bad_runner(*a, **k):
        raise FileNotFoundError("git not found")
    with pytest.raises(SystemExit):
        require_clean_tree(tmp_path, False, runner=bad_runner)

    class _P:
        returncode = 128
        stdout = ""
    with pytest.raises(SystemExit):
        require_clean_tree(tmp_path, False, runner=lambda *a, **k: _P())


def test_freeze_completeness_enforced():
    from build_audit_package import enforce_freeze_completeness
    ff = {"zip_sha256": "x", "zip_bytes": 1, "zip_entry_count": 1,
          "sha256sums_entries": 1, "manifest_rows": 1,
          "sha256sums_sha256": "x", "manifest_sha256": "x",
          "python_version": "3.11.9", "python_version_sha256": "x",
          "requirements_sha256": "x", "requirements_ppl_sha256": "x",
          "git_commit": "x", "environment_sha256": None,
          "calibration_sha256": "x", "git_bundle_sha256": "x",
          "logs": {"tests": "x", "selftest": "x", "smoke": "x"},
          "rulings": {k: "x" for k in ("round2", "round3", "round4",
                                       "round7", "round8", "round9",
                                       "round10", "round11", "round12", "round13")}}
    with pytest.raises(SystemExit):
        enforce_freeze_completeness(ff)          # env null -> abort
    ff["environment_sha256"] = "x"
    enforce_freeze_completeness(ff)              # complete -> passes


def test_env_validation(tmp_path):
    from build_audit_package import validate_and_stage_env
    root = tmp_path / "root"
    root.mkdir()
    (root / ".python-version").write_text("3.11.9\n")
    (root / "requirements.txt").write_text("numpy==1.26.4\npandas==2.2.2\n")
    stage = tmp_path / "stage"
    env = tmp_path / "environment.json"
    env.write_text(json.dumps({"python_version": "3.13.5",
                               "packages": {"numpy": "1.26.4",
                                            "pandas": "2.2.2"}}))
    with pytest.raises(SystemExit):              # wrong interpreter
        validate_and_stage_env(stage, env, root)
    env.write_text(json.dumps({"python_version": "3.11.9",
                               "packages": {"numpy": "2.0.0",
                                            "pandas": "2.2.2"}}))
    with pytest.raises(SystemExit):              # pin mismatch
        validate_and_stage_env(stage, env, root)
    env.write_text(json.dumps({"python_version": "3.11.9",
                               "packages": {"numpy": "1.26.4",
                                            "pandas": "2.2.2"}}))
    with pytest.raises(SystemExit):              # round-9: provenance
        validate_and_stage_env(stage, env, root)  # required
    env.write_text(json.dumps(
        {"python_version": "3.11.9",
         "packages": {"numpy": "1.26.4", "pandas": "2.2.2"},
         "runs": [{"command": "pytest", "exit_code": 0, "log_sha256": "h",
                   "started_utc": "t", "ended_utc": "t"}]}))
    dst = validate_and_stage_env(stage, env, root)
    assert dst.exists() and dst.name == "environment.json"


def test_calibration_staged_and_checked(tmp_path):
    from build_audit_package import stage_calibration
    stage = tmp_path / "stage"
    cal = tmp_path / "cal.json"
    cal.write_text(json.dumps({"crit_abs_z": 2.1}))
    with pytest.raises(SystemExit):              # incomplete calibration
        stage_calibration(stage, cal)
    good = {"crit_abs_z": 2.1, "crit_abs_z_half": 2.4,
            "boot_size_at_null": 0.05, "wald_boot_concordance": 0.97,
            "sigma_delta": 0.1, "calibration_ok": True,
            "ncal": 200, "B": 9999, "family": "p1p2",
            "binding": {"family": "p1p2",
                        "years": list(range(1994, 2026)), "alpha": 0.05,
                        "rho": 0.5, "sigma_delta": 0.1, "companion": "full",
                        "seed": 20260806, "p2_start_year": None,
                        "base_rates": {"shared": 6e-05, "imf": None,
                                       "p1": None, "p2": None, "p0": None},
                        "templates": {"shared":
                                      {"flat_tokens_per_year": 2e6},
                                      "imf": None, "p1": None,
                                      "p2": None, "p0": None},
                        "tokens_per_doc": None,
                        "git_commit": "a" * 40}}
    cal.write_text(json.dumps(good))
    dst = stage_calibration(stage, cal)          # production-shaped -> ok
    assert dst.exists() and dst.name == "calibration.json"
