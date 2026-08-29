"""Offline smoke tests. Sample texts are ORIGINAL synthetic sentences written for this
repo (no scraped WB text is shipped). They imitate registers, nothing more."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from textstats import compute_classic, compute_markers, tokens

OLD_STYLE = (
    "The mission visited the port in March 1958 and inspected the railway to the "
    "mining region. The loan of 20 million dollars will finance forty locomotives "
    "and the repair of the bridge across the river. Work began last year and the "
    "government expects completion in 1960."
)
NEW_STYLE = (
    "This transformative initiative will leverage innovative financing to foster "
    "resilient, sustainable growth, unlock private capital, and strengthen holistic "
    "governance frameworks for stakeholders, underscoring a pivotal commitment to "
    "empowering communities and showcasing scalable, robust solutions."
)

def test_tokens_nonzero():
    assert len(tokens(OLD_STYLE)) > 30
    assert len(tokens(NEW_STYLE)) > 30

def test_classic_features_sane():
    mgmt = ["governance", "stakeholder", "stakeholders", "framework", "frameworks"]
    old = compute_classic(OLD_STYLE, mgmt)
    new = compute_classic(NEW_STYLE, mgmt)
    for feats in (old, new):
        for v in feats.values():
            assert v == v and v >= 0  # finite, non-negative
    # old-style register anchors time explicitly; new-style does not
    assert old["temporal_per1k"] > new["temporal_per1k"]
    assert new["mgmt_per1k"] > old["mgmt_per1k"]

def test_marker_tiers_separate_registers():
    t1 = ["delve", "underscore", "underscoring", "showcase", "showcasing",
          "pivotal", "intricate", "meticulous"]
    t2 = ["foster", "leverage", "resilient", "sustainable", "holistic",
          "transformative", "unlock", "robust", "scalable", "empowering",
          "innovative", "strengthen"]
    old = compute_markers(OLD_STYLE, t1, t2)
    new = compute_markers(NEW_STYLE, t1, t2)
    assert new["tier2_per1k"] > old["tier2_per1k"] > -1
    assert new["tier1_per1k"] > 0.0
    assert old["tier1_per1k"] == 0.0

def test_rates_are_length_normalized():
    doubled = compute_markers(NEW_STYLE + " " + NEW_STYLE,
                              ["pivotal"], ["foster"])
    single = compute_markers(NEW_STYLE, ["pivotal"], ["foster"])
    assert abs(doubled["tier1_per1k"] - single["tier1_per1k"]) < 0.05
