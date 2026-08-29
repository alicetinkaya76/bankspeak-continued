# Round-3 third-eye review

**Package reviewed:** `round3_package_20260809.zip`  
**Review standard:** adversarial, file-grounded, and recomputed from the supplied artifacts.  
**Overall disposition:** the package passes file-integrity review, but the internal audit does not pass unchanged. Most headline arithmetic is reproducible. Four material defects were newly identified: an inconsistent family-collapse/HHI calculation, contamination of extraction-method denominators by 392 out-of-sample files, an incorrect “9 of 10 preceding units” statement, and invalid NLL values attached to zero-token documents.

# Data audit

## 0. Package integrity

**PASS, with one artifact-format defect.** The ZIP contains every required content file. All 28 manifest entries have the stated byte length and SHA-256 digest; there are no unmanifested content files. The separately uploaded preregistration and prompt are byte-identical to the copies inside the ZIP.

The root `MANIFEST.sha256` is not in standard `sha256sum -c` format because each line inserts a byte-count field between the digest and path. The hashes are correct when the three fields are parsed manually, but the file should either be renamed `MANIFEST.tsv` with a header or accompanied by a standard two-column `SHA256SUMS` file.

The package supports **artifact-level recomputation**, not end-to-end pipeline validation. Raw/extracted text, feature-generation code, the exact stopword list, tokenizer rules, and immutable model revisions are absent. Therefore regressions and aggregations can be independently regenerated from the CSVs, but lexical matching, stopword-share generation, token counts, and NLL generation cannot be rerun from source text. Claims at that lower layer are marked accordingly.

## 1. Formal A1–A3 / O3–O10 audit

| Label | Round-3 verdict | File-grounded ruling |
|---|---|---|
| **A1 — FY2002/FY2007 and QC** | **PARTIALLY RESOLVED** | Artifact values reproduce: FY2002 = 12 tokens, stopword share 0; FY2007 = 46,723 tokens, share 0.0094; 71 retained units have at least 17,023 tokens and share at least 0.2008. The current draft still falsely calls the gate “prespecified.” The stopword calculation itself is not end-to-end recomputable, and the promised grid/manual/independent-indicator validation is absent. |
| **A2 — two post years / level-only AR** | **RESOLVED AS A SPECIFICATION CORRECTION; NOT AS STRONG INFERENCE** | The level-only AR fit reproduces: `b2 = 0.069919`, HAC(2) p approximately `9.1e-8`, `n_post=2`. Removing pre-years gives a tight band; deleting either post year leaves a non-comparable one-post-observation fit. AR remains descriptive endpoint evidence despite the small model-based p-value. |
| **A3 — AR span** | **MOSTLY RESOLVED** | AR is generally labeled 2023–2024 while ICR/PAD extend through 2026. Residual defects remain: Table 2 says 1946–1965 although the assembled era begins in 1947, and the several corpus spans still need one explicit sentence. |
| **O3 — placebo/breakpoint specificity** | **PARTIALLY ADDRESSED; STILL BLOCKING** | The scan and ranks reproduce, but 72 AR calendar cuts are only 65 unique partitions. The largest ICR/PAD statistics occur at the final admissible 2025 cut with `n_post=2`. Raw rankings are endpoint-sensitive and do not identify a ramp or an unknown break. |
| **O4 — IMF comparator / Banga-style confounding** | **NOT ADDRESSED; PREREG REDESIGN REQUIRED** | No IMF result exists. The proposed ICR–Article IV comparison confounds institution with non-equivalent genre and cannot distinguish enterprise-LLM adoption from WB-specific leadership, template, or style-guide changes. |
| **O5 — Tier-1 concentration/construct** | **PARTIALLY ADDRESSED; STILL BLOCKING** | Counts and leave-two-family ratios reproduce, but concordance/domain-specific validation is absent. More seriously, the audit’s family-level HHI is internally inconsistent: under the preregistered 13-family mapping, HHI is 0.24451, not 0.240. The proposed “family collapse” also does not define whether occurrences or document-level family presences are counted. |
| **O6 — reference-model NLL** | **PARTIALLY ADDRESSED; NEW DATA DEFECT** | Robust period aggregations reproduce. Terminology and immutable revisions remain unfixed in the actual config; assembled-unit NLL is absent. Six zero-token documents are not cleanly excluded: Pythia is missing for all six, while GPT-2 assigns the identical value 5.8744 to five empty documents. Full NLL panels must be regenerated after a frozen document-level QC rule. |
| **O7 — within-stratum composition** | **NOT ADDRESSED** | No adjustment has been executed. The prereg’s proposed fields are not yet mapped across institutions; WB “instrument” and “sector” do not automatically have IMF equivalents. |
| **O8 — multiplicity** | **NOT RESOLVED** | A draft prereg exists but is not frozen and is materially underspecified. The secondary family mixes a two-post-year descriptive analysis with two unvalidated NLL outcomes, while exploratory blocks are not actually enumerated. |
| **O9** | **UNDEFINED AND STILL UNAUDITABLE** | The original round-1 review is still absent. Archiving the round-2 review does not reconstruct O9. Do not silently renumber historical labels: archive the round-1 review verbatim, preserve its original numbering, and add a one-row crosswalk explaining whether O9 was omitted by the authors or never assigned by the reviewer. |
| **O10 — residue/missingness** | **PARTIALLY ADDRESSED; NEW LOG-PROVENANCE DEFECT** | The 65-record residue and six zero-token records reproduce. Missingness-by-year/format is still absent. `extraction_log.csv` contains 392 IDs outside `frozen_sampling_v1.csv`; percentages computed from the unfiltered log are not percentages of the analyzed or frozen sample. |

