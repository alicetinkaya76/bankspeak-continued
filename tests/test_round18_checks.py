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
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Brackets the manuscript is SUPPOSED to carry until the author fills them.
# Anything else is a defect; this list is the difference between the two.
INTENTIONAL_MANUSCRIPT_FIELDS = ("AUTHOR ATTESTATION", "VERSION DOI")

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
    for need in ("s10_4_construction", "fitted_joint", "prereg_literal",
                 "fitted_joint_poisson_only", "fitted_joint_rho0.0"):
        assert need in by, need
    # the finding: the preregistered null is near nominal, the fitted one is not
    assert by["prereg_literal"]["holm_c1_family_rejection_rate"] < 0.05
    assert by["fitted_joint"]["holm_c1_family_rejection_rate"] > 0.06
    # and the paper's stated range must bracket what the file holds
    # Two brackets, and the paper must state both. The narrow one ranges over
    # mean structures at the preregistered dependence parameters; the wide one
    # over every null in the file. An earlier draft printed only the narrow one,
    # and two rows of its own table sat above it.
    rates = [s["holm_c1_family_rejection_rate"] for s in d["scenarios"]]
    paper = (ROOT / "docs" / "PAPER_DRAFT_v2.md").read_text(encoding="utf-8")
    supp = (ROOT / "docs" / "PAPER_SUPPLEMENT_v1.md").read_text(encoding="utf-8")
    both = paper + supp
    for n in ("0.037", "0.094", "0.028", "0.121"):
        assert n in both, f"the manuscript no longer states {n}"
    # Half a printed unit; Python's %.3f rounds half to even on the binary
    # value, so string equality is the wrong test for a figure like 0.02775.
    tol = 0.0005 + 1e-9
    assert abs(min(rates) - 0.028) <= tol, min(rates)
    assert abs(max(rates) - 0.121) <= tol, max(rates)
    narrow = [by[k]["holm_c1_family_rejection_rate"] for k in
              ("prereg_literal", "fitted_joint", "fitted_joint_param_uncertainty")]
    assert abs(min(narrow) - 0.037) <= tol, min(narrow)
    assert abs(max(narrow) - 0.094) <= tol, max(narrow)


@pytest.mark.skipif(not JOINT_JSON.exists(),
                    reason="run tools/joint_holm_calibration.py first")
def test_serial_dependence_is_not_reported_as_the_sole_cause():
    """Two fifths of the excess survives at rho = 0; the earlier claim that
    serial dependence was the cause is what this guards against returning."""
    d = json.loads(JOINT_JSON.read_text(encoding="utf-8"))
    by = {s["name"]: s["holm_c1_family_rejection_rate"] for s in d["scenarios"]}
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
    assert (flat["holm_c1_family_rejection_rate"]
            < fit["holm_c1_family_rejection_rate"])
    assert (flat["diagnostics"]["leverage"]["block9_variance_share"]
            > fit["diagnostics"]["leverage"]["block9_variance_share"])


@pytest.mark.skipif(not JOINT_JSON.exists(),
                    reason="run tools/joint_holm_calibration.py first")
def test_the_conjunctive_rule_is_tighter_than_its_first_conjunct():
    d = json.loads(JOINT_JSON.read_text(encoding="utf-8"))
    for s in d["scenarios"]:
        if "holm_c1_and_c4_family_rate" in s:
            assert s["holm_c1_and_c4_family_rate"] <= s["holm_c1_family_rejection_rate"]


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


@pytest.mark.skipif(
    not TIER2_JSON.exists()
    or not (ROOT / "data" / "features" / "ar_fy_features.csv").exists(),
    reason="needs the derived feature table, which the public export omits")
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
    # The exit code is now the worst finding across all sections, so a
    # manuscript bracket (the author attestation) gives 1 even where no build
    # tree exists, as in the public export.
    assert r.returncode in (0, 1, 2), r.stdout
    if r.returncode == 1:
        assert "AUTHOR ATTESTATION" in r.stdout, r.stdout


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


# ------------------------------------ the guards, after their own controls ---
# Only what the guards actually open. The first version of this helper copied
# data/ whole, which is the licensed corpus at some gigabytes, and exhausted the
# disk mid-suite: twelve unrelated tests died with OSError. A control tree has
# to be the size of the thing under control.
_CONTROL_TREE = [
    "docs/PAPER_DRAFT_v2.md",
    "docs/PAPER_SUPPLEMENT_v1.md",
    "docs/PLOS_SUBMISSION_CHECKLIST.md",
    "data/analysis/citation_audit.json",
    "third_eye_kit/MANIFEST.md",
    "build/submission/PLOS_ONE_submission.pdf",
    "build/submission/submission.md",
]
_CONTROL_TOOLS = ["check_cross_references.py", "placeholder_report.py",
                  "check_stated_counts.py"]


