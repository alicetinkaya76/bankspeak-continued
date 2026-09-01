"""Pin what round 18 repaired, and the properties that make the repairs real.

Six things changed and each has a way of quietly coming undone:

  the joint calibration    could drift back to per-panel loops, or to a sampled
                           inner p, and still print a plausible number
  the seed derivation      could go back to len(label) and nothing would fail
  the Tier-2 table         could grow a fabricated source column, or resume
                           calling fiscal-year units documents
  the IMF frame            could publish an unreachable test's zero as a fact
                           again, or lose the replay
  the placeholder guard    could go back to reading only the two Markdown files
                           and miss the brackets on the built title page
  the count guard          could stop reading the checklist and the manifest

Each test below is aimed at the specific way its subject broke, not at a
restatement of what the code does.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

JOINT_JSON = ROOT / "data" / "analysis" / "joint_holm_calibration.json"
TIER2_JSON = ROOT / "data" / "analysis" / "tier2_item_provenance.json"
TIER2_CSV = ROOT / "data" / "analysis" / "tier2_item_provenance.csv"
FRAME_JSON = ROOT / "data" / "analysis" / "imf_frame_publication.json"
CELLS = ROOT / "data" / "analysis" / "panels" / "cells_P1.csv"
CHECKLIST_INPUTS = (ROOT / "build" / "submission" / "PLOS_ONE_submission.pdf",
                    ROOT / "third_eye_kit" / "MANIFEST.md")

# The public export ships the code and the design record but not the licensed
# panel cells, the built PDF or the review kit, so these run there as skips
# rather than as failures. That distinction is the point of the export.
needs_cells = pytest.mark.skipif(
    not CELLS.exists(), reason="panel cells are not in the public export")
needs_package = pytest.mark.skipif(
    not all(p.exists() for p in CHECKLIST_INPUTS),
    reason="the built PDF and the review kit are not in the public export")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------- seeds ------
def test_stream_seeds_do_not_collide_where_the_old_derivation_did():
    """The exact label pairs that shared a stream under SEED + len(label)."""
    from percell_seed import stream_seed
    assert len("P1") == len("P2")                      # the original defect
    assert len("poisson") == len("ar1_nb2")
    labels = ([("dispersion_size", p) for p in ("P1", "P2")]
              + [("ar1_null", p, a) for p in ("P1", "P2")
                 for a in ("poisson", "ar1", "ar1_nb2")]
              + [("passe_cov", p, b, n) for p in ("P1", "P2")
                 for b in ("beta=0", "beta=observed")
                 for n in ("poisson", "nb2_corrected", "ar1", "ar1_nb2")])
    seeds = [stream_seed(*t) for t in labels]
    assert len(set(seeds)) == len(seeds), "two named streams share a seed"


def test_stream_seed_is_stable_across_calls_and_processes():
    from percell_seed import stream_seed
    a = stream_seed("ar1_null", "P1", "poisson")
    assert a == stream_seed("ar1_null", "P1", "poisson")
    out = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, %r);"
         "from percell_seed import stream_seed;"
         "print(stream_seed('ar1_null', 'P1', 'poisson'))" % str(ROOT / "src")],
        capture_output=True, text=True, check=True)
    assert int(out.stdout.strip()) == a, "seed is not stable across processes"


def test_no_tool_derives_a_seed_from_a_label_length():
    """The defect class, not the three instances of it."""
    bad = []
    for f in sorted((ROOT / "tools").glob("*.py")):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if "default_rng" in line and "len(" in line:
                bad.append(f"{f.name}:{i}")
    assert not bad, f"seed derived from a label length: {bad}"


# ------------------------------------------------- joint Holm calibration ----
@needs_cells
def test_the_two_panels_really_do_share_their_comparator_arm():
    """The whole joint construction rests on this, so assert it, do not assume."""
    a = pd.read_csv(ROOT / "data/analysis/panels/cells_P1.csv")
    b = pd.read_csv(ROOT / "data/analysis/panels/cells_P2.csv")
    a = a[a.institution == "IMF"].sort_values("year")
    b = b[b.institution == "IMF"].sort_values("year")
    for col in ("year", "count", "tokens"):
        assert np.array_equal(a[col].to_numpy(), b[col].to_numpy()), col


def test_holm_over_two_panels_is_the_preregistered_step_down():
    j = _load("joint_holm_calibration")
    # smaller p at alpha/2, larger at alpha, and the larger only if the
    # smaller already rejected
    assert j.holm2(0.01, 0.04) == (True, True)
    assert j.holm2(0.01, 0.06) == (True, False)
    assert j.holm2(0.03, 0.04) == (False, False)
    assert j.holm2(0.04, 0.01) == (True, True)          # order independence
    assert j.holm2(0.06, 0.01) == (False, True)


@needs_cells
def test_the_exact_inner_p_reproduces_the_frozen_sampled_one():
    """Enumeration must be the same test the engine runs, not a near neighbour."""
    j = _load("joint_holm_calibration")
    from bootstrap_engine import (build_design, _pair_index,  # noqa: E402
                                  wild_score_p, BLOCK_LEN)
    for panel in ("P1", "P2"):
        cells = pd.read_csv(ROOT / f"data/analysis/panels/cells_{panel}.csv")
        des = j.Design(cells)
        exact = des.exact_p(des.y0)
        assert round(exact * 512) == exact * 512, "support is not 512 points"
        df, X, names, y, off, years = build_design(
            cells[["institution", "year", "count", "tokens"]], "WB")
        pair, T = _pair_index(df, years, "WB")
        sampled, _, _ = wild_score_p(y, X, off, names, pair, T, 9999,
                                     BLOCK_LEN, 20260806, nb2=False)
        assert abs(exact - sampled) < 0.01, (panel, exact, sampled)


@needs_cells
def test_the_fast_fit_is_the_frozen_fit():
    """The calibration's speed must not be bought with a different estimator."""
    import statsmodels.api as sm
    from bootstrap_engine import _fit
    j = _load("joint_holm_calibration")
    cells = pd.read_csv(ROOT / "data/analysis/panels/cells_P1.csv")
    des = j.Design(cells)
    ref = np.asarray(_fit(des.y0, des.Xr, des.off,
                          sm.families.Poisson()).fittedvalues)
    got, _ = j.irls_poisson(des.y0, des.Xr, des.off)
    assert np.max(np.abs(got - ref) / ref) < 1e-9