## 2. Independent recomputation of audit §§3–4

The regression artifacts were independently regenerated from the feature CSVs. The supplied ITS table is exactly reproduced by unweighted document means within year, segmented OLS with HAC(2), and a placebo indicator equal to one when either the level or slope-change term has p < 0.05. All 45 rows reproduce to the published rounding.

| Claim | Verdict | Recomputed result |
|---|---|---|
| Corpus totals | **VERIFIED** | 2,818 sampled; 2,753 analyzed; coverage 97.6934%; residue 65; 2,747/2,753 nonzero-token records = 99.7821%; 70,246,055 tokens. Per-stratum rows reproduce exactly. |
| Tier-1 ITS headline | **VERIFIED AT ARTIFACT LEVEL** | AR assembled level-only `+0.0699`, placebo fraction 0.00, `n_post=2`; ICR `+0.0556`, p < 0.001, placebo fraction 1.00; PAD `+0.0266`, p = 0.01027, placebo fraction 0.50. |
| 72 cuts → 65 partitions | **VERIFIED** | Missing assembled FYs are 1971, 1981, 1990, 2000, 2002, 2007, 2010. Each creates one duplicate adjacent partition. After deduplication, 2023 remains rank 2; 2022 is first (`b2=0.0760`, `n_post=3`). |
| Other breakpoint ranks | **VERIFIED** | ICR: 2023 rank 3/27; PAD: 4/25; doc-level AR: 27/74. ICR and PAD maxima are 2025 with `n_post=2`; doc-level AR maximum is 2024 with `n_post=2`. |
| LOYO range | **VERIFIED, BUT THE UNQUALIFIED RANGE IS MISLEADING** | Base 0.0699. Dropping a pre-2023 year gives 0.0680–0.0746. Dropping FY2023 gives 0.0412 and dropping FY2024 gives 0.0986, each with only one post observation. |
| Post Tier-1 counts | **VERIFIED WITH A DENOMINATOR WARNING** | The decomposition table gives doc-level AR 20, ICR 417, PAD 338. The AR value is for the unassembled Annual-Report facet, including excluded sibling/duplicate documents and FY2025. The assembled FY2023–24 series has approximately 10 hits over 72,823 tokens, not 20. These two AR quantities must not be paired. |
| Underscore/pivotal shares | **VERIFIED** | Under the explicit 13-family mapping: underscore = 337/775 = 43.484%; pivotal = 114/775 = 14.710%. |
| HHI 0.240 / effective 4.2 | **REFUTED UNDER THE STATED 13-FAMILY DEFINITION** | Collapsing all 28 forms into the 13 families listed in the prereg gives seamless = 101/775 = 13.032%, HHI = **0.244507**, effective family count = **4.0899**. The reported 10.8% seamless share and HHI 0.239752 occur only when `seamlessly` is left outside the `seamless` family. This is an implementation/labeling inconsistency, not rounding. |
| Leave-underscore-and-pivotal ratios | **VERIFIED** | ICR 2.2238×; PAD 3.8479×; doc-level AR 2.1411×. These ratios remain vulnerable to near-zero baselines and do not establish construct specificity. |
| FY2022–24 extraction methods | **VERIFIED, WITH WORDING CORRECTION** | The assembled units FY2022, FY2023, and FY2024 each consist entirely of `server_txt`. FY2022 is not post under `post = year ≥ 2023`; it is the adjacent pre-cut year. |
| “9 of 10 preceding units are server_txt” | **REFUTED** | Among FY2012–21, **8/10** units are exclusively `server_txt`. FY2013 and FY2021 each contain two server-text documents and one PyMuPDF document. |
| ICR/PAD 2020s plain-text shares 83.5% / 76.7% | **REFUTED FOR THE ANALYSIS SAMPLE** | In the analyzed corpus, ICR = 258/280 = **92.14%** and PAD = 239/267 = **89.51%**. The reported 83.48% and 76.71% are obtained from the entire extraction log, which includes 168 extra ICR and 158 extra PAD records from the 2020s that are outside the frozen sample. |
| Overall server-text 2,705/3,145 | **ARITHMETIC VERIFIED; INTERPRETATION INVALID** | The log has 3,145 unique IDs, but only 2,753 are analyzed and 392 are outside the frozen sample. The analyzed share is 2,464/2,753 = **89.50%**. The log-wide 2,705/3,145 = 86.01% must not be called the analyzed-corpus share. |
| FY2007 passes token-only gate | **VERIFIED** | FY2007 has 46,723 tokens and therefore passes `min_tokens=5000`; only the stopword-share or another quality indicator excludes it. |
| Draft’s 27/71 below power gate | **REFUTED** | The regenerated count is **26/71**. The doc-level count is 22/144, comprising 21 Annual-Report years and PAD 1996. |
| Era means | **VERIFIED** | Temporal rate 39.9627 → 26.0983 → 27.9870; Tier-2 0.2523 → 9.0945. The exact unrounded Tier-2 ratio is 36.05×; 36.36× is the ratio of rounded display values 9.09/0.25. |
| 2020s Annual-Report plain-text share | **VERIFIED** | 14/25 = **56.0%** in the analyzed doc-level AR stratum. This does not characterize the assembled headline units. |
| Robust NLL medians | **VERIFIED** | Pythia ICR 2.4004 → 2.5331; PAD 2.4503 → 2.5994. GPT-2 moves in the same direction. The reported 2019–26 robust table is unaffected by the five old empty-document constants, but the full historical NLL panel is not clean. |
| Residue taxonomy | **PARTLY VERIFIED** | Total 62 HTTP-4xx-class records + 3 no-URL records is supported. A unique 61×403 + 1×404 split is not reproducible without a declared adjudication rule because two IDs accumulated both 403 and 404 failures across passes; the final logged failure for all 62 URL-bearing residue IDs is 403. |
| Raw lexical/NLL/QC generation | **NOT RECOMPUTABLE END TO END** | Missing inputs: raw/extracted text, source scripts, exact stopword list and tokenization rules, and immutable model revisions. The CSV-level arithmetic is reproducible; feature production is not. |

