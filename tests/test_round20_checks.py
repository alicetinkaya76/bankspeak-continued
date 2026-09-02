"""Pin what round 20 repaired, and the ways each repair could quietly come undone.

Round 20 answered an external audit of the built package. Five of its findings
were about our own text rather than the reviewer's reading of it, and those are
the ones with tests here, because a prose correction has nothing holding it in
place:

  the sibling attribution  said the excluded class's opposing trend WAS the
                           sibling organisations. Decomposed, every sibling
                           falls on its own series and the class rises only
                           because two of the three did not exist in 1946-65.
                           The bolded causal sentence could come back.
  the retrieval routes     said 354 documents came "through a public web
                           archive". Every PDF was fetched from www.imf.org;
                           the archive supplied a link on the IMF's own page.
                           The old phrasing produced the exact misreading it
                           invited, in a published review.
  the abstract's ratios    paired an equal-year figure with a pooled one. The
                           fix depends on equal-year cells that did not exist
                           in any artifact until this round, so a regenerated
                           provenance file could drop them and the abstract
                           would go back to quoting an unbacked number.
  the frame's unmapped     called 2,341 rows "documents the pipeline could not
                           place" when the listing types all but two of them.
  the metadata guard       had a pattern that stopped matching and therefore
                           passed: a checklist saying 16 pages against a built
                           18. Any guard that treats a non-match as success is
                           the same defect wearing a different regex.

The functional-form table is new rather than corrected, and its tests are about
the property that makes it readable at all: deleting a year moves the block
partition as well as the data, and one of its rows cannot be significant however
the data fall.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

PAPER = ROOT / "docs" / "PAPER_DRAFT_v2.md"
SUPP = ROOT / "docs" / "PAPER_SUPPLEMENT_v1.md"
DAS = ROOT / "docs" / "SUBMISSION_DATA_AVAILABILITY.md"
CHECKLIST = ROOT / "docs" / "PLOS_SUBMISSION_CHECKLIST.md"
FFS = ROOT / "data" / "analysis" / "functional_form_sensitivity.json"
EXCL = ROOT / "data" / "analysis" / "ar_exclusion_classes.json"
TIER2 = ROOT / "data" / "analysis" / "tier2_item_provenance.json"
FRAME = ROOT / "data" / "analysis" / "imf_frame_publication.json"


def _load(p):
    if not p.exists():
        pytest.skip(f"{p.relative_to(ROOT)} not built")
    return json.loads(p.read_text(encoding="utf-8"))


# --------------------------------------------------- functional-form table --
def test_frozen_row_reproduces_the_confirmatory_result():
    """The table's own baseline must be the published estimate.

    If this row drifts, every other row in Table 5d is being compared against
    something the paper never reported.
    """
    d = _load(FFS)["panels"]
    assert d["P1"]["as_published"]["exact_p"] == pytest.approx(8 / 512)
    assert d["P2"]["as_published"]["exact_p"] == pytest.approx(50 / 512)
    assert d["P1"]["as_published"]["beta"] == pytest.approx(0.5856, abs=5e-4)
    assert d["P2"]["as_published"]["beta"] == pytest.approx(0.3319, abs=5e-4)


def test_a_short_window_cannot_reach_significance_and_says_so():
    """Five blocks give a support of 32 and a smallest attainable p of 0.0625.

    A reader who saw only "p = 0.0625" in that row would read a null result out
    of an arithmetic ceiling. The flag is the whole point of publishing the row.
    """
    d = _load(FFS)["panels"]
    for panel in ("P1", "P2"):
        row = d[panel]["pre_start_2011"]
        assert row["n_blocks"] == 5
        assert row["support"] == 32
        assert row["min_attainable_p"] == pytest.approx(2 / 32)
        assert row["significance_arithmetically_possible"] is False
        assert row["exact_p"] >= 0.05
    # and every full-length row must NOT carry the flag, or it means nothing
    for panel in ("P1", "P2"):
        assert d[panel]["as_published"]["significance_arithmetically_possible"]


def test_every_row_reports_all_block_origins():
    """The claim that single-year deletions move the partition, not the
    evidence, rests entirely on this column existing for every row."""
    d = _load(FFS)["panels"]
    for panel, rows in d.items():
        for key, row in rows.items():
            assert len(row["p_by_block_origin"]) == 3, (panel, key)
            assert row["p_min_over_origins"] == pytest.approx(
                min(row["p_by_block_origin"]))
            assert row["p_max_over_origins"] == pytest.approx(
                max(row["p_by_block_origin"]))


def test_dropping_2020_looks_fatal_only_at_the_frozen_origin():
    """§6.2's third reading, pinned.

    At the frozen origin dropping fiscal 2020 sends P1 from 0.0156 to 0.3164.
    At the other two origins the same deletion returns values below 0.05. If a
    future change made all three origins agree, the paragraph explaining the
    difference would be describing something that no longer happens.
    """
    row = _load(FFS)["panels"]["P1"]["drop_2020"]
    assert row["exact_p"] > 0.2
    assert sum(p < 0.05 for p in row["p_by_block_origin"]) == 2


# ------------------------------------------------- the sibling composition --
def test_no_sibling_rises_on_its_own_series():
    """The correction that replaced a bolded causal claim in §6.1.

    The class rises 64.4%; each institution measured on its own years falls.
    Both halves have to hold for the paragraph to be true.
    """
    d = _load(EXCL)
    inst = d["sibling_decomposition"]["institutions"]
    assert set(inst) == {"IFC", "ICSID", "MIGA"}
    for name, row in inst.items():
        assert row["own_pct_change"] < 0, (name, row["own_pct_change"])
    assert d["classes"]["sibling organisation (IFC/MIGA/ICSID)"]["pct_change"] > 0


def test_two_siblings_have_no_early_window_at_all():
    """This is WHY the class-level figure is composition.

    ICSID was founded in 1966 and MIGA in 1988. If either acquired an early-window
    file, the composition reading would need rechecking rather than restating.
    """
    cov = _load(EXCL)["sibling_decomposition"]["window_coverage"]
    assert cov["ICSID"]["early_files"] == 0
    assert cov["MIGA"]["early_files"] == 0
    assert cov["IFC"]["early_files"] > 0


def test_removing_icsid_reverses_the_class_direction():
    d = _load(EXCL)["sibling_decomposition"]
    assert d["excluding_icsid"]["pct_change"] < 0


def test_the_paper_does_not_restate_the_withdrawn_causal_claim():
    t = PAPER.read_text(encoding="utf-8")
    assert "The opposing trend is entirely the sibling organisations" not in t
    # and the correction must actually be present, not merely the removal
    assert "not a rise in anyone's prose" in t


# ------------------------------------------------------- retrieval routes --
@pytest.mark.parametrize("path", [PAPER, DAS])
def test_no_document_is_said_to_come_from_a_web_archive(path):
    """The wording that produced a published misreading.

    The archive supplied 354 link resolutions; the manifest records
    www.imf.org as the host of every one of the 1,064 PDFs. Both files must say
    so positively, not merely avoid the old phrase -- a silent deletion would
    leave the reader with no correction.

    The first version of this test forbade the old phrase outright and failed on
    the paper, which quotes it inside its own correction note. Forbidding a
    retraction from naming what it retracts is the same mistake this suite made
    once before with the Holm worst-case sentence: the phrase is allowed only
    where a correction word sits beside it.
    """
    t = " ".join(path.read_text(encoding="utf-8").split())
    for m in re.finditer(r"through a public web archive", t):
        window = t[max(0, m.start() - 200):m.end() + 200]
        assert re.search(r"earlier wording|an earlier|previously|misread|"
                         r"read as|corrected", window), (
            f"{path.name} uses the withdrawn phrase outside a correction")
    assert re.search(r"none (?:was taken|came) from the archive", t), path.name


def test_the_manifest_still_supports_that_claim():
    """The prose above is only true while the data say so."""
    import csv
    from urllib.parse import urlparse
    man = ROOT / "data" / "meta" / "imf_retrieval" / "_manifest.csv"
    if not man.exists():
        pytest.skip("retrieval manifest not present")
    hosts = set()
    with man.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            u = (r.get("pdf_url") or "").strip()
            if u:
                hosts.add(urlparse(u).netloc)
    assert hosts == {"www.imf.org"}, hosts


# ------------------------------------------------------- abstract ratios --
def test_equal_year_cells_exist_for_both_subsets():
    """The abstract's matched pair depends on these; they are new this round."""
    agg = _load(TIER2)["aggregate"]
    for subset in ("all_35", "period_plausible_subset"):
        block = agg[subset]["production"]
        for key in ("early_equal_year", "late_equal_year", "ratio_equal_year"):
            assert key in block, (subset, key)


