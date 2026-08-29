# PREREG — Comparator round (DRAFT v0.3, 2026-08-09)

**Status: revised after the round-4 external review (REJECT WITH REQUIRED CHANGES); NOT
frozen.** v0.1 and v0.2 are withdrawn and archived. All twelve round-4 required changes
are addressed here; the freeze remains two-stage (§11) with external timestamps.
Post-freeze deviations are logged in `DESIGN_RATIONALE.md` and demote the affected
result to exploratory.

## 0. Epistemic status (unchanged from v0.2; E17)

Prospective only with respect to comparator data; outcome-informed on the World Bank
side (the 2023 cut, the Tier-1 lexicon, and the panel structure postdate observation of
WB outcomes). This is a *prospective external-comparator validation of an already
observed WB pattern*. Confirmatory interpretation is restricted to comparator
replication; "LLM-associated construct validity" remains exploratory. Where a design
constant below is informed by observed WB magnitudes (the MDE gate of §8), that
dependence is stated at the point of use rather than hidden.

## 1. Claims (mechanism-neutral; unchanged from v0.2)

- **H-DIFF (only confirmatory claim):** a differential post-2022 change between the
  prespecified WB and IMF series in the frozen lexical outcome; **mechanism
  unresolved.** Never described as enterprise-LLM-adoption evidence.
- **H-SHARED (descriptive companion):** the IMF's own pre/post change with CI; a
  similar IMF rise nulls H-DIFF while remaining informative about a shared post-2022
  shift. Reported separately, never conflated.
- Fixed success-language template: *"a differential post-2022 change between the
  prespecified WB and IMF series in the frozen lexical outcome; mechanism unresolved."*

## 2. Panels and the deterministic branch rule (round-4 required change 2)

**Default co-primary family:** P1 = WB ICR vs IMF Article IV; P2 = WB PAD vs IMF
Article IV. Article IV remains a **non-equivalent falsification comparator**
(institution and genre confounded); interpretation capped accordingly.

**P0 branch (single genre-matched primary), decided at Stage-B on metadata only, under
a fully deterministic rule:**

1. **Fixed candidate priority, no merging:** (1) Country Economic Memorandum,
   (2) Systematic Country Diagnostic, (3) Country Partnership Framework — exact `docty`
   strings as returned by s00 facet discovery, recorded verbatim before probing.
   Candidates are never combined across labels or successor series. The first candidate
   in priority order that passes ALL gates below becomes P0; later candidates are not
   evaluated further. (Note recorded in advance: SCD and CPF series begin circa
   2014–15 and are therefore expected to fail gate G2 by construction; the priority
   order makes the branch effectively CEM-or-nothing.)
2. **Gates (ALL required, metadata only):**
   - **G1 Genre adjudication:** a blind title/abstract audit of 20 candidate documents
     drawn with the per-cell seeded sampler (§Appendix B.7) against a fixed four-item
     checklist — recurring country-level macroeconomic surveillance; not tied to a
     single project or operation; staff-authored analytical report; periodic cycle.
     PASS requires ≥16/20. Conducted on titles/abstracts only, before any
     year-by-outcome information is viewed.
   - **G2 Coverage:** ≥25 usable pre-2023 common years (calendar years with ≥1 eligible
     document in BOTH the candidate genre and Article IV) and ≥3 completed post years
     (2023–2025).
   - **G3 Metadata support:** ≥80% of post-period candidate **documents** lie in
     country cells with support in both institutions (token support is a post-harvest
     locked condition, §6 — token information is never used to choose the branch).
   - **G4 Power:** the §8 simulation, run on the candidate's metadata cell counts,
     yields MDE₈₀ ≤ 0.60 log points.
3. **One-way switch:** if a candidate passes, the Holm family is frozen at the SAP as
   {P0} and P1/P2 become falsification analyses. If no candidate passes, the family is
   frozen as {P1, P2}. **After the SAP freeze there is no switchback in either
   direction:** if P0 later fails any locked analysis condition, the confirmatory claim
   fails; P1/P2 are reported as falsification analyses and are never promoted
   post-hoc. The "no active primary" state cannot arise: the family frozen at the SAP
   is the family, and a post-SAP failure is a failed confirmatory outcome, not a
   family re-selection.

