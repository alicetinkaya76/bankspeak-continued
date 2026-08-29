# Round-4 third-eye review

**Package reviewed:** `round4_package_20260809.zip`  
**Primary question:** whether `docs/PREREG_DRAFT_v0.2.md` may be frozen as the Stage-A protocol.  
**Overall disposition:** package integrity passes; the corrected audit is numerically sound with several stale/status-level defects; the preregistration is substantially redesigned but is **not freeze-ready**. The remaining problems are not cosmetic. The Stage-A acquisition frame is still a placeholder, the conditional-primary branch is not deterministic, the written model formula is rank-deficient if implemented literally, and the bootstrap/decision rules do not yet determine a unique analysis.

# Corrections

## 1. Package integrity and executable scope

**PASS on the stated Step-0 gate.** The archive contains every listed file. All 54 entries in `SHA256SUMS` pass `sha256sum -c`; byte sizes in `MANIFEST.tsv` agree; the separately uploaded `THIRD_EYE_REVIEW_PROMPT_v4.md` is byte-identical to the copy inside the ZIP. No listed file is missing or unreadable.

The supplied tests run successfully: **9 passed**. This was under the available Python 3.13.5 / pandas 2.2.3 / statsmodels 0.14.6 environment, not the declared Python 3.11.9 / pinned requirements environment, so exact environment reproduction is **NOT RECOMPUTABLE here**.

The disclosed feature-level code is partly executable from the package:

- `s08_its_analysis.py` regenerated all 27 document-level fits exactly to the supplied rounding.
- `s07_power_analysis.py` regenerated the 144 document-level cells and the reported 22/144 and 26/71 below-gate counts.
- `s11_paper_artifacts.py` does **not** run from the supplied package because `data/meta/manifest.tsv` is absent. That file is small metadata, not raw text, and `s11` requires it at `t1_corpus()`.
- `s12_robustness.py` cannot regenerate the lexical decomposition without `data/text/`; that limitation is declared. It also cannot be treated as a fully implemented version of the new preregistered robustness plan for reasons below.

Accordingly, the package now supports stronger definition-level review than round 3, but the claim “rerun `s11` to regenerate every paper-facing artifact from the released package” is false as packaged.

## 2. Verification of `ROUND2_AUDIT_COMPLETION_v1.1.md`

### 2.1 Six round-3 numerical corrections

| v1.1 correction | Ruling | Independent result |
|---|---|---|
| HHI / effective family count / seamless share | **VERIFIED, with one explanatory-clause error** | Full 28-form→13-family mapping gives 775 post-period hits, seamless 101/775 = 13.0323%, HHI = 0.24450697, effective count = 4.08986. Underscore = 337/775 = 43.4839%; pivotal = 114/775 = 14.7097%. |
| ICR/PAD 2020s server-text shares | **VERIFIED** | Filtering to analyzed IDs gives ICR 258/280 = 92.1429%; PAD 239/267 = 89.5131%. The extraction log contains 392 out-of-sample IDs, all in ICR/PAD and all from 2019–2024. |
| “9 of 10 preceding units” → 8 of 10 | **VERIFIED** | FY2013 and FY2021 are mixed; the other eight FY2012–21 units are exclusively `server_txt`. FY2022–24 are exclusively `server_txt`, with FY2022 correctly labeled adjacent pre-cut. |
| AR hit denominators | **VERIFIED** | Doc-level post AR has 20 hits. The assembled FY2023–24 series has approximately 10 hits over 72,823 tokens. They cannot share a denominator. |
| Residue split | **VERIFIED** | The 65-record residue is 62 URL-bearing 4xx-class records + 3 no-URL records. Sixty IDs have only 403 logs; two have both 403 and 404. The last logged row for all 62 is 403, so a unique 61/1 split is not defensible without a rule. |
| Zero-token NLL defect | **VERIFIED** | Six zero-`TOKEN_RE` documents exist. Pythia is missing for all six; GPT-2 has 5.8744 for five and missing for one. All five constants are pre-2019, so the supplied 2019–26 robust table is unaffected, while the historical panel remains contaminated. |

