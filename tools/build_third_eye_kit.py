#!/usr/bin/env python3
"""Assemble the third-eye review kit, and refuse to build it if IMF text is in it.

An external model gets this bundle. Condition 6 of the IMF permission forbids
sending document text outside; the project's standing rule is blunter — counts,
hashes, log lines and column names may travel, document text may not, and that
includes pasting it into a chat with any assistant.

So the guard here is not a comment. Every file staged is scanned before it is
written, and the build ABORTS on a hit. The scan looks for two things:

1. Any path under an IMF text or PDF tree. No file from those trees is ever
   listed for inclusion, so a hit means the include list was edited carelessly.
2. Prose that looks like it came out of a staff report rather than out of our
   own writing — long runs of Article-IV boilerplate. This is heuristic and it is
   meant to be: the include list is hand-curated and the heuristic exists to
   catch a future edit that pastes an excerpt in to illustrate something.

The kit is deliberately NOT the whole repository. A reviewer drowning in eighty
markdown files reviews nothing. What travels is the manuscript, the frozen
design it must be checked against, the decision and deviation records that
explain every departure, the generated tables, the figures, and the machine
outputs that carry the numbers. Everything else is reachable from those.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "third_eye_kit"

# (source, destination subdir, why it is in the kit)
def _cite_summary() -> str:
    f = ROOT / "data" / "analysis" / "citation_audit.json"
    if not f.exists():
        return "its output (not present at build time)"
    d = json.loads(f.read_text(encoding="utf-8"))
    ok = sum(1 for e in d["entries"]
             if e.get("doi")
             and "NOT" not in str((e.get("check") or {}).get("verdict", "")).upper())
    unc = len(d.get("uncited_entries", []))
    return (f"its output: {d['n_entries']} entries, {ok} Crossref-resolved, "
            f"{unc or 'no'} uncited entr" + ("y" if unc == 1 else "ies"))


CITE_SUMMARY = _cite_summary()

INCLUDE = [
    # --- what is being reviewed
    ("docs/PAPER_DRAFT_v2.md", "01_manuscript",
     "the manuscript under review"),
    # --- what it must be checked against
    ("docs/PREREG_DRAFT_v0.5.md", "02_frozen_design",
     "Stage-A preregistration, the governing document"),
    ("docs/SAP_FINAL_DRAFT_20260820.md", "02_frozen_design",
     "Stage-B statistical analysis plan, frozen and externally timestamped"),
    ("docs/SAP_FREEZE_RECORD_20260825.md", "02_frozen_design",
     "the freeze evidence: DOI, sha256, three-way verification"),
    # --- every departure from the plan, on the record
    ("docs/DECISIONS_20260820_stageb_close.md", "03_decisions",
     "decisions D-1..D-13, each with its reasoning"),
    ("docs/DEVIATION_20260820_stageb_retrieval.md", "03_decisions",
     "the sealing-order deviation: retrieval preceded the SAP freeze"),
    ("docs/DEVIATION_20260827_c2_standardization.md", "03_decisions",
     "condition 2 was computed on the wrong stratifier; repair and its limits"),
    ("docs/AUDIT_20260820_researcher_dof.md", "03_decisions",
     "self-audit of researcher degrees of freedom, incl. the one "
     "outcome-informed choice"),
    ("docs/MDE_P1P2_20260820.md", "03_decisions",
     "power, computed before any outcome existed"),
    ("docs/RESULTS_20260827_confirmatory.md", "03_decisions",
     "the confirmatory run's own report"),
    # --- the numbers, as generated
    ("docs/tables", "04_tables", "all seven numbered tables, generated from data/"),
    ("docs/figures", "05_figures", "the four figures, generated from data/"),
    # --- machine outputs a reviewer may want to check a number against
    ("data/analysis/panels/P1_battery.json", "06_machine_output",
     "panel P1: all conditions, event study, validation outcomes, H-SHARED"),
    ("data/analysis/panels/P2_battery.json", "06_machine_output", "panel P2, same"),
    ("data/analysis/panels/family_verdict.json", "06_machine_output",
     "the governing verdict: Holm across panels"),
    ("data/analysis/panels/cells_P1.csv", "06_machine_output",
     "P1 institution-year cells: counts, tokens, guard variants"),
    ("data/analysis/panels/cells_P2.csv", "06_machine_output", "P2 cells"),
    # Omitted from the first bundle, which is why the third-eye reviewer could
    # not run the preregistered document-level QML. Derived counts only.
    ("data/analysis/panels/docs_P1.csv", "06_machine_output",
     "P1 DOCUMENT-level counts and token totals"),
    ("data/analysis/panels/docs_P2.csv", "06_machine_output", "P2 document-level"),
    ("data/analysis/prereg_sensitivities.json", "06_machine_output",
     "the two PREREG §4 secondary sensitivities, run 2026-08-29"),
    ("tools/prereg_sensitivities.py", "07_code",
     "HAC(3) annual-difference and document-level clustered QML"),
    ("data/analysis/trend_analysis.json", "06_machine_output",
     "the differential-trend exploration (post-hoc, NOT in the manuscript)"),
    ("data/analysis/its_results.csv", "06_machine_output",
     "per-stratum ITS incl. placebo_sig_frac"),
    ("data/features/ar_fy_features.csv", "06_machine_output",
     "the 76 assembled Annual Report fiscal-year units"),
    # --- the code that produced the reported numbers
    ("src/bootstrap_engine.py", "07_code",
     "the frozen inference engine and its design matrix"),
    ("src/s13_validation_battery.py", "07_code",
     "the four conditions, the companions, the family verdict"),
    ("src/standardize.py", "07_code", "condition 2's standardization estimator"),
    ("tools/make_paper_tables.py", "07_code", "every numbered table comes from here"),
    ("tools/make_paper_figures.py", "07_code", "every figure comes from here"),
    # --- prior work the reviewer is asked to ATTACK, not adopt
    ("docs/VENUE_RESEARCH_20260828.md", "08_venue_research",
     "a prior venue-research pass; its conclusions are unacted-on and several "
     "of its facts are explicitly unverified"),
    # The submission package itself — the editor reads these before the paper.
    ("docs/SUBMISSION_COVER_LETTER.md", "09_submission",
     "the cover letter as it would be sent"),
    ("docs/SUBMISSION_DATA_AVAILABILITY.md", "09_submission",
     "the data-availability statement as it would be pasted into the form"),
    ("build/submission/PLOS_ONE_submission.pdf", "01_manuscript",
     "the single PDF an editor actually receives — the editor lens should read "
     "this rather than the Markdown, because layout is part of the ninety seconds"),
    ("docs/PAPER_SUPPLEMENT_v1.md", "01_manuscript",
     "the ten-section supplement the manuscript cross-references"),
    ("data/analysis/rq1_decomposition.json", "06_machine_output",
     "the corpus-selection decomposition behind the title's second claim"),
    ("data/meta/imf_access_probe.json", "06_machine_output",
     "byte-checked probe of the access routes the DAS describes"),
    # The access route itself, so a reviewer evaluating the data-availability
    # statement can see what it points at. Already public on GitHub; report
    # number, year, country, DOI and our SHA-256, with no title and no IMF URL.
    ("data/meta/imf_document_index.csv", "09_submission",
     "the 1,064-document access index the DAS relies on"),
    ("docs/ROUND15_PRESUBMISSION_REVIEW.md", "08_venue_research",
     "the round-15 adversarial review, verbatim — six lenses, refute-by-default "
     "verification; attack it rather than adopting it"),
    ("docs/ROUND15_RESPONSE.md", "03_decisions",
     "what was independently re-verified before acting, what was fixed, and the "
     "five deposit files whose licence position is the author's call"),
    ("data/analysis/block_origin_enumeration.json", "06_machine_output",
     "exact PASS-P p at all three block origins — Table 5c's source"),
    ("data/analysis/dispersion_calibration.json", "06_machine_output",
     "supplement S9: what the frozen dispersion estimator recovers, and what "
     "PASS-P's size does when it cannot see the dispersion"),
    ("tools/dispersion_calibration.py", "07_code",
     "the two experiments behind S9 — recovery and size, 1,000 replicates each"),
    ("data/analysis/retrieval_route_tally.json", "06_machine_output",
     "per-document retrieval routes, 705/4/1/354, against 1,120 attempt rows"),
    # Round 16. The manuscript now cites S10 and Table 3c; without these the
    # reviewer is asked to take three simulations and a decomposition on trust.
    ("data/analysis/ar_exclusion_classes.json", "06_machine_output",
     "Tables 3c and 3d: what the 195 excluded Annual-Report files are, by class and trend, and the sibling class decomposed by institution — each sibling falls on its own series and the class-level +64.4% is a membership change"),
    ("data/meta/ar_assembly_log.csv", "06_machine_output",
     "the assembler's rule per document — Table 3c's only source, and the only "
     "file that maps a volume to IFC vs MIGA vs ICSID"),
    ("tools/ar_exclusion_classes.py", "07_code",
     "what builds it, from the assembler's own logged rule per document"),
    ("data/analysis/dispersion_robust_inference.json", "06_machine_output",
     "S10.1: the d.o.f.-corrected dispersion, the exact p under it, and the size "
     "it does NOT repair"),
    ("tools/dispersion_robust_inference.py", "07_code",
     "the post-freeze dispersion-corrected analysis -- NOT size-controlled, which is S10.4's finding; the frozen engine is untouched"),
    ("data/analysis/stage_a_exposure_sensitivity.json", "06_machine_output",
     "S10.2: the panels rerun without every Stage-A-inspected document"),
    ("tools/stage_a_exposure_sensitivity.py", "07_code", "what reruns them"),
    ("data/analysis/ar_component_inventory.json", "06_machine_output",
     "Table 3e: the decline under three corpus definitions — narrative-only "
     "-58.8%, frozen -42.5%, full family -35.4%"),
    ("tools/ar_component_inventory.py", "07_code", "the component inventory"),
    ("data/analysis/tier2_period_fairness.json", "06_machine_output",
     "S10.6: the Tier-2 ratio is 28x on all terms and 11x on the terms that "
     "existed in 1946-65; 22 of 35 are absent from the early window"),
    ("tools/tier2_period_fairness.py", "07_code", "the period-fairness split"),
    ("data/analysis/imf_cadence_balance.json", "06_machine_output",
     "S10.5: the post window is LESS delayed than the pre window (56.8% vs "
     "61.7%), and balancing moves the p-value not the estimate"),
    ("tools/imf_cadence_balance.py", "07_code", "the cadence diagnostic and rerun"),
    ("tools/check_stated_counts.py", "07_code",
     "refuses if a count stated in prose disagrees with the filesystem"),
    ("data/analysis/companion_volume_adjudication.json", "06_machine_output",
     "Table 3c: four of the five records excluded as duplicates are distinct "
     "components sharing a metadata key; restoring them moves the headline "
     "from -42.5% to -35.4%"),
    ("tools/companion_volume_adjudication.py", "07_code",
     "what adjudicates them, by title rather than by key"),
    ("data/analysis/ar1_null_calibration.json", "06_machine_output",
     "per-panel PASS-P size under the preregistered differential AR(1) shock. "
     "This is the study S10.4 was built on and it measures a per-panel raw "
     "threshold, NOT the governing rule — see joint_holm_calibration"),
    ("tools/ar1_null_calibration.py", "07_code",
     "the per-panel calibration, kept because it is what the earlier claim "
     "rested on; its streams are now hashed rather than derived from a label's "
     "length, which had given both panels one stream"),
    ("data/analysis/joint_holm_calibration.json", "06_machine_output",
     "S10.4 rebuilt: both panels drawn together with one shared comparator "
     "arm, the preregistered Holm step-down applied every replicate, the inner "
     "p enumerated over all 512 sign patterns. The family error runs 0.0365 "
     "under the preregistered null to 0.086 under fitted means, with 0.094 when rho and sigma are redrawn too"),
    ("tools/joint_holm_calibration.py", "07_code",
     "the joint calibration, including two candidate mechanisms its own "
     "diagnostics refute"),
    ("data/analysis/functional_form_sensitivity.json", "06_machine_output",
     "Table 5d: the estimate without the institution trend, at three alternative "
     "pre-period starts, with 2020/2021 dropped and with each post year dropped "
     "-- each row also evaluated at all three block origins, because deleting a "
     "year moves the partition as well as the data"),
    ("tools/functional_form_sensitivity.py", "07_code",
     "what builds Table 5d; inner p enumerated, not sampled"),
    ("docs/ROUND20_RESPONSE.md", "03_decisions",
     "the response to the independent audit of the built package: what it got "
     "right, what it got wrong, and the two findings in our own text that it "
     "surfaced -- the sibling-class attribution and the retrieval-route wording"),
    ("data/analysis/tier2_item_provenance.csv", "06_machine_output",
     "S10.8: the per-term Tier-2 table. The source columns read 'not recorded "
     "in repository' because that is what the repository holds"),
    ("data/analysis/tier2_item_provenance.json", "06_machine_output",
     "the same, with both match rules and the denominator decomposition"),
    ("tools/tier2_item_provenance.py", "07_code",
     "the per-term table, World Bank assembled text only"),
    ("data/analysis/imf_frame_publication.csv", "06_machine_output",
     "S10.7: the comparator's per-year eligible frame, inclusion probabilities "
     "and per-cell seeds"),
    ("data/analysis/imf_frame_publication.json", "06_machine_output",
     "the draw replay, the within-cell fragility probe and the limitations"),
    ("tools/imf_frame_publication.py", "07_code",
     "the frame publication; metadata and counts only, no document text"),
    ("data/analysis/passe_coverage.json", "06_machine_output",
     "S10.3: measured PASS-E interval coverage against a nominal 0.95"),
    ("tools/passe_coverage.py", "07_code", "the coverage study"),
    ("data/analysis/hshared_draw_diagnostics.json", "06_machine_output",
     "why all 1,607 discarded H-SHARED draws failed the same way"),
    ("tools/hshared_draw_diagnostics.py", "07_code", "the discard classifier"),
    ("docs/PLOS_SUBMISSION_CHECKLIST.md", "09_submission",
     "the venue's stated limits, measured rather than assumed — including the "
     "abstract that was 374 words against a limit of 300"),
    ("tools/plos_compliance.py", "07_code",
     "what measures them, with the negative control that makes its clean "
     "verdict mean something"),
    ("docs/REFERENCES_vancouver.md", "09_submission",
     "the numbered reference list built from Crossref, ordered by first "
     "appearance, held ready for the accept-stage conversion"),
    ("tools/make_vancouver_refs.py", "07_code",
     "what builds it, and what it refuses to invent"),
    ("tools/rq1_decomposition.py", "07_code", "the decomposition"),
    ("tools/probe_imf_access.py", "07_code", "the access probe"),
    ("tools/audit_citations.py", "07_code",
     "the mechanical half of the citation audit — DOI resolution and the two-way"
     " in-text cross-check; the claim-support check is the reviewer's"),
    # Derived, not typed: this line said "25 entries, 22 Crossref-resolved"
    # while the file in the same bundle held 34 and 31, and the count guard
    # read only the manifest's opening file total. It is the one entry whose
    # description is a claim about its own file's contents, so it is the one
    # entry that computes it.
    ("data/analysis/citation_audit.json", "06_machine_output", CITE_SUMMARY),
    ("docs/VENUE_FINAL_20260828.md", "08_venue_research",
     "THE CURRENT RECOMMENDATION: PLOS ONE, with the Article-in-Press finding "
     "that eliminated the previous favourite"),
    ("docs/VENUE_DECISION_SCI_20260828.md", "08_venue_research",
     "the decision under a Web of Science constraint: 17 venues assessed on "
     "index, real publication lag and scope; none clears March 2027 at its "
     "median"),
    ("docs/UAK_RULES_VERBATIM_20260828.md", "08_venue_research",
     "the three UAK rules quoted from the source PDFs"),
    ("docs/VENUE_FACTS_VERIFIED_20260828.md", "08_venue_research",
     "the five previously-unverified venue facts, resolved against primary "
     "sources; several answers differ from the research pass"),
    ("docs/FRAMING_OPTION_B_20260828.md", "08_venue_research",
     "a drafted alternative framing (RQ1 leads, apparatus becomes warrant), "
     "written so option A and option B can be compared as texts rather than as "
     "descriptions; NOT applied to the manuscript"),
]

# Trees whose CONTENT may never leave the machine.
FORBIDDEN_TREES = ("data/raw/imf_article_iv", "data/text/imf_article_iv",
                   "data/raw/imf_cr_pdf", "data/meta/imf_articleiv_raw")

# Heuristic: Article IV boilerplate that would only appear if someone pasted
# document text in. Deliberately narrow — false positives here are cheap and a
# false negative is a licence breach.
LEAK_PATTERNS = [
    re.compile(r"staff\s+report\s+for\s+the\s+\d{4}\s+article\s+iv", re.I),
    re.compile(r"executive\s+board\s+concluded\s+the\s+article\s+iv", re.I),
    re.compile(r"in\s+the\s+context\s+of\s+the\s+\d{4}\s+article\s+iv\s+"
               r"consultation\s+with", re.I),
]
TEXT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".py", ".yaml", ".yml"}


def staged_files():
    for rel, sub, why in INCLUDE:
        src = ROOT / rel
        if src.is_dir():
            for f in sorted(src.rglob("*")):
                if f.is_file() and not f.name.startswith("."):
                    yield f, sub, why
        elif src.exists():
            yield src, sub, why
        else:
            print(f"[kit] MISSING, skipped: {rel}")


def scan(path: Path) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    hits = [f"path lies under a forbidden tree: {t}"
            for t in FORBIDDEN_TREES if rel.startswith(t)]
    if path.suffix.lower() in TEXT_SUFFIXES:
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:                       # unreadable is not clean
            return hits + [f"could not read to scan: {e}"]
        for pat in LEAK_PATTERNS:
            m = pat.search(body)
            if m:
                hits.append(f"looks like pasted document text: {pat.pattern!r} "
                            f"matched at offset {m.start()}")
    return hits


def main() -> int:
    files = list(staged_files())
    digests: dict[str, str] = {}
    # A path staged twice is copied once and listed twice, so the manifest's
    # count says one more file than the bundle holds. That is how a duplicate
    # got in: the count and the listing disagreed and only the external count
    # guard noticed. Refuse instead.
    seen, dupes = set(), []
    for f, sub, _why in files:
        key = (sub, f.resolve())
        if key in seen:
            dupes.append(f"{sub}/{f.name}")
        seen.add(key)
    if dupes:
        raise SystemExit(f"[kit] REFUSING: staged more than once: {dupes}")
    problems = {}
    for f, _, _ in files:
        h = scan(f)
        if h:
            problems[f.relative_to(ROOT).as_posix()] = h
    if problems:
        print("[kit] REFUSING TO BUILD — the bundle would carry IMF document "
              "text or a forbidden path:")
        for k, v in problems.items():
            for line in v:
                print(f"    {k}: {line}")
        return 1

    if KIT.exists():
        shutil.rmtree(KIT)
    manifest = ["| file | why it is in the kit |", "|---|---|"]
    total = 0
    for f, sub, why in files:
        dest = KIT / sub / f.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        total += f.stat().st_size
        digests[f"{sub}/{f.name}"] = hashlib.sha256(f.read_bytes()).hexdigest()
        manifest.append(f"| `{sub}/{f.name}` | {why} |")

    # +2 for the two files written after `files` is fixed: MANIFEST.md itself
    # and SHA256SUMS.json. The count shipped inside the bundle was one short of
    # what an unzip produced -- 91 against 92 -- in a file whose whole job is to
    # say what is in the bundle, and adding the digest record made it two short
    # until this line was corrected with it.
    n_shipped = len(files) + 2
    (KIT / "MANIFEST.md").write_text(
        "# Third-eye review kit\n\n"
        f"{n_shipped} files (this manifest included), {total/1e6:.2f} MB. "
        "Assembled by "
        "`tools/build_third_eye_kit.py`, which refuses to build if any staged "
        "file lies under an IMF text or PDF tree or looks like pasted document "
        "text.\n\n"
        "**No IMF document text is in this bundle, and none may be added.** The "
        "corpus is used under a written permission that forbids redistributing "
        "documents or extracted text. Counts, hashes, column names and log lines "
        "are permitted derived outputs and are what travels here.\n\n"
        + "\n".join(manifest) + "\n", encoding="utf-8")

    # The kit is gitignored, so git cannot see it go stale, and it did: four
    # files in the bundle differed from their repository originals while the
    # bundle claimed to be a copy of them. Recording the digests lets
    # check_kit_freshness answer the question without rebuilding.
    (KIT / "SHA256SUMS.json").write_text(
        json.dumps({"built_from": str(ROOT), "files": digests}, indent=1),
        encoding="utf-8")

    print(f"[kit] {n_shipped} files, {total/1e6:.2f} MB -> "
          f"{KIT.relative_to(ROOT)}")
    print("[kit] leak scan clean: no forbidden path, no document-text signature")
    return 0


if __name__ == "__main__":
    sys.exit(main())
