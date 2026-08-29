# Round-2 external review (received 2026-08-09; archived verbatim)

> Provenance note (added at archiving): the round-2 reviewer received ONLY
> `PAPER_DRAFT_v0.2.docx`; the memo, tables and robustness files never reached it.
> Its "NOT AUDITABLE" verdicts follow from that package failure, completed internally in
> `ROUND2_AUDIT_COMPLETION.md`. The Editor and Referee sections below are verbatim; the
> round-2 Reference audit (all 25 entries independently VERIFIED) is condensed to its
> findings and action list at the end — the full 25-row table lives in the round-2
> conversation record and is not re-audited in round 3.

---

# Editor

## Review basis

Only `PAPER_DRAFT_v0.2.docx` was available from the stated round-2 package. The current `RESPONSE_TO_REVIEW.md`, regenerated `tables/`, `robustness/`, figures, and aggregate feature files were not supplied. The manuscript itself still contains an unfilled comparator result, an unwritten Related Work section, an unwritten Discussion, and analyses explicitly described as planned rather than completed.

I therefore do not treat the older first-round bundle as evidence for the revised results. Claims visible in the draft can be evaluated; the exact A1–A3/O3–O10 mapping and current-CSV recomputation cannot be reconstructed honestly.

## 1. Disposition

**Disposition: desk-reject in the submitted form.**

The underlying scientific state is major revision, but an editor acts on the manuscript submitted, not on planned work. Even granting the hypothetical completed IMF section, this remains a seven-page analysis skeleton with core theory, discussion, within-stratum composition control, extraction-bias analysis, multiplicity treatment, and construct validation unfinished.

The topic could fit *Government Information Quarterly*: the journal explicitly covers work at the intersection of government, public policy, information technology, and information management. The present manuscript, however, has not yet converted its corpus audit into a developed information-governance argument about institutional accountability, AI-assisted public communication, records, transparency, or administrative practice.

**The sentence I would send the authors:**

> Even with the IMF comparator completed, the manuscript is not review-ready because the genre-composition thesis is not applied within strata, extraction-method bias and multiplicity remain untreated, the principal lexical construct is insufficiently validated, and the theoretical and discussion sections are unfinished.

## 2. Does the revised framing match the evidence?

### Measurement-discipline lead: **yes**

The revised hierarchy is coherent:

* corpus as infrastructure;
* replication as validation;
* post-2022 change as a conditional application;
* genre composition and extraction validity as the lead contribution.

That is consistent with the strongest evidence in the manuscript. The assembled and unassembled Annual Report series produce opposite temporal-anchoring trajectories, and provenance controls failed to detect two unusable fiscal-year units. Those are real measurement lessons independent of the LLM interpretation.

### Abandoning a unique "2023 discontinuity": **mostly yes**

The revised draft now discloses:

* only two post-cut Annual Report observations;
* a level-only Annual Report model;
* ICR placebo fraction of 1.00;
* PAD placebo fraction of 0.50;
* strongest ICR/PAD cuts in 2024–2025;
* 2023 ranked rather than assumed to be uniquely maximal.

That is materially more consistent with the evidence than the first-round framing.

### "Ramped adoption": **no**

The principal remaining overclaim is:

> "maximal break statistics cluster in 2022–2025, consistent with ramped adoption rather than a single break."

The Results repeat the same claim as:

> "a ramped post-2022 increase, not a single sharp 2023 break."

A ranking of cut statistics can establish that the largest values occur near the end of the series. It does **not** establish:

1. a ramp-shaped trajectory rather than endpoint instability;
2. gradual adoption rather than a step, nonlinear trend, topic shift, template change, leadership shift, or extraction change;
3. adoption as the mechanism.

The reported models do not directly compare a step model with a ramp model. The breakpoint scan does not test the adoption mechanism. The cross-series trajectories are also heterogeneous: the document-level Annual Report panel falls under every Tier-1 aggregator, while the assembled Annual Report panel rises.

A defensible replacement is:

> "Several measures show a late-period increase, but the available annual series do not distinguish a unique breakpoint within 2022–2025 or identify its mechanism."

### Two other claims require correction

**"Prespecified per-unit gate" is chronologically inaccurate.** The draft says an external audit first identified FY2002 and FY2007 and that the gate was imposed in response. It was therefore not prespecified relative to inspection of these units. The correct wording is:

> "an audit-derived gate, frozen before re-estimation of the revised outcome models."

The large observed separation between legitimate and defective units may make the rule sensible, but it does not make the threshold prespecified.