**Required correction to v1.1 §0 row 1.** The sentence saying that v1.0 orphaned both `seamlessly` and `intricacies` does not reproduce the exact v1.0 HHI stated by round 3. HHI 0.239751925 is obtained when `seamlessly` alone is split from the `seamless` family; splitting both `seamlessly` and `intricacies` gives 0.239691988. Remove the `intricacies` clause unless the authors can supply the exact old computation showing a different denominator rule. The corrected v1.1 HHI itself is right.

### 2.2 Surviving stale or internally inconsistent statements

No material v1.0 numerical error survives the verified-numbers register or E10–E15. The following status statements do survive and should be edited:

1. **A1 is stale.** v1.1 says the exact stopword list is absent. It is now disclosed in `src/s10_assemble_ar.py`; its sorted, newline-joined SHA-256 is `3b5d2b51754f73011aeb20ce28bcfcdeb2908ea9380d3d49decf6ee2bb22c41a`. End-to-end recomputation still fails because text is absent, not because the list is unknown.
2. **O4, O5, and O8 status labels are stale.** Their prose acknowledges v0.2’s redesign, defined occurrence outcome, co-primary Holm family, and removal of the secondary family, while their verdict cells still say “NOT ADDRESSED/NOT RESOLVED” or “defined family outcome pending.” These should be changed to specification-level rulings, with execution/freeze still pending.
3. **E16 is stale.** Source scripts, tokenizer definitions, requirements, `.python-version`, and a standard `SHA256SUMS` now ship. E16 should identify what remains: raw/extracted text or a controlled access/rebuild route, `data/meta/manifest.tsv`, immutable model revisions, implemented comparator/bootstrap/MDE code, and release-level regeneration tests.
4. **§6 plan is stale.** It still schedules standard checksums, source, environment, and stopword disclosure for “the next package,” although this package contains them. Mark those items complete and retain only the unmet pieces.
5. **The round-3 blocking table contains 15 rows, not 14.** The round-4 prompt miscounts it. All 15 are adjudicated below; none is silently dropped.

No round-3 numerical correction was wholly omitted. E3 language, O9 historical handling, the reordered path, 26/71, 8/10, corrected denominators, HHI, residue, and zero-token NLL are all registered.

## 3. Definition-level code review

### 3.1 Stopword gate

The implementation is clear and internally consistent:

- text is lowercased;
- tokens are `[A-Za-z']+`;
- the numerator is occurrences in the frozen 15-word set;
- the denominator is all such tokens;
- the unit passes only if tokens ≥5,000 and stopword share ≥0.15.

This matches prereg Appendix A and reproduces FY2002/FY2007 and retained-unit minima. It does **not** match the current paper wording “prespecified function-word share.” The gate was audit-derived, and the measure is a specific stopword share. E1/E6 remain necessary.

### 3.2 Matching rule and outcome implementation

The prereg contains two non-equivalent rules:

- §3 says lowercased ASCII word-boundary matching `\b...\b`;
- Appendix A and `src/textstats.py` use exact membership after `[A-Za-z']+` tokenization.

They differ in real cases. For example, code does not count `pivotal` in `pivotal's`, while `\bpivotal\b` does; code counts `pivotal` in `pivotalé`, while Python Unicode word-boundary matching does not. Replace §3 with the Appendix-A rule.

`rate_from_list` otherwise matches the intended occurrence estimand: repeated exact-token occurrences count, and the total across the 28 forms is invariant to family relabeling. However, the released pipeline stores only a **rounded per-document rate**, not the exact integer occurrence count required by M2. The 13-family mapping is not machine-readable in config or source. Reconstructing counts from `tier1_per1k × tokens` can be non-integer because the rate was rounded to four decimals.

Before any Stage-A freeze, the measurement code should output at least:

- exact `tier1_count`;
- exact `eligible_tokens`;
- one exact count for each of the 13 families;
- a machine-readable one-to-one 28-form mapping, content-hashed and unit-tested.