**P-A (Annual Reports): descriptive only. NLL: exploratory only** (pending §7
regeneration). There is no secondary confirmatory family.

## 3. Outcome and validation outcomes (round-4 required changes 7, 9; §7 ruling adopted)

- **Confirmatory outcome (unchanged): the family-occurrence count.** For document d,
  `count_d` = number of token occurrences matching any of the 28 forms under the single
  matching rule of Appendix A (there is exactly one rule; the v0.2 §3 `\b` wording is
  deleted). Aggregated under the fixed 28→13 mapping; the total is invariant to family
  relabeling, as already stated. Round-4's ruling that switching to breadth/prevalence
  now would itself be an outcome-informed primary change is adopted: occurrence count
  stays primary.
- **Concentration guard (fixed now, per round 4):** the mandatory guard family is
  **underscore** — already known to dominate on the WB side (43.48% of post-period
  hits). Condition 3 of §5 refits the primary model with the underscore family removed
  from the outcome. A prespecified non-gating stress test additionally removes
  underscore+pivotal jointly. The full leave-each-family-out profile is exploratory.
  No guard family is ever selected from unseen post-period outcomes.
- **Mandatory validation outcomes (defined models; reported alongside every
  confirmatory result):**
  - **Document prevalence:** doc-level indicator of ≥1 Tier-1 family occurrence;
    logistic regression with the §4 design (numeric WB indicator, C(year), WB
    differential trend, WB×post) plus `log tokens` as covariate; CI by delete-one-year
    jackknife over the common-year sequence.
  - **Family breadth:** number of distinct families present per document (0–13),
    modeled as **quasi-binomial** (13 trials; overdispersion-robust — the plain
    binomial assumption is not imposed) with the same design and `log tokens`
    covariate; same jackknife CI.
  - **Consistency rule (prespecified):** if either validation outcome's WB×post
    estimate has the opposite sign with a CI excluding 0, any confirmatory H-DIFF
    claim is downgraded to "count-specific" and reported as such.

## 4. Primary model and inference (round-4 required changes 3, 4)

### 4.1 Estimable model (explicit numeric coding)

Define `WB_i ∈ {0,1}` (1 = World Bank; IMF is the reference institution). Analysis
cells are institution×year over the **frozen common-year sequence** Y = (t₁ < … < t_T):
calendar years in the panel span with one eligible cell in BOTH institutions
(recorded verbatim at the SAP; calendar gaps permitted). `c_year = year − m`, where m
is the median calendar year of Y (recorded at the SAP). `post = 1{2023 ≤ year ≤ 2025}`
(§11.4: 2026 is excluded from the confirmatory frame entirely).

Frozen estimable form (statsmodels GLM Poisson, patsy formula given verbatim):

    Count ~ C(year) + WB + WB:c_year + WB:post

with `offset = log(Tokens)` and `WB` a numeric 0/1 column (never a factor). The
intercept plus C(year) dummies absorb common year effects; there are no standalone
`post` or `c_year` main effects (collinear with C(year) and intentionally absent).
The design has exactly T + 3 columns: intercept, T−1 year dummies, WB, WB·c_year,
WB·post. **Estimand:** the coefficient on `WB:post`, on the log-rate scale; positive =
the WB post-2022 change exceeds the IMF's. NB2 with the same design is the
overdispersion sensitivity. Prespecified display: the event-study variant replacing
WB:c_year + WB:post with WB × 3-year-bin indicators (reference bin = the bin containing
m).

### 4.2 Primary inference: fixed-design, null-imposed, paired-year residual block
bootstrap (executable specification)

1. Fit the **restricted model** M⁰ (the §4.1 formula without `WB:post`) by Poisson QML
   on the observed cells; obtain fitted means μ̂⁰_it.
2. Pearson residuals r_it = (y_it − μ̂⁰_it) / √μ̂⁰_it; paired vectors
   R_k = (r_{WB,t_k}, r_{IMF,t_k}) indexed by **position k = 1…T in Y** (blocks are
   defined on index positions, never on raw calendar years, so gaps cannot break
   blocks).
