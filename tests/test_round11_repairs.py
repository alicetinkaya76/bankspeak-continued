"""Round-11 test file — 16 tests. Old-commit (10266ba) matrix, recomputed
round-13: 13 FAIL + 3 PASS. The three passing arms are behavior-
preservation / layer-attribution, named here and docstring-marked below:
test_attribute_only_anchor_variants,
test_sproll_archives_verbatim_transport_bytes,
test_schema_accepts_real_calibrate_output. Every other test is a flip
that fails on 10266ba."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
import pytest

import s01_fetch_metadata as s01
from s09a_imf_articleiv_frame import fetch_live_sproll, page_has_anchor
from calib_schema import validate_calibration

_CFG = {"api": {"base_url": "http://f", "rows_per_page": 5, "format": "json",
                "lang_exact": "English", "fields": ["id"], "max_retries": 3,
                "timeout": 1, "backoff_base": 1, "sleep_seconds": 0}}
_DOC = {"id": "1", "docty": "X", "count": "5", "display_title": "A",
        "docdt": "2024-01-01T00:00:00Z", "repnb": "R1", "volnb": "1"}
_ROW = ('<a href="/p/a1">Kenya: 2024 Article IV Consultation; IMF Country '
        'Report No. 24/001</a> <span>July 10, 2024</span>')


class _BR:
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


class _SP:
    def __init__(self, pages):
        self.pages, self.n = pages, 0
    def get(self, url, timeout=None):
        self.n += 1
        class R:
            pass
        r = R()
        r.status_code = 200
        body = self.pages[min(self.n - 1, len(self.pages) - 1)]
        if isinstance(body, bytes):
            r.content = body
            r.text = body.decode("utf-8", errors="replace")
        else:
            r.text = body
            r.content = body.encode()
        return r


# ---------------------------------------------- R11-2a: structural anchor --
def test_self_closing_anchor_is_an_anchor(tmp_path):
    assert page_has_anchor("<a/>No results found")
    with pytest.raises(RuntimeError):
        fetch_live_sproll(_SP([_ROW, "<a/>No results found"]),
                          tmp_path, tmp_path / "l.csv", sleep=0)


def test_attribute_only_anchor_variants():
    """Behavior preservation / layer attribution: plain-div and attribute
    variants behave identically on the old commit."""
    assert page_has_anchor("<A HREF='/x'>No results</A>")
    assert page_has_anchor("<a\ndata-x=1>No results</a>")
    assert not page_has_anchor("<div>No results found</div>")


# ------------------------------------------------ R11-2b: canonical ids ---
def test_record_without_id_raises():
    D = {k: v for k, v in _DOC.items() if k != "id"}
    class S:
        def get(self, u, params=None, timeout=None):
            return _BR({"total": 1, "documents": {"D1": dict(D)}})
    with pytest.raises(RuntimeError):
        s01.fetch_stratum_year(S(), _CFG, ["X"], 2024)


def test_record_with_blank_id_raises():
    class S:
        def get(self, u, params=None, timeout=None):
            return _BR({"total": 1,
                        "documents": {"D1": dict(_DOC, id="   ")}})
    with pytest.raises(RuntimeError):
        s01.fetch_stratum_year(S(), _CFG, ["X"], 2024)


# ------------------------------------------- R11-2c: retry-attempt bodies --
def test_retried_bodies_reach_the_attempt_hook():
    seq = [_BR(raw=b"ERR-500-BODY-1", status=500),
           _BR(raw=b"ERR-503-BODY-2", status=503),
           _BR({"total": 1, "documents": {"D1": dict(_DOC)}})]
    class S:
        def __init__(self):
            self.i = 0
        def get(self, u, params=None, timeout=None):
            r = seq[self.i]
            self.i += 1
            return r
    got = []
    recs = s01.fetch_stratum_year(
        S(), _CFG, ["X"], 2024,
        attempt_hook=lambda p, raw, st: got.append((st, raw)))
    assert len(recs) == 1
    assert got == [(500, b"ERR-500-BODY-1"), (503, b"ERR-503-BODY-2")]


def test_retried_response_without_content_raises():
    class R:
        status_code = 500
        text = "err"
    class S:
        def get(self, u, params=None, timeout=None):
            return R()
    with pytest.raises(RuntimeError):
        s01.fetch_stratum_year(S(), _CFG, ["X"], 2024,
                               attempt_hook=lambda p, raw, st: None)


# --------------------------------------------- R11-2d: SPROLL byte truth ---
def test_sproll_archives_verbatim_transport_bytes(tmp_path):
    """Behavior preservation: a valid UTF-8 body round-trips identically
    on the old decode->encode path, so this arm passes on 10266ba; the
    transport-forgery flip lives in test_round12_repairs."""
    body = (_ROW + "<div>marker</div>").encode("utf-8")
    df = fetch_live_sproll(
        _SP([body, "<div>No results found</div>"]),
        tmp_path, tmp_path / "l.csv", sleep=0)
    assert len(df) == 1
    assert (tmp_path / "sproll_page_0001.html").read_bytes() == body


def test_sproll_non_utf8_body_fails_closed_after_archiving(tmp_path):
    body16 = (_ROW).encode("utf-16")           # not valid UTF-8
    with pytest.raises(RuntimeError):
        fetch_live_sproll(_SP([body16]), tmp_path, tmp_path / "l.csv",
                          sleep=0)
    assert (tmp_path / "sproll_page_0001.html").read_bytes() == body16


# ------------------------------------- R11-1: mandatory calibration hash ---
def _mk_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "x"],
                   cwd=repo, check=True)
    return repo


def _forge_production(repo):
    subprocess.run([sys.executable, str(ROOT / "src" / "mde_sim.py"),
                    "--mode", "calibrate", "--sigma-delta", "0.1",
                    "--ncal", "2", "--B", "19", "--out", "real.json"],
                   cwd=repo, check=True, capture_output=True, timeout=600)
    cal = json.loads((repo / "real.json").read_text())
    cal.update(ncal=200, B=9999, calibration_ok=True,
               crit_abs_z=1e-9, crit_abs_z_half=1e-9)
    (repo / "forged.json").write_text(json.dumps(cal))
    return repo / "forged.json"


def _curve(repo, extra):
    return subprocess.run(
        [sys.executable, str(ROOT / "src" / "mde_sim.py"), "--mode",
         "curve", "--family", "p1p2", "--theta-grid", "0.0:0.0:1.0",
         "--reps", "2", "--B", "19", "--sigma-delta", "0.1",
         "--calib-json", "forged.json"] + extra,
        capture_output=True, text=True, cwd=repo, timeout=600)


def test_external_calibration_without_hash_is_refused(tmp_path):
    repo = _mk_repo(tmp_path)
    _forge_production(repo)
    r = _curve(repo, [])
    assert r.returncode != 0                      # round-12: gate aborts
    assert "--calib-expected-sha256" in r.stderr
    assert "wald_shortcut" not in r.stdout


def test_correct_hash_licenses_and_is_reported(tmp_path):
    repo = _mk_repo(tmp_path)
    forged = _forge_production(repo)
    sha = hashlib.sha256(forged.read_bytes()).hexdigest()
    r = _curve(repo, ["--calib-expected-sha256", sha])
    assert f"calibration artifact sha256 verified: {sha}" in r.stdout
    assert "curve decision engine: wald_shortcut" in r.stdout


# --------------------------------------- R11-3: recursive strict schema ---
def _good_cal():
    return {"crit_abs_z": 2.1, "crit_abs_z_half": 2.4,
            "boot_size_at_null": 0.05, "wald_boot_concordance": 0.97,
            "sigma_delta": 0.1, "calibration_ok": False,
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
                        "tokens_per_doc": None, "git_commit": "a" * 40}}


def test_schema_rejects_reviewer_forgeries():
    c = _good_cal(); c["ncal"] = 200.0
    assert any("REAL positive JSON integer" in e
               for e in validate_calibration(c))
    c = _good_cal(); c["B"] = 9999.0
    assert validate_calibration(c)
    c = _good_cal(); c["binding"]["p2_start_year"] = "not-an-int-or-null"
    assert validate_calibration(c)
    c = _good_cal(); c["binding"]["years"] = [1994, 1994]
    assert any("strictly increasing" in e for e in validate_calibration(c))
    c = _good_cal(); c["binding"]["base_rates"]["shared"] = "not-a-number"
    assert validate_calibration(c)


def test_schema_rejects_unknown_fields_and_bad_templates():
    c = _good_cal(); c["surprise"] = 1
    assert any("unknown top-level" in e for e in validate_calibration(c))
    c = _good_cal(); c["binding"]["extra"] = 1
    assert any("unknown field" in e for e in validate_calibration(c))
    c = _good_cal()
    c["binding"]["templates"]["shared"] = {"sha256": "zz"}
    assert validate_calibration(c)


def test_schema_accepts_real_calibrate_output(tmp_path):
    """Behavior preservation: the schema accepts the engine's own real
    output on any commit that produces it."""
    repo = _mk_repo(tmp_path)
    subprocess.run([sys.executable, str(ROOT / "src" / "mde_sim.py"),
                    "--mode", "calibrate", "--sigma-delta", "0.1",
                    "--ncal", "2", "--B", "19", "--out", "real.json"],
                   cwd=repo, check=True, capture_output=True, timeout=600)
    cal = json.loads((repo / "real.json").read_text())
    assert validate_calibration(cal) == []


def test_packager_rejects_nonstandard_json_constants(tmp_path):
    """Round-12 hardening: the ONLY defect is the NaN literal — every
    other field is a fully valid production artifact, so the rejection
    is attributable to the parse-layer constant ban alone."""
    import re as _re
    from build_audit_package import stage_calibration
    txt = json.dumps(_good_cal())
    txt = _re.sub(r'"crit_abs_z": [0-9.]+', '"crit_abs_z": NaN', txt,
                  count=1)
    c = tmp_path / "cal.json"
    c.write_text(txt)
    with pytest.raises(SystemExit) as ei:
        stage_calibration(tmp_path / "stage", c)
    assert "strict JSON" in str(ei.value)


def test_curve_refuses_schema_broken_even_with_correct_hash(tmp_path):
    repo = _mk_repo(tmp_path)
    forged = _forge_production(repo)
    cal = json.loads(forged.read_text())
    cal["binding"]["years"] = [1994, 1994]        # schema violation
    forged.write_text(json.dumps(cal))
    sha = hashlib.sha256(forged.read_bytes()).hexdigest()
    r = _curve(repo, ["--calib-expected-sha256", sha])
    assert r.returncode != 0                      # round-12: gate aborts
    assert "calibration schema" in r.stderr
    assert "curve decision engine" not in r.stdout


# -------------------------------------------------- R11-4: record v3.2 ----
def test_freeze_record_covers_current_schema():
    """Round-12 evolution (declared in v13 §4): the v3.2-specific check is
    generalized so it can never again pass against a superseded template —
    EXACTLY ONE STAGE_A_FREEZE_RECORD_v*.md ships, and it carries the full
    current schema.

    Stage-B evolution (2026-08-19, docs/DEVIATION_20260819_phase1_sproll.md
    §D6): once the OSF registration was timestamped, the COMPLETED record
    (`STAGE_A_FREEZE_RECORD_COMPLETED_<date>.md`, the template with
    osf_timestamp and osf_registration_doi filled in) legitimately joined
    the template in docs/, and the original glob then read two files as a
    fossil. The fossil guard is therefore split rather than relaxed:
    exactly one VERSIONED template (the fossil condition that round 12
    actually targeted — two templates still fail), at most one COMPLETED
    record, and nothing else matching the family; the schema assertion
    stays on the template, and the completed record must carry the same
    schema with both OSF rows no longer placeholders. Old-commit matrix:
    at 20af74e71d7eedb0a23583d81982f816b645544f this arm PASSES on a tree
    without a completed record (behaviour preserved for the template-only
    case) and FAILS on the current tree, which is the drift it now
    describes.
    """
    fam = sorted((ROOT / "docs").glob("STAGE_A_FREEZE_RECORD*.md"))
    tmpl = [p for p in fam if re.match(r"STAGE_A_FREEZE_RECORD_v[\d.]+\.md$",
                                       p.name)]
    done = [p for p in fam if re.match(
        r"STAGE_A_FREEZE_RECORD_COMPLETED_\d{8}\.md$", p.name)]
    assert len(tmpl) == 1, [p.name for p in fam]    # versionless fossils too
    assert len(done) <= 1, [p.name for p in done]
    assert len(tmpl) + len(done) == len(fam), [p.name for p in fam]
    needles = ("v0.9", "PREREG_v0.10", "PREREG_v0.11_AMENDMENTS",
               "PREREG_v0.12", "C33", "C35", "logs.smoke",
               "rulings.round10", "rulings.round11", "rulings.round12",
               "rulings.round13", "built_utc")
    t = tmpl[0].read_text()
    for needle in needles:
        assert needle in t, needle
    if done:
        d = done[0].read_text()
        for needle in needles:
            assert needle in d, (done[0].name, needle)
        for row in ("osf_timestamp", "osf_registration_doi"):
            line = [ln for ln in d.splitlines() if ln.startswith(f"| {row} ")]
            assert len(line) == 1, (done[0].name, row)
            assert "<" not in line[0], (done[0].name, row, "placeholder")