## 3. Contested calls

### C1 — LOYO presentation

**Ruling: legitimate, not selective, under strict labeling.** Report 0.0680–0.0746 as the **pre-period deletion influence band**, retain the complete 72-row table, and separately report the FY2023/FY2024 deletions as **one-post-observation boundary sensitivities**. Calling the narrow band the unrestricted “LOYO range” would be selective; calling it the pre-period influence band is correct because the two post deletions change the estimand’s support.

### C2 — extraction method

**Ruling: the simple assembled-AR method-switch objection is substantially weakened, not neutralized.** FY2023 and FY2024 are server text, as is FY2022. That rules out a direct PDF-to-text switch exactly at the headline cut. It does not rule out server-text template changes, source-content changes, mixed-method influence earlier in the trend, or extraction defects within server text.

For the operational panels, use analysis-sample denominators: ICR 2020s server text = 92.14% versus 92.65% in the 1990s; PAD = 89.51% versus 93.39%. There is no large monotone ICR decline. PAD’s method mixture remains era-varying, with its lowest analyzed share in the 2010s (83.77%). A method covariate, institution/method interaction, and text-only sensitivity remain due, but the internal audit’s 83.5%/76.7% argument must be withdrawn.

### C3 — E3 replacement sentence

**Ruling: still slightly too strong.** “Neither distinguish a unique breakpoint within 2022–2025” makes 2022–2025 sound like an identified break interval. It is only the location of high-ranked, endpoint-sensitive candidate statistics. Use:

