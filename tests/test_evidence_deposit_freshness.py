"""The built evidence deposit must carry what its own list says it carries.

Round 20 added eighteen analysis outputs to the deposit list and rebuilt the
zip, and the zip did not change: the packager zipped a staging directory that
only the staging script refreshes, and the staging script was not run. The
inputs to S10.3-S10.9 and Tables 3c-5d were therefore on the list and absent
from the deposit, and an external review found it by opening the zip.

These tests read the list and the zip and compare them. They skip, not pass,
when the zip has not been built -- an absent artifact is not a fresh one.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ZIP = ROOT / "build" / "zenodo_evidence_deposit.zip"

# Outputs a reviewer was told to reproduce from and could not find.
LOAD_BEARING = [
    "data/analysis/block_origin_enumeration.json",      # Table 5c
    "data/analysis/functional_form_sensitivity.json",   # Table 5d
    "data/analysis/joint_holm_calibration.json",        # S10.4
    "data/analysis/ar_exclusion_classes.json",          # Tables 3c, 3d
    "data/analysis/imf_frame_publication.csv",          # S10.7
    "data/analysis/tier2_item_provenance.json",         # S10.8
]


def _names():
    if not ZIP.exists():
        pytest.skip("evidence deposit not built")
    with zipfile.ZipFile(ZIP) as z:
        return set(z.namelist())


def _present(names, rel):
    return any(n.endswith("/" + rel) for n in names)


def test_every_listed_file_that_exists_is_in_the_zip():
    from prepare_zenodo_deposit import INCLUDE_FILES as FILES
    names = _names()
    missing = [rel for rel in FILES if (ROOT / rel).exists() and not _present(names, rel)]
    assert not missing, missing


@pytest.mark.parametrize("rel", LOAD_BEARING)
def test_load_bearing_outputs_are_deposited(rel):
    if not (ROOT / rel).exists():
        pytest.skip(f"{rel} not built")
    assert _present(_names(), rel), rel


def test_the_deposited_block_origin_file_is_the_time_ordered_one():
    """Not merely present: the corrected computation, not the rotated one."""
    import json
    names = _names()
    hit = next((n for n in names
                if n.endswith("/data/analysis/block_origin_enumeration.json")), None)
    if hit is None:
        pytest.skip("block-origin output not deposited")
    with zipfile.ZipFile(ZIP) as z:
        d = json.loads(z.read(hit))
    assert d["panels"]["P1"]["1"]["support"] == 1024
    assert "circular_rotation_as_previously_published" in d["panels"]["P1"]["1"]