**"Frozen pre-2022 models" and "pre-LLM model surprise" are inaccurate descriptions of Pythia.** Pythia is itself a suite of large language models presented at ICML 2023. The manuscript may be able to say that its training corpus predates widespread ChatGPT-era writing, but it must document the corpus cutoff and use a term such as **reference-model NLL**, not "pre-LLM model surprise."

## 3. What must exist before submission?

The exact authors' "NOT done" list cannot be audited because the response memo was not supplied. The following evaluates every visible deferral in the manuscript.

| Item | Classification | Editorial judgment |
| --- | --- | --- |
| Completed Related Work and Discussion | **Blocking** | A reference list and bullet outline are not substitutes for an argument. GIQ fit cannot be assessed without theory and implications. |
| IMF comparison | **Blocking** | Correctly treated as publication-gating, but it must be an estimated controlled contrast, not parallel descriptive plots. |
| Within-stratum composition adjustment | **Blocking** | Explicitly deferred, but this is the manuscript's own central methodological principle "applied to itself." It cannot be deferred. |
| Extraction-method sensitivity | **Blocking** | Plain-text delivery falls to 56% for 2020s Annual Reports. That change is temporally aligned with the claimed effect and must be modeled or restricted away. |
| Missingness-by-format and zero-token analysis | **Blocking** | Overall missingness is small, but temporal and format selectivity—not merely the overall percentage—is the relevant threat. |
| Multiplicity control | **Blocking** | "FDR planned" is not an analysis. The primary estimand must be frozen and the exploratory family corrected before submission. |
| Breakpoint-scan inference | **Blocking** | Raw candidate rankings do not establish a ramp or provide an unknown-break significance test. |
| QC-rule validation and sensitivity | **Blocking** | Threshold-grid results, manual adjudication and alternative quality indicators must be supplied. |
| Tier-1 family-level construct validation | **Blocking** | A 43% underscore-family contribution remains too concentrated for confirmatory "LLM-associated" interpretation. |
| Per-word contributions and concordance samples | **Blocking as supplement** | These are necessary to establish that counts represent the intended lexical uses rather than tables, quotations, headings, or unrelated senses. |
| Primary evidence for World Bank LLM adoption | **Blocking** | The current introduction still contains citation placeholders. Availability of an internal tool is not evidence that the sampled reports used it. |
| Assembled-unit Annual Report NLL | **Conditional blocker** | It can be deferred only if Annual Report NLL is removed from all cross-stratum convergence claims. Otherwise it must be computed. |
| Title-span clarification | Cosmetic | Make explicit that Annual Reports end in 2024 while operational genres extend to 2026. |
| Figure readability and captions | Cosmetic but necessary | Axis text and legends are too small at the current page scale. Captions must state aggregation, uncertainty and candidate support. |
| Bibliographic normalization and layout | Cosmetic | Split the two Moretti/Pestre manifestations, cite the López Bernal corrigendum, and repair the compressed bibliography/near-empty final page. |

### Ranked editor action list

1. **Complete the manuscript as an article:** full theory, Related Work, Discussion, primary-source citations and comparator result.
2. **Estimate a composition-adjusted controlled design:** harmonized IMF genres, institution-by-post/ramp interaction, pretrend assessment and document-level covariates.
3. **Resolve the identification problems:** extraction-method sensitivity, unknown-break inference and the two-observation Annual Report endpoint.
4. **Redefine and validate Tier-1:** independent family-level lexicon, absolute effects, concordance audit and concentration diagnostics.
5. **Execute multiplicity control and freeze the comparator estimand before inspecting comparator results.**
6. **Recast the claims as late-period stylistic change unless a direct ramp comparison and controlled contrast support stronger language.**
7. **Only after the six blocking steps, rebuild the GIQ framing around public-sector information governance rather than a corpus-methods demonstration.**

---

# Referee

## 4. First-round demands

### Exact A1–A3 and O3–O10 audit

| Label | Verdict | Reason |
| --- | --- | --- |
| A1 | **NOT AUDITABLE** | `RESPONSE_TO_REVIEW.md`, which defines the label, was not supplied. |
| A2 | **NOT AUDITABLE** | Same package failure. |
| A3 | **NOT AUDITABLE** | Same package failure. |
| O3 | **NOT AUDITABLE** | Same package failure. |
| O4 | **NOT AUDITABLE** | Same package failure. |
| O5 | **NOT AUDITABLE** | Same package failure. |
| O6 | **NOT AUDITABLE** | Same package failure. |
| O7 | **NOT AUDITABLE** | Same package failure. |
| O8 | **NOT AUDITABLE** | Same package failure. |
| O9 | **NOT AUDITABLE** | Same package failure. |
| O10 | **NOT AUDITABLE** | Same package failure. |

