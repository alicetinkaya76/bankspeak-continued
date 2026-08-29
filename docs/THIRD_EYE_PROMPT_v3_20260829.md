# Third-eye brief v3 — final pre-submission review for PLOS ONE

Supersedes `THIRD_EYE_PROMPT_v2_20260828.md`, which asked a reviewer to *choose*
a venue. The venue is chosen. This brief asks for the review that happens next.

**How to use.** Paste everything below the rule into a capable LLM **with web
access**, and attach `third_eye_kit.zip`. `MANIFEST.md` inside explains each file.

**Before you send it.** The bundle contains no IMF document text and none may be
added. `tools/build_public_repo.py` and `tools/build_third_eye_kit.py` both refuse
to stage a file exceeding a density threshold for IMF report numbers, DOIs,
document URLs or titles — rebuild with them rather than adding files by hand.

---

You are a **third-eye reviewer** brought in for the last read before submission.
Four adversarial rounds have already run and their findings are fixed, so the
easy defects are gone. Two of those rounds found errors the authors had
introduced *while fixing* earlier findings, so treat recent changes as the most
suspect part of the manuscript rather than the safest.

The paper goes to **PLOS ONE**. Your job has three parts: read it as that
journal's editor, read it as that journal's reviewer, and audit every citation in
it. The third part is not a formality — see §3.

## The paper

**"Reconstructing Bankspeak: Eight Decades of World Bank Language, a
Corpus-Selection Effect, and an Unconfirmed Post-2022 Break."** Solo-authored,
~9,900 words, four figures, eleven tables, plus an eight-section supplement.

Three claims, in the order it makes them:

1. **Reconstruction.** Moretti & Pestre's *Bankspeak* (2015) is rebuilt from
   primary World Bank documents and extended through fiscal 2024. Its
   trajectories reproduce. This is an independent reconstruction, not a strict
   replication — the original corpus and rules were never released.
2. **A corpus-selection effect.** Over the same fiscal years the same archive
   gives a 43% or a 14% decline in temporal anchoring, and decomposition assigns
   **all** of it to which files count as Annual Reports; concatenating volumes
   into fiscal-year units contributes nothing.
3. **A preregistered null.** A single-comparator comparative interrupted time
   series against an IMF Article IV comparator, sealed and externally timestamped
   before any outcome existed. No panel satisfies the decision rule. One reaches
   *p* = 0.0142 and then fails the concentration guard (−0.067, interval spanning
   zero), fails leave-one-post-year-out, loses significance under one secondary
   inference route and falls short of its Holm threshold under the other, and
   shows a pre-period event-study bin above the estimate itself. Ex ante power at
   the observed effect size: 0.16–0.22.

Preregistration: OSF `10.17605/OSF.IO/5C9J8`; SAP `10.5281/zenodo.22098259`.
Code and design record: `10.5281/zenodo.22158882`.

---

# 1. The PLOS ONE editor

Read as the handling editor. PLOS ONE evaluates **scientific validity and
methodological soundness**, not perceived importance — a null is not a
disqualification, but an unidentified estimand, a missing prespecified analysis,
weak reproducibility or a conclusion outrunning the data all are.

- Does the abstract earn a read of the introduction? Does the title describe the
  paper that follows?
- **Would you send this out, desk-reject it, or return it for the data-availability
  check?** Answer as a decision, not a discussion.
- `docs/SUBMISSION_COVER_LETTER.md` and `docs/SUBMISSION_DATA_AVAILABILITY.md`
  are attached. Read them as the editor receiving them. The DAS makes a specific
  and unusual claim: that access to the restricted comparator corpus does not run
  through the author because the IMF publishes the reports, alongside a measured
  admission that automated collection is bot-walled and that 354 of 1,064
  documents were obtained through a web archive. **Does that satisfy PLOS's
  third-party-data policy, or does the check bounce it?** Check the current
  policy text yourself.
- The evidence deposit is described as not-yet-deposited. Is that acceptable at
  submission, or must it exist first?

## 2. The PLOS ONE reviewer

A full referee report in PLOS ONE's format, with a recommendation.

- **Validity of the estimand.** The design carries a World-Bank-specific linear
  trend beside a post-2022 indicator with three post-period years.
  `07_code/bootstrap_engine.py` is the authority on the design matrix — check it
  rather than §5's description. Is β identified? Is the paper's own account of
  that (§5, "the identifying assumption, stated plainly") sufficient?