3. **Circular moving blocks:** block length ℓ = 3 over positions 1…T with wrap-around;
   draw ⌈T/3⌉ block start positions uniformly with replacement (replicate b uses seed
   20260806 + b), concatenate, truncate to length T → resampled paired sequence R*.
   Pairs always move together; the design matrix (C(year), c_year, post, offsets) stays
   **fixed** at its original calendar positions — the intervention design is never
   resampled.
4. Pseudo-counts y*_it = max(0, round(μ̂⁰_it + √μ̂⁰_it · r*_it)); the fraction of
   floored-at-zero cells is reported.
5. Refit the **full** §4.1 model on y* → β*_b (the WB:post coefficient).
   B = 9,999 replicates. Non-converged replicates are dropped and counted; if >1% fail,
   escalate to the prespecified fallback: random sign-flip of the paired residual
   blocks (same seeds, same B) instead of block resampling.
6. **p-value (two-sided, finite-sample corrected):**
   p = (1 + #{|β*_b| ≥ |β̂|}) / (B_valid + 1), with β̂ from the full model on observed
   data. **CI:** basic bootstrap, [2β̂ − q_{0.975}(β*), 2β̂ − q_{0.025}(β*)].
7. **Reuse rule:** the identical algorithm (same seeds, same ℓ, same B) is used for
   NB2 (residuals from the restricted NB2 fit), the standardized variant (§6; weights
   fixed across replicates), the concentration-guard fit (§3), and every LOPO fit
   (the deleted year is removed from Y before blocking).

Secondary sensitivity: HAC(3) OLS on the annual paired log-rate difference
d_k = log((y_{WB,t_k} + 0.5)/Tokens_{WB,t_k}) − log((y_{IMF,t_k} + 0.5)/Tokens_{IMF,t_k})
regressed on {1, c_year, post} — the +0.5 continuity constant is the frozen zero-count
rule. Document-level Poisson QML with institution×year clustering is a reported
sensitivity only.

## 5. Decision rule, global success, and multiplicity families (round-4 required
change 5)

**Holm family, frozen at the SAP:** {P0} if the branch passed, else {P1, P2}; α = 0.05
(smaller p tested at 0.025, larger at 0.05 in the two-panel case).

All four conditions required, per panel:

1. Holm-adjusted §4.2 bootstrap p < 0.05 for `WB:post`.
2. **Stability:** |β_variant − β_M2| / |β_M2| < 0.50 on the log-rate scale, AND sign
   unchanged AND 95% basic-bootstrap CI excluding 0, under BOTH NB2 and the
   standardized variant. NB2 non-convergence ⇒ delete-one-year jackknife CI on QML;
   if that also fails, condition 2 fails.
3. **Concentration guard:** underscore-removed refit retains sign with 95% CI
   excluding 0.
4. **LOPO:** for each post-year deletion (2023, 2024, 2025 — three deletions), the
   refit retains sign and has **unadjusted** §4.2 bootstrap p < 0.10. This is a
   per-panel stability condition, explicitly NOT a Holm family; its p-values come from
   the same bootstrap algorithm.

**Global success rule (explicit):** the confirmatory H-DIFF claim is panel-specific
and is made for every family panel that passes all four conditions at its Holm level.
The headline claim "a differential post-2022 change was confirmed" is permitted iff
≥1 family panel passes; if exactly one of {P1, P2} passes, the claim names that panel
and reports the other panel's estimate and CI in the same sentence. Failure of any
condition in a panel ⇒ no confirmatory claim for that panel; results reported
descriptively with the failed condition named.

## 6. Composition standardization (exact; round-4 required change 6)

- **Common ontology (fixed at Stage-B, metadata only):** country (ISO3), region (WB
  grouping applied to both institutions), income group (WB fiscal-year classification,
  year-matched), calendar year. WB-only fields (sector, instrument) are excluded from
  the cross-institution model by design and used only WB-internally; stated, not
  silently dropped. A document with a missing ontology field is assigned to an explicit
  `unknown` cell, which counts as unsupported (conservative). Multi-country documents
  cannot occur (frame rule, Appendix B.4).
- **Target distribution** π_g: the pooled pre-2023 **document** distribution over
  country-region-income cells g, across both institutions, on common-support cells.
