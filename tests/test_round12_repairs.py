"""Round-12 test file — 9 tests. Old-commit (1b71b4f) matrix, recomputed
round-13: 7 FAIL + 2 PASS. The two passing arms are behavior-
preservation on 1b71b4f, named here and docstring-marked below:
test_canonical_string_ids_still_pass (preservation on both old commits)
and test_sproll_archive_ignores_forged_text (preservation on 1b71b4f;
it FLIPS against the pre-C30 commit 10266ba, whose text-sourced
archiving would write the forged text). Every other test fails on
1b71b4f."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import pytest

import s01_fetch_metadata as s01
from s09a_imf_articleiv_frame import fetch_live_sproll

_CFG = {"api": {"base_url": "http://f", "rows_per_page": 5, "format": "json",
                "lang_exact": "English", "fields": ["id"], "max_retries": 1,
                "timeout": 1, "backoff_base": 1, "sleep_seconds": 0}}
_B = {"docty": "X", "count": "5", "display_title": "A",
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


def _ids_session(ids):
    docs = {f"D{i}": dict(_B, id=x) for i, x in enumerate(ids)}
    class S:
        def get(self, u, params=None, timeout=None):
            return _FR({"total": len(ids), "documents": docs})
    return S()


# --------------------- R12-A: the REAL ok=false artifact meets the gate ---
def _mk_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "x"],
                   cwd=repo, check=True)
    return repo


def _frozen_false(repo):
    """A FULLY VALID production-shaped calibration_ok=false artifact —
    the reviewer's required fixture class."""
    subprocess.run([sys.executable, str(ROOT / "src" / "mde_sim.py"),
                    "--mode", "calibrate", "--sigma-delta", "0.1",
                    "--ncal", "2", "--B", "19", "--out", "real.json"],
                   cwd=repo, check=True, capture_output=True, timeout=600)
    cal = json.loads((repo / "real.json").read_text())
    cal.update(ncal=200, B=9999)                  # calibration_ok stays false
    f = repo / "frozen.json"
    f.write_text(json.dumps(cal))
    return f


def _curve(repo, extra):
    return subprocess.run(
        [sys.executable, str(ROOT / "src" / "mde_sim.py"), "--mode",
         "curve", "--family", "p1p2", "--theta-grid", "0.0:0.0:1.0",
         "--reps", "2", "--B", "19", "--sigma-delta", "0.1",
         "--calib-json", "frozen.json"] + extra,
        capture_output=True, text=True, cwd=repo, timeout=600)


def test_false_artifact_without_hash_aborts(tmp_path):
    repo = _mk_repo(tmp_path)
    _frozen_false(repo)
    r = _curve(repo, [])
    assert r.returncode != 0
    assert "--calib-expected-sha256" in r.stderr
    assert "curve decision engine" not in r.stdout


def test_false_artifact_with_hash_verifies_and_runs_nested(tmp_path):
    repo = _mk_repo(tmp_path)
    f = _frozen_false(repo)
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    r = _curve(repo, ["--calib-expected-sha256", sha])
    assert r.returncode == 0, r.stderr
    assert f"calibration artifact sha256 verified: {sha}" in r.stdout
    assert "curve decision engine: full_nested_pass_p" in r.stdout
    assert "engine=full_nested_pass_p" in r.stdout.strip().splitlines()[-1]


def test_schema_broken_false_artifact_aborts_despite_hash(tmp_path):
    repo = _mk_repo(tmp_path)
    f = _frozen_false(repo)
    cal = json.loads(f.read_text())
    cal["surprise"] = 1                           # the reviewer's probe
    cal["binding"]["years"] = [1994, 1994]
    f.write_text(json.dumps(cal, sort_keys=True))
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    r = _curve(repo, ["--calib-expected-sha256", sha])
    assert r.returncode != 0
    assert "calibration schema" in r.stderr
    assert "verified" not in r.stdout


def test_false_artifact_with_wrong_hash_aborts(tmp_path):
    repo = _mk_repo(tmp_path)
    _frozen_false(repo)
    r = _curve(repo, ["--calib-expected-sha256", "0" * 64])
    assert r.returncode != 0
    assert "does not match" in r.stderr


# ----------------------------- R12-B: canonical string ids ---------------
def test_int_id_is_a_schema_failure():
    with pytest.raises(RuntimeError):
        s01.fetch_stratum_year(_ids_session([1, "1"]), _CFG, ["X"], 2024)


def test_whitespace_variant_id_is_a_schema_failure():
    with pytest.raises(RuntimeError):
        s01.fetch_stratum_year(_ids_session(["1", " 1 "]), _CFG, ["X"],
                               2024)


def test_canonical_string_ids_still_pass():
    """Behavior preservation: the honest path is untouched."""
    recs = s01.fetch_stratum_year(_ids_session(["1", "2"]), _CFG, ["X"],
                                  2024)
    assert [r["id"] for r in recs] == ["1", "2"]


# ------------------------- R12-C: log byte column + transport truth -------
class _SP2:
    """text is a deliberate FORGERY of the transport bytes (wrong-charset
    simulation): archiving must come from content, never text."""
    def __init__(self, pages):
        self.pages, self.n = pages, 0
    def get(self, url, timeout=None):
        self.n += 1
        class R:
            pass
        r = R()
        r.status_code = 200
        body = self.pages[min(self.n - 1, len(self.pages) - 1)]
        r.content = body
        r.text = body.decode("utf-8").replace("Kenya", "KENYA-FORGED")
        return r


def test_sproll_archive_ignores_forged_text(tmp_path):
    """Behavior preservation on 1b71b4f (byte-sourced archiving already
    present); FLIPS against 10266ba, whose r.text-sourced archiving
    would persist the forgery."""
    body = (_ROW + "<div>caf\u00e9 marker</div>").encode("utf-8")
    fetch_live_sproll(_SP2([body, "<div>No results found</div>".encode()]),
                      tmp_path, tmp_path / "l.csv", sleep=0)
    assert (tmp_path / "sproll_page_0001.html").read_bytes() == body


def test_sproll_log_bytes_column_counts_bytes(tmp_path):
    body = (_ROW + "<div>caf\u00e9\u00e9\u00e9 marker</div>").encode("utf-8")
    fetch_live_sproll(_SP2([body, "<div>No results found</div>".encode()]),
                      tmp_path, tmp_path / "l.csv", sleep=0)
    row1 = [ln for ln in (tmp_path / "l.csv").read_text().splitlines()
            if "sproll_page_0001" in ln][0]
    assert str(len(body)) in row1                 # bytes, not characters
    assert len(body) != len(body.decode("utf-8"))  # fixture is multi-byte