def _mutated_copy(tmp_path, mutations):
    """A throwaway tree holding only the files the guards read, plus a defect.

    The controls have to run somewhere other than the repository, and the guards
    resolve ROOT from __file__, so a copied tree is enough.
    """
    import shutil
    for rel in _CONTROL_TREE:
        src = ROOT / rel
        if src.exists():
            dst = tmp_path / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    (tmp_path / "tools").mkdir(exist_ok=True)
    for name in _CONTROL_TOOLS:
        shutil.copy2(ROOT / "tools" / name, tmp_path / "tools" / name)
    # the manifest's file count has to match what the copy actually holds
    man = tmp_path / "third_eye_kit" / "MANIFEST.md"
    if man.exists():
        n = sum(1 for f in (tmp_path / "third_eye_kit").rglob("*") if f.is_file())
        t = man.read_text(encoding="utf-8")
        man.write_text(re.sub(r"^\d+ files", f"{n} files", t, count=1, flags=re.M),
                       encoding="utf-8")
    for rel, fn in mutations.items():
        f = tmp_path / rel
        f.write_text(fn(f.read_text(encoding="utf-8")), encoding="utf-8")
    return tmp_path


def _run(tmp_path, tool):
    return subprocess.run([sys.executable, str(tmp_path / "tools" / tool)],
                          capture_output=True, text=True)


def test_a_dangling_reference_inside_the_supplement_is_caught(tmp_path):
    """It was not: three of the four counters read the paper only, so a bad
    reference in the supplement passed for two rounds."""
    t = _mutated_copy(tmp_path, {
        "docs/PAPER_SUPPLEMENT_v1.md":
            lambda s: s + "\n\nSee §17.3, Table 99 and Figure 9.\n"})
    r = _run(t, "check_cross_references.py")
    assert r.returncode == 1, r.stdout
    for want in ("section 17.3", "table 99", "figure 9"):
        assert want in r.stdout, (want, r.stdout)


def test_an_unlisted_placeholder_keyword_is_caught(tmp_path):
    """[FIXME], [TK] and [PENDING] printed 'no placeholders' until round 18."""
    t = _mutated_copy(tmp_path, {
        "docs/PAPER_DRAFT_v2.md":
            lambda s: s + "\n\nThe coefficient is [FIXME], the CI is [TK], "
                          "see [PENDING FINAL RUN].\n"})
    r = _run(t, "placeholder_report.py")
    # Non-zero, not exactly 1: the exit code is the worst finding across all
    # sections now, so a manuscript hit alongside a built-artifact one gives 2.
    assert r.returncode != 0, r.stdout
    assert "[FIXME]" in r.stdout and "[TK]" in r.stdout


def test_numeric_intervals_are_never_reported_as_placeholders():
    """The manuscript is full of them; a guard that flags them is one nobody
    runs twice. Positive control on the real tree: the only manuscript bracket
    it may report is the author attestation, which is there on purpose."""
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "placeholder_report.py")],
                       capture_output=True, text=True, cwd=ROOT)
    body = r.stdout.split("MANUSCRIPT")[1] if "MANUSCRIPT" in r.stdout else r.stdout
    body = body.split("BUILT SUBMISSION")[0]
    hits = [l for l in body.splitlines() if l.strip().startswith("docs/")]
    for h in hits:
        assert any(k in h for k in INTENTIONAL_MANUSCRIPT_FIELDS), h
    assert not re.search(r"\[[\s\-\u2212]*\d[^\]]*\]", "\n".join(hits)), hits


def test_the_author_attestation_keeps_the_package_unsubmittable():
    """The AI-use disclosure carries one bracket only the author can sign, and a
    guard whose length budget misses it lets that field ship unfilled."""
    paper = (ROOT / "docs" / "PAPER_DRAFT_v2.md").read_text(encoding="utf-8")
    assert "AUTHOR ATTESTATION" in paper
    assert "Use of AI assistance" in paper
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "placeholder_report.py")],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode != 0, r.stdout
    assert "AUTHOR ATTESTATION" in r.stdout


def test_a_missing_artifact_does_not_read_as_clean(tmp_path):
    """Deleting the built PDF used to turn exit 2 into exit 0 and print
    'BUILT SUBMISSION ARTIFACT: clean'."""
    t = _mutated_copy(tmp_path, {})
    for f in ("PLOS_ONE_submission.pdf", "submission.md"):
        p = t / "build" / "submission" / f
        if p.exists():
            p.unlink()
    r = _run(t, "placeholder_report.py")
    assert "clean" not in r.stdout.split("BUILT SUBMISSION ARTIFACT")[-1]
    assert "NOT CHECKED" in r.stdout, r.stdout


