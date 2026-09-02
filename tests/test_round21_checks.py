"""Pin the round-21 correction: a shifted block origin keeps time order.

The block-origin sensitivity (Table 5c) and the origin sweep in Table 5d were
computed by ROTATING the year vector before blocking. That kept nine blocks and
a support of 512 at every offset, and it put the first year of the series in the
same block as the last -- at offset 1 the trailing block was [2024, 2025, 1999].
A block bootstrap groups dependent neighbours; wrapping manufactures a
neighbour. An external review reconstructed every cell from the deposited
panels, found they reproduced only under rotation, and gave the time-ordered
values. Those are now the reported ones.

Nothing about the frozen origin changed -- it never wrapped -- so the
preregistered result is exactly what it was. What these tests hold in place is
the shifted-origin arithmetic and the sentences that depend on it, because the
rotation was the natural thing to write (np.roll is one line) and could be
written again.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

PAPER = ROOT / "docs" / "PAPER_DRAFT_v2.md"
BO = ROOT / "data" / "analysis" / "block_origin_enumeration.json"
FFS = ROOT / "data" / "analysis" / "functional_form_sensitivity.json"


def _load(p):
    if not p.exists():
        pytest.skip(f"{p.relative_to(ROOT)} not built")
    return json.loads(p.read_text(encoding="utf-8"))


# ----------------------------------------------------------- the helper --
def test_shifted_origins_never_wrap():
    """The property, stated directly: every block is a run of consecutive
    indices, and the runs tile the series in order."""
    from block_origin_enumeration import time_ordered_blocks
    S = np.arange(27, dtype=float)
    for offset in range(3):
        blocks, bounds = time_ordered_blocks(S, offset)
        assert bounds[0] == 0 and bounds[-1] == 27
        assert bounds == sorted(bounds)
        # each block sums a contiguous slice, so the sum of an arange block is
        # the sum of consecutive integers -- which rotation would break at the
        # seam by summing e.g. 24 + 25 + 0
        for (a, b), val in zip(zip(bounds[:-1], bounds[1:]), blocks):
            assert val == pytest.approx(S[a:b].sum())
        if offset:
            assert bounds[1] == offset          # a short leading block
            assert len(blocks) == 10
        else:
            assert len(blocks) == 9


def test_rotation_and_time_order_agree_only_at_the_frozen_origin():
    d = _load(BO)["panels"]
    for panel in ("P1", "P2"):
        z = d[panel]["0"]
        assert z["p"] == pytest.approx(z["circular_rotation_as_previously_published"]["p"])
        assert z["support"] == 512 and z["n_blocks"] == 9
        for k in ("1", "2"):
            r = d[panel][k]
            assert r["support"] == 1024 and r["n_blocks"] == 10
            assert r["circular_rotation_as_previously_published"]["support"] == 512
            # the last block must end at 2025 and start no earlier than 2024
            lo, hi = r["last_block_years"]
            assert hi == 2025 and lo >= 2024


def test_the_auditors_time_ordered_cells_reproduce():
    """The four values the review computed independently, to the digit."""
    d = _load(BO)["panels"]
    assert d["P1"]["1"]["hits"] == 324 and d["P1"]["1"]["support"] == 1024
    assert d["P1"]["2"]["hits"] == 8 and d["P1"]["2"]["support"] == 1024
    assert d["P2"]["1"]["hits"] == 178
    assert d["P2"]["2"]["hits"] == 38


def test_the_two_year_shift_does_not_leave_p1_where_it_was():
    """The specific false sentence the wrap produced."""
    d = _load(BO)["panels"]["P1"]
    assert d["2"]["p"] < d["0"]["p"]
    t = PAPER.read_text(encoding="utf-8")
    assert "leaves P1 exactly where" not in t


# -------------------------------------------------------------- the sweep --
def test_table_5d_sweep_reports_a_doubled_support_off_the_frozen_origin():
    d = _load(FFS)["panels"]
    for panel in ("P1", "P2"):
        row = d[panel]["as_published"]
        assert "time order" in row["blocking"]
        assert row["support_by_block_origin"] == [512, 1024, 1024]


def test_table_5c_in_the_paper_matches_the_json():
    d = _load(BO)["panels"]
    t = PAPER.read_text(encoding="utf-8")
    for k, label in (("0", "| 0 — preregistered |"), ("1", "| 1 year |"),
                     ("2", "| 2 years |")):
        line = next((l for l in t.splitlines() if l.startswith(label)), None)
        assert line, label
        for panel in ("P1", "P2"):
            r = d[panel][k]
            assert f"{r['hits']}/{r['support']} = {r['p']:.4f}" in line, (label, panel)
    assert re.search(r"\| 1 year \|.*\| 10 \| 1,024 \|", t)


def test_the_paper_states_the_correction_rather_than_hiding_it():
    t = " ".join(PAPER.read_text(encoding="utf-8").split())
    assert "rotated the year vector before blocking" in t
    assert "1999 in the same block as 2024 and 2025" in t


# ------------------------------------------------- disclosure placement --
def test_ai_disclosure_lives_in_the_methods():
    """PLOS wants it in Methods, not in data availability."""
    t = PAPER.read_text(encoding="utf-8")
    i = t.index("### 5.1 Use of AI assistance")
    j = t.index("## 6. Results")
    assert i < j
    body = t[i:j]
    assert "AUTHOR ATTESTATION" in body          # still the author's to sign
    assert "No AI system is an author" in body
    # and section 9 only points at it now
    k = t.index("## 9. Data and code availability")
    assert "Disclosed in §5.1" in t[k:]
