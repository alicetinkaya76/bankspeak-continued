"""Pin the four checks added after the v5 editor+referee pass.

Each answers an objection that, if left standing, would have returned the paper
before review. Each is pinned because a reassuring number is worthless unless the
thing producing it can still fail.
"""
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_inv = _load("ar_component_inventory")
_t2 = _load("tier2_period_fairness")

INV = ROOT / "data" / "analysis" / "ar_component_inventory.json"
T2 = ROOT / "data" / "analysis" / "tier2_period_fairness.json"
CAD = ROOT / "data" / "analysis" / "imf_cadence_balance.json"


# --- the corpus-definition bracket ---------------------------------------------

def test_component_classification_separates_narrative_from_apparatus():
    assert _inv.component("World Bank Annual Report 2023") == "narrative volume"
    assert _inv.component(
        "... - IBRD and IDA Management Discussion & Analysis and Financial Statements"
    ) == "financial statements"
    assert _inv.component(
        "... - Organizational Information and Lending Data Appendixes"
    ) == "appendixes / organizational info"
    assert _inv.component("... - Executive Summary") == "executive summary"


@pytest.mark.skipif(not INV.exists(), reason="run tools/ar_component_inventory.py")
def test_the_decline_survives_every_corpus_definition():
    """The reviewer's charge was that the endpoint is a packaging artefact. It is
    not: the narrative-only series, which is the like-for-like one, declines MORE
    than the frozen series, not less."""
    d = json.loads(INV.read_text())["corpora"]
    frozen = d["as assembled (frozen)"]["pct"]
    main = d["MAIN narrative volume only"]["pct"]
    family = d["FAMILY, every component"]["pct"]
    assert main < frozen < family < 0, (main, frozen, family)
    assert main < -50


# --- Tier-2 period fairness -----------------------------------------------------

def test_the_modern_stem_matching_is_by_prefix_not_whole_word():
    """"leveraging" does not start with "leverage" -- the eighth character
    differs -- so a whole-word stem split leverage from leveraging."""
    assert _t2.is_modern("leveraging") and _t2.is_modern("leverage")
    assert _t2.is_modern("resilience") and _t2.is_modern("innovative")
    assert not _t2.is_modern("strengthen") and not _t2.is_modern("crucial")


@pytest.mark.skipif(not T2.exists(), reason="run tools/tier2_period_fairness.py")
def test_the_headline_ratio_is_carried_by_modern_vocabulary():
    d = json.loads(T2.read_text())
    S = d["subsets"]
    assert S["period-plausible only"]["ratio"] < S["all 35 terms"]["ratio"]
    assert len(d["absent_in_early_window"]) > 15, "the absence finding is gone"


# --- IMF cadence ----------------------------------------------------------------

@pytest.mark.skipif(not CAD.exists(), reason="run tools/imf_cadence_balance.py")
def test_the_post_window_is_not_more_delayed_than_the_pre_window():
    """The catch-up screen without a baseline reads as alarming. With one it
    reverses: the post window is less delayed, not more."""
    d = json.loads(CAD.read_text())
    assert d["share_delayed_post"] < d["share_delayed_pre"]


@pytest.mark.skipif(not CAD.exists(), reason="run tools/imf_cadence_balance.py")
def test_balancing_the_cadence_moves_the_p_value_not_the_estimate():
    d = json.loads(CAD.read_text())["panels"]["P1"]
    assert abs(d["cadence_balanced"]["beta"] - d["full"]["beta"]) < 0.05
    assert d["cadence_balanced"]["p"] > d["full"]["p"]


# --- stated counts --------------------------------------------------------------

def test_every_stated_count_matches_the_filesystem():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "check_stated_counts.py")],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