@pytest.mark.skipif(not JOINT_JSON.exists(),
                    reason="run tools/joint_holm_calibration.py first")
def test_the_ladder_spans_the_range_the_paper_claims():
    d = json.loads(JOINT_JSON.read_text(encoding="utf-8"))
    by = {s["name"]: s for s in d["scenarios"]}
    for need in ("s10_4_asbuilt", "fitted_joint", "prereg_literal",
                 "fitted_joint_poisson_only", "fitted_joint_rho0.0"):
        assert need in by, need
    # the finding: the preregistered null is near nominal, the fitted one is not
    assert by["prereg_literal"]["holm_familywise_error_rate"] < 0.05
    assert by["fitted_joint"]["holm_familywise_error_rate"] > 0.06
    # and the paper's stated range must bracket what the file holds
    rates = [s["holm_familywise_error_rate"] for s in d["scenarios"]]
    paper = (ROOT / "docs" / "PAPER_DRAFT_v2.md").read_text(encoding="utf-8")
    assert "0.037" in paper and "0.094" in paper, \
        "the manuscript no longer states the family error range"
    assert min(rates) <= 0.037 + 1e-9 and max(rates) >= 0.094 - 1e-9, \
        (min(rates), max(rates))


@pytest.mark.skipif(not JOINT_JSON.exists(),
                    reason="run tools/joint_holm_calibration.py first")