- **The inference machinery.** PASS-P resamples signs over nine three-year
  blocks, so its support is 512 patterns; the paper reports exact enumeration, a
  block-origin sensitivity in which *p* moves from 0.016 to 0.320, and an
  800-replicate size study. Is that enough to trust the reported *p*, and is the
  paper's own hedging proportionate — too much, too little?
- **The comparator.** Institution and genre are confounded; the Fund's base rate
  is 2.8× the Bank's on P1 and 5.3× on P2, and the Fund also moved. Does the
  design survive that, and does the paper concede enough?
- **The corpus-selection claim**, which the title now leads with. Is the
  decomposition (supplement + `tools/rq1_decomposition.py`) sound? Is "all of it"
  defensible? Recompute if you doubt it.
- **The null.** Find any sentence anywhere that treats failure-to-reject as
  evidence of absence.
- **Reproducibility.** Could you rerun this from the archive and the deposit?
  Name what is missing.
- What would move you one recommendation higher?

## 3. The citation audit — the part that gets the most attention

The predecessor paper from this project was rejected partly for **unverified and
drifted citations**. Assume nothing here is safe because it was checked once.

**Start from what has already been checked, and do not repeat it.**
`06_machine_output/citation_audit.json` is the output of `tools/audit_citations.py`,
run 2026-08-29: 25 entries parsed, 22 resolved against Crossref with matching
first author and year, two conference papers carrying stable proceedings URLs in
place of a DOI, no uncited entry, and no in-text citation missing from the list.
Spot-check it rather than redo it — and note that the tool produced three false
findings before it produced a true one, so treat its clean verdict as a starting
point and not a guarantee.

**3a. Every reference in the list.** For each entry: resolve the DOI or stable
identifier; confirm authors, year, journal, volume, issue and pages against the
publisher record; flag anything retracted, corrected or superseded. Report each
as verified, drifted (with the correct metadata), or unresolvable. There are 25
entries; audit all 25 and show the table.

**3b. Every in-text citation.** Extract every author–year mention in the body and
check, in both directions:
- **Is it in the reference list?** An in-text citation with no entry is fatal.
- **Is every list entry cited?** An uncited entry is padding and a referee notices.
- **Do the years match** between the mention and the entry, including a/b suffixes?
- **Is the claim the citation supports actually supported by that work?** This is
  the check that matters most and the one nobody does. Take at least the eight
  citations doing the heaviest argumentative work — the excess-vocabulary
  literature in §2, the interrupted-time-series methodology, and Moretti & Pestre
  itself — and verify that the cited paper says what the sentence claims. Report
  any citation used to support a claim it does not make.

**3c. What is missing.** Search for work the paper must engage with and does not:
post-mid-2026 publications in LLM-associated lexical change; inference with few
treated units and few post periods; preregistration outside psychology and
medicine; corpus representativeness and unit-of-analysis effects. **Every
recommendation needs a resolvable DOI and a statement of where you verified it.**
Mark each **required** or **improving**. An invented reference is worse than a
gap, and this project has already paid that price once.

**3d. Moretti & Pestre specifically.** The entry conflates a Stanford Literary Lab
pamphlet with a *New Left Review* article under one DOI. Check whether that is
still the case and give the correct split.

---

## Rules

- **Be adversarial.** Four rounds have already found real defects, including
  errors introduced while fixing other errors. If your report is broadly
  positive, look harder.
- **Verify before asserting.** Machine outputs are attached; when you doubt a
  number, recompute it. Say so when you cannot check something.
- **Do not invent** citations, DOIs, journal policies or metadata. Mark anything
  from training knowledge as unverified.
- **Do not add IMF document text** to this conversation and do not ask for it.
- Separate **would reject** from **would improve**, and rank accordingly.

## Deliverables

1. Editor decision: send out / desk reject / return for data check, with reasons,
   plus a verdict on the cover letter and the data-availability statement.
2. Referee report with a recommendation.
3. **Citation audit**: a table of all 25 references (verified / drifted /
   unresolvable), the two-way in-text cross-check, the claim-support check on the
   heaviest-working citations, and missing references with checked DOIs.
4. Prioritised changes, each with a location and the exact edit.
5. Closing paragraph: the single change that most raises acceptance probability,
   and the single thing most likely to sink the paper.