> Several prespecified series rise in the final years, but the breakpoint scans are descriptive and endpoint-sensitive; they do not identify a unique break date, trajectory shape, or mechanism.

“Post-2022 increase” may remain a descriptive period label. “Ramp,” “adoption,” and “break within 2022–2025” should not appear as results until explicit model comparison and a credible controlled design exist.

### C4 — QC-gate defense

**Ruling: insufficient in the current package; conditionally defensible after the promised validation.** The observed gap is large and makes the two exclusions practically plausible. It does not substitute for the threshold grid, token-only re-estimation, independent quality indicator, blinded adjudication, exact stopword-list disclosure, and unchanged transfer to IMF. Because “and” contributes to the gate and is itself an outcome, the primary analysis of “and” should use an independent QC rule or demonstrate invariance across independent-rule sensitivities. The current defense is a plan, not completed evidence.

## 4. Ranked data-audit actions

1. **Correct the newly refuted audit statements before any freeze:** implement the 13-family mapping explicitly; report HHI 0.244507/effective 4.09 or change the family definition; replace 9/10 with 8/10; replace the contaminated ICR/PAD extraction shares; distinguish doc-level AR 20 hits from assembled AR 10 hits.
2. **Repair artifact provenance:** split pilot/out-of-sample extraction records from frozen-sample records or add `sampling_version`, `run_id`, and `analysis_eligible`; regenerate every extraction-method table from the analysis IDs.
3. **Freeze and apply document-level QC:** exclude zero-token documents before feature/NLL modeling; regenerate NLL so empty text cannot receive GPT-2 value 5.8744; specify handling of short documents and missing model outcomes.
4. **Complete the QC and extraction sensitivity package:** exact stopword list/hash, threshold grid, independent indicators, blinded manual audit, text-only fits, and method interactions.
5. **Replace raw breakpoint ranks with deduplicated, supported analyses:** full support columns, defensible trimming, calibrated unknown-break procedure, and no ramp language.
6. **Restore the audit trail:** archive the original round-1 review, resolve O9 without renumbering history, and issue a corrected audit completion file.
7. **Release executable provenance:** source scripts, environment lock, tokenizer/regex specifications, immutable model hashes, and a standard checksum file. Until then, describe the release as artifact-recomputable rather than end-to-end reproducible.

# Prereg

## 1. Disposition

**DO NOT FREEZE `PREREG_DRAFT_v0.1`.** It is prospective only with respect to the unseen IMF data. It is retrospective and outcome-informed with respect to the WB breakpoint, panel choice, lexicon, observed post-period hits, and many sensitivity choices. That does not make a prospective comparator test useless, but it must be described as a **prospective external-comparator validation of an already observed WB pattern**, not as a pristine confirmatory discovery design.

## 2. Blocking design defects and exact required changes

