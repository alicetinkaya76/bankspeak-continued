# Third-eye prompt, round 4 (paste everything below the line into the external model; attach round4_package zip)

Round 4 reviews the response to your round-3 review. The authors adopted every round-3
refutation, corrected the audit record (v1.1), withdrew PREREG v0.1, and produced a
redesigned PREREG v0.2. This round has one central deliverable: **a binary ruling on
whether v0.2 may be frozen as the Stage-A protocol** — APPROVE AS WRITTEN / APPROVE WITH
LISTED LINE EDITS / REJECT WITH REQUIRED CHANGES. Everything else supports that ruling.

---

## Step 0 — Package integrity (do this before anything else)

You should have received a zip containing exactly these files (bytes, path):

            7  .python-version
          568  Makefile
        4,120  config/config.pilot.yaml
        4,295  config/config.yaml
      218,133  data/analysis/paper/F1_ar_assembled_classic.png
      208,719  data/analysis/paper/F2_marker_tiers_by_stratum.png
        8,324  data/analysis/paper/NUMBERS.md
          208  data/analysis/paper/T1_corpus.csv
        3,668  data/analysis/paper/T2_its.csv
          109  data/analysis/paper/T3_power.csv
          172  data/analysis/robustness/breakpoint_rank_2023.csv
        7,854  data/analysis/robustness/breakpoint_scan_tier1.csv
        1,524  data/analysis/robustness/loyo_ar_tier1.csv
        2,701  data/analysis/robustness/robust_aggregation.csv
        6,212  data/analysis/robustness/tier1_decomposition.csv
        6,224  data/features/ar_fy_features.csv
      191,528  data/features/classic.csv
      103,588  data/features/markers.csv
      222,800  data/features/ppl.csv
       43,182  data/meta/ar_assembly_log.csv
        2,792  data/meta/ar_unit_qc.csv
    1,602,123  data/meta/download_failures.csv
      133,837  data/meta/extraction_log.csv
      888,682  data/meta/frozen_sampling_v1.csv
       14,039  docs/DESIGN_RATIONALE.md
       14,366  docs/PAPER_DRAFT_v0.md
        7,441  docs/PREREG_DRAFT_v0.1.md
       13,507  docs/PREREG_DRAFT_v0.2.md
        5,113  docs/RESPONSE_TO_REVIEW.md
       13,417  docs/ROUND2_AUDIT_COMPLETION.md
       12,076  docs/ROUND2_AUDIT_COMPLETION_v1.1.md
       36,443  docs/ROUND3_THIRD_EYE_REVIEW.md
        8,180  docs/THIRD_EYE_REVIEW_PROMPT_v3.md
       25,236  docs/round2_external_review.md
          121  requirements-ppl.txt
          154  requirements.txt
        1,382  src/s00_discover_facets.py
        3,575  src/s01_fetch_metadata.py
        4,642  src/s02_download_texts.py
        2,342  src/s03_extract_text.py
        1,836  src/s04_features_classic.py
        1,464  src/s05_features_markers.py
        3,831  src/s06_perplexity_panel.py
        2,893  src/s07_power_analysis.py
        4,595  src/s08_its_analysis.py
          772  src/s09_imf_comparator_stub.py
        9,004  src/s10_assemble_ar.py
        8,739  src/s11_paper_artifacts.py
        7,681  src/s12_robustness.py
        3,261  src/textstats.py
        3,167  src/utils.py
        3,345  tests/test_assembly_rules.py
        2,457  tests/test_features_smoke.py
    (plus this prompt as docs/THIRD_EYE_REVIEW_PROMPT_v4.md, a standard SHA256SUMS, and MANIFEST.tsv)

**If ANY listed file is missing or unreadable, STOP and output only the missing-file
list.** Checksums are now provided in standard `sha256sum -c` format (`SHA256SUMS`),
with sizes in `MANIFEST.tsv` — the round-3 format complaint is adopted.

## What is new since round 3

- `docs/ROUND3_THIRD_EYE_REVIEW.md` — your round-3 review, archived verbatim.
- `docs/ROUND2_AUDIT_COMPLETION_v1.1.md` — corrected audit record. Its §0 version log
  adopts all six round-3 corrections **using round-3's own numbers** (HHI 0.244507 /
  effective 4.09 / seamless 13.03%; ICR 92.14% and PAD 89.51% on analyzed 2020s ids;
  8-of-10 preceding units; doc-level 20 vs assembled ≈10 hits; residue as 62 4xx + 3
  no-URL; the 5.8744 zero-token GPT-2 constants). v1.0 remains archived unchanged.
