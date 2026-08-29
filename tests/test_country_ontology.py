"""The grouping that condition 2 was supposed to standardize over.

The confirmatory run of 2026-08-27 handed the standardized arm `<stratum>:<year>`
-- a key that is institution-specific by construction -- and the estimator dutifully
reported `no_common_support_groups`, which reads as a fact about the World Bank
and the Fund and is not one. These tests pin the two things that would let that
recur: the resolution rules that turn a D&R country string into a group, and the
default that keeps the defective run reproducible instead of silently repairing it.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


onto = _load("build_country_ontology")

KEN = {"iso3": "KEN", "region": "Sub-Saharan Africa", "income": "Low income",
       "aggregate": False}
UGA = {"iso3": "UGA", "region": "Sub-Saharan Africa", "income": "Low income",
       "aggregate": False}
WLD = {"iso3": "WLD", "region": "Aggregates", "income": "Aggregates",
       "aggregate": True}
YEM = {"iso3": "YEM", "region": "Middle East", "income": "Low income",
       "aggregate": False}
SOM = {"iso3": "SOM", "region": "Sub-Saharan Africa", "income": "Low income",
       "aggregate": False}

BY_NAME = {onto.norm("Kenya"): KEN, onto.norm("Uganda"): UGA,
           onto.norm("World"): WLD, onto.norm("Yemen, Rep."): YEM,
           onto.norm("Somalia, Fed. Rep."): SOM}
BY_ISO = {r["iso3"]: r for r in (KEN, UGA, WLD, YEM, SOM)}


def resolve(name, alias=None):
    return onto.resolve(name, BY_NAME, BY_ISO, alias or {})


def test_a_country_whose_own_name_contains_a_comma_is_not_split():
    """"Yemen, Republic of" is one country. Splitting on the comma first -- the
    obvious implementation -- shreds it into two unresolvable fragments and sends
    an ordinary single-country document to `unknown`."""
    rec, src = resolve("Yemen, Republic of")
    assert rec is not None, f"resolved to nothing via {src}"
    assert rec["iso3"] == "YEM", src
    assert src != "multi_country"


def test_two_distinct_countries_are_multi_country_not_a_coin_flip():
    rec, src = resolve("Kenya,Uganda")
    assert rec is None and src == "multi_country"
    assert onto.group_of(rec) == "unknown"


def test_an_aggregate_beside_a_country_is_still_that_country():
    """PREREG §6 sends regional and multi-country documents to `unknown`, but a
    regional TAG is not a second country: "Senegal,World" names one country and
    one aggregate. Counting the aggregate as a country would discard ordinary
    single-country documents wholesale."""
    rec, src = resolve("Kenya,World")
    assert rec is not None and rec["iso3"] == "KEN", src
    assert onto.group_of(rec) == "Sub-Saharan Africa|Low income"


def test_the_same_country_written_twice_is_one_country():
    rec, _ = resolve("Kenya,Kenya")
    assert rec is not None and rec["iso3"] == "KEN"


def test_prefix_match_is_single_word_and_unambiguous_only():
    """D&R writes "Somalia", the endpoint writes "Somalia, Fed. Rep.". The prefix
    rule bridges that -- but only for a one-word query resolving to exactly one
    country, so it cannot quietly pick a winner between two candidates."""
    rec, src = resolve("Somalia")
    assert rec is not None and rec["iso3"] == "SOM"
    assert src == "wb_country_endpoint_prefix"


def test_a_pure_region_resolves_to_nothing():
    for region in ("Western Africa", "OECS Countries", "Latin America"):
        rec, src = resolve(region)
        assert rec is None, region
        assert onto.group_of(rec) == "unknown"


def test_an_aggregate_alone_is_unknown_not_a_group():
    assert onto.group_of(WLD) == "unknown"


def test_unclassified_income_is_unknown_rather_than_a_group_named_unclassified():
    rec = {"iso3": "XXX", "region": "Sub-Saharan Africa",
           "income": "Not classified", "aggregate": False}
    assert onto.group_of(rec) == "unknown"


def test_diacritics_do_not_split_a_country_from_itself():
    """The endpoint writes "Turkiye", the D&R listing writes it with a diaeresis.
    Without NFD folding the two never meet and a real country falls to unknown."""
    assert onto.norm("Türkiye") == onto.norm("Turkiye")


def test_panel_builder_still_defaults_to_the_grouping_the_frozen_run_used():
    """The repair must not retroactively change the confirmatory artifacts. If
    the default ever flips, rerunning the pipeline would quietly produce a
    different C2 than the one that was reported and timestamped."""
    src = (ROOT / "tools" / "build_panel_cells.py").read_text(encoding="utf-8")
    import ast
    tree = ast.parse(src)
    found = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and getattr(node.func, "attr", "") == "add_argument"
                and node.args
                and getattr(node.args[0], "value", "") == "--group-source"):
            for kw in node.keywords:
                if kw.arg == "default":
                    found.append(kw.value.value)
    assert found == ["stratum_year"], found


def test_the_two_groupings_are_actually_different_on_the_real_batteries():
    """A regression guard on the finding itself: the frozen run retained zero
    standardization groups, the repaired one retains some. If both ever report
    the same pi_groups, one of the two files is stale."""
    a = ROOT / "data/analysis/panels/P1_battery.json"
    b = ROOT / "data/analysis/panels_country/P1_battery.json"
    if not (a.exists() and b.exists()):
        import pytest
        pytest.skip("batteries not present in this checkout")

    def pi(p):
        return (json.loads(p.read_text(encoding="utf-8"))["conditions"]
                ["c2_stability"]["variants"]["standardized"]["pi_groups"])
    assert pi(a) == 0
    assert pi(b) > 0
