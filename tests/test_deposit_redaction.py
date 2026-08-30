"""The deposit must carry what the generators read, and not what the permission
forbids.

The data-availability statement promises that every table regenerates from the
deposit by a named command. It did not: five generator inputs were staged
nowhere, and `make_paper_tables.py` died on a ZeroDivisionError because Table 1's
denominator came from a file the deposit had never heard of.

Four of the five travel unchanged. The fifth, `frozen_sampling_v2.csv`, carries
`display_title` and `pdfurl` for all 1,064 IMF documents — verbatim titles and
imf.org document URLs, the bibliographic frame the permission forbids. The
decision taken was to drop those columns rather than the file, for every row
rather than only the IMF ones, because neither generator reads any of the three
and a whole-column rule cannot leak through a misclassified row.

These tests pin both halves: the redaction removes exactly those columns, and the
check that guards it can still fail.
"""
import importlib.util
import io
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "prepare_zenodo_deposit", ROOT / "tools" / "prepare_zenodo_deposit.py")
_dep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_dep)

FROZEN = ROOT / "data" / "meta" / "frozen_sampling_v2.csv"
needs_frozen = pytest.mark.skipif(
    not FROZEN.exists(),
    reason="needs data/meta/frozen_sampling_v2.csv (deposited redacted, not in git)")


def test_the_redaction_plan_names_the_two_columns_that_carry_imf_material():
    plan = {rel: drop for rel, drop, _ in _dep.REDACT_FILES}
    assert "data/meta/frozen_sampling_v2.csv" in plan
    assert set(plan["data/meta/frozen_sampling_v2.csv"]) == {
        "display_title", "txturl", "pdfurl"}


def test_the_unredacted_original_is_still_hashed():
    """Dropping columns must not cost verifiability: a holder of the licensed
    material has to be able to confirm byte identity with what we analysed."""
    assert "data/meta/frozen_sampling_v2.csv" in _dep.HASH_ONLY_FILES


@needs_frozen
def test_redaction_removes_the_columns_and_keeps_the_rest():
    text = _dep.redact_csv(FROZEN, ("display_title", "txturl", "pdfurl"))
    header = text.splitlines()[0].split(",")
    assert header == ["id", "stratum", "year", "docdt", "repnb"], header

    # RECORDS, not physical lines. 62 of the dropped titles contain embedded
    # newlines, so the source file has 3,864 lines for 3,802 records and the
    # first version of this assertion failed on that gap — reading a correct
    # redaction as a lossy one.
    import csv as _csv
    with FROZEN.open(newline="", encoding="utf-8") as fh:
        n_src = sum(1 for _ in _csv.DictReader(fh))
    n_out = sum(1 for _ in _csv.DictReader(io.StringIO(text)))
    assert n_out == n_src, (n_out, n_src)


@needs_frozen
def test_no_imf_title_or_url_survives_the_redaction():
    text = _dep.redact_csv(FROZEN, ("display_title", "txturl", "pdfurl"))
    for pat, what in _dep.REDACT_MUST_NOT_CONTAIN:
        assert not pat.search(text), what


def test_redaction_refuses_a_plan_that_does_not_match_the_file(tmp_path):
    """A plan naming a column the file does not have would drop nothing and ship
    the file unchanged — a silent no-op where a refusal belongs."""
    f = tmp_path / "x.csv"
    f.write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        _dep.redact_csv(f, ("display_title",))
    assert "no column" in str(e.value)


def test_every_generator_input_is_covered_by_the_deposit():
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_deposit_covers_generators.py")],
        capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