- `docs/PREREG_DRAFT_v0.2.md` — full redesign. v0.1 is withdrawn and archived.
- `src/`, `tests/`, `Makefile`, `requirements*.txt`, `.python-version`,
  `config/config.pilot.yaml` — the source and environment disclosure you demanded
  (E16, partially met). Definition pointers: the QC stopword list is the 15-word
  frozenset in `src/s10_assemble_ar.py` (sha256 of the sorted newline-joined list
  begins `3b5d2b51754f73011aeb20ce28bcfcde`); the tokenizer is `TOKEN_RE = [A-Za-z']+`
  over lowercased text in `src/textstats.py`; marker counting is exact token membership
  (`rate_from_list`); `config/config.pilot.yaml` is the pilot that produced the 392
  out-of-sample extraction-log ids.

## Declared open items — do NOT spend effort re-flagging these; rule only on their
placement

1. Round-1 review text: not yet retrieved (author-side); O9/E8 crosswalk therefore still
   pending.
2. Immutable model revision hashes: config still says `revision: main`; the prereg
   requires hashes at Stage-A. Stage-A cannot complete without them; this review can.
3. Regenerated artifacts (family-mapped decomposition, eligibility-filtered NLL,
   provenance-columned extraction log, E-series draft edits): scheduled step-1 code
   work. The `data/` CSVs in this package are **unchanged from round 3** by design.
4. External timestamps (OSF or equivalent): executed at the freezes, after this review.
5. Raw/extracted text: still excluded (2.4 GB). End-to-end recomputation remains out of
   scope; **definition-level** checks are now in scope via `src/`.

## Role 1 — Correction verifier

1. Confirm v1.1 §0 matches your round-3 numbers, and check that no v1.0 error survives
   anywhere else in v1.1 (verdict tables, verified-numbers register, E10–E17).
2. Definition-level code check (no raw text needed): does the disclosed implementation
   match the paper/prereg definitions — stopword list and share computation vs the
   draft's wording; `TOKEN_RE`/lowercasing vs the prereg Appendix-A matching rule;
   marker counting vs the outcome definition; seed usage; anything in `src/s08`
   (centered-interaction ITS form) or `src/s12` that contradicts a documented claim.
3. Flag any correction the round-3 review required that v1.1 failed to register.

## Role 2 — Preregistration freeze review (primary role)

1. Walk your round-3 blocking-defect table (14 rows) and rule each one
   **RESOLVED / PARTIALLY / UNRESOLVED** in v0.2, with the v0.2 section that answers it.
2. Stress-test the elements v0.2 introduced that round 3 never saw:
   - the **conditional-primary switch** (Stage-B metadata-only probe of WB
     country-surveillance genres — CEM/SCD/CPF; fixed feasibility criteria; if PASS,
     genre-matched P0 replaces the co-primaries). Is a prespecified conditional primary
     acceptable, or a forking-paths risk as written?
   - the paired moving-block bootstrap (block length 3; 9,999 replications; null by
     recentering; joint resampling of paired institution-years);
   - the numeric constants: <50% magnitude-stability, Holm p<0.10 leave-one-post-year,
     80% common-support hard-fail, 50% effective-sample-size floor, 99th-percentile
     weight truncation, NLL eligibility ≥100 tokens, Holm over two co-primaries;
   - the concentration guard identifying the top family **at analysis time** from
     pooled post-period data — should it instead be fixed now (underscore is already
     known to lead on the WB side)?
   - the δ pretrend-credibility bound derived from the MDE simulation;
   - the outcome choice: occurrence count with an honest no-total-change note — right
     call, or should breadth/prevalence be primary?
3. Give the binary ruling: **APPROVE AS WRITTEN / APPROVE WITH LISTED LINE EDITS /
   REJECT WITH REQUIRED CHANGES** — with the exact line edits or changes.

## Role 3 — Editor

1. Minimal preconditions: exactly which step-1 repairs and which of the declared open
   items must complete **before** the Stage-A freeze, and which may proceed in parallel
   or wait for the locked-robustness step?
2. Is reviewing and freezing the prereg before the code-level artifact regeneration an
   acceptable sequencing, per your own reordered path?
3. Update the blocking table only where this package changes a status; confirm or amend
   the fallback decision point (RQ1/measurement paper with RQ2 exploratory) relative to
   the March 2027 target.

## Output format

Three headed sections — **Corrections / Prereg freeze / Editor** — each ending with a
ranked action list, blocking items first. The prereg section MUST end with the binary
ruling. English. Recompute what you assert or label it NOT RECOMPUTABLE. No praise;
review. No new literature unless strictly required (then authors, year, venue, DOI,
confidence).