def test_serial_dependence_is_not_reported_as_the_sole_cause():
    """Two fifths of the excess survives at rho = 0; the earlier claim that
    serial dependence was the cause is what this guards against returning."""
    d = json.loads(JOINT_JSON.read_text(encoding="utf-8"))
    by = {s["name"]: s["holm_familywise_error_rate"] for s in d["scenarios"]}
    none_, iid, ar1 = (by["fitted_joint_poisson_only"],
                       by["fitted_joint_rho0.0"], by["fitted_joint"])
    assert none_ < iid < ar1, (none_, iid, ar1)
    assert (iid - none_) / (ar1 - none_) > 0.25, "the rho=0 share vanished"


@pytest.mark.skipif(not JOINT_JSON.exists(),
                    reason="run tools/joint_holm_calibration.py first")
def test_the_refuted_diagnostics_are_still_published_refuted():
    """Both candidate mechanisms run the wrong way, and the output has to keep
    saying so — an artifact that quietly stopped reporting them would leave the
    supplement's refutation unsupported."""
    d = json.loads(JOINT_JSON.read_text(encoding="utf-8"))
    by = {s["name"]: s for s in d["scenarios"] if "diagnostics" in s}
    flat, fit = by["observed_rates_flat"], by["fitted_joint"]
    assert (flat["diagnostics"]["P1"]["shock_to_noise"]
            > fit["diagnostics"]["P1"]["shock_to_noise"])
    assert (flat["holm_familywise_error_rate"]
            < fit["holm_familywise_error_rate"])
    assert (flat["diagnostics"]["leverage"]["block9_variance_share"]
            > fit["diagnostics"]["leverage"]["block9_variance_share"])


@pytest.mark.skipif(not JOINT_JSON.exists(),
                    reason="run tools/joint_holm_calibration.py first")
def test_the_conjunctive_rule_is_tighter_than_its_first_conjunct():
    d = json.loads(JOINT_JSON.read_text(encoding="utf-8"))
    for s in d["scenarios"]:
        if "c1_and_c4_family_rate" in s:
            assert s["c1_and_c4_family_rate"] <= s["holm_familywise_error_rate"]


# ------------------------------------------------------ Tier-2 provenance ----
@pytest.mark.skipif(not TIER2_JSON.exists(),
                    reason="run tools/tier2_item_provenance.py first")
def test_no_tier2_term_is_given_a_source_the_repository_does_not_record():
    d = json.loads(TIER2_JSON.read_text(encoding="utf-8"))
    marker = d["provenance"]["per_term_source"]
    assert "not recorded" in marker.lower()
    rows = list(pd.read_csv(TIER2_CSV).itertuples())
    assert len(rows) == 35
    for r in rows:
        assert r.source == marker, (r.term, r.source)
        assert r.source_location == d["provenance"]["per_term_source_location"]
    blob = json.dumps(d)
    for name in ("Kobak", "Juzek", "Ward", "Liang"):
        assert name not in blob, f"a Tier-2 term was attributed to {name}"


@pytest.mark.skipif(not TIER2_CSV.exists(),
                    reason="run tools/tier2_item_provenance.py first")
def test_fiscal_year_units_are_not_called_documents():
    """76 assembled units stand behind 135 documents; the column said
    n_documents and meant units."""
    cols = pd.read_csv(TIER2_CSV, nrows=1).columns
    assert not [c for c in cols if c.startswith("n_documents")], list(cols)
    assert [c for c in cols if c.startswith("n_fy_units")]


@pytest.mark.skipif(not TIER2_JSON.exists(),
                    reason="run tools/tier2_item_provenance.py first")
def test_both_match_rules_are_reported_and_neither_is_declared_normative():
    d = json.loads(TIER2_JSON.read_text(encoding="utf-8"))
    agg = d["aggregate"]["all_35"]
    assert {"production", "boundary"} <= set(agg)
    assert agg["production"]["ratio"] != agg["boundary"]["ratio"]
    assert "not recorded" in d["match_rules"]["frozen_for_tier2"].lower()