### 3.3 Seed usage

`seed: 20260806` is actually used in `s01` and in CPU-mode `s06`. The usage is not yet suitable for the conditional Stage-B design:

- `s01` uses one sequential RNG across all sorted strata and years. Adding, removing, or reordering a candidate P0 stratum changes downstream samples even when the underlying P1/P2 frames are unchanged. Stage-A needs a stable per-cell seed derived from master seed + institution + genre + year.
- `s06` analyzes all documents on MPS/CUDA but a random 10-per-cell subset on CPU. NLL results therefore depend on hardware. Exploratory status does not make a hardware-dependent analysis sample acceptable. Freeze one sample rule and apply it on every device.
- The bootstrap and MDE simulation seeds are written in v0.2, but no implementation exists, so their use is **NOT RECOMPUTABLE**.

The config comment saying cells below five documents will be widened is also not implemented: `s01` only prints `LOW`. Remove the promise or implement and freeze the widening algorithm.

### 3.4 `s08` ITS implementation

The centered segmented interaction itself is correct: `t_post = max(year − break_year, 0)` implements the documented slope-change term, and the level-only assembled-AR specification is correctly separate in `s11`.

Three contradictions remain:

1. `s08` still prints that outputs “describe discontinuities,” contrary to the adopted E3 language that the scans do not identify a unique break date or trajectory.
2. Placebo significance is decided from p-values already rounded to four decimals. Threshold decisions must use full-precision p-values and round only for display.
3. `yearly_series()` uses unweighted means of document rates. That is the artifact-level design already reviewed, but it must not be confused with v0.2’s new cell-level exact-count model.

### 3.5 `s12` robustness implementation

The present code contradicts several documented claims:

- breakpoint partitions are **not deduplicated**;
- no sup-Wald/QLR or step-versus-ramp comparison is implemented;
- the docstring promises leave-one-word-out contrasts, but the code outputs only per-word counts/rates/shares;
- the 28→13 mapping and family-level decomposition are absent;
- marker robustness includes zero-token records, and NLL robustness does not enforce tokens ≥100;
- the raw LOYO table does not label pre-period influence separately from one-post-observation boundary fits.

These are declared step-1 repairs, so they do not invalidate the old CSV arithmetic. They do mean the released `s12` cannot yet be cited as implementing v0.2’s locked robustness plan.

## Ranked correction actions

1. Correct v1.1’s `intricacies` explanation and update the stale A1/O4/O5/O8/E16/§6 statuses.
2. Make the Appendix-A tokenizer rule the sole rule everywhere; delete `\b...\b` wording.
3. Move the 28→13 mapping into machine-readable config/source and emit exact total and per-family integer counts.
4. Replace global sequential sampling with stable per-cell seeds; eliminate hardware-dependent NLL sampling.
5. Repair `s08` thresholding/language and implement the promised `s12` eligibility, deduplication, family, and robustness logic.
6. Add `data/meta/manifest.tsv` or revise `s11` so the released package can actually regenerate T1; add a package-level regeneration test.
7. Keep end-to-end lexical/NLL claims explicitly **NOT RECOMPUTABLE** until text access and immutable model revisions are available.

# Prereg freeze

## 1. Round-3 blocking-defect walk

The referenced round-3 table has **15** defect rows. Their v0.2 status is:

