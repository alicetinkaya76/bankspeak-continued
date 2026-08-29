# Round-2 audit completion — v1.1 (corrected, 2026-08-09)

Supersedes v1.0 as the audit record. v1.0 remains archived unmodified (append-only
discipline); every change below was triggered by the round-3 external review and has been
independently re-verified against the package CSVs before acceptance.

## 0. Version log (v1.0 → v1.1) — round-3 refutations accepted

| # | v1.0 claim | v1.1 correction | Verification |
|---|---|---|---|
| 1 | Family HHI 0.240, effective ≈ 4.2, seamless 10.8% | **HHI 0.244507, effective 4.09, seamless 101/775 = 13.03%.** v1.0's ad-hoc stem list orphaned `seamlessly` (17 hits) and `intricacies` (2 hits) outside their families; the explicit 28-form→13-family mapping fixes it. Underscore 43.48% and pivotal 14.71% unaffected. | Recomputed with the full mapping; matches round 3 exactly. |
| 2 | ICR/PAD 2020s plain-text shares 83.5% / 76.7% | **Withdrawn — contaminated denominators.** `extraction_log.csv` holds 3,145 ids; 392 are pilot-only (all ICR/PAD), outside `frozen_sampling_v1.csv`. On the analyzed sample: **ICR 2020s 258/280 = 92.14%** (1990s: 92.65% — no monotone decline); **PAD 2020s 239/267 = 89.51%** (lowest analyzed decade is the 2010s: 83.77%). The draft's own figures (89.5% overall = 2,464/2,753; AR 2020s 56.0% = 14/25) were computed on the analyzed sample and stand. | Recomputed after filtering the log to `classic.csv` ids; matches round 3. |
| 3 | "9 of 10 preceding units are server_txt" | **8 of 10** (FY2012–21): FY2013 and FY2021 are mixed (2× server_txt + 1× pymupdf each). v1.0 never inspected FY2012–14. Also: FY2022 is the **adjacent pre-cut** year, not post-cut; the correct statement is that the top-ranked cut years' units (FY2022–24) are all exclusively server_txt. | Recomputed from `ar_fy_features.doc_ids` × `extraction_log`; matches round 3. |
| 4 | "Post-2022 hits: AR 20 … assembled post base 72,823 tokens" | **Denominators must not be paired.** The 20 hits belong to the unassembled doc-level AR facet (siblings/duplicates included, through 2025). The assembled FY2023–24 series contains **≈10 hits** (FY2023 ≈ 7.0, FY2024 ≈ 3.0) over 72,823 tokens; FY2022 ≈ 6.0 is pre-cut. | Recomputed from `tier1_per1k × tokens`; matches round 3. |
| 5 | Residue split "61×403 + 1×404" | **Withdrawn.** Two residue ids (34063779, 34454721) carry both 403 and 404 across passes, and `date` is day-granular, so a "last attempt" split is order-dependent. Correct reporting (as the draft already had it): **62 HTTP-4xx-class + 3 no-URL**, unless a deterministic per-id adjudication rule is declared. | Recomputed per-id code sets; matches round 3. |
| 6 | — (not caught in v1.0) | **New defect (round 3): zero-token NLL contamination.** Six zero-token docs; Pythia NLL missing for all six; GPT-2 assigns the constant **5.8744** to five of them (ids 2017573/AR-2002, 733403 & 733630/ICR-1996, 728021/ICR-1998, 1695624/PAD-2002; 33464456/AR-2021 is NaN for both). The 2019–22 vs 2023–26 robust table is unaffected (all five constants pre-2019), but historical NLL panels must be regenerated under a frozen eligibility rule. | Verified from `ppl.csv` × `classic.csv`. |

Also accepted from round 3: the E3 replacement sentence is superseded by the C3 wording
(see §5); §6's plan is superseded by the round-3 reordered path; O9 handling revised
(archive the round-1 review verbatim, preserve numbering, add a crosswalk row — never
renumber history); `MANIFEST.sha256` to be reissued in standard `sha256sum -c` two-column
format alongside the metadata table.

## 1. Round-2 "NOT AUDITABLE" — package failure (unchanged from v1.0)

Round 2 received only the docx; the prompt's promised memo/tables/robustness never
arrived. Round-3's Step-0 integrity gate confirmed the corrected packaging works: all 28
manifest entries matched byte-for-byte and hash-for-hash. Two round-2-prompt defects
stand: the reference count was misstated (actual: 25 = 23 DOI + 2 proceedings), and O9
does not exist in `RESPONSE_TO_REVIEW.md`.

