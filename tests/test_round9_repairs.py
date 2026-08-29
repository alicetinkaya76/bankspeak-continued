"""Round-9 flip regressions: every reviewer probe from ROUND9 must stay
dead. Each flip test FAILS on commit 7fb89a5 (the reviewed object)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
import numpy as np
import pandas as pd
import pytest

import s01_fetch_metadata as s01
import s13_validation_battery as s13
from s09a_imf_articleiv_frame import fetch_live_sproll
from s09b_wb_p0_frame import apply_docty_verification, build_frame
from mde_sim import load_template, wald_holm2_decide

_CFG = {"api": {"base_url": "http://f", "rows_per_page": 5, "format": "json",
                "lang_exact": "English", "fields": ["id"], "max_retries": 1,
                "timeout": 1, "backoff_base": 1, "sleep_seconds": 0}}
_DOC = {"id": "1", "docty": "X", "count": "5", "display_title": "A",
        "docdt": "2024-01-01T00:00:00Z", "repnb": "R1", "volnb": "1"}


class _BR:
    """Byte-faithful fake response."""
    def __init__(self, payload=None, raw=None, status=200):
        self._p = payload
        self.status_code = status
        self.content = (raw if raw is not None
                        else json.dumps(payload).encode())
        self.text = self.content.decode("utf-8", errors="replace")

    def json(self):
        if self._p is None:
            raise ValueError("bad json")
        return self._p


# ------------------------------------------------ R9-1: byte-verbatim WB --
def test_utf16_transport_archived_byte_identical():
    body = json.dumps({"total": 1, "documents": {"D1": dict(_DOC)}})
    raw16 = body.encode("utf-16")

    class R:
        status_code = 200
        content = raw16
        text = raw16.decode("utf-16")
        def json(self):
            return json.loads(self.text)

    got = {}
    class S:
        def get(self, u, params=None, timeout=None):
            return R()
    s01.fetch_stratum_year(S(), _CFG, ["X"], 2024,
                           page_hook=lambda p, raw: got.update(raw=raw))
    assert got["raw"] == raw16                    # the round-9 probe


def test_malformed_body_archived_before_parse_failure():
    fired = []
    class S:
        def get(self, u, params=None, timeout=None):
            return _BR(payload=None, raw=b"NOT JSON")
    with pytest.raises(ValueError):
        s01.fetch_stratum_year(S(), _CFG, ["X"], 2024,
                               page_hook=lambda p, raw: fired.append(raw))
    assert fired == [b"NOT JSON"]                 # archive precedes parse


def test_schemaless_payload_raises():
    class S:
        def get(self, u, params=None, timeout=None):
            return _BR(payload={})
    with pytest.raises(RuntimeError):
        s01.fetch_stratum_year(S(), _CFG, ["X"], 2024)


def test_declared_total_drift_raises():
    cfg = {"api": dict(_CFG["api"], rows_per_page=1)}
    class S:
        def __init__(self):
            self.n = 0
        def get(self, u, params=None, timeout=None):
            self.n += 1
            if self.n == 1:
                return _BR({"total": 3, "documents": {"D1": dict(_DOC)}})
            return _BR({"total": 1, "documents": {"D2": dict(_DOC)}})
    with pytest.raises(RuntimeError):
        s01.fetch_stratum_year(S(), cfg, ["X"], 2024)


def test_transport_without_content_raises():
    class R:
        status_code = 200
        text = "{}"
        def json(self):
            return {"total": 0, "documents": {}}
    class S:
        def get(self, u, params=None, timeout=None):
            return R()
    with pytest.raises(RuntimeError):
        s01.fetch_stratum_year(S(), _CFG, ["X"], 2024,
                               page_hook=lambda p, raw: None)


def test_rerun_raw_archive_write_once(tmp_path, monkeypatch):
    import utils
    from s09b_wb_p0_frame import fetch_live
    docs = {"total": 1, "documents": {"D1": dict(_DOC)}}

    class S:
        def get(self, u, params=None, timeout=None):
            return _BR(docs)
    monkeypatch.setattr(utils, "session_for", lambda cfg: S())
    raw = tmp_path / "raw"
    dm = [{"genre": "cem", "docty": "X"}]
    df = fetch_live(_CFG, dm, 2024, 2024, raw)
    assert len(df) == 1
    assert (raw / "cem_2024_os0.json").read_bytes() == _BR(docs).content
    with pytest.raises(RuntimeError):             # round-9: run-immutable
        fetch_live(_CFG, dm, 2024, 2024, raw)     # target directory
    assert (raw / "cem_2024_os0.json").read_bytes() == _BR(docs).content


# ------------------------------------------- R9-1b: positive terminal IMF --
_ROW = ('<a href="/p/a1">Kenya: 2024 Article IV Consultation; IMF Country '
        'Report No. 24/001</a> <span>July 10, 2024</span>')


class _SP:
    def __init__(self, pages):
        self.pages, self.n = pages, 0
    def get(self, url, timeout=None):
        self.n += 1
        class R:
            pass
        r = R()
        r.status_code = 200
        r.text = self.pages[min(self.n - 1, len(self.pages) - 1)]
        r.content = r.text.encode()
        return r


def test_sproll_interstitial_marker_raises(tmp_path):
    with pytest.raises(RuntimeError):
        fetch_live_sproll(_SP([_ROW,
                               "<div>Service temporarily unavailable</div>"]),
                          tmp_path, tmp_path / "l.csv", sleep=0)


def test_sproll_unmarked_blank_page_raises(tmp_path):
    with pytest.raises(RuntimeError):
        fetch_live_sproll(_SP([_ROW, "<div>some drifted markup</div>"]),
                          tmp_path, tmp_path / "l.csv", sleep=0)


def test_sproll_positive_terminal_ok(tmp_path):
    df = fetch_live_sproll(_SP([_ROW, "<div>No results found</div>"]),
                           tmp_path, tmp_path / "l.csv", sleep=0)
    assert len(df) == 1


# ------------------------------------------------ R9-1c: docty probe bind --
def _docty_json(tmp_path, probe_hash):
    v = tmp_path / "v.json"
    v.write_text(json.dumps({"verified_utc": "2026-11-01T00:00:00Z",
                             "source": "s00", "probe_sha256": probe_hash,
                             "labels": {"cem": "A", "scd": "B",
                                        "cpf": "C"}}))
    return v


def test_docty_probe_hash_recomputed(tmp_path):
    art = tmp_path / "probe.bin"
    art.write_bytes(b"REAL S00 PROBE")
    v = _docty_json(tmp_path, "ab" * 32)          # well-formed but WRONG
    with pytest.raises(SystemExit):
        apply_docty_verification([{"genre": "cem", "docty": "X"}], str(v),
                                 probe_artifact=str(art))
    v2 = _docty_json(tmp_path,
                     hashlib.sha256(b"REAL S00 PROBE").hexdigest())
    out = apply_docty_verification([{"genre": "cem", "docty": "X"}],
                                   str(v2), probe_artifact=str(art))
    assert out[0]["docty"] == "A"


def test_docty_probe_artifact_required(tmp_path):
    v = _docty_json(tmp_path, "ab" * 32)
    with pytest.raises(SystemExit):
        apply_docty_verification([{"genre": "cem", "docty": "X"}], str(v))


# --------------------------------------- R9-2: family-bound calibration ---
def _mini_calibrate(tmp_path, name, extra):
    out = tmp_path / name
    cmd = [sys.executable, str(ROOT / "src" / "mde_sim.py"),
           "--mode", "calibrate", "--years", "2018-2025",
           "--sigma-delta", "0.05", "--ncal", "4", "--B", "19",
           "--out", str(out)] + extra
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT,
                       timeout=600)
    assert r.returncode == 0, r.stderr
    return json.loads(out.read_text())


def test_p1p2_calibration_binds_p2_inputs(tmp_path):
    a = _mini_calibrate(tmp_path, "a.json", [])
    b = _mini_calibrate(tmp_path, "b.json", ["--base-rate-p2", "0.01"])
    assert a["crit_abs_z"] != b["crit_abs_z"] or \
        a["boot_size_at_null"] != b["boot_size_at_null"] or \
        a["binding"] != b["binding"]              # the invariance probe dies


def test_calibration_carries_binding_block(tmp_path):
    a = _mini_calibrate(tmp_path, "c.json", [])
    b = a["binding"]
    for k in ("family", "years", "alpha", "rho", "sigma_delta", "companion",
              "seed", "base_rates", "templates", "git_commit"):
        assert k in b, k
    assert a["family"] == "p1p2"


def test_cross_family_reuse_refused(tmp_path):
    cal = _mini_calibrate(tmp_path, "d.json", [])
    cal["calibration_ok"] = True                  # force a licensed p1p2 cal
    p = tmp_path / "licensed.json"
    p.write_text(json.dumps(cal))
    import hashlib as _h
    base = [sys.executable, str(ROOT / "src" / "mde_sim.py"),
            "--mode", "curve", "--family", "p0",
            "--years", "2018-2025", "--theta-grid", "0.0:0.0:1.0",
            "--reps", "2", "--B", "19", "--sigma-delta", "0.05",
            "--calib-json", str(p)]
    r = subprocess.run(base, capture_output=True, text=True, cwd=ROOT,
                       timeout=600)
    assert r.returncode != 0                      # round-12: gate ABORTS
    assert "--calib-expected-sha256" in r.stderr
    sha = _h.sha256(p.read_bytes()).hexdigest()
    r2 = subprocess.run(base + ["--calib-expected-sha256", sha],
                        capture_output=True, text=True, cwd=ROOT,
                        timeout=600)
    assert r2.returncode != 0
    assert "binding mismatch" in r2.stderr        # cross-family stays dead
    assert "wald_shortcut" not in r.stdout + r2.stdout


def test_engine_banner_tells_truth_when_refusing(tmp_path):
    cal = {"crit_abs_z": 2.0, "boot_size_at_null": 0.05,
           "wald_boot_concordance": 0.99, "calibration_ok": True,
           "ncal": 4, "B": 19, "sigma_delta": 0.05}   # half + binding absent
    p = tmp_path / "c.json"
    p.write_text(json.dumps(cal))
    r = subprocess.run([sys.executable, str(ROOT / "src" / "mde_sim.py"),
                        "--mode", "curve", "--family", "p1p2",
                        "--years", "2018-2025", "--theta-grid",
                        "0.0:0.0:1.0", "--reps", "2", "--B", "19",
                        "--sigma-delta", "0.05", "--calib-json", str(p)],
                       capture_output=True, text=True, cwd=ROOT, timeout=600)
    assert r.returncode != 0                      # round-12: gate aborts
    assert "--calib-expected-sha256" in r.stderr   # before ANY banner
    assert "curve decision engine" not in r.stdout
    assert "wald_shortcut" not in r.stdout


def test_template_extra_years_and_nonpositive_raise(tmp_path):
    p = tmp_path / "t.csv"
    p.write_text("year,tokens\n2023,1000\n2024,1000\n2025,1000\n")
    with pytest.raises(SystemExit):               # extra year 2025
        load_template(p, np.array([2023, 2024]))
    p2 = tmp_path / "t2.csv"
    p2.write_text("year,tokens\n2023,-10\n2024,0\n")
    with pytest.raises(SystemExit):               # non-positive tokens
        load_template(p2, np.array([2023, 2024]))


def test_calibrated_holm_stepdown_semantics():
    assert wald_holm2_decide(3.0, 2.1, 2.0, 2.5) == (True, True)
    assert wald_holm2_decide(3.0, 1.5, 2.0, 2.5) == (True, False)
    assert wald_holm2_decide(2.4, 2.1, 2.0, 2.5) == (False, False)


# -------------------------------------- R9-3: event-study failure surface --
def test_event_study_propagates_engine_failure(monkeypatch):
    from bootstrap_engine import _mk
    d = _mk(0.3, 300_000)
    real = s13.passe_multi

    def failing(*args, **kw):
        res = real(*args, **kw)
        res = dict(res, governing_ci="failed", method_ci="failed",
                   B_valid_ci=0)
        return res
    monkeypatch.setattr(s13, "passe_multi", failing)
    res = s13.event_study(d, B=29)
    assert res["status"] == "failed"
    assert "no_valid_bootstrap_ci" in res["failure_reasons"]


def test_event_study_zero_valid_ci_is_failed(monkeypatch):
    from bootstrap_engine import _mk
    d = _mk(0.3, 300_000)
    real = s13.passe_multi

    def zeroed(*args, **kw):
        return dict(real(*args, **kw), B_valid_ci=0)
    monkeypatch.setattr(s13, "passe_multi", zeroed)
    res = s13.event_study(d, B=29)
    assert res["status"] == "failed"


def test_event_study_healthy_still_ok():
    from bootstrap_engine import _mk
    res = s13.event_study(_mk(0.3, 300_000), B=29)
    assert res["status"] == "ok" and res["failure_reasons"] == []


# ------------------------------------------- R9-4: packager fail-closed ---
def test_stage_calibration_rejects_reviewer_junk(tmp_path):
    from build_audit_package import stage_calibration
    c = tmp_path / "cal.json"
    c.write_text(json.dumps({"crit_abs_z": "not-a-number",
                             "boot_size_at_null": -7,
                             "calibration_ok": "truthy-string"}))
    with pytest.raises(SystemExit):
        stage_calibration(tmp_path / "stage", c)


def test_stage_calibration_rejects_pilot_B(tmp_path):
    from build_audit_package import stage_calibration
    good = {"crit_abs_z": 2.1, "crit_abs_z_half": 2.4,
            "boot_size_at_null": 0.05, "wald_boot_concordance": 0.97,
            "sigma_delta": 0.1, "calibration_ok": False,
            "ncal": 200, "B": 999,
            "binding": {"family": "p1p2", "years": "x", "alpha": 0.05,
                        "rho": 0.5, "sigma_delta": 0.1, "companion": "full",
                        "seed": 1, "base_rates": {}, "templates": {},
                        "git_commit": "a" * 40}}
    c = tmp_path / "cal.json"
    c.write_text(json.dumps(good))
    with pytest.raises(SystemExit):               # B=999 pilot -> abort
        stage_calibration(tmp_path / "stage", c)


def test_required_ruling_chain_enforced():
    from build_audit_package import enforce_freeze_completeness
    ff = {k: "x" for k in ("zip_sha256", "sha256sums_sha256",
                           "manifest_sha256", "python_version",
                           "python_version_sha256", "requirements_sha256",
                           "requirements_ppl_sha256", "git_commit",
                           "environment_sha256", "calibration_sha256",
                           "git_bundle_sha256")}
    ff.update(zip_bytes=1, zip_entry_count=1, sha256sums_entries=1,
              manifest_rows=1, logs={"tests": "x", "selftest": "x"},
              rulings={"round7": "x"})            # single-key map
    with pytest.raises(SystemExit):
        enforce_freeze_completeness(ff)


def test_env_runs_crosscheck(tmp_path):
    from build_audit_package import crosscheck_env_runs
    env = tmp_path / "environment.json"
    env.write_text(json.dumps({"runs": [
        {"command": "pytest", "exit_code": 0, "log_sha256": "aaa",
         "started_utc": "t", "ended_utc": "t"},
        {"command": "selftest", "exit_code": 1, "log_sha256": "bbb",
         "started_utc": "t", "ended_utc": "t"}]}))
    crosscheck_env_runs(env, {"tests": "aaa"})    # bound + zero-exit -> ok
    with pytest.raises(SystemExit):               # nonzero-exit run
        crosscheck_env_runs(env, {"selftest": "bbb"})
    with pytest.raises(SystemExit):               # unbound log
        crosscheck_env_runs(env, {"tests": "ccc"})


def test_freeze_requires_bundle_flagpair():
    src = (ROOT / "tools" / "build_audit_package.py").read_text()
    assert "--freeze-fields requires --git-bundle" in src
    assert "calibration binding commit" in src    # commit-equality gate
