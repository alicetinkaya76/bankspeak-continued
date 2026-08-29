# PREREG — Comparator round (DRAFT v0.2, 2026-08-09)

**Status: revised after the round-3 external critique; NOT frozen.** v0.1 is withdrawn.
Freeze is two-stage (Section 11): Stage-A (acquisition protocol) is externally
timestamped BEFORE any IMF metadata access; Stage-B ends with the final Statistical
Analysis Plan (SAP), externally timestamped BEFORE any IMF or new-WB text is downloaded
or feature-processed. Post-freeze deviations are logged in `DESIGN_RATIONALE.md` and
demote the affected result to exploratory.

## 0. Epistemic status (E17 — stated, not hidden)

This design is **prospective only with respect to comparator data**. It is
**outcome-informed on the World Bank side**: the 2023 cut, the Tier-1 lexicon, and the
panel structure were chosen after WB outcomes were observed. The study is therefore a
*prospective external-comparator validation of an already observed WB pattern*, not a
confirmatory discovery design. Confirmatory interpretation is restricted to comparator
replication; "LLM-associated construct validity" remains exploratory throughout.

## 1. Claims, separated (mechanism-neutral)

- **H-DIFF (the only confirmatory claim).** A differential post-2022 change between the
  prespecified WB and IMF series in the frozen lexical outcome; **mechanism unresolved.**
  A positive institution×post interaction is never described as evidence of
  enterprise-LLM adoption; it is equally compatible with WB-specific leadership,
  template, style-guide, or thematic change.
- **H-SHARED (prespecified descriptive companion; not a test).** The IMF's own pre/post
  change, reported with a CI. A similar IMF rise nulls H-DIFF while remaining
  informative about a shared post-2022 shift; the two claims are reported separately and
  never conflated.
- Fixed success-language template: *"a differential post-2022 change between the
  prespecified WB and IMF series in the frozen lexical outcome; mechanism unresolved."*

## 2. Panels and comparator status

- **Co-primary operational panels (outcome-blind selection restored):**
  P1 = WB ICR vs IMF Article IV staff reports; P2 = WB PAD vs IMF Article IV.
  **Holm correction over the two co-primary tests (α = 0.05).** v0.1's single-primary
  rationale (largest observed post-2022 hit mass) is withdrawn as outcome-based
  selection; no neutral criterion uniquely favors either panel (ICR has more post hits,
  PAD more post tokens), so both are carried.
- **Comparator label.** Article IV is a **non-equivalent falsification comparator**:
  institution and genre are perfectly confounded (project reports vs country
  surveillance). The word "harmonized" is withdrawn. Interpretation is capped
  accordingly: the interaction is comparative descriptive evidence about differential
  change, not an institution-specific mechanism result.
- **Stage-B genre-crosswalk decision (metadata only, outcomes sealed).** Probe whether a
  WB country-surveillance genre with adequate coverage exists in the D&R API —
  candidate facets to test: *Country Economic Memorandum*, *Systematic Country
  Diagnostic*, *Country Partnership Framework*. Feasibility criteria, fixed now: an
  exact `docty` facet exists; ≥15 pre-2023 years with ≥20 English documents/year; span
  reaching 2026. **If PASS:** P0 = WB country-surveillance vs IMF Article IV becomes the
  single primary (genre-matched); P1/P2 are demoted to falsification comparisons and the
  Holm family becomes {P0}. **If FAIL:** P1/P2 stand as co-primaries under the
  non-equivalent-comparator interpretation cap. This decision uses metadata only and is
  made before any text of the new strata is downloaded.
- **P-A (Annual Reports): descriptive only.** Removed from all confirmatory testing
  (n_post = 2 on the WB side). Reported with n_post disclosed.
- **NLL: exploratory only**, pending E14 regeneration under the eligibility rule
  (Section 7) and construct validation. **There is no secondary confirmatory family in
  v0.2.**

## 3. Outcome definition (E10 — exact)

- **Confirmatory outcome:** the family-occurrence count. For document d,
  `count_d` = number of token occurrences matching any of the 28 case-folded forms
  (lowercased text; ASCII word-boundary matching `\b...\b`; no lemmatizer; repeated
  occurrences counted), aggregated under the fixed 28-form→13-family mapping of
  Appendix A. Stated honestly: family collapse changes labeling and diagnostics, not the
  total (Σ family counts ≡ Σ form counts); concentration is addressed by the numeric
  guard below and by validation diagnostics, not by relabeling.
