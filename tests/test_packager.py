import sys, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import pytest
from build_audit_package import (_keep, freeze_fields, regeneration_check,
                                 copy_evidence)


def test_keep_excludes_junk_keeps_audit_baks():
    assert _keep(Path("src/x.py"))
    assert _keep(Path("src/s08_its_analysis.py.bak-round4"))
    assert not _keep(Path("src/.DS_Store"))
    assert not _keep(Path("src/__pycache__/x.cpython-311.pyc"))
    assert not _keep(Path("a/b/__pycache__/deep.py"))
    assert not _keep(Path("src/x.pyc"))


def test_freeze_fields_binding(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / ".python-version").write_text("3.11.9\n")
    z = tmp_path / "pkg.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("a.txt", "hello")
    sums = tmp_path / "SHA256SUMS"; sums.write_text("deadbeef  a.txt\n")
    man = tmp_path / "MANIFEST.tsv"; man.write_text("path\tbytes\tsha256\n")
    log = tmp_path / "pytest.log"; log.write_text("48 passed\n")
    ff = freeze_fields(z, sums, man, 1, root, logs={"tests": log})
    assert ff["python_version"] == "3.11.9"
    assert ff["requirements_sha256"] is None               # pins absent -> warned
    assert ff["requirements_lock_sha256"] is None          # optional extra
    assert ff["zip_entry_count"] == 1 and ff["zip_bytes"] > 0
    assert ff["sha256sums_entries"] == 1 and ff["manifest_rows"] == 0
    assert len(ff["zip_sha256"]) == 64 and len(ff["logs"]["tests"]) == 64
    (root / "requirements.txt").write_text("numpy==1.26.4\n")
    (root / "requirements.lock.txt").write_text("numpy==1.26.4\n")
    ff2 = freeze_fields(z, sums, man, 1, root)
    assert len(ff2["requirements_sha256"]) == 64
    assert len(ff2["requirements_lock_sha256"]) == 64


def test_regeneration_check_fails_closed(tmp_path):
    def bad_runner(*a, **k):
        raise RuntimeError("regen broke")
    with pytest.raises(SystemExit):
        regeneration_check(tmp_path, runner=bad_runner)


def test_copy_evidence_missing_log_aborts(tmp_path):
    with pytest.raises(SystemExit):
        copy_evidence(tmp_path / "stage", {"tests": tmp_path / "nope.log"},
                      {}, tmp_path)


def test_copy_evidence_stages_and_binds(tmp_path):
    stage = tmp_path / "stage"; stage.mkdir()
    log = tmp_path / "pytest.log"; log.write_text("50 passed\n")
    rul = tmp_path / "r7.md"; rul.write_text("REJECT\n")
    ev = copy_evidence(stage, {"tests": log}, {"round7": rul}, tmp_path)
    assert (stage / "evidence" / "tests.log").exists()
    assert (stage / "evidence" / "rulings" / "round7.md").exists()
    import zipfile
    z = tmp_path / "p.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("a", "x")
    sums = tmp_path / "S"; sums.write_text("h  a\n")
    man = tmp_path / "M"; man.write_text("path\tbytes\tsha256\n")
    root = tmp_path / "root"; root.mkdir()
    ff = freeze_fields(z, sums, man, 1, root, ev["logs"], ev["rulings"])
    assert len(ff["logs"]["tests"]) == 64
    assert len(ff["rulings"]["round7"]) == 64
    assert ff["git_bundle_sha256"] is None