## 2. Completed A/O crosswalk (v1.1 verdicts, incorporating round 3)

| Label | Verdict | Ground truth |
|---|---|---|
| A1 | **PARTIALLY RESOLVED** | QC values reproduce (FY2002: 12 tokens, share 0.0000; FY2007: 46,723, 0.0094; retained: ≥17,023, ≥0.2008). "Prespecified" wording still in the draft (E1 pending); grid/manual/independent-indicator validation absent; stopword computation not end-to-end recomputable without the exact list. |
| A2 | **RESOLVED AS SPECIFICATION, NOT AS STRONG INFERENCE** | Level-only b2 = 0.0699, HAC(2) p ≈ 9.1e-8, n_post = 2, placebo 0.00. Pre-year LOYO band 0.0680–0.0746; post-year deletions are one-observation boundary fits (0.0412 / 0.0986). AR stays descriptive endpoint evidence. |
| A3 | **MOSTLY RESOLVED** | Spans mostly correct; Table 2 era label and the one-sentence span statement pending (E7). |
| O3 | **PARTIALLY ADDRESSED; BLOCKING** | 72 calendar cuts = 65 unique partitions (missing FYs 1971/1981/1990/2000/2002/2007/2010); 2023 rank 2 after dedup (2022 first, b2 = 0.0760, n_post = 3). ICR/PAD maxima at the last admissible cut (2025, n_post = 2); doc-level AR max 2024, n_post = 2. Raw ranks are endpoint-sensitive; calibrated unknown-break inference pending. |
| O4 | **NOT ADDRESSED; PREREG REDESIGN REQUIRED** | v0.1 prereg rejected by round 3 (institution⊥genre confound, outcome-informed panel choice, wrong intervention-unit inference); redesigned in PREREG_DRAFT_v0.2. |
| O5 | **PARTIALLY ADDRESSED; BLOCKING** | Shares and leave-two-family ratios reproduce (ICR 2.2238×, PAD 3.8479×, AR doc-level 2.1411×); corrected concentration: HHI 0.2445, effective 4.09; assembled post mass ≈10 hits. Concordance, domain-transfer validation, and a defined family outcome pending. |
| O6 | **PARTIALLY ADDRESSED; NEW DATA DEFECT** | Robust medians reproduce (Pythia ICR 2.4004→2.5331; PAD 2.4503→2.5994). Zero-token NLL bug (version-log #6) requires regeneration; `revision: main` is not an immutable pin; assembled-unit NLL absent; terminology fix (E2) pending. |
| O7 | **NOT ADDRESSED** | No executed adjustment; no common cross-institution ontology yet (Stage-B task in PREREG v0.2). |
| O8 | **NOT RESOLVED** | v0.1's four-member secondary family rejected (AR n_post=2 cannot be confirmatory; NLL unvalidated). v0.2 abolishes the secondary family: two co-primary panels under Holm, everything else descriptive/exploratory with enumerated blocks. |
| O9 | **UNDEFINED** | Round-1 review must be archived verbatim with original numbering + a crosswalk row stating whether O9 was omitted by the authors or never assigned. No renumbering. |
| O10 | **PARTIALLY ADDRESSED; LOG-PROVENANCE DEFECT** | Residue 65 = 62 4xx-class + 3 no-URL (finer split withdrawn, version-log #5). `extraction_log.csv` needs `sampling_version` / `analysis_eligible` columns; every method percentage must use analyzed-sample denominators. Missingness-by-year×format model pending. |

## 3. Verified-numbers register (v1.1)

Verified and standing: corpus totals (2,818 / 2,753 / 97.69% / 65 / 99.78% / 70,246,055
tokens); ITS Table 3 (+0.0699 / +0.0556 / +0.0266; placebos 0.00 / 1.00 / 0.50 — all 45
ITS rows independently reproduced by round 3); breakpoint ranks (2/72→2/65, 3/27, 4/25,
27/74); leave-two-family ratios; robust-aggregation medians; QC values; era means
(39.9627 → 26.0983 / 27.9870; Tier-2 0.2523 → 9.0945, unrounded ratio 36.05×); analyzed
plain-text shares (overall 89.50%; AR 2020s 56.0%); power counts 26/71 and 22/144.

Corrected in v1.1 (see §0): family HHI/shares, ICR/PAD method shares, preceding-unit
method count, AR hit denominators, residue split, zero-token NLL.

Draft-side errata confirmed: "27/71" → 26/71 (E5); the draft's own extraction and
residue statements were computed correctly and are NOT affected by v1.0's audit errors.

## 4. Contested calls — round-3 rulings (adopted)

- **C1 (LOYO):** legitimate under strict labeling — report 0.0680–0.0746 as the
  *pre-period deletion influence band*, keep the full table, and report FY2023/FY2024
  deletions separately as one-post-observation boundary sensitivities.
- **C2 (extraction):** assembled-AR method-switch objection *substantially weakened, not
  neutralized* (server-text template/content changes and earlier mixed-method influence
  remain); operational panels get analysis-sample denominators, a method covariate,
  method interactions, and text-only sensitivity; the v1.0 83.5%/76.7% argument is
  withdrawn.
- **C3 (claim language):** adopted verbatim for v0.3: *"Several prespecified series rise
  in the final years, but the breakpoint scans are descriptive and endpoint-sensitive;
  they do not identify a unique break date, trajectory shape, or mechanism."*
  "Post-2022 increase" stays as a descriptive period label only.
- **C4 (QC gate):** conditionally defensible after the promised validation; until the
  grid, token-only re-estimation, independent indicator, blinded adjudication, exact
  stopword hash, and unchanged IMF transfer exist, it is a plan, not evidence. The
  "and" outcome additionally requires an independent-QC-rule sensitivity.

## 5. Errata register for v0.3 (E1–E17)

E1 audit-derived-gate wording; E2 reference-model NLL + immutable revisions + corpus
cutoffs; **E3 (revised)** = the C3 sentence above; E4 "30–35%" split; E5 26/71;
E6 stopword-share rename + list hash + independent-QC "and" sensitivity; E7 span
sentence + 1947–1965 era label; E8 round-1 review archived verbatim + O9 crosswalk row;
E9 bibliography actions (Moretti/Pestre split, López Bernal corrigendum, eight verified
additions through the Crossref pipeline).

New (round 3, all verified here): **E10** explicit 28→13 family mapping; seamless
13.03%, HHI 0.244507, effective 4.09. **E11** extraction-log provenance columns; all
method percentages from analyzed ids; ICR/PAD 2020s = 92.1% / 89.5%. **E12** 8-of-10
preceding units; FY2022 = adjacent pre-cut. **E13** doc-level AR 20 hits vs assembled
FY2023–24 ≈ 10 hits, denominator stated at every mention. **E14** frozen document
eligibility; regenerate NLL; purge the 5.8744 empty-document constants. **E15** residue
reported as 62 4xx-class + 3 no-URL. **E16** describe the release as
artifact-recomputable until source scripts, stopword/tokenizer definitions, immutable
model hashes, and a standard `SHA256SUMS` ship. **E17** prereg declared prospective only
on the comparator side, outcome-informed on the WB side.

## 6. Plan — superseded by the round-3 reordered path (adopted)

1. **Artifact repair and audit trail** (this file; E10–E16 fixes in code/tables; round-1
   review archive + O9 crosswalk; standard checksums; src/ + environment + stopword hash
   in the next package).
2. **Stage-A acquisition preregistration** — freeze IMF source/frame/query/dedup rules,
   eligibility rules, family mapping, model revision hashes; external timestamp (OSF
   registration recommended) BEFORE any IMF metadata access.
3. **Stage-B metadata-only feasibility** — text and outcomes sealed; genre crosswalk
   (including the WB country-surveillance candidates), common covariates, coverage,
   overlap, interaction MDE; then freeze the final SAP with a second external timestamp.
4. **Locked robustness + comparator harvest** — the WB sensitivity battery (QC grid,
   dedup/sup-Wald scans, method interactions, family diagnostics) runs under the frozen
   SAP; IMF harvested with rules unchanged; any rule change demotes the affected result.
5. **One-shot confirmatory analysis** — immutable inputs, full logs,
   machine-recomputable outputs; independent recomputation invited.
6. **Manuscript completion** — governance theory, Related Work, Discussion,
   adoption-source section with explicit scope limits, captions, bibliography.
7. **Final external audit → submission decision** (successor to round 3). Prespecified
   fallback if the Stage-B crosswalk fails: an RQ1/measurement-discipline paper with RQ2
   explicitly exploratory — decided early enough to protect the March 2027 target.