def test_the_abstracts_two_ratios_come_from_one_convention():
    """The finding the auditor got right and mislabelled.

    Both figures in the abstract's Tier-2 clause must be the equal-year mean of
    the production rule -- the same convention as the temporal-anchoring figures
    beside them in the same sentence.
    """
    agg = _load(TIER2)["aggregate"]
    all35 = agg["all_35"]["production"]
    plaus = agg["period_plausible_subset"]["production"]
    t = PAPER.read_text(encoding="utf-8")
    m = re.search(r"rises from ([\d.]+) to ([\d.]+): thirtyfold, but "
                  r"([\d.]+)-fold on the twelve terms", t)
    assert m, "the abstract's Tier-2 clause has been reworded; recheck the convention"
    early, late, subset_ratio = (float(m.group(i)) for i in (1, 2, 3))
    assert all35["early_equal_year"] == pytest.approx(early, abs=5e-3)
    assert all35["late_equal_year"] == pytest.approx(late, abs=5e-2)
    assert all35["ratio_equal_year"] == pytest.approx(30, abs=1.0)
    assert plaus["ratio_equal_year"] == pytest.approx(subset_ratio, abs=5e-2)


def test_the_abstract_does_not_quote_the_old_mixed_range():
    assert "9- to 11-fold" not in PAPER.read_text(encoding="utf-8")