| # | Round-3 defect | v0.2 status | Where addressed / remaining defect |
|---:|---|---|---|
| 1 | Primary selected from observed hit mass | **RESOLVED for P1/P2; PARTIAL overall** | §2 withdraws the hit-mass choice and carries ICR/PAD under Holm. The new P0 switch is outcome-blind in principle but not deterministic as written. |
| 2 | ICR–Article IV mislabeled harmonized/controlled | **RESOLVED for P1/P2** | §2 calls it a non-equivalent falsification comparator and caps interpretation. A passing metadata facet is not by itself enough to call P0 genre-matched. |
| 3 | Positive interaction interpreted as enterprise-LLM evidence | **RESOLVED** | §§0–1 and §9 make H-DIFF mechanism-neutral and separate H-SHARED. |
| 4 | Family-collapse response undefined | **PARTIALLY RESOLVED** | §3 defines occurrence count and admits relabeling does not change the total. The §3 matching rule conflicts with Appendix A/code, and exact count/family outputs are not implemented. |
| 5 | WB-informed lexicon treated as pristine confirmatory discovery | **RESOLVED** | §0 states partial prospectivity and restricts construct validity to exploratory interpretation. |
| 6 | Common pretrend imposed after a pretest | **RESOLVED in concept; formula needs repair** | §4 includes a differential trend without pretest. Literal factor-formula implementation is rank-deficient; use a numeric WB indicator and one differential slope. |
| 7 | Wrong intervention-unit inference | **PARTIALLY RESOLVED** | §4 moves to paired institution-year inference. The bootstrap algorithm is not specified sufficiently to be implementable or validated. |
| 8 | Non-rejection mislabeled equivalence | **PARTIALLY RESOLVED** | The pretest is removed, but §9 reintroduces a point-estimate δ gate derived from MDE; it is not an equivalence test and has no uncertainty rule. |
| 9 | Subjective “sign/order-of-magnitude stable” | **PARTIALLY RESOLVED** | §5 supplies numbers, but formulas, p-value families, global success logic, and fallback interpretation remain ambiguous. |
| 10 | Composition standardization absent | **PARTIALLY RESOLVED** | §6 adds an ontology, target, truncation, ESS, support, and failure rule. The estimand/weight formula, missing/multi-country handling, variance, renormalization, and metadata-versus-token timing remain unspecified. |
| 11 | Incoherent secondary confirmatory family | **RESOLVED** | §2 removes AR/NLL from confirmatory testing and abolishes the secondary family. |
| 12 | Exploratory blocks not enumerated | **PARTIALLY RESOLVED** | §10 enumerates X1–X4 for two panels. It does not define the P0 branch, and sup-Wald is incorrectly called a no-error-rate descriptive diagnostic. |
| 13 | Document inclusion absent | **PARTIALLY RESOLVED** | §7 fixes zero/NLL eligibility and intention-to-sample reporting. “Existing repnb/volnb rules applied identically to IMF” is not viable and is not an existing rule for ICR/PAD. |
| 14 | Power gate not matched to H1 | **PARTIALLY RESOLVED** | §8 proposes interaction-specific simulation. The DGP, effect scale, serial dependence, Holm procedure, code, and branch handling are not specified; 15 pre years for P0 conflicts with the ≥25-cell gate. |
| 15 | One-stage freeze too early for feasibility | **RESOLVED structurally, not operationally** | §11 adopts Stage-A/Stage-B external freezes. Stage-A still lacks the actual acquisition frame/query/dedup protocol it claims to freeze. |

## 2. Conditional-primary switch

A prespecified metadata-only primary switch is acceptable **in principle**. It is not acceptable as written because the branch can still be chosen discretionarily.

The present criteria do not specify:

- which candidate wins if two or three facets pass;
- whether candidates may be combined across historical successor labels;
- a title/purpose audit that establishes actual comparability to Article IV;
- common-country/year overlap, post-period support, or MDE as part of the switch;
- what happens if P0 passes the volume screen but later fails the ≥25-pre-cell, ≥3-post-cell, extraction, overlap, or MDE gates;
- whether P1/P2 can be promoted again after P0 fails after text processing.

There is also a direct inconsistency: P0 may pass with 15 pre-2023 years, while §8 requires at least 25 usable pre cells. Under the current wording, P0 can replace P1/P2 and then be demoted, leaving no active primary.

**Required branch rule:** freeze a candidate priority or a fixed composite-series rule; require genre adjudication, ≥25 common usable pre years, ≥3 completed post years, metadata-level support, and the Stage-B MDE gate before P0 replaces P1/P2. Once the branch is chosen at Stage-B, there is no switchback after text or outcome processing. If P0 later fails a locked analysis condition, the confirmatory claim fails; P1/P2 remain falsification analyses.

