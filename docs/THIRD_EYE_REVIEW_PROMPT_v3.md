# Third-eye prompt, round 3 (paste everything below the line into the external model; attach round3_package zip)

Round-3 purpose differs from round 2. The round-2 manuscript review stands and is included.
Round 3 exists because the round-2 package failed in transit — only the docx reached the
reviewer, so the file-grounded audit was never performed — and because an internal audit
has since recomputed every number and must itself be adversarially checked. A comparator
preregistration is also included for critique BEFORE any comparator data exists.

---

## Step 0 — Package integrity (do this before anything else)

You should have received a zip containing exactly these files (bytes, path):

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
        5,113  docs/RESPONSE_TO_REVIEW.md
       13,417  docs/ROUND2_AUDIT_COMPLETION.md
       25,236  docs/round2_external_review.md
    (plus this prompt as docs/THIRD_EYE_REVIEW_PROMPT_v3.md and a root MANIFEST.sha256)

**If ANY listed file is missing or unreadable, STOP immediately and output only the list
of missing files. Do not review a partial package.** Round 2 failed exactly this way and
produced eleven wasted NOT AUDITABLE verdicts.

## Context

- `docs/RESPONSE_TO_REVIEW.md` — the authors' round-1 point-by-point memo; it defines
  labels A1–A3, O3–O8, O10. **O9 is absent from the memo** (a labeling defect the
  internal audit flags in its §1).
- `docs/round2_external_review.md` — the round-2 review, performed on the draft alone:
  disposition "desk-reject in the submitted form" / scientific state major revision;
  every A/O item NOT AUDITABLE for lack of files. Treat it as your own predecessor round.
- `docs/ROUND2_AUDIT_COMPLETION.md` — the internal audit completing round 2 from the
  data files. **Treat every statement in it as a claim to verify, not a fact.**
- `docs/PAPER_DRAFT_v0.md` — the reviewed draft (v0.2; content-identical to the docx
  round 2 saw).
- **Concessions:** the authors concede errata E1–E9 (audit §5) in full — including
  dropping "ramped adoption" and "pre-LLM model surprise", and rewording the QC gate as
  audit-derived. Do not spend effort re-arguing conceded points; DO judge whether the
  errata list is complete and whether the replacement language is adequate.
- **Numbers policy:** every number you assert must be recomputed from the package files,
  or explicitly labeled NOT RECOMPUTABLE with the missing input named.
- **Data notes:** raw/extracted document text is not included (2.4 GB; licensing), so
  concordance-level checks are out of scope this round. `data/features/*.csv` hold
  per-document features (2,753 docs); `ppl.csv` has 5,506 doc×model NLL rows;
  `data/features/ar_fy_features.csv` is the assembled 71-unit series with `doc_ids`;
  `data/meta/download_failures.csv` logs all attempts across resumable passes (4,276
  rows) — the residue is the 65 sampled ids in `frozen_sampling_v1.csv` absent from
  `classic.csv`; `config/config.yaml` holds the QC thresholds and marker lexicons.

## Role 1 — Adversarial data auditor (primary role)

1. Complete the formal **A1–A3 / O3–O10 audit** against the files, replacing round 2's
   NOT AUDITABLE column with grounded verdicts. Note O9's absence and judge the proposed
   fix (restore-or-renumber + archive the round-1 review).
2. Independently recompute each claim in audit §§3–4 and output
   **VERIFIED / REFUTED / NOT RECOMPUTABLE** per claim, at minimum:
   (a) 72 calendar cuts collapse to **65 unique pre/post partitions**; 2023 ranks 2nd
   after deduplication; missing FYs = 1971, 1981, 1990, 2000, 2002, 2007, 2010;
   (b) the LOYO split — pre-year-drop band **0.0680–0.0746** vs n_post=1 extremes
   0.0412 / 0.0986;
   (c) pooled post-2022 family shares underscore **43.5%** / pivotal **14.7%**,
   HHI **0.240**, absolute hits AR **20** / ICR **417** / PAD **338**;
   (d) all three post-cut assembled AR units (FY2022–24) are `server_txt`
   (cross-reference `ar_fy_features.doc_ids` ↔ `extraction_log.csv` ↔ `ar_unit_qc.csv`);
   (e) FY2007 (46,723 tokens) **passes** a token-count-only gate;
   (f) the draft's "27/71" vs `T3_power.csv`'s **26**/71;
   (g) the era means (39.96 → 26.10 / 27.99; Tier-2 0.25 → 9.09) and the **56.0%**
   2020s Annual-Report plain-text share.
3. Adjudicate four contested calls, one clear ruling each:
   - **C1.** Is reporting the pre-year LOYO band as the influence result, with the two
     n_post=1 rows flagged separately, legitimate — or selective presentation?
   - **C2.** Does (d) neutralize the extraction-method objection for the assembled-AR
     headline (+0.070)? State exactly what remains for the doc-level ICR/PAD panels
     (2020s plain-text shares 83.5% / 76.7%).
   - **C3.** Given deduplication and the fact that the maximal ICR and PAD cuts sit at
     the last admissible candidate (2025, n_post=2), is the conceded E3 replacement
     sentence evidence-proportionate — or still too strong or too weak?
   - **C4.** Is the QC-gate defense (audit-derived wording + observed separation
     ≥20.1% vs ≤0.94% + planned threshold grid + independent-indicator variant)
     sufficient, given the outcome-adjacent stopword criterion ("and" is both in the
     gate share and a reported outcome)?

## Role 2 — Preregistration referee

Attack `docs/PREREG_DRAFT_v0.1.md` as the design that will be **frozen before any IMF
document is downloaded**. Cover at minimum: the single-primary choice (ICR vs Article IV)
and its stated justification; the validity of Article IV as the operational analog and
what the genre mismatch does to identification; model M1 (Poisson QML, institution×year
clustering, wild cluster bootstrap, NB2 sensitivity); the pretrend gate and the
three-condition decision rule; the frozen family-collapsed confirmatory lexicon
(13 families) as the answer to the concentration objection; the 4-member secondary FDR
family; composition standardization; the disconfirming-outcomes list; and anything a
hostile reviewer would call post-hoc if left as-is. Output the exact changes required
before freezing. A prereg that survives you should survive a journal.

## Role 3 — Editor (path to submission)

Given the audit, the concessions, the prereg, `docs/DESIGN_RATIONALE.md` (D1–D12) and the
plan in audit §6 (P0–P5): (a) update your round-2 blocking table — for each item:
resolved / still blocking / newly discovered; (b) is P0–P5 complete and correctly ordered
for a March 2027 GIQ submission — name anything blocking that the plan misses; (c) is
E1–E9 complete for v0.3, and is any conceded replacement wording inadequate?

## Output format

Three headed sections — **Data audit / Prereg / Editor** — each ending with a ranked
action list, blocking items first. English. Recompute, don't trust. No praise; review.
No new literature suggestions this round unless a methods citation is strictly required;
if so: authors, year, venue, DOI, confidence label — fabricated citations discredit the
entire review.