# ----------------------------------------------------------- the IMF frame --
def test_the_unmapped_rows_are_typed_rather_than_unknown():
    """The supplement said these were documents the pipeline could not place.

    The listing carries the Fund's own content-type label and places all of
    them. Understating what we know made our own frame look weaker than it is.
    """
    d = _load(FRAME).get("unmapped_country_types")
    if d is None:
        pytest.skip("frame publication not rebuilt")
    assert d["n"] == d["n_joined"], "some unmapped rows no longer join to the listing"
    types = d["by_src_imftype"]
    assert types.get("Public Information Notice", 0) > 1000
    # at most a handful may be untyped, or the sentence in S10.7 overstates
    untyped = sum(v for k, v in types.items() if k in ("Pdf", "nan", "None"))
    assert untyped <= 10, types
    # Whitespace-normalised, because the first version of this assertion pinned
    # a particular line wrapping: the withdrawn sentence could come back with a
    # different break and the test would not have noticed. What must not return
    # is the ASSERTION; the retraction quotes the phrase and must stay legal.
    t = " ".join(SUPP.read_text(encoding="utf-8").split())
    assert "are not established non-Article-IV documents; they are documents" not in t
    assert "content-type label" in t, (
        "the retraction and the type tally have gone; the supplement is back to "
        "calling these rows unplaceable")