def test_a_missing_kit_manifest_does_not_read_as_checked(tmp_path):
    t = _mutated_copy(tmp_path, {})
    man = t / "third_eye_kit" / "MANIFEST.md"
    if man.exists():
        man.unlink()
    r = _run(t, "check_stated_counts.py")
    assert "NOT CHECKED" in r.stdout, r.stdout


def test_a_doi_that_does_not_resolve_stops_counting_as_resolved(tmp_path):
    """'Resolved from Crossref' was checked against entries that merely carried
    a doi field, so a 404 counted as a resolution."""
    import json as _json

    def break_one(s):
        d = _json.loads(s)
        for e in d["entries"]:
            if e.get("doi"):
                e.setdefault("check", {})["verdict"] = "DOI DOES NOT RESOLVE"
                break
        return _json.dumps(d)

    if not (ROOT / "data" / "analysis" / "citation_audit.json").exists():
        pytest.skip("no citation audit in this tree")
    # The expected counts are DERIVED, not typed. This control asserted
    # "30 of 34" literally and broke the moment round 20 split the Moretti and
    # Pestre record into its two publication objects and the reference list
    # became 35. A negative control that fails when an unrelated true number
    # changes is testing the number, not the guard.
    audit = _json.loads((ROOT / "data" / "analysis" / "citation_audit.json")
                        .read_text(encoding="utf-8"))
    n_entries = audit["n_entries"]
    n_resolved_after_break = sum(
        1 for e in audit["entries"]
        if e.get("doi")
        and "NOT" not in str((e.get("check") or {}).get("verdict", "")).upper()) - 1

    t = _mutated_copy(tmp_path, {"data/analysis/citation_audit.json": break_one})
    r = _run(t, "check_stated_counts.py")
    assert r.returncode == 1, r.stdout
    assert (f"{n_resolved_after_break} of {n_entries}" in r.stdout
            or f"actual {n_resolved_after_break}/{n_entries}" in r.stdout), r.stdout


def test_the_citation_audit_has_a_real_offline_mode_and_rejects_unknown_flags():
    """--offline was accepted by the shell and ignored by the program: it made
    31 live HTTP requests and rewrote a tracked file during a read-only audit."""
    src = (ROOT / "tools" / "audit_citations.py").read_text(encoding="utf-8")
    assert "--offline" in src and "argparse" in src
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "audit_citations.py"),
                        "--not-a-flag"], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode != 0 and "unrecognized" in r.stderr


@pytest.mark.skipif(not (ROOT / "third_eye_kit" / "SHA256SUMS.json").exists(),
                    reason="no review kit in this tree")
def test_the_kit_records_a_digest_per_staged_file_and_matches_the_repo():
    """third_eye_kit/ is gitignored, so nothing could see it drift, and it had."""
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "check_kit_freshness.py")],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout


def test_no_type_3_font_reaches_the_submission_pdf():
    """matplotlib's default; several journal pipelines reject it outright."""
    pdf = ROOT / "build" / "submission" / "PLOS_ONE_submission.pdf"
    if not pdf.exists():
        pytest.skip("no built PDF in this tree")
    import fitz
    d = fitz.open(pdf)
    bad = [(i + 1, f) for i in range(d.page_count)
           for f in d.get_page_fonts(i, full=True) if "Type3" in str(f)]
    assert not bad, bad


def test_the_pdf_text_layer_records_what_the_source_holds():
    """Every semicolon in both PDFs was U+037E GREEK QUESTION MARK, which is
    canonically equivalent to U+003B and therefore invisible to a notdef scan."""
    import unicodedata
    for name in ("PLOS_ONE_submission.pdf", "PLOS_ONE_supplement.pdf"):
        pdf = ROOT / "build" / "submission" / name
        if not pdf.exists():
            pytest.skip("no built PDF in this tree")
        import fitz
        text = "".join(p.get_text() for p in fitz.open(pdf))
        strays = sorted({hex(ord(c)) for c in text
                         if unicodedata.normalize("NFC", c) != c})
        assert not strays, (name, strays)


def test_nothing_is_typeset_past_the_page_edge():
    """The title page printed 62 of the deposit's 64 sha256 hex digits."""
    for name in ("PLOS_ONE_submission.pdf", "PLOS_ONE_supplement.pdf"):
        pdf = ROOT / "build" / "submission" / name
        if not pdf.exists():
            pytest.skip("no built PDF in this tree")
        import fitz
        d = fitz.open(pdf)
        over = [(i + 1, l["bbox"][2]) for i, p in enumerate(d)
                for b in p.get_text("dict")["blocks"]
                for l in b.get("lines", []) if l["bbox"][2] > p.rect.width - 1]
        assert not over, (name, over[:5])