| Defect | Why it fails hostile review | Required change before freeze |
|---|---|---|
| **Primary panel selected by 417 versus 338 observed post hits** | This is direct outcome-based panel selection. ICR also has fewer post tokens than PAD, so “largest hit mass” is not a neutral power criterion. | Delete the hit-count rationale. Choose the primary by an independent genre-method adjudication using document purpose and pre-2023 metadata only. If no unambiguous choice exists, designate ICR and PAD co-primary and control the two tests, while explicitly acknowledging the WB outcomes were already seen. |
| **ICR versus Article IV called a harmonized controlled contrast** | Institution and genre are perfectly confounded: project-completion reports versus country-surveillance reports. Within-series changes remove level differences, not differential genre-specific shocks, templates, authorship systems, or policy cycles. | Either identify a genuinely comparable WB country-surveillance genre, or relabel ICR–Article IV as a non-equivalent falsification comparator and cap interpretation accordingly. Do not call the panel “harmonized.” |
| **Positive WB×post interaction interpreted as enterprise-LLM-consistent** | A WB-specific interaction is equally consistent with Banga, a WB template/style-guide change, or WB-specific thematic change. Conversely, a similar IMF increase could support a shared LLM-era shift while making the interaction null. The current disconfirmation logic conflates two different hypotheses. | Replace the success claim with: “a differential post-2022 change between the prespecified WB and IMF series in the frozen lexical outcome; mechanism unresolved.” Separate a generic shared LLM-era hypothesis from a WB-specific-change hypothesis. |
| **“Family collapse” outcome undefined** | If every token occurrence is mapped to a family and summed, the total count is identical to the current 28-form count and concentration is not reduced. If each family counts once per document, the log-token offset is inappropriate. | Define the exact response mathematically: occurrence count, distinct-family count, or family prevalence. Include the 28-form→13-family mapping, case/token boundary rules, and treatment of repeated occurrences. Use a model appropriate to that response. |
| **Lexicon treated as confirmatory despite WB-informed construction** | The same WB outcomes motivated the family collapse and primary selection. Freezing before IMF prevents further tuning but does not erase WB-side selection. | State this limitation in the prereg. Prefer an externally defined, independently justified family set or a held-out validation set. At minimum, restrict the confirmatory interpretation to comparator replication and keep “LLM-associated construct validity” exploratory. |
| **M1 imposes common linear pretrend** | The model omits `institution×year`; a non-significant pretest is then used to justify imposing equality. This produces pretest dependence and leaves bias when differential trends are real but imprecisely estimated. | Put the differential pretrend in the primary model, not only in a gate. A defensible cell-level form is `Count_it ~ institution + C(year) + institution:centered_year + institution:post + offset(log Tokens_it)` after prespecified standardization. Document-level QML may be a sensitivity. |
| **Clustering/bootstrap level is wrong or incomplete** | Treatment varies at institution×time, with only four WB post-year cells. Clustering 66 institution-year cells treats adjacent years and paired WB/IMF shocks as independent; thousands of documents do not create thousands of intervention units. | Base primary inference on paired institution-year cells and preserve time dependence: paired moving-block/wild bootstrap over years, or a prespecified annual-difference time-series method. Freeze cluster unit, block length, null-imposed algorithm, bootstrap replications, seed, software, and two-sided/one-sided test. |
| **Pretrend gate is not an equivalence test** | “Does not reject at α=.10” is ordinary non-rejection, not equivalence. Reporting a CI without an equivalence margin does not fix that. | Define a substantively justified equivalence bound for the differential pretrend and require its CI to lie inside the bound, or remove the gate and estimate differential trends directly. Do not use the term “equivalence-style” without a bound. |
| **“Sign and order of magnitude stable” is discretionary** | The decision rule can be adjudicated after results because “order of magnitude” has no threshold. | Replace it with numerical criteria fixed in advance, including what happens when NB2 fails, standardization is infeasible, or confidence intervals widen materially. |
| **Composition standardization is not operationalized** | Region/sector/instrument are not automatically common across ICR and Article IV; “drop symmetrically” can hide failed measurement. No target population, weighting estimator, overlap rule, truncation, effective sample size, or variance method is given. | Freeze a common cross-institution ontology, target distribution, weighting/standardization formula, missing-category handling, positivity diagnostics, weight truncation, minimum effective sample size, and failure rule. If common support is inadequate, the confirmatory claim must fail rather than silently drop fields. |
| **Secondary FDR family is incoherent** | S2 is called confirmatory despite two post observations and “descriptive-plus” interpretation. S3/S4 are unvalidated, highly correlated NLL outcomes and currently contain zero-document defects. | Remove P-A from confirmatory testing. Keep it descriptive. Move NLL to exploratory unless construct validation and clean document QC are completed before freeze. A single PAD secondary test needs no artificial four-test BH family. |
| **Exploratory blocks are not enumerated** | “Classic features × panels” and other phrases do not define the number of tests or family boundaries. | List every outcome×panel hypothesis, direction, p-value definition, and FDR block. Distinguish hypothesis tests from descriptive diagnostics such as HHI and prevalence. |
| **Document inclusion is absent from M1** | Six zero-token WB records exist; `offset(log tokens)` is undefined at zero. IMF extraction failures and short records will occur. | Freeze document-level eligibility, zero/short-text handling, duplicate/version rules, missing-NLL rules, and intention-to-sample reporting before analysis. |
| **D7 power gate is not power for H1** | The 41,981-token two-rate calculation ignores only two institutions, serial time dependence, four post years, composition weighting, and the interaction estimand. | Add a simulation-based MDE/power analysis for the interaction under the planned time-level inference. Freeze a minimum number of usable pre/post institution-year cells and an action if the gate fails. |
| **Freeze timing is too early for a feasible crosswalk** | Freezing before any IMF metadata protects against outcome peeking but leaves genre definitions, covariates, duplicates, and sample-frame feasibility unknown, inviting many deviations. | Use two stages: freeze the acquisition protocol now; then inspect metadata only with text/outcomes sealed, establish the frame/crosswalk/power/overlap, and freeze the final statistical analysis plan before downloading or feature-processing IMF text. Timestamp both stages externally, not only with a mutable local commit. |