## 3. Primary model and paired bootstrap

### 3.1 Model formula

The written formula

`institution + C(year) + institution:c_year + institution:post`

is rank-deficient if `institution` is implemented as a two-level factor: it creates institution-specific trend and post columns whose sums are functions already absorbed by `C(year)`. The design matrix has two redundant columns in a standard Patsy expansion.

Define `WB_i` numerically as 1 for WB and 0 for IMF and freeze the estimable form:

`Count_it ~ C(year) + WB_i + WB_i:c_year + WB_i:post + offset(log Tokens_it)`.

Use only common years with one eligible WB and one eligible IMF cell, and define treatment coding, reference institution, coefficient sign, and software formula exactly.

### 3.2 Bootstrap

“Moving-block bootstrap over paired years; null imposed by recentering” is not a complete algorithm. A pairs bootstrap that resamples calendar rows would resample the deterministic break/trend design, can duplicate or omit the four post years, and does not preserve a fixed 2023 intervention. Recentring the estimated coefficient is not, by itself, a null-imposed bootstrap for Poisson QML.

Before freeze, specify at minimum:

- fixed-design residual/score bootstrap versus pairs bootstrap;
- restricted/null model and how null pseudo-data or score draws are formed;
- circular versus ordinary blocks, edge handling, number of blocks, and truncation;
- treatment of gaps and the exact common-year sequence;
- coefficient or studentized statistic;
- finite-sample p-value formula, including the `+1` correction;
- CI construction;
- whether the same procedure is used for NB2, standardization, concentration, and LOPO fits.

A fixed-calendar, null-imposed block bootstrap on paired year-level residual or score vectors is defensible. Resampling the intervention design itself is not.

The HAC(3) log-rate-difference sensitivity also needs a zero-count rule. `log(Count/Tokens)` is undefined when Tier-1 count is zero.

## 4. Decision constants and multiplicity

- **<50% magnitude stability:** acceptable as a transparent robustness threshold only after writing the formula, e.g. `|β_sens−β_M2| / |β_M2| < 0.50`, on the log-rate scale. “Absolute magnitude” is currently ambiguous.
- **LOPO Holm p < 0.10:** the family is undefined. State whether Holm is over four deletions per panel, all deletions across active co-primaries, or co-primary panels within each deletion. State that the p-values come from the same bootstrap. Also state whether one or every active primary must pass.
- **80% common support:** acceptable as a hard failure threshold, but Stage-B is metadata-only and cannot know “post-period token” coverage before text processing. Use a metadata/document support gate at Stage-B and retain token support as a post-harvest locked failure condition; do not use token information to choose the branch.
- **50% ESS:** define `ESS=(Σw)^2/Σw²`, the unit to which weights attach, and the nominal denominator. “Nominal cell count” is not enough.
- **99th-percentile truncation:** define whether the percentile is panel-, institution-, period-, or pooled-specific, then renormalize weights under a stated rule.
- **NLL ≥100 tokens:** defensible for exploratory NLL if “tokens” means the frozen `[A-Za-z']+` count and the code applies it before model scoring/aggregation.
- **Holm over two co-primaries:** valid under dependence and correctly preferable to BH. The branch-specific family must be frozen: `{P0}` after a valid P0 switch, otherwise `{P1,P2}`.

The global success rule is missing. State whether one Holm-significant co-primary passing all robustness conditions permits a panel-specific H-DIFF claim, or whether both P1 and P2 must pass. “Primary panel(s)” does not decide this.

## 5. Concentration guard

Selecting the removed family from pooled WB+IMF post-period counts at analysis time is an outcome-adaptive selection step, and the ensuing ordinary CI ignores that selection. It is also not targeted to the family driving the differential interaction; a common high-frequency family could be selected even when another family drives H-DIFF.

The WB side is already observed, and underscore is already known to be the dominant family (43.48%; underscore+pivotal = 58.19%). The honest rule is to **fix underscore now** as the mandatory concentration guard. A stronger prespecified stress test may also remove underscore+pivotal jointly. Leave-each-family-out results can be reported as an exploratory profile. Do not reselect the mandatory guard from unseen post outcomes.