- **Weights:** document-level w_d = π_{g(d)} / p̂_{i(d),g(d)}, where p̂ is institution
  i's own pre-2023 document share of cell g. Truncation: at the 99th percentile of the
  pooled w_d distribution (both institutions, both periods, computed once), then
  renormalized to mean 1 within each institution×period. Weighted cell aggregates
  Ỹ_it = Σ w_d y_d and T̃okens_it = Σ w_d tokens_d replace the §4 cell inputs; the §4.2
  bootstrap is re-run on the weighted cells with **weights fixed across replicates**
  (weights are part of the frozen design, not re-estimated).
- **ESS floor:** ESS = (Σw)²/Σw² over documents, computed per institution×period; the
  floor is ESS ≥ 0.50 × (that institution×period's document count). Below floor ⇒ the
  standardized variant is infeasible ⇒ condition 2 fails.
- **Support:** Stage-B gate on documents (§2 G3). Post-harvest locked condition on
  tokens: ≥80% of post-period tokens in each institution must lie in common-support
  cells; below ⇒ condition 2 fails. Excluded zero-support cells and their token shares
  are reported. Fields are never dropped to rescue the analysis.

## 7. Document eligibility (round-4 defect 13 repaired)

- Lexical counts: tokens ≥ 1 under the Appendix-A tokenizer (the six current WB
  zero-token records are excluded everywhere and logged).
- NLL (exploratory): tokens ≥ 100 under the same tokenizer, applied in code before
  model scoring and aggregation; missing model output ⇒ excluded from that model's
  panel and counted; no constant or imputed values (the five GPT-2 5.8744 records are
  purged on regeneration); one frozen document-sampling rule applied identically on
  every device (the hardware-dependent CPU subsample is abolished).
- **Duplicates/versions (corrected):** the v0.2 sentence "existing repnb/volnb rules
  applied identically to IMF" is deleted — those are WB Annual-Report assembly fields
  only. WB ICR/PAD: one unit per D&R document id (the frame already samples unique
  ids; no version system applies). IMF: one unit per Country Report number, latest
  revision, per Appendix B.5.
- Assembled annual units: the QC gate (≥5,000 tokens AND ≥0.15 stopword share, 15-word
  frozen list, hash in Appendix A) transfers to IMF annual units unchanged.
- Intention-to-sample reporting: sampled → downloaded → nonzero → eligible, per
  institution×genre×year, in every analysis output.

## 8. Interaction MDE simulation (round-4 required change 10)

- **Scale:** the WB:post coefficient in log points. **Post years:** 3 (2023–2025).
- **DGP:** for each common-year cell, Poisson counts with
  log μ_it = a_i + γ_t + b_i·WB_i·c_year + θ·WB_i·post + log Tokens_it. Year effects
  γ_t follow AR(1) with ρ = 0.5 and innovation variance set by method-of-moments to
  match the observed WB pre-2023 cell-level deviance dispersion; a_i and Tokens_it
  from observed data (P1/P2) or metadata-projected tokens (P0: candidate document
  counts × the WB mean tokens-per-document of the nearest genre); b_i = 0 in the base
  scenario, with a ±0.01/yr differential-trend scenario as sensitivity; IMF baseline
  rate at parity with the WB pre-2023 rate.
- **Decision replication:** θ grid 0.00–1.20 by 0.05; 1,000 simulated datasets per θ.
  The full nested §4.2 bootstrap is approximated by the studentized Wald statistic
  whose critical value is calibrated once from 200 full nested bootstrap runs at θ = 0
  (calibration procedure and seed 20260806 fixed); Holm applied exactly as in §5.
- **Outputs and gates:** MDE₈₀ = smallest θ with ≥80% rejection. Branch gate G4:
  MDE₈₀ ≤ 0.60 log points — a WB-informed constant (≈ two-thirds of the smaller
  observed WB co-primary shift, ICR ≈ 0.90 log points), declared as such under §0.
  Active-panel gates: ≥25 usable pre-2023 cells and ≥3 post cells per institution;
  failure demotes that panel to descriptive. Simulation code is a Stage-A release
  precondition (§11.2).

## 9. Interpretation matrix (δ gate removed; round-4 required change 8)

The MDE-derived δ pretrend gate is **removed from the confirmatory decision rule**
(round-4 option 1 adopted). Instead:

- The differential-trend estimate `WB:c_year` is reported with its 95% CI in every
  confirmatory output, prominently.
- Two **fixed, non-gating sensitivity analyses**: (a) trend-form — the §4.1 event-study
  variant, with the WB:post-window effects read against the pre-window bins; (b) a
  placebo cut at 2016 estimated on pre-2023 common years only (expected null;
  reported).
- Fixed interpretive lines: IMF post/pre ratio ≥ WB's ⇒ H-DIFF null, reported as
  compatible with a shared shift (H-SHARED), not as generic evidence against an
  LLM-era reading. Condition-2 failure under standardization ⇒ composition explanation
  favored. Text-only subsample interaction losing sign or CI covering 0 ⇒ extraction
  explanation flagged. A differential-trend CI excluding 0 with |trend × post-window|
  comparable to the WB:post estimate ⇒ reported as a first-order extrapolation threat
  in the same paragraph as the estimate (no hard gate).

## 10. Exploratory blocks, per branch (round-4 required change 11)

BH q = 0.05 within each block; two-sided; families are branch-specific and frozen at
the SAP.

- Family {P1, P2}: X1 classic features 7×2 = 14; X2 Tier-2 ×2 = 2; X3 NLL 2 models
  ×2 = 4 (only after §7 regeneration); X4 prevalence + breadth ×2 = 4.
- Family {P0}: X1 = 7; X2 = 1; X3 = 2; X4 = 2; plus P1/P2 falsification interactions
  reported with unadjusted CIs, labeled falsification (not members of any test block).
- **XW (WB-internal locked robustness, runs after the SAP under frozen rules):**
  deduplicated breakpoint scan with full support columns; **sup-Wald/QLR unknown-break
  test with bootstrap critical values — an inferential test with its own error rate,
  reported as exploratory inference (the v0.2 "no-error-rate descriptive" label is
  withdrawn)**; step-vs-ramp BIC + bootstrap LR comparison; QC threshold grid,
  token-only and independent-indicator QC variants, "and" independent-QC sensitivity;
  extraction-method covariate/interaction and text-only fits;
  missingness-by-year×format model. Descriptive diagnostics without error rates: HHI,
  family shares, prevalence tables, event-study plots.

## 11. Freeze protocol, calendar rule, and go/no-go (round-4 required changes 1, 12)

1. **Stage-A (acquisition preregistration):** freeze Appendix A (mapping + matching
   rule + stopword hash), Appendix B (the full acquisition protocol), the eligibility
   rules (§7), immutable model revision hashes (replacing `revision: main`), and the
   per-cell seeded sampler. External timestamp (OSF registration of the frozen PDF;
   fallback Zenodo/OpenTimestamps) BEFORE any IMF metadata access.
2. **Stage-A code preconditions (must exist before the timestamp; round-4 editor list
   adopted):** machine-readable 28→13 mapping in config/source with unit tests
   (including the `seamlessly` case); exact integer outputs `tier1_count`,
   per-family counts, `eligible_tokens`; the stable per-cell seed sampler
   (seed_cell = SHA256(master_seed | institution | genre | year)); provenance schema
   with `sampling_version`, `run_id`, `analysis_eligible`, source/version identifiers,
   branch/panel labels; the §4.2 bootstrap and §8 simulation code skeletons.
3. **Stage-B (metadata only; text and outcomes sealed):** facet probes and the §2
   deterministic branch decision; the §6 ontology and document-support diagnostics;
   the §8 MDE runs; the frozen common-year sequences. Ends with the final SAP (this
   document, every Stage-B constant filled), externally timestamped. Only then: text
   download and feature processing.
4. **Calendar rule (2026):** the confirmatory post window is the completed years
   **2023–2025** (three post cells; meets the ≥3 gate). Calendar-2026 is excluded from
   the confirmatory frame (Appendix B cutoff: publication date ≤ 2025-12-31). A
   prespecified **descriptive update** uses a second frame snapshot on 2027-01-15
   covering full calendar-2026; it is reported in an appendix and never pooled into
   any confirmatory analysis. The August-2026 partial year is never counted as a post
   cell.
5. **Go/no-go (round-4 editor rule adopted):** hard Stage-B deadline **31 October
   2026** — Stage-A frozen, branch decided, support and MDE diagnostics complete, SAP
   frozen. The RQ1/measurement-paper fallback triggers iff **neither branch** ({P0}
   nor {P1, P2}) survives the Stage-B gates by that date; P0 failing its gates alone
   is not a fallback trigger (the family is then {P1, P2}). No comparator rescue work
   after 31 October 2026.

## 12. Out of scope

Mechanism/authorship (D2); WB press releases (D8); UNGDC (hard firewall); AR
confirmatory claims; NLL confirmatory claims; any 2026 confirmatory use.

## Appendix A — Outcome definition artifacts (frozen at Stage-A)

**28→13 family mapping** (verbatim; machine-readable copy in config, content-hashed):

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

**The single matching rule** (the only rule; used everywhere): text lowercased;
tokenized with `[A-Za-z']+` (`src/textstats.py` TOKEN_RE); a hit is exact token
membership in the 28-form set; repeated occurrences counted; no lemmatization. Known
consequences accepted and frozen: `pivotal's` tokenizes to `pivotal's` and does NOT
count; `pivotalé` tokenizes to `pivotal` and DOES count. QC stopword share uses the
same tokenizer with the frozen 15-word list in `src/s10_assemble_ar.py`
(sha256 of the sorted newline-joined list:
`3b5d2b51754f73011aeb20ce28bcfcdeb2908ea9380d3d49decf6ee2bb22c41a`).

## Appendix B — Stage-A acquisition protocol (round-4 required change 1)

1. **Sources.** IMF Article IV staff reports: the *IMF Staff Country Reports* series —
   catalog anchors: IMF eLibrary series listing (elibrary.imf.org, series 002,
   volume = year, issue = report number) and the imf.org rolling list
   "Article IV Staff Reports" (imf.org/en/Publications/SPROLLs/Article-iv-staff-reports);
   secondary frame-verification mirror: RePEc `imf/imfscr`. IMF Annual Reports (P-A
   descriptive only): imf.org Annual Report archive. The exact query strings /
   navigation paths executed are captured verbatim into the frozen Stage-A record at
   execution, with page-count and per-year record-count logs.
2. **Inclusion (Article IV frame).** Series = IMF Staff Country Reports; title
   contains "Article IV Consultation"; language English; publication year 1994–2025
   (P1 span; the P2 common-year sequence starts 1996). Combined reports (Article IV
   plus program reviews in one Country Report) are IN frame with a recorded flag
   `combined_with_program` = title contains "Review Under" or "Arrangement";
   a prespecified sensitivity re-estimates excluding flagged documents.
3. **Exclusion.** Selected Issues papers; standalone press releases, statements,
   supplements, corrigenda; Financial System Stability Assessments; any report whose
   title lacks "Article IV Consultation".
4. **Unit, country, and year.** One unit per Country Report number (the combined
   publication is the unit). Country: the single ISO-3166 entity named before the
   colon in the title; titles naming a currency union, region, or multiple countries
   are excluded (deterministic single-country rule). Year: the publication (cover)
   date year.
5. **Versions and duplicates.** One unit per Country Report number; where a
   corrigendum or revised issue shares the base number, the latest revision at the
   frame snapshot is kept and the supersession is logged.
6. **Frame and cutoff.** A complete metadata listing per year is captured and hashed
   at the Stage-B snapshot date (recorded); confirmatory cutoff: publication date
   ≤ 2025-12-31. The 2027-01-15 snapshot (§11.4) builds the 2026 descriptive frame
   under identical rules.
7. **Sampling.** Cap 40/year/genre by the stable per-cell sampler:
   seed_cell = SHA256("20260806|{institution}|{genre}|{year}") → 64-bit int seeding an
   independent RNG per cell; adding or removing any other stratum cannot change a
   cell's draw. Frozen sampling CSV, write-once, with the append-only SHA256 manifest.
8. **Retrieval and logging.** Text URL preferred where the source offers text;
   otherwise PDF with PyMuPDF extraction; per-document logging of method, source
   identifiers, `sampling_version`, `run_id`, `analysis_eligible`, branch/panel
   labels; failures retried across resumable passes and reported in the
   intention-to-sample table.
9. **Metadata retained for Stage-B:** title, country, series, report number,
   publication date, department, language, URL(s), DOI where present.