## 3. Specific rulings on the requested prereg elements

**Single-primary choice.** Not defensible as written because the justification is post-outcome hit mass. The cleaner options are an independently adjudicated primary based on genre comparability or two co-primary operational panels. The current rationale must not survive the freeze.

**Article IV as operational analog.** It is a contextual comparator, not a close genre analog. Difference-in-changes does not require equal levels, but it does require a credible counterfactual trend and absence of differential post shocks. With one distinct genre per institution, those assumptions cannot be separated from institution effects. A positive interaction is therefore descriptive comparative evidence, not an institution-specific mechanism result.

**Poisson QML / NB2.** QML with exposure is reasonable for occurrence counts, but the current covariate and time structure is insufficient. NB2 is a distributional sensitivity, not a remedy for wrong intervention-unit inference, genre confounding, serial correlation, or composition imbalance.

**Pretrend and three-condition rule.** The gate is invalidly labeled as equivalence, and condition 3 is subjective. Both require replacement before freeze. A model that always includes differential trend is preferable to pretest-then-pool.

**Frozen 13-family lexicon.** Freezing exact forms is necessary but not sufficient. The current family arithmetic is inconsistent, the config has a flat form list rather than a family mapping, and collapsing labels alone leaves total occurrence counts unchanged. The prereg must define an estimand that actually addresses concentration.

**Four-member secondary family.** Reject it. AR cannot become confirmatory by FDR adjustment, and NLL should not enter a confirmatory family before zero-document cleanup and construct validation.

**Composition standardization.** Conceptually necessary, operationally absent. “Drop failed fields symmetrically” is not a valid fallback when the fields are institution-specific. Standardization must be precomputable from a common data dictionary and have a hard failure rule.

**Disconfirming outcomes.** The list is useful only after separating two claims: a shared LLM-era shift and a WB-specific differential shift. A similar IMF increase contradicts H1 but may support the shared-era claim; it is not generically evidence against an LLM-era reading. Terms such as “driven by 2023” and “rising only through one family” need numerical thresholds.

## 4. Ranked prereg actions

1. **Redefine the inferential claim as a mechanism-neutral differential change; stop treating a positive interaction as LLM-adoption evidence.**
2. **Resolve the institution–genre confounding:** find a credible analog or demote ICR–Article IV to a non-equivalent falsification comparison.
3. **Remove outcome-based primary-panel selection and declare the design’s partial prospectivity.**
4. **Define the family outcome mathematically and fix the `seamless/seamlessly` mapping before any freeze.**
5. **Replace document-level cluster logic with time-level paired inference and include differential pretrend in the primary model.**
6. **Replace non-rejection and subjective robustness gates with prespecified equivalence bounds and numeric sensitivity rules.**
7. **Operationalize composition standardization, overlap, missingness, and failure rules.**
8. **Remove AR and unvalidated NLL from the secondary confirmatory family; enumerate every remaining multiplicity block.**
9. **Add document-level QC, zero-token/NLL handling, and interaction-specific power/MDE.**
10. **Use a two-stage, externally timestamped acquisition/SAP freeze with IMF outcomes sealed during metadata feasibility work.**

# Editor

## 1. Disposition