## 6. Pretrend credibility bound δ

The proposed δ is not a defensible hard gate as written.

- It is derived from the MDE, which is sample-size dependent rather than a substantive bias tolerance. A weaker design produces a larger MDE and therefore a more permissive credibility bound.
- “Differential drift generating 50% of the MDE over the post window” has no exact formula or scale.
- The rule compares a point estimate to δ and ignores uncertainty.
- M2 already estimates the differential linear trend; a large linear trend does not automatically invalidate extrapolation. The threat is unsupported trend form or extrapolation sensitivity.

Either remove δ from the confirmatory decision rule and report the differential-trend estimate/CI plus fixed sensitivity analyses, or replace it with an independently justified equivalence margin and require a prespecified CI to lie within that margin. Do not derive the credibility threshold from the study’s own MDE.

## 7. Outcome choice

Keep occurrence count as the primary outcome. It is a coherent lexical-mass estimand for Poisson QML, and replacing it now with breadth/prevalence would be another WB-outcome-informed primary switch. The prereg’s explicit admission that family relabeling does not change the total is correct.

Breadth and document prevalence should nevertheless be mandatory validation outcomes because occurrence mass can be driven by repeated wording in a small number of documents. The current breadth specification also needs correction: “distinct families present, 0–13, binomial-logit” assumes a binomial structure that is not automatically justified. Define either a quasi-/beta-binomial family-presence model, an ordinal/count model, or 13 family-level presence indicators with an explicit aggregation rule. Document prevalence (`any Tier-1 family present`) is simpler and should be included.

## 8. Stage-A protocol is still missing its acquisition protocol

Section 11 says Stage-A freezes “query/frame and deduplication rules,” but those rules are not in v0.2 or elsewhere in the package. Naming IMF eLibrary/Archives is not an acquisition frame.

Before metadata access, the frozen appendix must state:

- exact source endpoints/collections and query strings or reproducible navigation rules;
- exact Article IV document types included and excluded, including staff reports, press releases, statements, supplements, annexes, corrigenda, and combined files;
- language rule and the date field that assigns year;
- one-document/one-report unit definition;
- country and multi-country assignment;
- version/corrigendum and duplicate resolution before sampling;
- frame construction, cap application, and stable per-cell sampling algorithm;
- URL preference, retrieval fallback, extraction logging, and failure handling;
- metadata fields retained for the Stage-B crosswalk;
- a frozen data cutoff.

“Existing repnb/volnb rules applied identically to IMF” must be deleted. Those are WB Annual-Report assembly fields, not a general ICR/PAD rule and not an IMF identifier scheme.

The cutoff is especially important. On **9 August 2026**, calendar year 2026 is incomplete. The protocol must either specify a future full-year cutoff after 31 December 2026 and a harvest date in January 2027, or use matched year-to-date windows. It may not count the current partial 2026 cell as a completed fourth post year.

## 9. Required changes before another freeze ruling

1. Add the full Stage-A acquisition/frame/query/version/dedup/cutoff appendix and executable stable-per-cell sampler.
2. Make the P0 branch deterministic, align it with the ≥25-pre/≥3-post/MDE/support gates, and prohibit post-outcome switchback.
3. Replace the factor-ambiguous M2 formula with an explicit numeric WB indicator and common-year rule.
4. Specify a valid fixed-design null-imposed paired-year bootstrap in executable pseudocode, including statistic, p-value, CI, gaps, and all sensitivity uses.
5. Define the global co-primary success rule and every Holm family, especially LOPO and the conditional P0 branch.
6. Make the standardization estimand and weighting algorithm exact; separate Stage-B document support from post-harvest token support.
7. Fix underscore now as the concentration guard; add joint underscore+pivotal or full leave-family-out only as prespecified sensitivity/exploration.
8. Remove the MDE-derived point-estimate δ gate or replace it with an independent CI-based equivalence rule.
9. Harmonize the tokenizer language and implement exact integer/family counts in machine-readable code with tests.
10. Specify the MDE simulation scale, DGP, serial dependence, Holm decision, post-year count, and nested-bootstrap implementation; release the promised code before Stage-A if v0.2 continues to say it is released then.
11. Enumerate branch-specific exploratory blocks and stop labeling sup-Wald inference as a no-error-rate descriptive diagnostic.
12. Freeze the treatment of incomplete 2026 data and the date on which the final frame becomes complete.