Assigning substantive objections to these codes by guesswork would fabricate the response structure. The draft does, however, permit the following thematic audit of the first-round demands named in the round-2 prompt.

### Substantive crosswalk

| First-round demand visible from the round-2 prompt | Verdict | Assessment |
| --- | --- | --- |
| Remove defective FY2002 and suspect FY2007 | **PARTIALLY ADDRESSED** | Both are identified and excluded through a gate, but the revised QC log and threshold sensitivity are unavailable. Calling the rule prespecified is incorrect. |
| Do not estimate an Annual Report post-break slope from two years | **ADDRESSED** | The primary Annual Report model is now level-only and `n_post=2` is disclosed. |
| Stop labeling Annual Report evidence "2023–2026" | **ADDRESSED** | The revised era is correctly labeled 2023–2024. Operational genres still extend through 2026. |
| Lead with measurement discipline rather than a dated break | **ADDRESSED** | The abstract and introduction now make the audit design the lead contribution. |
| Acknowledge placebo non-specificity | **PARTIALLY ADDRESSED** | The caveat is prominent, but "ramped adoption" restores an interpretation that the placebo and scan evidence do not identify. |
| Add an empirical breakpoint scan | **PARTIALLY ADDRESSED** | Rankings are reported, but candidate comparability, endpoint trimming and unknown-break inference are not resolved. |
| Add influence and robust aggregation | **PARTIALLY ADDRESSED** | Median, trimmed-mean and leave-one-year-out results are reported. The current CSVs were not supplied, and these checks do not address composition or mechanism. |
| Address Tier-1 circularity and concentration | **PARTIALLY ADDRESSED** | Leave-word-out evidence is useful, but 58% of post-period mass remains in two lexical families and no independent family-level confirmatory definition is shown. |
| Recast perplexity as a non-detector deviation measure | **PARTIALLY ADDRESSED** | The non-detector caveat is now explicit; the "pre-LLM/pre-2022" terminology is inaccurate and assembled Annual Report NLL remains missing. |
| Model within-stratum composition | **NOT ADDRESSED** | The draft explicitly says this remains to be done. |
| Address multiplicity | **NOT ADDRESSED** | A future confirmatory estimand and future FDR procedure are described, but not executed. |
| Test extraction-method and missingness bias | **PARTIALLY ADDRESSED** | Extraction method is logged and the problem acknowledged; no sensitivity model is reported. |
| Resolve leadership/style-guide confounding with IMF | **NOT ADDRESSED IN THE SUPPLIED FILE** | The comparator is still a placeholder and publication gate. |

### Numerical spot-checks possible from the manuscript

The visible arithmetic is internally consistent:

| Check | Result |
| --- | --- |
| Sampled total | 331 + 1,286 + 1,201 = **2,818** |
| Downloaded total | 323 + 1,270 + 1,160 = **2,753** |
| Coverage | 2,753 / 2,818 = **97.693%**, correctly rounded to 97.7% |
| Residue | 8 + 16 + 41 = **65** |
| Error decomposition | 62 server errors + 3 no-URL records = **65** |
| Nonzero extraction rate | 2,747 / 2,753 = **99.782%**, correctly reported as 99.78% |
| Tier-2 historical ratio | 9.09 / 0.25 = **36.36×**, so "36×" is correct |
| Temporal decline to 1986–2005 | 39.96 → 26.10 = **34.7%** |
| Temporal decline to 2006–2012 | 39.96 → 27.99 = **30.0%** |

The sentence claiming a "~35%" decline to "~26–28" compresses two different declines. "Approximately 30–35%" would be exact. Corpus totals and era values are reported in the draft.

I could not independently recompute the breakpoint ranks, HAC p-values, leave-one-year-out range, median/trimmed results, or word-level shares because the revised CSVs named in the prompt were absent.

## 5. Assessment of the new evidence

### 5.1 Breakpoint scan

**Does it support "maximal cuts cluster in 2022–2025"?**

**Descriptively, yes. Inferentially, no.**

According to the manuscript:

* Annual Reports: 2022 is first and 2023 second;
* ICR: 2023 is third, with stronger late cuts;
* PAD: 2023 is fourth, with stronger 2024–2025 cuts.

It is therefore accurate to say that **high-ranked candidate cuts are concentrated near the end of the period**. It is not accurate to infer a ramped process from those ranks.

The comparability caveat does not hold up merely because the "same specification" was used. Different cut dates imply:

* different numbers of post observations;
* different leverage of individual years;
* different estimands for the slope-change component;
* different effective HAC behavior;
* overlapping alternatives that are strongly dependent.

Fewer post years do not mechanically guarantee a larger statistic, but they materially change its sampling distribution and sensitivity to endpoints. Raw ranks are therefore descriptive, not a calibrated comparison.

There is also a specific audit question: the Annual Report scan reports **72 candidate cuts for 71 observed fiscal-year units**. Because the level-only model partitions observed years into pre/post sets, the implementation should demonstrate that calendar cuts falling around missing years do not generate duplicate or near-duplicate partitions. At minimum, report the number of **unique design matrices**, not merely candidate calendar dates.

**Required repair:**

1. Deduplicate candidate cuts by unique pre/post partition.
2. Report `n_pre`, `n_post`, coefficient, standard error and confidence interval for every candidate.
3. Use a common trimmed candidate interval with a meaningful minimum post window.
4. Apply a sup-Wald/QLR-style unknown-break test with finite-sample or bootstrap critical values.
5. Compare explicit models: no change, level step, slope change and ramp.
6. Show a controlled institution-by-event-time trajectory once IMF is available.

Unknown-break procedures require adjustment because the breakpoint is unidentified under the null; raw pointwise rankings are not a substitute. Andrews provides the canonical unknown-change-point framework, and Bai–Perron provides the multiple-break methodology.

For Annual Reports, none of these methods creates information that is not present. With only 2023 and 2024 after the focal date, the post-period result should remain **descriptive endpoint evidence**.

### 5.2 QC gate

**Is it defensible as prespecified? No.**

It was calibrated after inspection of the same 73 units it filters. The manuscript explicitly states that an external audit first discovered FY2002 and FY2007 and that the gate was imposed as a consequence.

The gate may nevertheless be defensible as an **audit-derived deterministic quality rule** because the observed separation is large:

* legitimate units: at least 17,000 tokens and at least 20% function-word share;
* defective units: at most 0.9% function-word share, with FY2002 only 12 tokens.

The clean wording is:

> "Following a blinded external audit, we defined and froze an extraction-quality gate before regenerating all outcome analyses."

However, the function-word-share criterion is outcome-adjacent. One reported outcome is the rate of **"and,"** itself a function word. Conditioning inclusion on function-word prevalence can create a selection relationship with the feature under study, even if the threshold is far below all legitimate observations.

The required sensitivity package is:

* threshold grid for token count and function-word share;
* results under token-count-only QC;
* results using independent extraction-quality indicators such as alphabetic-character share, sentence yield, table density or line-length structure;
* blind manual audit of all exclusions and the lowest-quality retained units;
* application of the frozen rule to the IMF corpus without recalibration;
* proof that no result changes over the wide interval separating legitimate and defective units.

### 5.3 Leave-word-out and concentration

The result does **not** fully defuse concentration.

The manuscript reports:

* underscore family: 43%;
* pivotal: 15%;
* combined: **58%** of post-period Tier-1 mass.

Removing both and retaining ratios above 2× shows that the finding is not literally generated by those two entries alone. It does not show that the remainder is a coherent, specific or externally valid LLM-associated construct.

Three issues remain:

1. **Ratios can be large when the baseline is nearly zero.** Absolute rate differences, counts and uncertainty are required.
2. **Morphological duplication inflates a lexical family.** `underscore`, `underscores`, `underscored` and `underscoring` should not be treated as independent confirmatory evidence.
3. **Domain transfer remains untested.** Words found to be LLM-associated in scientific writing may have long-standing bureaucratic meanings in World Bank prose.

A valid confirmatory Tier-1 should be defined independently of the World Bank outcomes, collapsed to lemma/semantic families, and frozen before comparator analysis. Report:

* leave-family-out rather than only leave-word-out;
* top-1/top-2/top-3-family deletion;
* Herfindahl concentration or effective lexicon size;
* absolute pre/post counts and rate differences with intervals;
* document prevalence, not only total token frequency;
* stratified concordance samples;
* external specificity in comparable pre-ChatGPT institutional corpora.

Until then, Tier-1 is an **exploratory lexical index**, not a confirmatory fingerprint.

## 6. Weakest remaining link and cheapest strengthening analysis

### Weakest link

The weakest link is the **counterfactual and mechanism link between late-period textual change and World Bank LLM adoption**.

Primary World Bank sources can establish that the institution experimented with GPT-based evaluation and later operated enterprise generative-AI capabilities. They do not establish that the sampled Annual Reports, ICRs or PADs were drafted with those tools, nor when assistance entered each genre. That is an inference, not direct provenance.

The remaining alternatives include:

* leadership change;
* style-guide revision;
* document-template revision;
* sector and region composition;
* thematic change;
* extraction-format change;
* human uptake of newly fashionable vocabulary.

### Cheapest useful analysis

Estimate a **document-level, composition-adjusted controlled count model** using the IMF comparison:

Tier1Count_d ~ institution + time + post/ramp + institution×post/ramp + genre + region + sector + instrument + template era + extraction method + offset(log tokens_d)

Use Poisson quasi-maximum likelihood or negative binomial sensitivity, with inference robust to institution-year clustering and small numbers of time clusters. Standardize or reweight the World Bank and IMF document cells to a common observed composition.

What would strengthen the paper:

* parallel or near-parallel pre-period controlled trajectories;
* a positive World Bank-by-post or World Bank-by-ramp interaction;
* stability after sector, region, template and extraction adjustment;
* similar direction across genuinely comparable genres;
* no single year or lexical family carrying the interaction.

What would weaken it:

* disappearance after composition standardization;
* a similar or larger IMF increase;
* an effect confined to extraction method or template era;
* pre-period differential trends;
* an interaction driven by 2023 alone.

### Ranked referee action list

1. **Supply the actual response memo and regenerated robustness files; otherwise the formal round-2 audit is irreproducible.**
2. **Estimate the composition-adjusted controlled IMF model and freeze its primary interaction before inspecting results.**
3. **Replace raw breakpoint rankings with calibrated unknown-break and explicit step-versus-ramp analyses.**
4. **Rename and validate the QC gate; execute threshold and extraction-method sensitivities.**
5. **Redefine Tier-1 at the family level and report absolute effects, uncertainty, concentration and concordance.**
6. **Execute multiplicity correction; do not describe an outcome selected after examining World Bank results as confirmatory.**
7. **Treat Annual Report post-2022 inference as descriptive unless more post-period years become available.**
8. **Use "reference-model NLL," and remove any suggestion that Pythia is a pre-LLM or pre-2022 model.**

---

# Reference audit (round 2) — summary of outcome

All 25 bibliography entries were independently resolved and **VERIFIED** (23 DOI-bearing
works; two DOI-less proceedings records: Juzek & Ward COLING 2025, Mitchell et al. PMLR
202). No unresolvable entries; no author/year/venue mismatches. Two material corrections:
(1) split the Stanford-pamphlet and NLR manifestations of Moretti & Pestre — the DOI
belongs to the NLR version; (2) cite the López Bernal corrigendum (10.1093/ije/dyaa118)
alongside the 2017 ITS tutorial and verify the code uses the corrected centered
interaction. The prompt's count ("25 DOI entries plus two additional proceedings") was
wrong; the correct count is 25 total = 23 + 2.

Module-fit warnings: Barnett/Finnemore and Mosse are conceptual, not quantitative-methods
validation; excess-vocabulary studies (Kobak, Liang, Juzek/Ward) do not establish domain
specificity in World Bank prose or authorship identification; GLTR/DetectGPT/detector
benchmarks justify restraint, not "convergent detection," and do not validate annual mean
NLL; the ITS module lacks unknown-break inference and controlled-comparison sources; FAIR
and reproducibility citations do not establish sampling or construct validity.

Eight verified must-cite additions (all high confidence): Andrews 1993 *Econometrica*
(10.2307/2951764); Bai & Perron 2003 *J. Applied Econometrics* (10.1002/jae.659); Linden
2015 *Stata Journal* (10.1177/1536867X1501500208); Bottomley et al. 2019 *Epidemiologic
Methods* (10.1515/em-2018-0010); Benjamini & Hochberg 1995 *JRSS-B*
(10.1111/j.2517-6161.1995.tb02031.x); Grimmer & Stewart 2013 *Political Analysis*
(10.1093/pan/mps028); Egami et al. 2022 *Science Advances* (10.1126/sciadv.abg2652);
Zuiderwijk, Chen & Salem 2021 *GIQ* (10.1016/j.giq.2021.101577).

Ranked reference-audit actions: (1) write Section 2 as a claim-to-source argument; (2) add
the unknown-break / controlled-ITS / multiplicity / text-validity works before
interpreting the scan or comparator; (3) add GIQ-specific public-governance theory;
(4) replace WB-adoption placeholders with primary sources and state exactly what they do
and do not establish; (5) split Moretti/Pestre; (6) cite the López Bernal corrigendum and
check s08; (7) prevent scope inflation (detectors ≠ mean-NLL validation; FAIR ≠ corpus
validity; excess vocabulary ≠ authorship); (8) normalize style last.
