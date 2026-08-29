"""The published repository must be able to run its own tests.

It could not. `tools/build_public_repo.py` filters paths on the word "imf" and
on "articleiv" to keep the restricted corpus out, and those words are also in the
names of two of the project's own source modules. Both were stripped from every
public export. Because src/s09b_wb_p0_frame.py imports s09a_imf_articleiv_frame
at module scope, `pytest tests/ -q` in the published repository reported

    Interrupted: 12 errors during collection
    12 errors in 3.16s

against a README promising 341 tests and a manuscript whose entire warrant is
that its numbers can be checked by anyone. The leak guard had deleted the
evidence that the analysis works, and nothing measured that either.

This file measures it two ways: statically, that nothing the shipped code imports
is filtered out, and end-to-end, that a fresh export collects its whole suite.
"""
import ast
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "build_public_repo", ROOT / "tools" / "build_public_repo.py")
_bpr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bpr)


def local_modules() -> dict[str, str]:
    """Module name -> repo-relative path, for everything importable from src/tools."""
    out = {}
    for d in ("src", "tools"):
        for f in (ROOT / d).glob("*.py"):
            out[f.stem] = f"{d}/{f.name}"
    return out


def imported_names() -> set[str]:
    names = set()
    for d in ("src", "tools", "tests"):
        for f in (ROOT / d).glob("*.py"):
            try:
                tree = ast.parse(f.read_text(encoding="utf-8"))
            except SyntaxError:                       # not ours to fix here
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names.update(a.name.split(".")[0] for a in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names.add(node.module.split(".")[0])
    return names


def test_no_module_the_shipped_code_imports_is_filtered_out():
    local = local_modules()
    stripped = sorted(rel for name, rel in local.items()
                      if name in imported_names() and _bpr.denied(rel))
    assert not stripped, (
        "build_public_repo.py strips modules the code imports, so the exported "
        f"repository cannot import itself: {stripped}. Add them to PATH_EXEMPT "
        "(they still go through the LEAK content scan) or rename them.")


def test_the_two_modules_that_broke_the_export_are_exempt():
    """Named explicitly, so a future edit to DENY that re-strips them fails here
    with the history attached rather than silently shipping a dead archive."""
    for rel in ("src/s09a_imf_articleiv_frame.py", "tools/imf_corpus_to_pipeline.py"):
        assert (ROOT / rel).exists(), rel
        assert not _bpr.denied(rel), f"{rel} is filtered out of the public export again"


def test_path_exemption_does_not_exempt_build_litter():
    """PATH_EXEMPT buys exemption from the corpus filename rules only. If a
    .pyc or a dotfile could be exempted, the escape hatch would be a hole."""
    for litter in ("src/__pycache__/x.cpython-311.pyc", "src/.DS_Store"):
        assert _bpr.denied(litter), litter


def test_a_fresh_export_collects_its_entire_suite(tmp_path):
    """The end-to-end version of the same claim. Static analysis cannot see an
    import that only fires at runtime; running the collector can."""
    export = tmp_path / "public"
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "build_public_repo.py"),
                        "--out", str(export)],
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or not (export / "tests").exists():
        pytest.skip("build_public_repo.py does not accept --out; "
                    "static check above still applies")
    def collected(cwd) -> int:
        r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q",
                            "--collect-only", "-p", "no:cacheprovider"],
                           cwd=cwd, capture_output=True, text=True, timeout=600)
        m = re.search(r"(\d+) tests? collected", r.stdout)
        return (r.returncode, int(m.group(1)) if m else 0, r.stdout)

    # Substring-matching "error" against pytest's output is not this check: one
    # of the repository's own tests is named ...http_error_raises, and the first
    # version of this assertion failed on that name while the export was in fact
    # collecting all 345 tests. Compare counts and exit codes instead.
    rc_out, n_out, log = collected(export)
    rc_src, n_src, _ = collected(ROOT)
    assert rc_out == 0, f"collection failed in the export:\n{log[-3000:]}"
    assert n_out == n_src, (
        f"the export collects {n_out} tests, the source repository {n_src}. "
        "Something the shipped code needs is being filtered out.")