**REJECT WITH REQUIRED CHANGES.**

# Editor

## 1. Minimal preconditions by stage

### Must be complete before Stage-A freeze

1. The revised preregistration containing the exact acquisition appendix, deterministic P0/P1/P2 branch, completed-year cutoff, estimable M2 formula, bootstrap algorithm, decision families, and machine-readable outcome rule.
2. Immutable model revision hashes replacing `revision: main`, plus the exact stopword and 28→13 mapping hashes.
3. Executable acquisition/sampling code with stable per-cell seeds and a provenance schema containing `sampling_version`, `run_id`, `analysis_eligible`, source/version identifiers, and branch/panel labels.
4. Exact integer/family counter code and tests. The mapping bug must be impossible by construction before it is frozen.
5. The bootstrap/MDE code skeleton promised for Stage-A, or an honest revision moving its release to Stage-B before the final SAP.
6. External timestamping of the final Stage-A artifact. A local mutable commit alone is insufficient under the prereg’s own rule.

### May proceed in parallel with or immediately after Stage-A

- Backfill provenance columns into the existing WB extraction log.
- Archive the original round-1 review and resolve O9 without renumbering.
- Correct v1.1’s stale status text and apply E1–E17 manuscript edits.
- Add `data/meta/manifest.tsv` and package-level regeneration tests.
- Write Related Work, governance framing, Discussion, captions, and bibliography, provided no comparator result language is inserted.

### May wait for the locked-robustness/comparator step, but must precede final analysis claims

- Eligibility-filtered NLL regeneration and hardware-invariant NLL sampling.
- Family-mapped decomposition, prevalence/breadth, concordance and intended-sense audit.
- QC grid, independent QC indicator, blinded adjudication, and “and” sensitivity.
- Extraction-method covariate/interactions and text-only fits.
- Deduplicated breakpoint scan, supported unknown-break analysis, and step/ramp comparison.
- Executed composition weighting, overlap/ESS diagnostics, and missingness-by-format/year analysis.

The round-1/O9 archive is a final-audit documentation blocker, not a scientific reason to delay Stage-A. Raw text release is not a Stage-A precondition. Immutable hashes, exact acquisition rules, and the executable measurement/branch logic are.

## 2. Sequencing ruling

Reviewing and freezing the prospective acquisition/measurement protocol **before** regenerating outcome-facing WB artifacts is the correct sequence. It prevents the family, eligibility, robustness, and comparator rules from being tuned to regenerated results.

That sequencing does not justify freezing an incomplete protocol. Code-level artifact regeneration may follow Stage-A, but the code and definitions that Stage-A purports to freeze must already exist uniquely enough to prevent alternative implementations. The present v0.2 fails that condition.

## 3. Blocking-table updates where round 4 changes status

Rows not shown retain their round-3 status.