# --------------------------------------------- the guards, negatively tested --
_TREE = ["docs/PAPER_DRAFT_v2.md", "docs/PAPER_SUPPLEMENT_v1.md",
         "docs/PLOS_SUBMISSION_CHECKLIST.md", "docs/SUBMISSION_COVER_LETTER.md",
         "docs/SUBMISSION_DATA_AVAILABILITY.md",
         "docs/SUBMISSION_DAS_AUTHOR_NOTE.md", "third_eye_kit/MANIFEST.md"]


def _tree(tmp_path, mutations):
    for rel in _TREE:
        src = ROOT / rel
        if src.exists():
            dst = tmp_path / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    (tmp_path / "tools").mkdir(exist_ok=True)
    shutil.copy2(ROOT / "tools" / "check_submission_metadata.py",
                 tmp_path / "tools" / "check_submission_metadata.py")
    # The guard skips a check whose input is absent, which is right in the repo
    # and useless in a control: the first version of these controls asserted a
    # failure the guard never had the data to produce, and passed for the wrong
    # reason. So the tree carries a tests/ directory pytest can collect and the
    # built PDFs the page counts come from.
    (tmp_path / "tests").mkdir(exist_ok=True)
    (tmp_path / "tests" / "test_stub.py").write_text(
        "def test_a():\n    assert True\n\n\ndef test_b():\n    assert True\n",
        encoding="utf-8")
    for rel in ("build/submission/PLOS_ONE_submission.pdf",
                "build/submission/PLOS_ONE_supplement.pdf"):
        src = ROOT / rel
        if src.exists():
            dst = tmp_path / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    for rel, fn in mutations.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(fn(p.read_text(encoding="utf-8") if p.exists() else ""),
                     encoding="utf-8")
    return tmp_path