- **Concentration guard (numeric, prespecified):** the H-DIFF interaction must retain
  its sign with a 95% CI excluding 0 after removing the single largest-contributing
  family (identified from pooled WB+IMF post-period counts at analysis time). Failure ⇒
  the confirmatory claim fails and the result is reported as family-concentrated.
- **Breadth outcome (exploratory):** distinct families present per document (0–13),
  binomial-logit with log tokens as covariate.

## 4. Primary model and inference (time-level; v0.1's cluster logic withdrawn)

- **Analysis unit:** institution×year cells (counts and eligible tokens summed over
  documents). Documents are not intervention units; treatment varies at
  institution×time with only four WB post-year cells.
- **Model M2 (cell level):**

      Count_it ~ institution + C(year) + institution:c_year + institution:post
                 + offset(log Tokens_it)

  Poisson QML; `c_year` centered at 2011 (midpoint of 1996–2026); `post = year ≥ 2023`
  (prespecified; no scan feeds the confirmatory cut). `C(year)` absorbs common year
  shocks; **the differential pretrend `institution:c_year` is in the model** — there is
  no pretest-then-pool. NB2 re-estimation is the overdispersion sensitivity.
  Prespecified display: an event-study variant with institution × 3-year-bin
  coefficients.
- **Primary inference:** moving-block bootstrap over **paired years** (WB and IMF cells
  of the same year resampled jointly, preserving contemporaneous cross-institution
  dependence): block length 3, 9,999 replications, seed 20260806, null imposed by
  recentering the interaction, two-sided. Secondary: HAC(3) on the annual paired
  log-rate-difference series. Exact library versions pinned at Stage-A. Document-level
  QML with institution×year clustering is demoted to a reported sensitivity.

## 5. Decision rule (all numeric; all four required)

1. Holm-adjusted block-bootstrap p < 0.05 for `institution:post` in the primary
   panel(s).
2. Sign unchanged and 95% CI excluding 0 under BOTH NB2 and the composition-standardized
   variant (Section 6), with the point estimate changing by **< 50%** in absolute
   magnitude relative to M2. NB2 non-convergence ⇒ jackknife-over-years CI on QML; if
   that also fails, condition 2 fails (fixed in advance).
3. Concentration guard of Section 3 passes.
4. Leave-one-post-year-out on the interaction: sign unchanged and Holm p < 0.10 in every
   deletion (the numeric replacement for "not driven by 2023 alone").

Failure of any condition ⇒ no confirmatory claim; results are reported descriptively
with the failed condition named.

## 6. Composition standardization (operationalized)

- **Common ontology (fixed at Stage-B from metadata only):** country (ISO3), region
  (WB grouping applied to both institutions), income group (WB fiscal-year
  classification, year-matched), calendar year. Sector and instrument are WB-only
  fields: they are **excluded from the cross-institution model by design** (used only in
  WB-internal within-stratum analyses) and this exclusion is stated, not silently
  dropped.
- **Target distribution:** the pooled pre-2023 country-region-income×year composition of
  both institutions.
- **Estimator:** direct standardization by cell reweighting. Positivity: cells with zero
  support in either institution are excluded and their token share reported. Weight
  truncation at the 99th percentile. Minimum effective sample size: 50% of the nominal
  cell count.
- **Hard failure rule:** if common-support coverage is < 80% of post-period tokens in
  either institution, the standardized variant is infeasible ⇒ decision-rule condition 2
  fails ⇒ the confirmatory claim fails (reported descriptively). Fields are never
  silently dropped to rescue the analysis.

## 7. Document eligibility (frozen; applies to ALL analyses, including regeneration of
the existing WB panels)

- Lexical counts: tokens ≥ 1 (zero-token documents excluded everywhere; the six current
  WB zero-token records are excluded and logged).
- NLL: tokens ≥ 100; a missing model output excludes the document from that model's
  panel and is counted in the intention-to-sample table; **no constant or imputed NLL
  values** — the five GPT-2 5.8744 empty-document constants are purged on regeneration
  (E14).
- Duplicates/versions: existing repnb/volnb rules, applied identically to IMF.
- Assembled annual units: the QC gate (≥5,000 tokens AND ≥0.15 stopword share)
  transfers to IMF unchanged; the exact stopword list is content-hashed and released at
  Stage-A.