| Round-2/3 item | Round-4 status | Editorial ruling |
|---|---|---|
| IMF controlled comparison | **DESIGN PARTLY RESOLVED; EXECUTION STILL BLOCKING** | Mechanism-neutral comparator logic is much better, but acquisition and branch rules are not freeze-ready and no comparator exists. |
| Within-stratum/comparator composition | **PARTLY RESOLVED AT PROTOCOL LEVEL** | Ontology/support/weight thresholds are proposed; exact weighting and execution remain blocking. |
| Missingness / zero-token analysis | **ELIGIBILITY SPECIFIED; REGENERATION STILL BLOCKING** | Zero and NLL rules are now explicit, but current artifacts/code do not apply them. |
| Multiplicity | **MOSTLY RESOLVED; BRANCH LOGIC STILL BLOCKING** | Holm co-primaries and X blocks replace the incoherent secondary family. P0 and LOPO families/global success remain undefined. |
| Breakpoint-scan inference | **DEMOTED FROM CONFIRMATORY; LOCKED REPAIR STILL REQUIRED** | This is no longer a Stage-A estimand blocker, but current `s12` still does not implement the promised diagnostics. |
| QC validation/sensitivity | **DEFINITION PARTLY RESOLVED** | Exact list and code now exist; validation and independent-rule sensitivity remain. |
| Tier-1 construct/family validation | **MAPPING/OUTCOME PARTLY RESOLVED; VALIDATION STILL BLOCKING** | Correct mapping and occurrence definition exist in text, but not machine-readable implementation; concentration guard requires revision. |
| Primary evidence for WB LLM adoption | **NARROWED, NOT A CONFIRMATORY BLOCKER** | H-DIFF no longer claims adoption. Primary-source evidence remains necessary only for carefully bounded contextual framing. |
| Assembled AR NLL | **NO LONGER A PREREG BLOCKER** | AR and NLL are exploratory/descriptive. Clean regeneration or deletion is still required before any manuscript convergence claim. |
| Family-collapse/HHI inconsistency | **NUMERICALLY RESOLVED; IMPLEMENTATION PENDING** | v1.1 and Appendix A have the correct mapping/numbers. Machine-readable mapping and regenerated family artifacts remain due. |
| Zero-token GPT-2 values | **RULE RESOLVED; DATA NOT REPAIRED** | NLL ≥100/no imputation is correct; current panel still contains the constants. |
| Intervention-unit inference | **PARTLY RESOLVED; STILL FREEZE-BLOCKING** | Time-level paired inference is the right direction, but formula rank and bootstrap algorithm are unresolved. |
| Incomplete audit provenance | **PARTLY RESOLVED** | Standard checksums, source, tests, environment specs, tokenizer, and stopword list now ship. Round-1/O9, immutable hashes, runnable `s11` inputs, comparator code, and raw-text rebuild route remain. |

## 4. Fallback decision and March 2027 target

The fallback should not be triggered merely because no P0 country-surveillance facet passes. Under v0.2, P1/P2 are the prespecified non-equivalent fallback. The fallback to an RQ1/measurement paper should occur if **neither branch** survives Stage-B genre, common-year, support, and MDE gates.

For a March 2027 submission, impose a hard Stage-B go/no-go date of **31 October 2026**. By that date the team should have:

- frozen Stage-A;
- completed metadata-only P0 adjudication and branch selection;
- completed common-year/country support and MDE diagnostics;
- frozen the final SAP.

If no active comparator branch is viable by 31 October 2026, switch immediately to the RQ1/measurement-discipline paper with all RQ2 results explicitly exploratory. Do not spend November–January rescuing a failed comparator ontology.

The treatment of 2026 may force a second decision. A full calendar-2026 cell cannot be harvested until after 31 December 2026. Either predeclare a January 2027 full-year harvest, accepting a compressed analysis/writing window, or use completed 2023–2025 post cells as the confirmatory minimum and treat 2026 as a later/descriptive update. Counting the August 2026 partial year as the fourth post cell is not acceptable.

## Ranked editor actions

1. Do not timestamp/freeze v0.2; produce v0.3 with a complete acquisition appendix, deterministic branch, estimable model, and exact bootstrap.
2. Freeze machine-readable measurement and sampling code, hashes, and completed-year cutoff before any IMF metadata access.
3. Complete Stage-B and make the comparator-versus-fallback decision no later than 31 October 2026.
4. Run existing-WB artifact repairs only under the frozen rules; no outcome-informed changes after Stage-A.
5. Execute the selected comparator once under the final SAP, with immutable inputs and machine-recomputable outputs.
6. If either design viability or completed-year timing fails, pivot to the RQ1/measurement paper rather than weakening the confirmatory standard.
7. Finish the manuscript and final external audit only after the regenerated artifacts, comparator analysis, and historical audit trail agree.
