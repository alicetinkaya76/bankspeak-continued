"""Round-10 flip regressions: every reviewer probe from ROUND10 must stay
dead. Flip tests FAIL on commit f24e0ef (the reviewed object)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
import numpy as np
import pytest

import s01_fetch_metadata as s01
from s09a_imf_articleiv_frame import fetch_live_sproll
from mde_sim import parse_years

_CFG = {"api": {"base_url": "http://f", "rows_per_page": 1, "format": "json",
                "lang_exact": "English", "fields": ["id"], "max_retries": 1,
                "timeout": 1, "backoff_base": 1, "sleep_seconds": 0}}
_DOC = {"id": "1", "docty": "X", "count": "5", "display_title": "A",
        "docdt": "2024-01-01T00:00:00Z", "repnb": "R1", "volnb": "1"}
_ROW = ('<a href="/p/a1">Kenya: 2024 Article IV Consultation; IMF Country '
        'Report No. 24/001</a> <span>July 10, 2024</span>')


class _FR:
    def __init__(self, payload):
        self._p = payload
        self.status_code = 200
        self.text = json.dumps(payload)
        self.content = self.text.encode()
    def json(self):
        return self._p


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


# ------------------------------------------------- R10-1: SPROLL symmetry --
def test_sproll_rerun_raises_and_preserves(tmp_path):
    df = fetch_live_sproll(_SP([_ROW, "<div>No results found</div>"]),
                           tmp_path, tmp_path / "l.csv", sleep=0)
    assert len(df) == 1
    before = (tmp_path / "sproll_page_0001.html").read_bytes()
    log_before = (tmp_path / "l.csv").read_text()
    with pytest.raises(RuntimeError):             # run-immutable target
        fetch_live_sproll(_SP([_ROW, "<div>No results found</div>"]),
                          tmp_path, tmp_path / "l.csv", sleep=0)
    assert (tmp_path / "sproll_page_0001.html").read_bytes() == before
    assert (tmp_path / "l.csv").read_text() == log_before


def test_sproll_log_is_append_only(tmp_path):
    log = tmp_path / "l.csv"
    log.write_text("PRIOR-HISTORY-LINE\n")        # pre-existing history
    fetch_live_sproll(_SP([_ROW, "<div>No results found</div>"]),
                      tmp_path, log, sleep=0)
    txt = log.read_text()
    assert txt.startswith("PRIOR-HISTORY-LINE")   # never truncated
    assert "sproll_page_0001.html" in txt


def test_sproll_bare_anchor_terminal_raises(tmp_path):
    with pytest.raises(RuntimeError):             # <a> without space
        fetch_live_sproll(_SP([_ROW, "<a>No results found</a>"]),
                          tmp_path, tmp_path / "l.csv", sleep=0)


def test_sproll_newline_anchor_terminal_raises(tmp_path):
    with pytest.raises(RuntimeError):
        fetch_live_sproll(_SP([_ROW, "<a\nhref='/x'>No results found</a>"]),
                          tmp_path, tmp_path / "l.csv", sleep=0)


# -------------------------------------------------- R10-1b: WB unique ids --
def test_duplicate_ids_across_pages_raise():
    class S:
        def __init__(self):
            self.n = 0
        def get(self, u, params=None, timeout=None):
            self.n += 1
            key = f"D{self.n}"
            return _FR({"total": 2, "documents": {key: dict(_DOC)}})
    with pytest.raises(RuntimeError):
        s01.fetch_stratum_year(S(), _CFG, ["X"], 2024)


# --------------------------------------------- R10-2: template/binding fix --
def _calibrate(tmp_path, name, extra):
    out = tmp_path / name
    r = subprocess.run([sys.executable, str(ROOT / "src" / "mde_sim.py"),
                        "--mode", "calibrate", "--years", "2018-2025",
                        "--sigma-delta", "0.05", "--ncal", "2", "--B", "19",
                        "--out", str(out)] + extra,
                       capture_output=True, text=True, cwd=ROOT, timeout=600)
    return r, out


def test_file_based_template_binding_works(tmp_path):
    t = tmp_path / "cells.csv"
    t.write_text("year,tokens\n" +
                 "\n".join(f"{y},1000000" for y in range(2018, 2026)))
    r, out = _calibrate(tmp_path, "c.json", ["--cells-template", str(t)])
    assert r.returncode == 0, r.stderr             # the Path NameError probe
    b = json.loads(out.read_text())["binding"]
    assert b["templates"]["shared"]["sha256"] == hashlib.sha256(
        t.read_bytes()).hexdigest()


def test_years_with_calendar_gaps():
    assert list(parse_years("2018,2020")) == [2018, 2020]
    assert list(parse_years("1994-1996,1999")) == [1994, 1995, 1996, 1999]
    with pytest.raises(SystemExit):
        parse_years("2020,2018")                  # disorder
    with pytest.raises(SystemExit):
        parse_years("2018,2018")                  # duplicate


def test_binding_carries_full_year_vector(tmp_path):
    r, out = _calibrate(tmp_path, "g.json",
                        ["--years", "1994-2000,2005-2025"])
    assert r.returncode == 0, r.stderr
    ys = json.loads(out.read_text())["binding"]["years"]
    assert ys == list(range(1994, 2001)) + list(range(2005, 2026))
    assert 2003 not in ys                          # the gap is real


def test_tokens_per_doc_enters_binding(tmp_path):
    t = tmp_path / "docs.csv"
    t.write_text("year,docs\n" +
                 "\n".join(f"{y},100" for y in range(2018, 2026)))
    ra, oa = _calibrate(tmp_path, "a.json",
                        ["--cells-template", str(t),
                         "--tokens-per-doc", "1000"])
    rb, ob = _calibrate(tmp_path, "b.json",
                        ["--cells-template", str(t),
                         "--tokens-per-doc", "2000"])
    assert ra.returncode == 0 and rb.returncode == 0
    ba = json.loads(oa.read_text())["binding"]
    bb = json.loads(ob.read_text())["binding"]
    assert ba != bb and ba["tokens_per_doc"] == 1000.0


# ------------------------------- R10-3: packaged calibration is exclusive --
def test_forged_pilot_cannot_open_wald(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "x"],
                   cwd=repo, check=True)
    r0 = subprocess.run([sys.executable, str(ROOT / "src" / "mde_sim.py"),
                        "--mode", "calibrate", "--sigma-delta", "0.1",
                        "--ncal", "2", "--B", "19", "--out", "real.json"],
                       capture_output=True, text=True, cwd=repo, timeout=600)
    assert r0.returncode == 0, r0.stderr
    cal = json.loads((repo / "real.json").read_text())
    cal.update(ncal=1, B=19, calibration_ok=True,
               crit_abs_z=0.0, crit_abs_z_half=0.0)
    (repo / "forged.json").write_text(json.dumps(cal))
    r = subprocess.run([sys.executable, str(ROOT / "src" / "mde_sim.py"),
                        "--mode", "curve", "--family", "p1p2",
                        "--theta-grid", "0.0:0.0:1.0", "--reps", "2",
                        "--B", "19", "--sigma-delta", "0.1",
                        "--calib-json", "forged.json"],
                       capture_output=True, text=True, cwd=repo, timeout=600)
    assert r.returncode != 0                      # round-12: gate aborts
    assert "--calib-expected-sha256" in r.stderr
    import hashlib as _h
    sha = _h.sha256((repo / "forged.json").read_bytes()).hexdigest()
    r2 = subprocess.run([sys.executable, str(ROOT / "src" / "mde_sim.py"),
                         "--mode", "curve", "--family", "p1p2",
                         "--theta-grid", "0.0:0.0:1.0", "--reps", "2",
                         "--B", "19", "--sigma-delta", "0.1",
                         "--calib-json", "forged.json",
                         "--calib-expected-sha256", sha],
                        capture_output=True, text=True, cwd=repo,
                        timeout=600)
    assert r2.returncode != 0
    assert "production sizes" in r2.stderr
    assert "wald_shortcut" not in r.stdout + r2.stdout


def test_calib_expected_sha_pins_the_artifact(tmp_path):
    cal = {"crit_abs_z": 2.0, "crit_abs_z_half": 2.4,
           "boot_size_at_null": 0.05, "wald_boot_concordance": 0.99,
           "calibration_ok": True, "ncal": 200, "B": 9999,
           "sigma_delta": 0.1}
    p = tmp_path / "c.json"
    p.write_text(json.dumps(cal))
    r = subprocess.run([sys.executable, str(ROOT / "src" / "mde_sim.py"),
                        "--mode", "curve", "--family", "p1p2",
                        "--theta-grid", "0.0:0.0:1.0", "--reps", "2",
                        "--B", "19", "--sigma-delta", "0.1",
                        "--calib-json", str(p),
                        "--calib-expected-sha256", "0" * 64],
                       capture_output=True, text=True, cwd=ROOT, timeout=600)
    assert r.returncode != 0                      # round-12: gate aborts
    assert "does not match --calib-expected-sha256" in r.stderr
    assert "curve decision engine" not in r.stdout


# --------------------------------------------- R10-4: packager fail-closed --
def _prod_cal(**over):
    cal = {"crit_abs_z": 2.1, "crit_abs_z_half": 2.4,
           "boot_size_at_null": 0.05, "wald_boot_concordance": 0.97,
           "sigma_delta": 0.1, "calibration_ok": False,
           "ncal": 200, "B": 9999, "family": "p1p2",
           "binding": {"family": "p1p2", "years": list(range(1994, 2026)),
                       "alpha": 0.05, "rho": 0.5, "sigma_delta": 0.1,
                       "companion": "full", "seed": 20260806,
                       "p2_start_year": None,
                       "base_rates": {"shared": 6e-05, "imf": None,
                                      "p1": None, "p2": None, "p0": None},
                       "templates": {"shared":
                                     {"flat_tokens_per_year": 2e6},
                                     "imf": None, "p1": None,
                                     "p2": None, "p0": None},
                       "tokens_per_doc": None, "git_commit": "a" * 40}}
    cal.update({k: v for k, v in over.items() if not k.startswith("b_")})
    for k, v in over.items():
        if k.startswith("b_"):
            cal["binding"][k[2:]] = v
    return cal


def _stage(tmp_path, cal):
    from build_audit_package import stage_calibration
    c = tmp_path / "cal.json"
    c.write_text(json.dumps(cal))
    return stage_calibration(tmp_path / "stage", c)


def test_packager_rejects_nan_and_inf(tmp_path):
    with pytest.raises(SystemExit):
        _stage(tmp_path, _prod_cal(crit_abs_z=float("nan")))
    with pytest.raises(SystemExit):
        _stage(tmp_path, _prod_cal(crit_abs_z_half=-1.0))
    with pytest.raises(SystemExit):
        _stage(tmp_path, _prod_cal(sigma_delta=float("inf")))


def test_packager_requires_p2_start_year_key(tmp_path):
    cal = _prod_cal()
    del cal["binding"]["p2_start_year"]
    with pytest.raises(SystemExit):
        _stage(tmp_path, cal)


def test_packager_rejects_mistyped_binding(tmp_path):
    with pytest.raises(SystemExit):
        _stage(tmp_path, _prod_cal(b_alpha="bad"))
    with pytest.raises(SystemExit):
        _stage(tmp_path, _prod_cal(b_years="1994-2025"))
    with pytest.raises(SystemExit):
        _stage(tmp_path, _prod_cal(b_base_rates="nope"))
    _stage(tmp_path, _prod_cal())                 # well-typed still stages


def test_calibration_bound_to_recorded_run(tmp_path):
    from build_audit_package import crosscheck_calibration_run
    cal = tmp_path / "calibration.json"
    cal.write_text("{}")
    sha = hashlib.sha256(b"{}").hexdigest()
    env = tmp_path / "environment.json"
    env.write_text(json.dumps({"runs": [
        {"command": "calibrate", "exit_code": 0, "log_sha256": "x",
         "artifact_sha256": sha, "started_utc": "t", "ended_utc": "t"}]}))
    crosscheck_calibration_run(env, cal)          # bound -> ok
    env.write_text(json.dumps({"runs": [
        {"command": "calibrate", "exit_code": 1, "log_sha256": "x",
         "artifact_sha256": sha, "started_utc": "t", "ended_utc": "t"}]}))
    with pytest.raises(SystemExit):               # nonzero exit
        crosscheck_calibration_run(env, cal)


def test_run_evidence_covers_all_four_steps():
    sys.path.insert(0, str(ROOT / "tools"))
    import run_evidence
    steps = run_evidence.build_steps("0.1")
    names = [s[0] for s in steps]
    assert names == ["pytest.log", "selftest.log", "smoke.log",
                     "calibrate.log"]
    assert steps[3][2] == "calibration_pinned.json"
    assert "--B" in steps[3][1] and "9999" in steps[3][1]