@pytest.mark.skipif(not TIER2_JSON.exists(),
                    reason="run tools/tier2_item_provenance.py first")
def test_the_boundary_rule_reproduces_the_section_it_replaces():
    d = json.loads(TIER2_JSON.read_text(encoding="utf-8"))
    old = json.loads((ROOT / "data/analysis/tier2_period_fairness.json")
                     .read_text(encoding="utf-8"))
    assert abs(d["aggregate"]["all_35"]["boundary"]["ratio"]
               - old["subsets"]["all 35 terms"]["ratio"]) < 1e-9


@pytest.mark.skipif(not TIER2_JSON.exists(),
                    reason="run tools/tier2_item_provenance.py first")
def test_the_production_rule_agrees_with_the_production_pipeline():
    """The cross-check that the two paths compute the same quantity."""
    d = json.loads(TIER2_JSON.read_text(encoding="utf-8"))
    f = pd.read_csv(ROOT / "data/features/ar_fy_features.csv")
    late = f[(f.year >= 2020) & (f.year <= 2024)]
    tw = float(np.average(late.tier2_per1k, weights=late.tokens))
    assert abs(d["aggregate"]["all_35"]["production"]["late"] - tw) < 1e-3


# ---------------------------------------------------------- the IMF frame ----
@pytest.mark.skipif(not FRAME_JSON.exists(),
                    reason="run tools/imf_frame_publication.py first")
def test_the_frozen_draw_replays_exactly():
    d = json.loads(FRAME_JSON.read_text(encoding="utf-8"))
    r = d["reproducibility_replay"]
    assert r["exact_match"] is True
    assert r["in_replay_not_in_frozen"] == 0
    assert r["in_frozen_not_in_replay"] == 0
    assert r["n_frozen_rows"] == 1064


@pytest.mark.skipif(not FRAME_JSON.exists(),
                    reason="run tools/imf_frame_publication.py first")
def test_an_unreachable_test_is_not_published_as_an_empirical_zero():
    """excluded_language reads 0 because the listing has no language column."""
    d = json.loads(FRAME_JSON.read_text(encoding="utf-8"))
    row = next(r for r in d["disposition_of_all_listing_hits"]["rows"]
               if r["status"] == "excluded_language")
    assert row["n"] == 0
    assert "UNREACHABLE" in row["rule"], row["rule"]


@pytest.mark.skipif(not FRAME_JSON.exists(),
                    reason="run tools/imf_frame_publication.py first")
def test_the_cap_rationale_carries_a_measured_spread_not_an_estimate():
    d = json.loads(FRAME_JSON.read_text(encoding="utf-8"))
    m = d["cap"]["eligible_spread_measured"]
    frame = pd.read_csv(ROOT / "data/meta/imf_articleiv_frame.csv")
    early = frame[frame.year <= 2001].groupby("year").size().mean()
    late = frame[frame.year >= 2002].groupby("year").size().mean()
    assert abs(m["mean_eligible_1999_2001"] - early) < 1e-3
    assert abs(m["ratio_of_means"] - late / early) < 1e-3
    assert "three to five times" not in json.dumps(d)


@pytest.mark.skipif(not FRAME_JSON.exists(),
                    reason="run tools/imf_frame_publication.py first")
def test_the_narrower_unmapped_denominator_is_published_too():
    d = json.loads(FRAME_JSON.read_text(encoding="utf-8"))
    text = " ".join(d["needs_human_review"])
    assert "reached the alias lookup" in text
    assert "42.2" in text and "31.4" in text


@pytest.mark.skipif(not FRAME_JSON.exists(),
                    reason="run tools/imf_frame_publication.py first")