def test_the_deposit_hash_survives_typesetting_in_full():
    pdf = ROOT / "build" / "submission" / "PLOS_ONE_submission.pdf"
    if not pdf.exists():
        pytest.skip("no built PDF in this tree")
    import fitz
    import re as _re
    text = "".join(p.get_text() for p in fitz.open(pdf)).replace("\n", "")
    m = _re.search(r"sha256\s*([0-9a-f]{40,80})", text)
    assert m, "the provenance hash is not in the built PDF"
    assert len(m.group(1)) == 64, len(m.group(1))


# ------------------------------------------- every shipped script must parse --
def _public_scripts(root: Path):
    return sorted(p for d in ("tools", "src", "tests")
                  for p in (root / d).rglob("*.py")
                  if "__pycache__" not in p.parts)


def test_every_script_in_the_repository_compiles():
    """A markdown editor was run over a Python file and collapsed a multi-line
    comment into prose, so tools/tier2_item_provenance.py raised SyntaxError on
    import while the supplement told readers to run it. Nothing compiled the
    scripts, so 432 tests passed with a broken one in the bundle."""
    broken = []
    for f in _public_scripts(ROOT):
        try:
            ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        except SyntaxError as e:
            broken.append(f"{f.relative_to(ROOT)}:{e.lineno}: {e.msg}")
    assert not broken, broken


@pytest.mark.skipif(not (ROOT / "third_eye_kit" / "07_code").exists(),
                    reason="no review kit in this tree")
def test_every_script_inside_the_review_kit_compiles():
    """The kit is what an external reviewer actually runs, and it is a copy
    rather than the original, so it gets its own check."""
    broken = []
    for f in sorted((ROOT / "third_eye_kit").rglob("*.py")):
        try:
            ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        except SyntaxError as e:
            broken.append(f"{f.name}:{e.lineno}: {e.msg}")
    assert not broken, broken


def test_the_calibration_reports_four_decision_rules_off_one_set_of_draws():
    """holm2 ran unconditionally while two rows were labelled 'no Holm', and the
    three opening rungs used three different seeds, so their movement mixed the
    stated change with Monte Carlo noise."""
    if not JOINT_JSON.exists():
        pytest.skip("run tools/joint_holm_calibration.py first")
    d = json.loads(JOINT_JSON.read_text(encoding="utf-8"))
    by = {s["name"]: s for s in d["scenarios"]}
    assert "s10_4_construction" in by, sorted(by)
    c = by["s10_4_construction"]
    for k in ("raw_any_panel_below_0.05", "holm_c1_family_rejection_rate",
              "holm_c1_and_c4_family_rate", "same_data_sampled_inner_p"):
        assert k in c, (k, sorted(c))
    # A step-down cannot reject more often than the raw threshold it steps down
    # from, and the conjunction with C4 cannot reject more often than C1 alone.
    assert c["holm_c1_family_rejection_rate"] <= c["raw_any_panel_below_0.05"]
    assert c["holm_c1_and_c4_family_rate"] <= c["holm_c1_family_rejection_rate"]
    # The three mislabelled scenarios must be gone, not merely renamed.
    for dead in ("s10_4_asbuilt", "s10_4_exact", "s10_4_exact_holm"):
        assert dead not in by, dead
    assert "holm_familywise_error_rate" not in c, \
        "the rate is a C1 upper bound and must not be named a familywise error"


def test_the_reported_rate_is_named_an_upper_bound_everywhere():
    """C2 and C3 are not simulated, so this is not the governing rule's error
    rate, and calling it one was the second review's F2."""
    if not JOINT_JSON.exists():
        pytest.skip("run tools/joint_holm_calibration.py first")
    d = json.loads(JOINT_JSON.read_text(encoding="utf-8"))
    assert d["family_rates_are_upper_bounds"] is True
    assert "UPPER BOUND" in d["reported_quantity"]
    for f in ("PAPER_DRAFT_v2.md", "PAPER_SUPPLEMENT_v1.md"):
        text = (ROOT / "docs" / f).read_text(encoding="utf-8")
        assert "family error rate of the governing rule" not in text, f


def test_holm_is_not_claimed_to_have_independence_as_its_worst_case():
    """min(p1,p2) <= alpha/2 reaches alpha when the lower tails are disjoint;
    independence gives alpha - alpha^2/4, which is close but is not the max.

    The phrase may still appear -- both documents withdraw it by name, and a
    withdrawal has to quote what it withdraws. So the test is that every
    occurrence sits in a retraction, not that none occurs.
    """
    marks = ("that is false", "which is false", "is withdrawn", "is false and",
             "an earlier version")
    for f in ("PAPER_DRAFT_v2.md", "PAPER_SUPPLEMENT_v1.md"):
        low = " ".join((ROOT / "docs" / f).read_text(encoding="utf-8").lower().split())
        for m in re.finditer(r"holm's worst case|worst case is independence", low):
            window = low[max(0, m.start() - 200):m.end() + 240]
            assert any(k in window for k in marks), (f, window[:220])
