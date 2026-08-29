"""Round-13 test file — the archived reproducer regression (C38) plus the
fossil-template guard exercised via the generalized record test in
test_round11_repairs. The reproducer test FAILS on commit d9ddef5, whose
archived script dies on the first expected ABORT under set -e."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
import pytest


def test_archived_reproducer_prints_all_four_verdicts(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "x"],
                   cwd=repo, check=True)
    (repo / "src").mkdir()
    for f in (ROOT / "src").glob("*.py"):
        shutil.copy2(f, repo / "src" / f.name)
    subprocess.run([sys.executable, "src/mde_sim.py", "--mode", "calibrate",
                    "--sigma-delta", "0.1", "--ncal", "2", "--B", "19",
                    "--out", "real.json"],
                   cwd=repo, check=True, capture_output=True, timeout=600)
    cal = json.loads((repo / "real.json").read_text())
    cal.update(ncal=200, B=9999)                  # calibration_ok stays false
    (repo / "frozen.json").write_text(json.dumps(cal))
    # PYTHON, not PATH. The script falls back to bare `python`, so without this
    # the test silently measures whichever interpreter happens to be first on
    # PATH -- here a pyenv 3.11.9 whose statsmodels is ABI-mismatched against
    # its numpy ("dtype size changed ... expected 96, got 88"). Both mde_sim
    # runs then die on import, A1 prints rc=1/rc=1, and the failure reads as a
    # reproducer regression when nothing in the repository moved. The script
    # already offers the override; the test simply has to use it.
    env = {**os.environ, "PYTHON": sys.executable}
    r = subprocess.run(["bash", str(ROOT / "docs" /
                                    "reproduce_round12_blockers.sh"),
                        str(repo), str(repo / "frozen.json")],
                       capture_output=True, text=True, timeout=900, env=env)
    out = r.stdout
    assert "A1 NOT REPRODUCED" in out, out + r.stderr
    assert "A2 NOT REPRODUCED" in out
    assert out.count("REJECTED") >= 2
    assert "B int-vs-string REJECTED" in out
    assert "B trim-variant REJECTED" in out