def test_inclusion_probabilities_are_published_and_the_cap_binds_where_stated():
    d = json.loads(FRAME_JSON.read_text(encoding="utf-8"))
    t = d["per_year_table"]
    assert len(t) == 27
    below = [r for r in t if not r["cap_binds"]]
    assert [r["year"] for r in below] == [1999]
    assert all(r["n_sampled"] == 40 for r in t if r["cap_binds"])
    ps = [r["inclusion_probability"] for r in t]
    assert min(ps) > 0.30 and max(ps) == 1.0


def test_no_imf_document_text_reaches_either_new_artifact():
    """Counts, ids and column names travel; document text does not."""
    for path in (FRAME_JSON, TIER2_JSON):
        if not path.exists():
            continue
        blob = json.loads(path.read_text(encoding="utf-8"))
        flat = json.dumps(blob).lower()
        for phrase in ("staff report for the", "executive board",
                       "the mission met", "article iv consultation with"):
            assert phrase not in flat, (path.name, phrase)


# ------------------------------------------------------------- the guards ----
def test_the_placeholder_guard_reads_the_built_artifact():
    """It read two Markdown files while the brackets sat on the built title
    page, and reported the package clean."""
    mod = _load("placeholder_report")
    assert hasattr(mod, "scan_pdf")
    assert mod.BUILT_PDF.name.endswith(".pdf")
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "placeholder_report.py")],
                       capture_output=True, text=True, cwd=ROOT)
    assert "BUILT SUBMISSION ARTIFACT" in r.stdout
    assert r.returncode in (0, 2), r.stdout


@needs_package
def test_the_count_guard_reads_the_checklist_and_the_manifest():
    """Both drifted for rounds while the guard reported every count matching."""
    src = (ROOT / "tools" / "check_stated_counts.py").read_text(encoding="utf-8")
    assert "PLOS_SUBMISSION_CHECKLIST" in src
    assert "MANIFEST.md" in src
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "check_stated_counts.py")],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout
    assert "PDF pages" in r.stdout and "kit files" in r.stdout


def test_the_xref_guard_reads_the_supplements_own_cross_references():
    """A dangling S6.3 inside the supplement passed every check for two rounds
    because the checker scanned only the paper for supplement references."""
    src = (ROOT / "tools" / "check_cross_references.py").read_text(encoding="utf-8")
    assert 'paper + "\\n" + supp' in src
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "check_cross_references.py")],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout


# ------------------------------------------------- the hand-typed tables -----
DISP_JSON = ROOT / "data" / "analysis" / "dispersion_calibration.json"


@pytest.mark.skipif(not DISP_JSON.exists(),
                    reason="run tools/dispersion_calibration.py first")
def test_the_s9_table_matches_the_file_it_reports():
    """S9's ten rows are typed into the supplement by hand, and a reseeded
    rerun moved every one of them. Nothing was watching."""
    import re
    d = json.loads(DISP_JSON.read_text(encoding="utf-8"))
    supp = (ROOT / "docs" / "PAPER_SUPPLEMENT_v1.md").read_text(encoding="utf-8")
    rows = re.findall(
        r"^\| (P[12]) \| (\d\.\d\d) \| (\d\.\d{4}) \| [^|]+ \| \*{0,2}(\d\.\d{3})\*{0,2} \|$",
        supp, re.M)
    assert len(rows) == 10, f"found {len(rows)} S9 rows, expected 10"
    panels = d["panels"] if "panels" in d else d
    for panel, alpha, ahat, size in rows:
        entry = panels[panel]
        rec = entry["recovery"][str(float(alpha))]
        siz = entry["size"][str(float(alpha))]
        got_a = rec["mean"] if isinstance(rec, dict) else rec
        got_s = siz["size_05"] if isinstance(siz, dict) else siz
        assert abs(float(ahat) - got_a) < 5e-5, (panel, alpha, ahat, got_a)
        assert abs(float(size) - got_s) < 5e-4, (panel, alpha, size, got_s)