- Intention-to-sample reporting: sampled → downloaded → nonzero → eligible, per
  institution×genre×year.

## 8. Power / MDE for the interaction (completed before the SAP freeze)

Simulation-based: synthetic institution×year panels generated from WB pre-2023 observed
family rates and dispersion, IMF at parity, analyzed with M2 + the block bootstrap;
report the minimum detectable interaction at 80% power given four post years. Gates:
≥25 usable pre-2023 cells per institution per panel and ≥3 post cells; failure demotes
the panel to descriptive. The pretrend credibility bound δ (Section 9) is derived from
this simulation as the differential drift that would generate ≥50% of the MDE over the
post window. Simulation seed 20260806; code released at Stage-A.

## 9. Interpretation matrix (fixed in advance)

- IMF post/pre rate ratio ≥ WB's ⇒ H-DIFF null; reported as compatible with a shared
  post-2022 shift (H-SHARED) — explicitly NOT generic evidence against an LLM-era
  reading.
- Condition-2 failure under standardization ⇒ composition explanation favored.
- Text-only subsample interaction losing sign or CI covering 0 ⇒ extraction explanation
  flagged.
- |`institution:c_year`| exceeding δ ⇒ counterfactual credibility fails ⇒ descriptive
  reporting only.
- Condition-4 failure ⇒ single-year dependence. Concentration-guard failure ⇒ family
  concentration.

## 10. Exploratory blocks (enumerated; BH q = 0.05 within each block; two-sided)

- **X1:** 7 classic features × 2 operational panels = 14 interaction tests.
- **X2:** Tier-2 rate × 2 panels = 2 tests.
- **X3:** reference-model NLL, 2 models × 2 panels = 4 tests (only after E14
  regeneration).
- **X4:** breadth outcome × 2 panels = 2 tests.
- Descriptive diagnostics — HHI, prevalence, event-study plots, deduplicated breakpoint
  scans, sup-Wald, step-vs-ramp comparisons — are **not** hypothesis tests and carry no
  error rate.

## 11. Freeze protocol (two-stage, externally timestamped)

- **Stage-A (now):** freeze the acquisition protocol — IMF sources (IMF
  eLibrary/Archives; Article IV series and IMF Annual Reports), query/frame and
  deduplication rules, per-year caps (40), sampling seed 20260806, WB candidate-genre
  probe list, document-eligibility rules (Section 7), the Appendix-A mapping, immutable
  model revision hashes (replacing `revision: main`), and the stopword-list hash.
  External timestamp: OSF registration of the frozen PDF (fallback: Zenodo deposit or an
  OpenTimestamps proof of the git commit). Only after this: IMF **metadata** access.
- **Stage-B (metadata only; text and lexical/NLL outcomes sealed for IMF and any new WB
  genre):** facet probes, coverage tables, the genre-crosswalk decision (Section 2),
  the common ontology and overlap/positivity diagnostics (Section 6), the MDE simulation
  and δ (Section 8). Then the **final SAP** — this document with every Stage-B constant
  filled — is frozen and externally timestamped. Only after that: text download and
  feature processing.

## 12. Out of scope

Mechanism and authorship attribution (D2); WB press releases (D8); UNGDC (hard
firewall); AR confirmatory claims; NLL confirmatory claims.

## Appendix A — 28-form → 13-family mapping (frozen verbatim at Stage-A)

    delve        <- delve, delves, delved, delving
    underscore   <- underscore, underscores, underscored, underscoring
    showcase     <- showcase, showcases, showcased, showcasing
    pivotal      <- pivotal
    intricate    <- intricate, intricacies
    meticulous   <- meticulous, meticulously
    boast        <- boast, boasts, boasted
    commendable  <- commendable
    realm        <- realm, realms
    testament    <- testament
    tapestry     <- tapestry
    seamless     <- seamless, seamlessly
    multifaceted <- multifaceted

Matching rule (aligned to the disclosed implementation, `src/textstats.py`): text is
lowercased and tokenized with `[A-Za-z']+`; a hit is exact token membership in the form
set; repeated occurrences counted; no lemmatization; no additions or removals after
Stage-A. The QC stopword share uses the same tokenizer with the 15-word frozen list in
`src/s10_assemble_ar.py` (content-hashed at Stage-A). The Stage-A commit hash and this table are pasted into the
frozen PDF and never edited afterward.