def _metadata(tmp_path):
    r = subprocess.run([sys.executable, "tools/check_submission_metadata.py"],
                       cwd=tmp_path, capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr


def test_guard_catches_a_checklist_page_count_that_stops_matching(tmp_path):
    """The exact defect found in the built package.

    The old pattern needed a backtick immediately before the filename. The
    checklist wrote the whole path inside the backticks, re.search returned
    None, and the comparison was skipped in silence for two rounds. Deleting the
    sentence must now fail, not pass.
    """
    t = _tree(tmp_path, {"docs/PLOS_SUBMISSION_CHECKLIST.md":
                         lambda s: re.sub(r"[^\n]*PLOS_ONE_supplement\.pdf[^\n]*",
                                          "", s)})
    code, out = _metadata(t)
    assert code == 1
    assert "checks nothing" in out or "states no supplement page count" in out


def test_guard_catches_a_stale_test_count(tmp_path):
    """437 against a collected 438 shipped in the PDF for a round."""
    t = _tree(tmp_path, {"docs/PAPER_DRAFT_v2.md":
                         lambda s: s.replace("test suite", "test suite of 999 tests")})
    code, out = _metadata(t)
    assert code == 1
    assert "999 tests" in out


def test_guard_catches_a_superseded_release_named_as_the_archive(tmp_path):
    """The data-availability statement cited the release the manuscript says
    must not be cited. Both documents were internally consistent, so nothing
    saw it."""
    t = _tree(tmp_path, {"docs/SUBMISSION_DATA_AVAILABILITY.md":
                         lambda s: s + "\n\nThe materials are archived at "
                                       "10.5281/zenodo.22168611.\n"})
    code, out = _metadata(t)
    assert code == 1
    assert "superseded release" in out


def test_the_superseded_guard_does_not_fire_on_a_bare_mention(tmp_path):
    """A guard that fires on any mention of the old DOI would forbid saying
    which release is superseded, which is the sentence we want kept."""
    t = _tree(tmp_path, {"docs/SUBMISSION_DATA_AVAILABILITY.md":
                         lambda s: s + "\n\nDo not cite 10.5281/zenodo.22168611.\n"})
    _, out = _metadata(t)
    assert "superseded release" not in out


# --------------------------------------------- the archive must hold the kit --
def test_every_machine_output_in_the_kit_is_also_in_the_public_archive():
    """The invariant that would have caught Table 5d's input going missing.

    `functional_form_sensitivity.json` reached the third-eye kit, because the
    kit's manifest names it, and did NOT reach the public archive, because the
    export carries its own explicit ANALYSIS list and nothing cross-checked the
    two. A reviewer could read Table 5d and its input; a reader of the permanent
    archive could read the table alone.

    The kit is the reviewer package and the public repo is the archive of
    record, so anything good enough for the first belongs in the second.
    """
    kit = ROOT / "third_eye_kit" / "06_machine_output"
    pub = ROOT.parent / "bankspeak-public" / "data" / "analysis"
    if not kit.exists() or not pub.exists():
        pytest.skip("kit or public export not built here")
    shipped = {p.name for p in kit.glob("*.json")}
    archived = {p.name for p in pub.glob("*.json")}
    # Panel cells and per-document tables are deliberately kit-only: they carry
    # document identifiers the public export withholds.
    #
    # The three imf_* files are a DIFFERENT case and are listed here to record
    # it, not to bless it. They are named individually on the public export's
    # own ANALYSIS/INCLUDE list and then dropped by a path rule that denies any
    # basename starting with "imf" -- so two lists in one file contradict each
    # other, and until round 20 they did it silently. Their contents are counts,
    # inclusion probabilities, seeds and column NAMES; the content scan passes
    # them. Whether an IMF-derived aggregate may be redistributed is a licensing
    # judgement, so it is flagged needs_human_review rather than decided by
    # loosening the pattern. build_public_repo.py now prints the contradiction
    # on every run.
    KIT_ONLY = {"P1_battery.json", "P2_battery.json", "family_verdict.json",
                "imf_access_probe.json", "imf_cadence_balance.json",
                "imf_frame_publication.json"}
    missing = shipped - archived - KIT_ONLY
    assert not missing, (
        f"in the reviewer kit but not the public archive: {sorted(missing)}. "
        f"Add them to ANALYSIS in tools/build_public_repo.py, or to KIT_ONLY "
        f"here with the reason they cannot be published.")


def test_table_3d_matches_the_json_it_was_generated_from():
    """Table 3d's cells were written into Markdown from the JSON once.

    Round 19 found S10.3's sixteen-cell table had disagreed with its JSON in
    fifteen cells while the paragraph beneath it stayed correct, because nobody
    regenerated the table after the numbers moved. This is the same shape of
    table and the same risk.
    """
    inst = _load(EXCL)["sibling_decomposition"]["institutions"]
    excl = _load(EXCL)["sibling_decomposition"]["excluding_icsid"]
    t = PAPER.read_text(encoding="utf-8")
    rows = {
        "IFC": (inst["IFC"], f"| IFC | {inst['IFC']['n_files']} |"),
        "ICSID": (inst["ICSID"], f"| ICSID | {inst['ICSID']['n_files']} |"),
        "MIGA": (inst["MIGA"], f"| MIGA | {inst['MIGA']['n_files']} |"),
    }
    for name, (row, prefix) in rows.items():
        line = next((l for l in t.splitlines() if l.startswith(prefix)), None)
        assert line, f"Table 3d has no row for {name} with {row['n_files']} files"
        assert f"{row['own_pct_change']:.1f}%".lstrip("-") in line.replace("−", "-"), (
            name, row["own_pct_change"], line)
        assert f"{row['first_year']}–{row['last_year']}" in line, (name, line)
    line = next(l for l in t.splitlines()
                if l.startswith("| the class without ICSID |"))
    assert f"{excl['n_files']}" in line
    assert f"{abs(excl['pct_change']):.1f}%" in line.replace("−", "-").replace("-", "")


def test_table_5d_matches_the_json_it_was_generated_from():
    """Same risk, same pin, for the functional-form table."""
    d = _load(FFS)["panels"]
    t = PAPER.read_text(encoding="utf-8").replace("−", "-")
    for key, label in (("as_published", "| frozen design |"),
                       ("no_wb_trend", "| no WB trend ‡ |"),
                       ("drop_2020", "| less 2020 |"),
                       ("drop_post_2024", "| less 2024 (C4) |")):
        line = next((l for l in t.splitlines() if l.startswith(label)), None)
        assert line, f"Table 5d has no row {label!r}"
        for panel in ("P1", "P2"):
            row = d[panel][key]
            assert f"{row['beta']:+.3f}" in line, (label, panel, row["beta"], line)
            assert f"{row['exact_p']:.4f}" in line, (label, panel, row["exact_p"])
            assert f"{row['origins_below_05']}/3" in line, (label, panel)


def test_the_unmapped_share_is_era_selective_and_explained():
    """The audit asked twice for the unmapped rows tallied BY YEAR.

    The share does swing from over 80% in 1999 to near zero from 2017, which on
    its own reads as a frame that loses pre-period documents and would bias a
    pre/post contrast. Both halves of the answer have to hold: the swing is real,
    AND it is the lifecycle of two discontinued publication types rather than
    failure on staff reports. If a future change broke the second half, the
    supplement paragraph would be asserting something untrue about the first.
    """
    d = _load(FRAME).get("unmapped_country_by_year")
    if d is None:
        pytest.skip("frame publication not rebuilt")
    assert d["share_1999_2016"] > 10 * d["share_2017_2025"], (
        "the era gradient the paragraph explains has gone")
    assert d["discontinued_share_of_early_unmapped"] > 0.95, (
        "the early unmapped rows are no longer overwhelmingly the two "
        "discontinued types, so the explanation no longer holds")
    pins = {int(y) for y, v in d["years"].items()
            if v["by_type"].get("Public Information Notice")}
    assert max(pins) <= 2013, f"PINs now appear after 2013: {sorted(pins)[-3:]}"
    t = " ".join(SUPP.read_text(encoding="utf-8").split())
    assert "era-selective" in t


def test_inverse_probability_weighting_is_degenerate_for_a_rate():
    """The audit asked for the comparator reweighted to the population.

    Inflating a sampled cell to its population total scales the count and the
    token offset by the same 1/pi, and the estimand is a rate, so beta cannot
    move except through integer rounding. The supplement note says so; this
    checks it rather than trusting the argument. The counts-only row must
    move, or the contrast the note draws is not visible.
    """
    d = _load(FFS)["panels"]
    for panel in ("P1", "P2"):
        base = d[panel]["as_published"]["beta"]
        ipw = d[panel].get("ipw_comparator")
        if ipw is None:
            pytest.skip("frame CSV absent; IPW rows not computed")
        assert abs(ipw["beta"] - base) < 0.005, (panel, base, ipw["beta"])
        wrong = d[panel]["ipw_counts_only"]["beta"]
        assert abs(wrong - base) > 0.02, (
            f"{panel}: scaling counts without tokens no longer differs from the "
            f"published estimate, so the note's contrast has gone")


def test_the_supplement_does_not_describe_a_superseded_abstract():
    """S10.8 said "the abstract now reports the subset figure as a 9- to 11-fold
    range". After the abstract was repaired it reported 10.8-fold, and that
    sentence became false while every count guard stayed green.

    A supplement that narrates what the manuscript says is a second copy of the
    manuscript, and it drifts like one.
    """
    t = " ".join(SUPP.read_text(encoding="utf-8").split())
    assert "9- to 11-fold" not in t
    agg = _load(TIER2)["aggregate"]
    ratio = agg["period_plausible_subset"]["production"]["ratio_equal_year"]
    assert f"{ratio:.1f}×" in t, (
        "S10.8 no longer states the equal-year subset ratio the abstract quotes")