**If submitted now: desk reject. Scientific state: major revision.** The package is more auditable than round 2, but the manuscript remains a skeleton, the comparator is absent, and the proposed prereg does not yet identify the claim it wants to make. The new data-audit defects also mean the internal completion memo cannot be used as the final audit record.

A March 2027 submission remains possible only if the comparator design is settled quickly and the genre/covariate crosswalk proves feasible. If that feasibility test fails, the defensible fallback is an RQ1/measurement-discipline paper with RQ2 explicitly exploratory, not a forced confirmatory interaction.

## 2. Updated round-2 blocking table

| Round-2 item | Round-3 status | Editorial ruling |
|---|---|---|
| Full Related Work and Discussion | **STILL BLOCKING** | Both remain unwritten; GIQ fit cannot be judged from headings and reference modules. |
| IMF controlled comparison | **STILL BLOCKING** | No result; current prereg needs redesign before harvest. |
| Within-stratum composition | **STILL BLOCKING** | No executed adjustment or common ontology. |
| Extraction-method sensitivity | **STILL BLOCKING, NARROWED FOR AR** | The exact assembled cut is not a simple method switch, but operational-panel sensitivity is unfinished and the audit used contaminated denominators. |
| Missingness-by-format / zero-token analysis | **STILL BLOCKING; NEW NLL BUG** | Six zeros are encoded as feature zeros; five receive a constant GPT-2 NLL. |
| Multiplicity | **STILL BLOCKING** | Draft family is not coherent or frozen. |
| Breakpoint-scan inference | **STILL BLOCKING** | Deduplication and calibrated inference are not in the artifacts; E3 remains too strong. |
| QC validation/sensitivity | **STILL BLOCKING** | Planned, not executed; exact stopword list absent. |
| Tier-1 construct validation | **STILL BLOCKING; NEW FAMILY BUG** | Family mapping/HHI inconsistent; external specificity and concordance absent. |
| Per-word contributions and concordances | **PARTLY RESOLVED, STILL BLOCKING AS SUPPLEMENT** | Counts exist; concordance and intended-sense audit do not. |
| Primary evidence for WB LLM adoption | **STILL BLOCKING** | Draft still has placeholders; even primary sources would establish availability/adoption, not use in sampled documents. |
| Assembled-unit AR NLL | **STILL CONDITIONAL BLOCKER** | Either compute cleanly or remove AR from all NLL convergence claims. |
| Title/span clarification | **PARTLY RESOLVED, MINOR** | Table-era and corpus-span corrections remain. |
| Figure captions/readability | **STILL MINOR** | Native PNGs are legible, but uncertainty/support and extraction/assembly distinctions are not carried in captions. |
| Bibliographic normalization | **STILL MINOR BUT UNFINISHED** | E9 is a plan, not a v0.3 bibliography. |
| **New: extraction-log sample contamination** | **NEWLY DISCOVERED, BLOCKING FOR METHOD CLAIMS** | 392 out-of-sample IDs must be separated or marked. |
| **New: family-collapse/HHI inconsistency** | **NEWLY DISCOVERED, BLOCKING FOR PREREG OUTCOME** | Must be fixed before the outcome is frozen. |
| **New: zero-token GPT-2 NLL values** | **NEWLY DISCOVERED, BLOCKING FOR NLL ANALYSIS** | Regenerate after document QC. |
| **New: prereg intervention-unit inference** | **NEWLY DISCOVERED, BLOCKING** | Institution×year clustering does not address serial dependence or four treated post-year cells. |
| **New: incomplete audit provenance** | **NEWLY DISCOVERED, DOCUMENTATION BLOCKER** | Round-1 review/O9 absent; source scripts and standard checksums absent. |

## 3. Is P0–P5 complete and correctly ordered?

**No.** The order `P1 existing-data extensions → P2 freeze` invites further outcome-informed tuning. The freeze must precede optional new WB outcome analyses, except for corrections needed to define a valid outcome and data-eligibility rule. P5 is also misnamed: this package is already round 3. What is needed later is a post-analysis independent audit.

A defensible order is:

1. **Artifact repair and audit trail:** correct the family, extraction-log, zero-NLL, span, and O9 defects; add standard checksums, code, environment, and exact lexical/QC definitions.
2. **Acquisition preregistration:** freeze IMF source/frame/query/deduplication rules before metadata access, with an external timestamp.
3. **Metadata-only feasibility stage:** keep text and outcomes sealed; establish genre mapping, common covariates, country/year coverage, overlap, missingness expectations, and interaction MDE. Then freeze the final SAP.
4. **Locked robustness and comparator harvest:** run the already specified WB sensitivities and apply unchanged extraction/QC rules to IMF. Any rule change demotes the affected result.
5. **One-shot confirmatory analysis:** produce immutable inputs, full logs, and a machine-recomputable output table; then invite independent recomputation.
6. **Manuscript completion:** write the governance theory, Related Work, Discussion, primary-source adoption section with scope limits, captions, and bibliography.
7. **Final external audit and submission decision:** this is the successor to the current round-3 review.

The current P0–P5 plan also omits interaction-specific power, a common metadata ontology, overlap/weight diagnostics, document-level QC for M1/NLL, external timestamping, sample-versioned extraction logs, and an explicit fallback if no valid IMF analog exists.

## 4. Are E1–E9 complete and adequate?

| Erratum | Ruling |
|---|---|
| **E1** | Adequate replacement, but not yet applied to the draft/memo. |
| **E2** | Adequate terminology direction; incomplete until immutable revisions, corpus-cutoff support, and clean zero-document handling are present. |
| **E3** | **Inadequate.** Replace with the endpoint-sensitive wording given under C3; do not present 2022–2025 as an identified break window. |
| **E4** | Adequate. |
| **E5** | Adequate: 26/71. |
| **E6** | Incomplete: rename to stopword share, disclose/hash the exact list, and address the “and” outcome with an independent QC sensitivity. |
| **E7** | Adequate if one sentence states doc-level AR 1946–2025, assembled AR 1947–2024, ICR 1994–2026, PAD 1996–2026, and the first era is relabeled 1947–1965. |
| **E8** | Inadequate without the original round-1 review and a preserved historical crosswalk. |
| **E9** | Necessary but not sufficient; it does not cover the newly discovered data/audit errata. |

Add at least the following v0.3 errata:

- **E10 — Family aggregation:** define the exact 28-form→13-family mapping; correct seamless to 13.03%, HHI to 0.244507, and effective family count to 4.09 if all listed variants are collapsed.
- **E11 — Extraction denominators:** state that `extraction_log.csv` contains 392 out-of-sample IDs; use frozen/analyzed IDs for every method percentage; replace ICR/PAD 83.5%/76.7% with 92.1%/89.5% for analyzed 2020s documents.
- **E12 — Assembled-unit methods:** replace “9 of 10 preceding” with “8 of 10 exclusively server text; FY2013 and FY2021 mixed”; call FY2022 adjacent pre-cut, not post-cut.
- **E13 — AR absolute hits:** distinguish doc-level AR 20 hits from assembled FY2023–24 approximately 10 hits; state the document/genre denominator each time.
- **E14 — Zero-token NLL:** exclude six zero-token records under a frozen document rule and regenerate NLL; remove GPT-2’s empty-document constant values.
- **E15 — Residue codes:** report 62 4xx-class + 3 no-URL unless a deterministic per-ID 403/404 adjudication rule is added.
- **E16 — Reproducibility language:** change “fully regenerated/reproducible” claims to match the actual release, or add source scripts, text-access procedure, stopword/tokenizer definitions, immutable model hashes, and standard checksums.
- **E17 — Prereg status:** identify the design as prospective only for the IMF comparator and outcome-informed on the WB side.

## 5. Ranked editor action list

1. **Do not freeze the current prereg; repair its estimand, comparator logic, family outcome, and time-level inference first.**
2. **Correct and regenerate the audit artifacts:** HHI/family mapping, extraction denominators, assembled-method count, AR hit denominators, and zero-token NLL.
3. **Establish a metadata-only IMF feasibility stage and a valid genre/covariate crosswalk before committing to ICR–Article IV as the primary comparison.**
4. **Complete the locked QC, extraction, missingness, breakpoint, concentration, and composition analyses.**
5. **Execute the comparator once under the final SAP; interpret only the differential textual change, not its mechanism.**
6. **Write the manuscript as a GIQ article rather than a methods skeleton: full governance theory, implications, adoption-source scope, and Discussion.**
7. **Run a final independent audit with code and standard checksums before deciding whether March 2027 submission is responsible.**
